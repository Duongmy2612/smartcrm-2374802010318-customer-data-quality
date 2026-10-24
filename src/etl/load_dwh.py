"""② load_dwh.py – FR-09: nạp kho dữ liệu schema dwh từ schema ops.  Sprint 2 (buổi 10), TD-14.

Hợp đồng dữ liệu (chốt ở BT1, docs/data-requirements.md mục 5.2):
    Chạy sau mỗi lần đo (UC1 «include» UC7), mỗi lần phát hiện cặp (UC3) và mỗi lần lưu cấu hình quy tắc (UC6).
    1. Dimension trước, theo KHÓA NGHIỆP VỤ:
       dim_date  : sinh sẵn 2024 – 2027 trong sql/002; ngày đo/phát hiện/quyết định nằm ngoài khoảng thì thêm (TD-15).
       dim_batch : thêm đợt chưa có (batch_id); không cập nhật đợt cũ (SCD loại 0).
       dim_rule  : SCD loại 2 – so ops.dq_rule với phiên bản hiện hành theo rule_code; khác thì đóng phiên bản
                   cũ (valid_to = updated_at) rồi thêm phiên bản mới. Lưu cấu hình mà không đổi gì → không sinh
                   phiên bản.
    2. Fact sau, theo lô (đợt nạp × lần đo) và theo khóa nghiệp vụ:
       fact_dq_check : thêm dòng ops.dq_result chưa có (result_id); rule_key = phiên bản có
                       valid_from ≤ measured_at < valid_to.
       fact_dup_pair : thêm cặp mới (pair_id); cặp đã có chỉ cập nhật status, decided_date_key khi đổi.
    Nạp lần hai không nhân đôi dòng: mọi lệnh INSERT có ON CONFLICT / NOT EXISTS theo khóa nghiệp vụ.

Chạy riêng (ví dụ để kiểm phép thử nạp lại):  python -m src.etl.load_dwh
"""
import sys
from datetime import datetime

from sqlalchemy import text

THUOC_TINH_SCD2 = ('rule_name', 'rule_type', 'field_name', 'weight', 'pass_threshold', 'is_active')


# ------------------------------------------------------------------ hàm thuần (kiểm thử ở tests/test_load_dwh.py)
def _chuan(v):
    """So sánh giá trị cấu hình không phụ thuộc kiểu: Decimal('0.25') == 0.25, '98.00' == 98."""
    if isinstance(v, bool) or v is None:
        return v
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return str(v)


def quyet_dinh_scd2(hien_hanh: dict[str, dict], cau_hinh: list[dict]) -> tuple[list[dict], list[dict]]:
    """SCD loại 2 cho dim_rule.

    hien_hanh: {rule_code: phiên bản đang hiệu lực trong dwh.dim_rule (valid_to IS NULL)}.
    cau_hinh : các dòng ops.dq_rule (cấu hình hiện hành, kể cả quy tắc đã tắt).
    Trả về (dong, them):
        dong – [{rule_key, valid_to}] phiên bản phải đóng;
        them – [dòng cấu hình] cần thêm thành phiên bản mới, valid_from = updated_at.
    Chỉ sinh phiên bản mới khi một thuộc tính trong THUOC_TINH_SCD2 thật sự đổi; lưu lại cùng cấu hình (chỉ
    updated_at đổi) không sinh phiên bản, để đường xu hướng ở K1 không bị cắt vụn.
    """
    dong, them = [], []
    for q in cau_hinh:
        cu = hien_hanh.get(q['rule_code'])
        if cu is None:
            them.append(q)
            continue
        if any(_chuan(cu[k]) != _chuan(q[k]) for k in THUOC_TINH_SCD2):
            if q['updated_at'] <= cu['valid_from']:
                # Cấu hình đổi mà thời điểm không tiến lên: không thể đóng phiên bản cũ đúng thứ tự thời gian
                raise ValueError(f"{q['rule_code']}: updated_at {q['updated_at']} không sau valid_from "
                                 f"{cu['valid_from']} của phiên bản hiện hành")
            dong.append({'rule_key': cu['rule_key'], 'valid_to': q['updated_at']})
            them.append(q)
    return dong, them


# ------------------------------------------------------------------ nạp từng bảng
SQL_NGAY_THIEU = """
INSERT INTO dwh.dim_date (date_key, full_date, day_of_month, month, month_label, quarter, year)
SELECT DISTINCT TO_CHAR(d, 'YYYYMMDD')::INT, d, EXTRACT(DAY FROM d), EXTRACT(MONTH FROM d),
       TO_CHAR(d, 'MM/YYYY'), EXTRACT(QUARTER FROM d), EXTRACT(YEAR FROM d)
FROM (
    SELECT measured_at::DATE AS d FROM ops.dq_result
    UNION SELECT detected_at::DATE FROM ops.dup_candidate
    UNION SELECT decided_at::DATE FROM ops.dup_candidate WHERE decided_at IS NOT NULL
) x
ON CONFLICT (date_key) DO NOTHING
"""

