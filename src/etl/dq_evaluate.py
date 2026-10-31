"""② dq_evaluate.py – pha QUALITY, FR-07, FR-08 (UC6, UC7): đo chất lượng từng đợt nạp ở hai giai đoạn.

Sáu HÀM KIỂM, mỗi hàm một quy tắc DQ-01 … DQ-06, đều trả về KetQua có số dòng lỗi (so_loi) và tỉ lệ lỗi
(ti_le_loi) đo được. Chỉ có hàm THUẦN – ghi ops.dq_result là việc của load_ops.ghi_ket_qua_do (TD-22, TD-24).

TRƯỚC = đo trên giá trị thô (*_raw); SAU = đo sau chuẩn hóa (phone_norm, name_norm). Mỗi quy tắc có MẪU SỐ
riêng là phạm vi áp dụng của nó (docs/data-requirements.md mục 6), để hồ sơ thiếu số chỉ bị trừ điểm một lần ở DQ-01, không bị
phạt lại ở DQ-02, DQ-05.

ops.dq_result chỉ lưu số kiểm (total_records) và số đạt (pass_count). Tỉ lệ đạt và chỉ số mức độ sạch là
giá trị tính được nên KHÔNG lưu (thay đổi số 10 của SRS 1.1); ở đây tính để in báo cáo, ở kho dữ liệu là
view v_rule_rate, v_batch_score (Sprint 2).
"""
from dataclasses import dataclass

import pandas as pd

from src.etl.tien_ich import la_trong

MAU_SO_CHUAN = r'0[0-9]{9}'                                      # chữ số ASCII, như CHECK ở sql/001
MAU_EMAIL = r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}'   # giống notebooks/profiling_customers.py

# Nội dung mặc định của ops.dq_rule (docs/data-requirements.md mục 6). Quản lý cửa hàng đổi trọng số/ngưỡng ở UC6 (Sprint 3);
# tệp này chỉ dùng để khởi tạo lần đầu và khi chạy --khong-ghi-csdl.
QUY_TAC_MAC_DINH = [
    dict(rule_code='DQ-01', rule_name='Số điện thoại không trống', rule_type='COMPLETENESS',
         field_name='phone', weight=0.25, pass_threshold=98),
    dict(rule_code='DQ-02', rule_name='Số điện thoại đúng mẫu 0xxxxxxxxx', rule_type='VALIDITY',
         field_name='phone', weight=0.25, pass_threshold=95),
    dict(rule_code='DQ-03', rule_name='Họ tên không trống', rule_type='COMPLETENESS',
         field_name='full_name', weight=0.15, pass_threshold=99),
    dict(rule_code='DQ-04', rule_name='Họ tên 2–120 ký tự, không chứa chữ số', rule_type='VALIDITY',
         field_name='full_name', weight=0.10, pass_threshold=97),
    dict(rule_code='DQ-05', rule_name='Số điện thoại không trùng', rule_type='UNIQUENESS',
         field_name='phone', weight=0.20, pass_threshold=98),
    dict(rule_code='DQ-06', rule_name='Email đúng mẫu', rule_type='VALIDITY',
         field_name='email', weight=0.05, pass_threshold=95),
]
GIAI_DOAN = ('TRUOC', 'SAU')


@dataclass
class KetQua:
    """Kết quả của MỘT hàm kiểm trên MỘT đợt ở MỘT giai đoạn. Số đo được: số kiểm, số đạt, số dòng lỗi, tỉ lệ."""
    rule_code: str
    measure_stage: str
    total_records: int      # mẫu số: số hồ sơ thuộc phạm vi áp dụng
    pass_count: int         # số hồ sơ đạt

    @property
    def so_loi(self) -> int:
        """Số dòng lỗi = số hồ sơ thuộc phạm vi mà không đạt."""
        return self.total_records - self.pass_count

    @property
    def ti_le(self) -> float:
        """Tỉ lệ đạt. QL7-06: mẫu số bằng 0 (ví dụ tệp không có email) → tỉ lệ đạt = 1."""
        return self.pass_count / self.total_records if self.total_records else 1.0

    @property
    def ti_le_loi(self) -> float:
        """Tỉ lệ lỗi = số dòng lỗi / số kiểm (= 1 − tỉ lệ đạt; mẫu số 0 → 0)."""
        return 1.0 - self.ti_le


# ------------------------------------------------------------------ 6 hàm kiểm chất lượng (hàm thuần)
# Mỗi hàm: nhận bảng tạm của một đợt (cột *_raw, phone_norm, name_norm, status) và giai đoạn TRUOC/SAU,
# trả về KetQua. Mẫu số là PHẠM VI ÁP DỤNG của quy tắc (docs/data-requirements.md mục 6).
def _ket_qua(ma: str, giai_doan: str, pham_vi: pd.Series, dat: pd.Series) -> KetQua:
    dat = dat.fillna(False).astype(bool)
    return KetQua(ma, giai_doan, int(pham_vi.sum()), int((pham_vi & dat).sum()))


