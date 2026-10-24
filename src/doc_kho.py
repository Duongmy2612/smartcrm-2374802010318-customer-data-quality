"""Đọc kho dữ liệu dwh cho dashboard (UC8, khung K1 – K3) – chỉ SELECT, không ghi.

Tách khỏi dashboard/report.py để lớp ① chỉ hiển thị: quy tắc QT-14, câu giải thích khi bộ lọc rỗng và cách
chia khoảng điểm nằm ở đây và có unit test (tests/test_doc_kho.py), không cần Streamlit hay CSDL.

Mỗi biểu đồ gắn một câu hỏi phân tích ở docs/data-requirements.md mục 8:
    K1 – Q2: chỉ số mức độ sạch của từng đợt TRƯỚC và SAU làm sạch, đã đạt mức Tốt chưa?
    K2 – Q3: quy tắc nào kéo chỉ số xuống nhiều nhất?
    K3 – Q4, Q5: bao nhiêu cặp nghi trùng còn Chờ xử lý; điểm tương đồng phân bố thế nào quanh ngưỡng?
"""
from datetime import date

import pandas as pd
from sqlalchemy import bindparam, text

TOAN_CONG_TY = 'VAN_PHONG'                    # đơn vị của nhân viên văn phòng → xem mọi đơn vị nguồn (Bảng 1.2)
KHOANG_DIEM = ['< 85', '85 – <90', '90 – <95', '≥ 95']   # docs/data-requirements.md mục 5.2 (K3)
TRANG_THAI_CAP = {'PENDING': 'Chờ xử lý', 'MERGED': 'Gộp', 'KEEP_SEPARATE': 'Giữ riêng'}
GIAI_DOAN = {'TRUOC': 'TRƯỚC làm sạch', 'SAU': 'SAU làm sạch'}


# ------------------------------------------------------------------ hàm thuần
def don_vi_duoc_xem(cau_hinh: dict, ten_dang_nhap: str) -> list[str] | None:
    """QT-14: None = xem mọi đơn vị nguồn; danh sách = chỉ các đơn vị đó.

    Nhân viên Marketing thuộc văn phòng công ty nên xem toàn công ty; Quản lý cửa hàng chỉ xem đơn vị mình.
    Tên đăng nhập không có trong cấu hình → không được xem gì (danh sách rỗng), không đoán quyền.
    """
    for nd in cau_hinh.get('nguoi_dung', []):
        if nd['ten_dang_nhap'] == ten_dang_nhap:
            return None if nd['don_vi'] == TOAN_CONG_TY else [nd['don_vi']]
    return []


def khoang_diem(score: float) -> str:
    """Chia điểm tương đồng theo khoảng của K3; biên thuộc khoảng trên (85 → '85 – <90')."""
    s = float(score)
    return '< 85' if s < 85 else '85 – <90' if s < 90 else '90 – <95' if s < 95 else '≥ 95'


def _ngay(d) -> str:
    return d.strftime('%d/%m/%Y') if d else '…'


def cau_giai_thich_rong(pham_vi: list[str] | None, don_vi_chon: list[str], tu: date | None, den: date | None,
                         co_du_lieu_trong_kho: bool) -> str:
    """Câu hiện khi bộ lọc không ra dòng nào: nói rõ VÌ SAO rỗng và nên làm gì tiếp."""
    if not co_du_lieu_trong_kho:
        return ('Kho dữ liệu chưa có đợt nạp nào. Chạy luồng chính trước: '
                '`python -m src.pipeline --tep data/raw/customers_raw.csv`, rồi bấm "Làm mới dữ liệu".')
    if pham_vi == []:
        return 'Tài khoản này không có trong configs/config.yaml nên không được xem dữ liệu đơn vị nào (QT-14).'
    don_vi = ', '.join(don_vi_chon) if don_vi_chon else ('mọi đơn vị' if pham_vi is None else ', '.join(pham_vi))
    cau = f'Không có đợt nạp nào của {don_vi} nạp trong khoảng {_ngay(tu)} – {_ngay(den)}.'
    if pham_vi is not None:
        cau += (f' Theo QT-14, tài khoản này chỉ xem được đơn vị {", ".join(pham_vi)}; các đợt nạp hiện có '
                'thuộc đơn vị khác.')
    return cau + ' Thử mở rộng khoảng ngày nạp hoặc chọn đơn vị nguồn khác.'


