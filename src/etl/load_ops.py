"""② load_ops.py – pha LOAD của schema ops (tác nghiệp) và tệp hồ sơ lỗi.  BT2 (buổi 12), TD-22.

Mọi câu lệnh đọc/ghi schema ops nằm ở đây; extract.py, transform.py, dq_evaluate.py, match.py chỉ còn hàm
THUẦN (không import sqlalchemy, không có câu SQL) – tests/test_ranh_gioi_lop.py giữ ranh giới này.

    pha E  extract.py      đọc tệp nguồn, kiểm cột, SHA-256                       (không CSDL)
    pha T  transform.py    chuẩn hóa, mã lỗi, phân loại; match.py tìm cặp        (không CSDL)
           dq_evaluate.py  6 hàm kiểm chất lượng                                  (không CSDL)
    pha L  load_ops.py     ghi/đọc schema ops, CSV hồ sơ lỗi                       ← tệp này
           load_dwh.py     nạp kho dwh từ ops

Mỗi hàm nhận `conn` của giao dịch do src/pipeline.py mở (`with engine.begin()`), nên lỗi ở bất kỳ hàm nào
làm ROLLBACK cả use case (TD-09). Hàm chỉ chạy lệnh SQL, không quyết định nghiệp vụ: dữ liệu ghi vào đã được
pha T tính sẵn.
"""
import pandas as pd
from sqlalchemy import text

# Bảng đích của luồng chính – in số dòng trước/sau mỗi lần chạy để thấy chạy lại không nhân đôi (C5)
BANG_DICH = ('ops.load_batch', 'ops.stg_customer', 'ops.customer_clean', 'ops.dq_result', 'ops.dup_candidate',
             'dwh.dim_batch', 'dwh.fact_dq_check', 'dwh.fact_dup_pair')


# ------------------------------------------------------------------ UC1 – đợt nạp, hồ sơ thô (FR-01)
def tim_dot_cung_tep(conn, file_hash: str) -> list[tuple]:
    """Các đợt đã nạp có cùng giá trị băm (AC1.4: cảnh báo, chỉ nạp khi người dùng xác nhận)."""
    rows = conn.execute(text('SELECT batch_id, file_name, loaded_at FROM ops.load_batch '
                             'WHERE file_hash = :h ORDER BY batch_id'), {'h': file_hash})
    return [tuple(r) for r in rows]


def ghi_dot_nap(conn, file_name: str, file_hash: str, source_unit: str, row_count: int, loaded_by: str) -> int:
    """Tạo một dòng ops.load_batch (FR-01) và trả về batch_id; loaded_at do CSDL ghi (DEFAULT now())."""
    return conn.execute(text(
        'INSERT INTO ops.load_batch (file_name, file_hash, source_unit, row_count, loaded_by) '
        'VALUES (:f, :h, :u, :n, :by) RETURNING batch_id'),
        {'f': file_name, 'h': file_hash, 'u': source_unit, 'n': row_count, 'by': loaded_by}).scalar_one()


def ghi_ho_so_tho(conn, batch_id: int, bang_tam: pd.DataFrame) -> int:
    """Ghi hồ sơ thô với status = LOADED; trả về số dòng đã ghi (phải bằng row_count)."""
    df = bang_tam.assign(batch_id=batch_id, status='LOADED')
    df.to_sql('stg_customer', conn, schema='ops', if_exists='append', index=False,
              chunksize=5000)   # SQLAlchemy 2 gộp nhiều dòng vào một lệnh INSERT (insertmanyvalues)
    return conn.execute(text('SELECT count(*) FROM ops.stg_customer WHERE batch_id = :b'),
                        {'b': batch_id}).scalar_one()


def co_dot(conn, batch_id: int) -> bool:
    return conn.execute(text('SELECT 1 FROM ops.load_batch WHERE batch_id = :b'), {'b': batch_id}).first() is not None


# ------------------------------------------------------------------ UC1 – kết quả chuẩn hóa (FR-02, FR-10)
def lay_so_dang_hieu_luc(conn) -> set[str]:
    """Số điện thoại của mọi hồ sơ đang hiệu lực (QT-01 so trên toàn bộ customer_clean, không chỉ đợt này)."""
    return {r[0] for r in conn.execute(text('SELECT phone FROM ops.customer_clean WHERE is_active'))}