SQL_DIM_BATCH = """
INSERT INTO dwh.dim_batch (batch_id, file_name, source_unit, loaded_by, loaded_at)
SELECT batch_id, file_name, source_unit, loaded_by, loaded_at
FROM   ops.load_batch
ORDER  BY batch_id
ON CONFLICT (batch_id) DO NOTHING
"""

# rule_key = phiên bản bao phủ measured_at. Nếu lần đo xảy ra TRƯỚC phiên bản đầu tiên (đồng hồ hai máy lệch nhau)
# thì gán phiên bản sớm nhất của quy tắc thay vì làm rơi dòng; số dòng như vậy được báo ở đối soát (TD-16).
SQL_FACT_DQ = """
INSERT INTO dwh.fact_dq_check (date_key, batch_key, rule_key, result_id, measure_stage, measured_at,
                               total_records, pass_count)
SELECT TO_CHAR(r.measured_at, 'YYYYMMDD')::INT, b.batch_key,
       COALESCE(pb.rule_key, sm.rule_key), r.result_id, r.measure_stage, r.measured_at,
       r.total_records, r.pass_count
FROM   ops.dq_result r
JOIN   ops.dq_rule   q ON q.rule_id = r.rule_id
JOIN   dwh.dim_batch b ON b.batch_id = r.batch_id
LEFT JOIN LATERAL (
       SELECT d.rule_key FROM dwh.dim_rule d
       WHERE  d.rule_code = q.rule_code AND d.valid_from <= r.measured_at
         AND  (d.valid_to IS NULL OR r.measured_at < d.valid_to)
       ORDER  BY d.valid_from DESC LIMIT 1) pb ON TRUE
LEFT JOIN LATERAL (
       SELECT d.rule_key FROM dwh.dim_rule d
       WHERE  d.rule_code = q.rule_code ORDER BY d.valid_from LIMIT 1) sm ON TRUE
WHERE  NOT EXISTS (SELECT 1 FROM dwh.fact_dq_check f WHERE f.result_id = r.result_id)
ORDER  BY r.result_id
"""

SQL_FACT_CAP = """
INSERT INTO dwh.fact_dup_pair (pair_id, batch_key, detected_date_key, decided_date_key, match_type, status, score)
SELECT c.pair_id, b.batch_key, TO_CHAR(c.detected_at, 'YYYYMMDD')::INT,
       CASE WHEN c.decided_at IS NULL THEN NULL ELSE TO_CHAR(c.decided_at, 'YYYYMMDD')::INT END,
       c.match_type, c.status, c.score
FROM   ops.dup_candidate c
JOIN   ops.stg_customer  s ON s.stg_id = c.stg_id_b
JOIN   dwh.dim_batch     b ON b.batch_id = s.batch_id
ORDER  BY c.pair_id
ON CONFLICT (pair_id) DO UPDATE
SET    status = EXCLUDED.status, decided_date_key = EXCLUDED.decided_date_key
WHERE  dwh.fact_dup_pair.status IS DISTINCT FROM EXCLUDED.status
   OR  dwh.fact_dup_pair.decided_date_key IS DISTINCT FROM EXCLUDED.decided_date_key
"""


def nap_dim_rule(conn) -> dict:
    """SCD loại 2: đọc hai phía, quyết định bằng quyet_dinh_scd2(), rồi ghi."""
    hien_hanh = {r['rule_code']: r for r in (dict(x._mapping) for x in conn.execute(text(
        'SELECT rule_key, rule_code, ' + ', '.join(THUOC_TINH_SCD2) + ', valid_from '
        'FROM dwh.dim_rule WHERE valid_to IS NULL')))}
    cau_hinh = [dict(x._mapping) for x in conn.execute(text(
        'SELECT rule_code, ' + ', '.join(THUOC_TINH_SCD2) + ', updated_at FROM ops.dq_rule ORDER BY rule_code'))]
    dong, them = quyet_dinh_scd2(hien_hanh, cau_hinh)
    if dong:
        conn.execute(text('UPDATE dwh.dim_rule SET valid_to = :valid_to WHERE rule_key = :rule_key'), dong)
    if them:
        conn.execute(text(
            'INSERT INTO dwh.dim_rule (rule_code, rule_name, rule_type, field_name, weight, pass_threshold, '
            'is_active, valid_from) VALUES (:rule_code, :rule_name, :rule_type, :field_name, :weight, '
            ':pass_threshold, :is_active, :updated_at)'), them)
    return {'dong_phien_ban': len(dong), 'them_phien_ban': len(them)}