# ------------------------------------------------------------------ truy vấn (chỉ SELECT)
def doc_dot(conn, pham_vi: list[str] | None, don_vi_chon: list[str], tu: date | None, den: date | None) -> pd.DataFrame:
    """Các đợt nạp được xem (QT-14) và khớp bộ lọc; kèm chỉ số mức độ sạch của lần đo mới nhất."""
    sql = """
        SELECT b.batch_key, b.batch_id, b.file_name, b.source_unit, b.loaded_by, b.loaded_at,
               t.clean_index AS truoc, s.clean_index AS sau, s.grade AS xep_loai, s.measured_at
        FROM   dwh.dim_batch b
        LEFT JOIN dwh.v_batch_score t ON t.batch_key = b.batch_key AND t.measure_stage = 'TRUOC' AND t.is_latest
        LEFT JOIN dwh.v_batch_score s ON s.batch_key = b.batch_key AND s.measure_stage = 'SAU' AND s.is_latest
        WHERE  (:tu IS NULL OR b.loaded_at::DATE >= :tu) AND (:den IS NULL OR b.loaded_at::DATE <= :den)
    """
    tham = {'tu': tu, 'den': den}
    loc = don_vi_chon or pham_vi
    if loc is not None:
        if not loc:
            return pd.DataFrame(columns=['batch_key'])
        sql += ' AND b.source_unit IN :dv'
        tham['dv'] = list(loc)
    q = text(sql + ' ORDER BY b.batch_id').bindparams(*( [bindparam('dv', expanding=True)] if 'dv' in tham else []))
    return pd.read_sql(q, conn, params=tham)


def doc_ty_le_quy_tac(conn, batch_keys: list[int], giai_doan: str | None = None) -> pd.DataFrame:
    """v_rule_rate của lần đo mới nhất từng đợt (K1 thẻ chỉ số, K2)."""
    if not batch_keys:
        return pd.DataFrame()
    q = text("""
        SELECT v.* FROM dwh.v_rule_rate v
        WHERE  v.batch_key IN :bk AND (:gd IS NULL OR v.measure_stage = :gd)
          AND  v.measured_at = (SELECT max(f.measured_at) FROM dwh.fact_dq_check f
                                WHERE f.batch_key = v.batch_key AND f.measure_stage = v.measure_stage)
        ORDER  BY v.batch_id, v.measure_stage, v.rule_code
    """).bindparams(bindparam('bk', expanding=True))
    return pd.read_sql(q, conn, params={'bk': list(batch_keys), 'gd': giai_doan})


def doc_cap(conn, batch_keys: list[int]) -> pd.DataFrame:
    """Số cặp theo đợt × loại so khớp × trạng thái × điểm (K3); điểm được chia khoảng ở phía Python."""
    if not batch_keys:
        return pd.DataFrame()
    q = text("""
        SELECT b.batch_id, f.match_type, f.status, f.score, count(*) AS so_cap
        FROM   dwh.fact_dup_pair f JOIN dwh.dim_batch b ON b.batch_key = f.batch_key
        WHERE  f.batch_key IN :bk
        GROUP  BY b.batch_id, f.match_type, f.status, f.score
    """).bindparams(bindparam('bk', expanding=True))
    df = pd.read_sql(q, conn, params={'bk': list(batch_keys)})
    if len(df):
        df['khoang_diem'] = df['score'].map(khoang_diem)
        df['trang_thai'] = df['status'].map(TRANG_THAI_CAP)
    return df


def doc_thoi_diem_du_lieu(conn) -> dict:
    """Thời điểm dữ liệu mới nhất trong kho – ghi lên mỗi biểu đồ."""
    r = conn.execute(text('SELECT (SELECT max(measured_at) FROM dwh.fact_dq_check) AS lan_do, '
                          '(SELECT max(loaded_at) FROM dwh.dim_batch) AS lan_nap, '
                          '(SELECT count(*) FROM dwh.dim_batch) AS so_dot')).mappings().one()
    return dict(r)
