"""② dq_evaluate.py – FR-07, FR-08 (UC6, UC7): đo chất lượng từng đợt nạp ở hai giai đoạn.

TRƯỚC = đo trên giá trị thô (*_raw); SAU = đo sau chuẩn hóa (phone_norm, name_norm). Mỗi quy tắc có MẪU SỐ
riêng là phạm vi áp dụng của nó (docs/data-requirements.md mục 6), để hồ sơ thiếu số chỉ bị trừ điểm một lần ở DQ-01, không bị
phạt lại ở DQ-02, DQ-05.

ops.dq_result chỉ lưu số kiểm (total_records) và số đạt (pass_count). Tỉ lệ đạt và chỉ số mức độ sạch là
giá trị tính được nên KHÔNG lưu (thay đổi số 10 của SRS 1.1); ở đây tính để in báo cáo, ở kho dữ liệu là
view v_rule_rate, v_batch_score (Sprint 2).
"""
from dataclasses import dataclass

import pandas as pd
from sqlalchemy import text

from src.etl.extract import la_trong

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
    rule_code: str
    measure_stage: str
    total_records: int      # mẫu số: số hồ sơ thuộc phạm vi áp dụng
    pass_count: int         # số hồ sơ đạt

    @property
    def ti_le(self) -> float:
        """QL7-06: mẫu số bằng 0 (ví dụ tệp không có email) → tỉ lệ đạt = 1."""
        return self.pass_count / self.total_records if self.total_records else 1.0


# ------------------------------------------------------------------ hàm thuần
def do_quy_tac(df: pd.DataFrame, rule_code: str, giai_doan: str) -> KetQua:
    """Đo một quy tắc trên bảng tạm của một đợt (cột *_raw, phone_norm, name_norm, status)."""
    sau = giai_doan == 'SAU'
    co_so = ~la_trong(df['phone_raw'])
    co_ten = ~la_trong(df['full_name_raw'])
    if rule_code == 'DQ-01':                       # mọi hồ sơ; cả hai giai đoạn như nhau (chuẩn hóa không bù được số thiếu)
        pham_vi, dat = pd.Series(True, index=df.index), co_so
    elif rule_code == 'DQ-02':                     # hồ sơ có số điện thoại
        pham_vi = co_so
        dat = df['phone_norm'].notna() if sau else df['phone_raw'].str.strip().str.fullmatch(MAU_SO_CHUAN)
    elif rule_code == 'DQ-03':                     # mọi hồ sơ
        pham_vi, dat = pd.Series(True, index=df.index), co_ten
    elif rule_code == 'DQ-04':                     # hồ sơ có họ tên
        ten = df['name_norm'].fillna('') if sau else df['full_name_raw']
        pham_vi = co_ten
        dat = ten.str.len().between(2, 120) & ~ten.str.contains(r'\d', regex=True)
    elif rule_code == 'DQ-05':
        # Hồ sơ có số hợp lệ; so theo phone_norm ở CẢ HAI giai đoạn (giá trị thô của cùng một số có thể
        # viết khác nhau nên không so được). Đạt = không phải hồ sơ lặp đang chờ quyết định: hồ sơ nạp sớm
        # nhất của mỗi số là CLEAN; hồ sơ lặp chỉ đạt khi cặp của nó đã Gộp/Giữ riêng (Sprint 3) – TD-08.
        pham_vi = df['phone_norm'].notna()
        dat = df['status'] != 'PENDING_DUP'
    elif rule_code == 'DQ-06':                     # hồ sơ có email
        email = df['email_raw'].fillna('').str.strip()
        pham_vi, dat = email != '', email.str.fullmatch(MAU_EMAIL)
    else:
        # Lỗi CẤU HÌNH (lỗi kỹ thuật, khác với 'dưới ngưỡng'): UC6 ở Sprint 3 chỉ cho thêm quy tắc đã có cách đo ở đây
        raise ValueError(f'Quy tắc {rule_code} đang bật nhưng chưa có cách đo trong dq_evaluate.py')
    dat = dat.fillna(False).astype(bool)
    return KetQua(rule_code, giai_doan, int(pham_vi.sum()), int((pham_vi & dat).sum()))


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


# ------------------------------------------------------------------ đọc / ghi CSDL
def khoi_tao_quy_tac(conn, nguoi: str) -> int:
    """Ghi bộ quy tắc mặc định nếu chưa có (ON CONFLICT DO NOTHING: không ghi đè cấu hình Quản lý đã sửa)."""
    n = 0
    for q in QUY_TAC_MAC_DINH:
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


def ghi_ket_qua(conn, batch_id: int, ket_qua: list[KetQua], quy_tac: list[dict], measured_at) -> int:
    """Ghi mỗi (quy tắc × giai đoạn) một dòng ops.dq_result, cùng một measured_at cho cả lần đo (GRAIN)."""
    ma_id = {q['rule_code']: q['rule_id'] for q in quy_tac}
    conn.execute(text(
        'INSERT INTO ops.dq_result (batch_id, rule_id, measure_stage, measured_at, total_records, pass_count) '
        'VALUES (:b, :rule_id, :stage, :t, :total, :pass)'),
        [{'b': batch_id, 'rule_id': ma_id[k.rule_code], 'stage': k.measure_stage, 't': measured_at,
          'total': k.total_records, 'pass': k.pass_count} for k in ket_qua])
    return len(ket_qua)