def _moi_ho_so(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def kiem_dq01_so_dien_thoai_khong_trong(df: pd.DataFrame, giai_doan: str) -> KetQua:
    """DQ-01 (COMPLETENESS) – phạm vi: mọi hồ sơ. Hai giai đoạn như nhau: chuẩn hóa không bù được số thiếu."""
    return _ket_qua('DQ-01', giai_doan, _moi_ho_so(df), ~la_trong(df['phone_raw']))


def kiem_dq02_so_dien_thoai_dung_mau(df: pd.DataFrame, giai_doan: str) -> KetQua:
    """DQ-02 (VALIDITY) – phạm vi: hồ sơ CÓ số (thiếu số đã bị trừ ở DQ-01, không phạt lần hai).
    TRƯỚC: giá trị thô khớp 0xxxxxxxxx; SAU: chuẩn hóa được (phone_norm khác rỗng)."""
    co_so = ~la_trong(df['phone_raw'])
    if giai_doan == 'SAU':
        dat = df['phone_norm'].notna()
    else:
        dat = df['phone_raw'].str.strip().str.fullmatch(MAU_SO_CHUAN)
    return _ket_qua('DQ-02', giai_doan, co_so, dat)


def kiem_dq03_ho_ten_khong_trong(df: pd.DataFrame, giai_doan: str) -> KetQua:
    """DQ-03 (COMPLETENESS) – phạm vi: mọi hồ sơ."""
    return _ket_qua('DQ-03', giai_doan, _moi_ho_so(df), ~la_trong(df['full_name_raw']))


def kiem_dq04_ho_ten_hop_le(df: pd.DataFrame, giai_doan: str) -> KetQua:
    """DQ-04 (VALIDITY) – phạm vi: hồ sơ có họ tên. Đạt: 2–120 ký tự, không chứa chữ số.
    TRƯỚC đo trên giá trị thô, SAU đo trên name_norm."""
    ten = df['name_norm'].fillna('') if giai_doan == 'SAU' else df['full_name_raw']
    dat = ten.str.len().between(2, 120) & ~ten.str.contains(r'\d', regex=True)
    return _ket_qua('DQ-04', giai_doan, ~la_trong(df['full_name_raw']), dat)


def kiem_dq05_so_dien_thoai_khong_trung(df: pd.DataFrame, giai_doan: str) -> KetQua:
    """DQ-05 (UNIQUENESS) – phạm vi: hồ sơ có số hợp lệ; so theo phone_norm ở CẢ HAI giai đoạn (giá trị thô của
    cùng một số có thể viết khác nhau nên không so được). Đạt = không phải hồ sơ lặp đang chờ quyết định: hồ sơ
    nạp sớm nhất của mỗi số là CLEAN; hồ sơ lặp chỉ đạt khi cặp của nó đã Gộp/Giữ riêng (UC5) – TD-08."""
    return _ket_qua('DQ-05', giai_doan, df['phone_norm'].notna(), df['status'] != 'PENDING_DUP')


def kiem_dq06_email_dung_mau(df: pd.DataFrame, giai_doan: str) -> KetQua:
    """DQ-06 (VALIDITY) – phạm vi: hồ sơ có email. Email không chuẩn hóa nên hai giai đoạn như nhau."""
    email = df['email_raw'].fillna('').str.strip()
    return _ket_qua('DQ-06', giai_doan, email != '', email.str.fullmatch(MAU_EMAIL))


HAM_KIEM = {
    'DQ-01': kiem_dq01_so_dien_thoai_khong_trong,
    'DQ-02': kiem_dq02_so_dien_thoai_dung_mau,
    'DQ-03': kiem_dq03_ho_ten_khong_trong,
    'DQ-04': kiem_dq04_ho_ten_hop_le,
    'DQ-05': kiem_dq05_so_dien_thoai_khong_trung,
    'DQ-06': kiem_dq06_email_dung_mau,
}


def do_quy_tac(df: pd.DataFrame, rule_code: str, giai_doan: str) -> KetQua:
    """Gọi hàm kiểm của một quy tắc. Quy tắc đang bật mà chưa có hàm kiểm là lỗi CẤU HÌNH (lỗi kỹ thuật, khác
    với 'dưới ngưỡng'): UC6 chỉ cho thêm quy tắc đã có hàm kiểm trong HAM_KIEM."""
    ham = HAM_KIEM.get(rule_code)
    if ham is None:
        raise ValueError(f'Quy tắc {rule_code} đang bật nhưng chưa có hàm kiểm trong dq_evaluate.HAM_KIEM')
    return ham(df, giai_doan)


def kiem_trong_so(quy_tac: list[dict]) -> None:
    """FR-07: tổng trọng số các quy tắc đang bật phải bằng 1,00."""
    tong = round(sum(float(q['weight']) for q in quy_tac), 2)
    if tong != 1.00:
        raise ValueError(f'Tổng trọng số các quy tắc đang bật là {tong}, phải bằng 1,00 (FR-07)')


def do_mot_lan(df: pd.DataFrame, quy_tac: list[dict]) -> list[KetQua]:
    """Một lần đo = mọi quy tắc đang bật × hai giai đoạn TRƯỚC, SAU (FR-08)."""
    kiem_trong_so(quy_tac)
    return [do_quy_tac(df, q['rule_code'], gd) for gd in GIAI_DOAN for q in quy_tac]


def chi_so_muc_do_sach(ket_qua: list[KetQua], quy_tac: list[dict], giai_doan: str) -> float:
    """QL7-06: Σ(trọng số × tỉ lệ đạt) × 100 trên các quy tắc đang bật."""
    trong_so = {q['rule_code']: float(q['weight']) for q in quy_tac}
    return sum(trong_so[k.rule_code] * k.ti_le for k in ket_qua if k.measure_stage == giai_doan) * 100


def xep_loai(chi_so: float) -> str:
    """QL7-06: ≥ 90 Tốt; 75 – < 90 Chấp nhận được; < 75 Kém."""
    return 'Tốt' if chi_so >= 90 else 'Chấp nhận được' if chi_so >= 75 else 'Kém'