def nap_kho(conn) -> dict:
    """Nạp dimension rồi fact; trả về số dòng thêm/cập nhật theo bảng (lần nạp thứ hai: toàn số 0)."""
    ra = {'dim_date (thêm ngày)': conn.execute(text(SQL_NGAY_THIEU)).rowcount,
          'dim_batch': conn.execute(text(SQL_DIM_BATCH)).rowcount}
    scd = nap_dim_rule(conn)
    ra['dim_rule (phiên bản mới)'] = scd['them_phien_ban']
    ra['dim_rule (đóng phiên bản)'] = scd['dong_phien_ban']
    ra['fact_dq_check'] = conn.execute(text(SQL_FACT_DQ)).rowcount
    ra['fact_dup_pair (thêm/cập nhật)'] = conn.execute(text(SQL_FACT_CAP)).rowcount
    return ra


# ------------------------------------------------------------------ đối soát staging ↔ kho
DOI_SOAT = [
    # (mục, câu SQL phía nguồn, câu SQL phía kho, giải thích khi KHÁC GRAIN)
    ('Đợt nạp', 'SELECT count(*) FROM ops.load_batch', 'SELECT count(*) FROM dwh.dim_batch',
     'cùng GRAIN: 1 dòng = 1 đợt'),
    ('Kết quả đo', 'SELECT count(*) FROM ops.dq_result', 'SELECT count(*) FROM dwh.fact_dq_check',
     'cùng GRAIN: 1 dòng = 1 quy tắc × 1 đợt × 1 giai đoạn × 1 lần đo'),
    ('Cặp nghi trùng', 'SELECT count(*) FROM ops.dup_candidate', 'SELECT count(*) FROM dwh.fact_dup_pair',
     'cùng GRAIN: 1 dòng = 1 cặp'),
    ('Hồ sơ thô ↔ mẫu số DQ-01 (lần đo mới nhất)',
     'SELECT count(*) FROM ops.stg_customer',
     "SELECT COALESCE(SUM(total_records), 0) FROM dwh.v_rule_rate v WHERE rule_code = 'DQ-01' "
     "AND measure_stage = 'SAU' AND measured_at = (SELECT max(measured_at) FROM dwh.fact_dq_check f "
     "WHERE f.batch_key = v.batch_key)",
     'khác GRAIN: kho không lưu từng hồ sơ; mẫu số của DQ-01 là mọi hồ sơ của đợt nên phải bằng số hồ sơ thô'),
    ('Hồ sơ lặp chờ quyết định ↔ cặp EXACT_PHONE chờ xử lý',
     "SELECT count(*) FROM ops.stg_customer WHERE status = 'PENDING_DUP'",
     "SELECT count(*) FROM dwh.fact_dup_pair WHERE match_type = 'EXACT_PHONE' AND status = 'PENDING'",
     'QL7-02: mỗi hồ sơ lặp sinh đúng một cặp EXACT_PHONE với hồ sơ nạp sớm nhất của cùng số'),
]


def doi_soat(conn) -> list[dict]:
    """Đếm dòng hai phía và nói rõ vì sao bằng / khác nhau (nhiệm vụ DA buổi 10)."""
    ra = []
    for muc, sql_nguon, sql_kho, giai_thich in DOI_SOAT:
        n, k = conn.execute(text(sql_nguon)).scalar_one(), conn.execute(text(sql_kho)).scalar_one()
        ra.append({'muc': muc, 'nguon': int(n), 'kho': int(k), 'khop': int(n) == int(k), 'giai_thich': giai_thich})
    lech = conn.execute(text(
        'SELECT count(*) FROM dwh.fact_dq_check f JOIN dwh.dim_rule d ON d.rule_key = f.rule_key '
        'WHERE f.measured_at < d.valid_from')).scalar_one()
    ra.append({'muc': 'Lần đo trước phiên bản quy tắc đầu tiên (gán phiên bản sớm nhất)', 'nguon': 0,
               'kho': int(lech), 'khop': lech == 0, 'giai_thich': 'phải bằng 0; khác 0 là đồng hồ hai máy lệch (TD-16)'})
    return ra


def in_doi_soat(rows: list[dict], in_ra=print) -> None:
    so = lambda n: f'{n:,}'.replace(',', '.')                   # noqa: E731
    for r in rows:
        dau = '✔' if r['khop'] else '✘'
        in_ra(f"      {dau} {r['muc']}: ops {so(r['nguon'])} · dwh {so(r['kho'])} – {r['giai_thich']}")


def main(argv=None) -> int:
    """Nạp lại kho từ ops (không đọc tệp nguồn). Mã thoát: 0 thành công · 1 lỗi kỹ thuật."""
    from src import db
    try:
        engine = db.tao_engine()
        with engine.begin() as conn:
            db.khoi_tao_csdl(conn)
            t0 = datetime.now()
            ra = nap_kho(conn)
            print('load_dwh: ' + ' · '.join(f'{k} +{v}' for k, v in ra.items())
                  + f' ({(datetime.now() - t0).total_seconds():.1f} s)'.replace('.', ','))
            print('Đối soát staging (ops) ↔ kho (dwh):')
            in_doi_soat(doi_soat(conn))
        return 0
    except Exception as e:                            # noqa: BLE001
        print(f'LỖI: {type(e).__name__}: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