def ghi_ket_qua_chuan_hoa(conn, batch_id: int, df: pd.DataFrame) -> int:
    """Cập nhật phone_norm, name_norm, error_code, status của đợt bằng MỘT lệnh UPDATE … FROM bảng tạm thời."""
    conn.exec_driver_sql(
        'CREATE TEMP TABLE tmp_chuan_hoa (row_no INT PRIMARY KEY, phone_norm CHAR(10), '
        'name_norm VARCHAR(120), error_code VARCHAR(20), status VARCHAR(12)) ON COMMIT DROP')
    df[['row_no', 'phone_norm', 'name_norm', 'error_code', 'status']].to_sql(
        'tmp_chuan_hoa', conn, if_exists='append', index=False, chunksize=5000)
    return conn.execute(text(
        'UPDATE ops.stg_customer s SET phone_norm = t.phone_norm, name_norm = t.name_norm, '
        'error_code = t.error_code, status = t.status '
        'FROM tmp_chuan_hoa t WHERE s.batch_id = :b AND s.row_no = t.row_no'), {'b': batch_id}).rowcount


def ghi_customer_clean(conn, batch_id: int) -> int:
    """FR-02: hồ sơ CLEAN của đợt → customer_clean, rồi gắn customer_id ngược lại cho hồ sơ thô (truy vết).
    Chỉ mục duy nhất từng phần ux_customer_clean_phone_active là lưới an toàn cuối cùng cho QT-01:
    nếu hai người nạp cùng lúc cùng một số, lệnh INSERT thứ hai lỗi và cả đợt ROLLBACK."""
    n = conn.execute(text(
        "INSERT INTO ops.customer_clean (full_name, phone, email, address) "
        "SELECT name_norm, phone_norm, NULLIF(BTRIM(email_raw), ''), NULLIF(BTRIM(address_raw), '') "
        "FROM ops.stg_customer WHERE batch_id = :b AND status = 'CLEAN' ORDER BY row_no"), {'b': batch_id}).rowcount
    conn.execute(text(
        "UPDATE ops.stg_customer s SET customer_id = c.customer_id FROM ops.customer_clean c "
        "WHERE s.batch_id = :b AND s.status = 'CLEAN' AND c.phone = s.phone_norm AND c.is_active"), {'b': batch_id})
    return n


def xuat_csv_ho_so_loi(bang: pd.DataFrame, duong_dan) -> int:
    """FR-10 / UC9: ghi bảng hồ sơ lỗi (do transform.bang_ho_so_loi lập) ra CSV. utf-8-sig để Excel mở đúng
    tiếng Việt. Tệp có dữ liệu cá nhân → nằm trong data/processed (không commit)."""
    bang.to_csv(duong_dan, index=False, encoding='utf-8-sig')
    return len(bang)


def doc_reject(conn, batch_id: int | None = None) -> pd.DataFrame:
    """Đọc view ops.v_reject (sql/004): hồ sơ bị loại kèm lý do viết cho người đọc (TD-23)."""
    sql = 'SELECT batch_id, row_no, source_record_id, phone_raw, error_code, ly_do FROM ops.v_reject'
    if batch_id is not None:
        sql += ' WHERE batch_id = :b'
    sql += ' ORDER BY batch_id, row_no'
    return pd.DataFrame(conn.execute(text(sql), {'b': batch_id}).fetchall(),
                        columns=['batch_id', 'row_no', 'source_record_id', 'phone_raw', 'error_code', 'ly_do'])


# ------------------------------------------------------------------ UC1 «include» UC7 – quy tắc và kết quả đo
def khoi_tao_quy_tac(conn, quy_tac_mac_dinh: list[dict], nguoi: str) -> int:
    """Ghi bộ quy tắc mặc định nếu chưa có (ON CONFLICT DO NOTHING: không ghi đè cấu hình Quản lý đã sửa)."""
    n = 0
    for q in quy_tac_mac_dinh:
        n += conn.execute(text(
            'INSERT INTO ops.dq_rule (rule_code, rule_name, rule_type, field_name, weight, pass_threshold, updated_by) '
            'VALUES (:rule_code, :rule_name, :rule_type, :field_name, :weight, :pass_threshold, :nguoi) '
            'ON CONFLICT (rule_code) DO NOTHING'), {**q, 'nguoi': nguoi}).rowcount
    return n


def doc_quy_tac_dang_bat(conn) -> list[dict]:
    """Cấu hình HIỆN HÀNH của các quy tắc đang bật – lần đo dùng đúng trọng số lúc đo (lập luận 3, NFR-05)."""
    rows = conn.execute(text('SELECT rule_id, rule_code, rule_name, rule_type, field_name, weight, pass_threshold '
                             'FROM ops.dq_rule WHERE is_active ORDER BY rule_code'))
    return [dict(r._mapping) for r in rows]


