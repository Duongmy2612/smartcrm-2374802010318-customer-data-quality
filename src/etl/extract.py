"""② extract.py – pha EXTRACT, FR-01 (UC1): đọc tệp khách hàng thô, kiểm cột bắt buộc, băm SHA-256, đổi tên
cột sang cột *_raw của bảng tạm. KHÔNG đọc/ghi CSDL: ghi đợt nạp và hồ sơ thô là việc của pha load
(load_ops.ghi_dot_nap, ghi_ho_so_tho – TD-22).

KHÔNG biến đổi giá trị. Mọi cột được đọc dạng chuỗi (dtype=str) để pandas không tự đoán kiểu – nếu để
pandas tự đoán, số 0901234567 thành số nguyên 901234567 và mất số 0 đầu trước khi kịp kiểm tra.
Ô trống đọc thành chuỗi rỗng (keep_default_na=False) để giữ đúng giá trị gốc ở cột *_raw (NFR-05).
"""
import hashlib
import pathlib

import pandas as pd

from src.etl.tien_ich import la_trong

COT_BAT_BUOC = ('ho_ten', 'so_dien_thoai')                 # FR-01: thiếu một cột → từ chối cả đợt
# Ánh xạ cột nguồn → cột của bảng tạm (Bảng 4.1 của BT1). Cột không bắt buộc mà tệp không có → để trống.
ANH_XA_COT = {
    'record_id': 'source_record_id',
    'ho_ten': 'full_name_raw',
    'so_dien_thoai': 'phone_raw',
    'email': 'email_raw',
    'dia_chi': 'address_raw',
    'ngay_tao': 'created_raw',
}
DO_DAI_TOI_DA = {'source_record_id': 20, 'full_name_raw': 200, 'phone_raw': 30,
                 'email_raw': 200, 'address_raw': 300, 'created_raw': 30}   # khớp VARCHAR ở sql/001


class TepBiTuChoi(ValueError):
    """Tệp không được nạp; bảng tạm và load_batch không thay đổi (AC1.3)."""


def doc_tep(duong_dan) -> pd.DataFrame:
    """Đọc .csv (UTF-8) hoặc .xlsx thành DataFrame toàn chuỗi; kiểm hai cột bắt buộc (AC1.3)."""
    p = pathlib.Path(duong_dan)
    if not p.is_file():
        raise FileNotFoundError(f'Không tìm thấy tệp {p}')
    duoi = p.suffix.lower()
    if duoi == '.csv':
        # utf-8-sig: bỏ được ký tự BOM mà Excel hay chèn vào đầu tệp CSV
        df = pd.read_csv(p, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    elif duoi == '.xlsx':
        # Lưu ý: ô Excel định dạng Number đã mất số 0 đầu từ trong Excel → sẽ bị gắn INVALID_PHONE
        df = pd.read_excel(p, dtype=str, keep_default_na=False)
    else:
        raise TepBiTuChoi(f'Chỉ nhận tệp .csv hoặc .xlsx, không nhận "{p.name}"')
    df.columns = [str(c).strip() for c in df.columns]
    kiem_cot_bat_buoc(df)
    return df


def kiem_cot_bat_buoc(df: pd.DataFrame) -> None:
    """FR-01, AC1.3: thiếu ho_ten hoặc so_dien_thoai → từ chối cả đợt, báo đủ tên các cột thiếu."""
    thieu = [c for c in COT_BAT_BUOC if c not in df.columns]
    if thieu:
        raise TepBiTuChoi(f"Thiếu cột bắt buộc: {', '.join(thieu)} – từ chối cả đợt, bảng tạm không thay đổi")


def ho_so_tep(df: pd.DataFrame) -> dict:
    """Số dòng, số cột, số ô trống và tỉ lệ ô trống từng cột – in ra khi chạy (nhiệm vụ DA buổi 8)."""
    n = len(df)
    return {
        'so_dong': n,
        'so_cot': df.shape[1],
        'o_trong': {c: (int(la_trong(df[c]).sum()), float(la_trong(df[c]).mean()) if n else 0.0)
                    for c in df.columns},
    }


def bam_sha256(duong_dan) -> str:
    """Giá trị băm của nội dung tệp: cùng tệp → cùng giá trị, dù đổi tên tệp (AC1.4)."""
    h = hashlib.sha256()
    with open(duong_dan, 'rb') as f:
        for khoi in iter(lambda: f.read(1 << 20), b''):
            h.update(khoi)
    return h.hexdigest()


def sang_bang_tam(df: pd.DataFrame) -> pd.DataFrame:
    """Đổi tên cột nguồn sang cột *_raw của stg_customer, thêm row_no; giá trị giữ nguyên."""
    bt = pd.DataFrame({'row_no': range(1, len(df) + 1)})
    for nguon, dich in ANH_XA_COT.items():
        bt[dich] = df[nguon].to_numpy() if nguon in df.columns else ''
    qua_dai = {c: int((bt[c].str.len() > n).sum()) for c, n in DO_DAI_TOI_DA.items()}
    qua_dai = {c: k for c, k in qua_dai.items() if k}
    if qua_dai:
        raise TepBiTuChoi(f'Giá trị dài hơn cột của bảng tạm: {qua_dai} – kiểm tra lại tệp nguồn')
    return bt