def thoi_diem_csdl(conn):
    """Đồng hồ của CSDL (clock_timestamp – giờ thật lúc gọi), cùng đồng hồ với dq_rule.updated_at (TD-16)."""
    return conn.execute(text('SELECT clock_timestamp()::timestamp')).scalar_one()


def ghi_ket_qua_do(conn, batch_id: int, ket_qua: list, quy_tac: list[dict], measured_at) -> int:
    """Ghi mỗi (quy tắc × giai đoạn) một dòng ops.dq_result, cùng một measured_at cho cả lần đo (GRAIN)."""
    ma_id = {q['rule_code']: q['rule_id'] for q in quy_tac}
    conn.execute(text(
        'INSERT INTO ops.dq_result (batch_id, rule_id, measure_stage, measured_at, total_records, pass_count) '
        'VALUES (:b, :rule_id, :stage, :t, :total, :pass)'),
        [{'b': batch_id, 'rule_id': ma_id[k.rule_code], 'stage': k.measure_stage, 't': measured_at,
          'total': k.total_records, 'pass': k.pass_count} for k in ket_qua])
    return len(ket_qua)


# ------------------------------------------------------------------ UC3 – phát hiện cặp (FR-04)
def doc_ho_so_hop_le_cua_dot(conn, batch_id: int) -> pd.DataFrame:
    """Hồ sơ có số hợp lệ của MỘT đợt (QL7-04: hồ sơ lỗi không tham gia so khớp)."""
    return pd.DataFrame(conn.execute(text(
        'SELECT stg_id, name_norm FROM ops.stg_customer '
        'WHERE batch_id = :b AND error_code IS NULL AND phone_norm IS NOT NULL'), {'b': batch_id}).fetchall(),
        columns=['stg_id', 'name_norm'])


def ghi_name_key(conn, bang: pd.DataFrame) -> None:
    """Ghi name_key (pha T đã tính) vào stg_customer bằng một lệnh UPDATE … FROM bảng tạm thời."""
    conn.exec_driver_sql('CREATE TEMP TABLE tmp_name_key (stg_id BIGINT PRIMARY KEY, name_key VARCHAR(120)) '
                         'ON COMMIT DROP')
    bang[['stg_id', 'name_key']].to_sql('tmp_name_key', conn, if_exists='append', index=False, chunksize=5000)
    conn.execute(text('UPDATE ops.stg_customer s SET name_key = t.name_key FROM tmp_name_key t '
                      'WHERE s.stg_id = t.stg_id'))
    conn.exec_driver_sql('DROP TABLE tmp_name_key')


def doc_ho_so_so_khop(conn, batch_id: int) -> pd.DataFrame:
    """Hồ sơ hợp lệ của đợt này VÀ các đợt trước (hồ sơ mới được so cùng hồ sơ cũ)."""
    return pd.DataFrame(conn.execute(text(
        'SELECT stg_id, phone_norm, name_norm FROM ops.stg_customer '
        'WHERE batch_id <= :b AND error_code IS NULL AND phone_norm IS NOT NULL'), {'b': batch_id}).fetchall(),
        columns=['stg_id', 'phone_norm', 'name_norm'])


def doc_cap_da_co(conn) -> set[tuple[int, int]]:
    """Cặp đã có trong dup_candidate, kể cả đã Giữ riêng (QL7-05) – không tạo lại."""
    return {tuple(r) for r in conn.execute(text('SELECT stg_id_a, stg_id_b FROM ops.dup_candidate'))}


def ghi_cap(conn, cap: pd.DataFrame) -> int:
    """Ghi cặp mới ở trạng thái PENDING. ON CONFLICT theo khóa (stg_id_a, stg_id_b): chạy lại không nhân đôi.
    Trả về số cặp đem ghi (match.tim_cap đã bỏ cặp đã có, nên đó cũng là số cặp mới)."""
    if not len(cap):
        return 0
    conn.execute(text(
        'INSERT INTO ops.dup_candidate (stg_id_a, stg_id_b, match_type, score) '
        'VALUES (:stg_id_a, :stg_id_b, :match_type, :score) ON CONFLICT (stg_id_a, stg_id_b) DO NOTHING'),
        [{k: (int(v) if k.startswith('stg') else v) for k, v in r.items()} for r in cap.to_dict('records')])
    return len(cap)


# ------------------------------------------------------------------ kiểm chứng chạy lại
def dem_dong_bang_dich(conn) -> dict[str, int]:
    """Số dòng của từng bảng đích (BANG_DICH) – so trước/sau để thấy lần chạy thứ hai không nhân đôi (C5)."""
    return {b: int(conn.execute(text(f'SELECT count(*) FROM {b}')).scalar_one()) for b in BANG_DICH}
