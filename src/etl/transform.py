"""② transform.py – pha TRANSFORM, FR-02, FR-03, FR-10 (UC2, UC9). Chỉ có hàm THUẦN: không đọc/ghi CSDL,
không có câu SQL, không ghi tệp – ghi kết quả là việc của load_ops.py (TD-22).

1. Chuẩn hóa số điện thoại về 0xxxxxxxxx (QT-02) và họ tên (FR-03) – hàm THUẦN, kiểm thử ở tests/.
2. Gắn mã lỗi chính cho hồ sơ không dùng được (MISSING_PHONE / INVALID_PHONE / MISSING_NAME).
3. Phân loại hồ sơ: ERROR (ở lại bảng tạm – QL7-04), CLEAN (vào customer_clean), PENDING_DUP (hồ sơ lặp,
   không tạo hồ sơ mới mà chờ quyết định ở UC5 – QT-01).
4. Lập bảng hồ sơ lỗi kèm lý do viết cho người đọc (FR-10) – load_ops ghi ra CSV, view ops.v_reject (sql/004)
   cho xem cùng lý do đó trong CSDL.

name_key KHÔNG tạo ở đây: theo thay đổi số 2 của SRS 1.1, khóa tên thuộc FR-04 (match.py – Sprint 2).
"""
import re
import unicodedata

import pandas as pd

from src.etl.tien_ich import la_trong

KY_TU_BO = re.compile(r'[\s.\-]')          # QT-02: bỏ dấu cách, dấu chấm, dấu gạch
MAU_SO_CHUAN = re.compile(r'0[0-9]{9}')    # 10 chữ số ASCII, bắt đầu bằng 0 – khớp CHECK '^0[0-9]{9}$' ở sql/001
#   (không dùng \d: trong Python \d nhận cả chữ số Unicode như '９', CSDL sẽ từ chối)

# Lý do dạng câu chữ suy ra từ error_code, KHÔNG lưu vào bảng (tránh lưu giá trị tính được – TD-07).
# View ops.v_reject (sql/004) viết đúng ba câu này; test_ly_do_trong_view_reject_khop_transform giữ hai nơi khớp nhau.
LY_DO = {
    'MISSING_PHONE': 'Thiếu số điện thoại – không sửa được bằng làm sạch, cửa hàng cần bổ sung tại nguồn',
    'INVALID_PHONE': 'Số điện thoại không quy về được dạng 0xxxxxxxxx (sau khi bỏ dấu cách, chấm, gạch và đổi +84/84 thành 0)',
    'MISSING_NAME': 'Thiếu họ tên – hồ sơ đã làm sạch bắt buộc có họ tên',
}


# ------------------------------------------------------------------ hàm thuần
def chuan_hoa_so_dien_thoai(tho) -> str | None:
    """QT-02. Trả về số dạng 0xxxxxxxxx, hoặc None nếu trống / không quy về được.

    Năm dạng đo được trên customers_raw.csv: 0763247885 · 84763247885 · +84763247885 ·
    0763 247 885 · 0763.247.885. Thứ tự xử lý: bỏ ký tự phân cách TRƯỚC rồi mới xét tiền tố, để
    "+84 763 247 885" cũng chuẩn hóa được. Tiền tố 84 chỉ đổi khi có đúng 11 chữ số, để không biến
    một số 10 chữ số bắt đầu bằng 84… (vốn đã sai) thành số khác.
    Quy tắc giống hệt hàm norm_phone của notebooks/profiling_customers.py để số liệu khớp mục 4 BT1.
    """
    if tho is None or pd.isna(tho):
        return None
    s = KY_TU_BO.sub('', str(tho).strip())
    if s.startswith('+84'):
        s = '0' + s[3:]
    elif s.startswith('84') and len(s) == 11:
        s = '0' + s[2:]
    return s if MAU_SO_CHUAN.fullmatch(s) else None


def chuan_hoa_ho_ten(tho) -> str | None:
    """FR-03: bỏ khoảng trắng thừa, viết hoa chữ cái đầu mỗi từ, giữ nguyên dấu tiếng Việt.

    Đưa về dạng Unicode NFC trước: cùng chữ "ễ" có thể được gõ thành 1 ký tự hoặc "e" + 2 dấu rời;
    nếu không gộp lại, chữ cái ngay sau dấu rời sẽ bị viết hoa nhầm. Không dùng str.title() vì nó viết hoa
    cả chữ đứng sau dấu nháy/gạch nối. Tên đã mất dấu trong tệp gốc ("Hoang Kim Ha") giữ nguyên, không
    thể khôi phục dấu – việc nhận ra hai cách viết là một người thuộc name_key (FR-04).
    """
    if tho is None or pd.isna(tho):
        return None
    tu = unicodedata.normalize('NFC', str(tho)).split()
    if not tu:
        return None
    return ' '.join(t[:1].upper() + t[1:].lower() for t in tu)


def gan_ma_loi(phone_raw, phone_norm, name_norm) -> str | None:
    """Mã lỗi CHÍNH (stg_customer chỉ có một cột error_code). Thứ tự ưu tiên (TD-08):
    MISSING_PHONE > INVALID_PHONE > MISSING_NAME – lỗi số điện thoại quan trọng hơn vì số là khóa
    so khớp và là cột không thể sửa bằng làm sạch."""
    # pd.isna thay vì "is None": cột chuỗi của pandas 3 lưu giá trị thiếu là NaN chứ không phải None
    if pd.isna(phone_raw) or str(phone_raw).strip() == '':
        return 'MISSING_PHONE'
    if pd.isna(phone_norm):
        return 'INVALID_PHONE'
    if pd.isna(name_norm):
        return 'MISSING_NAME'
    return None


def chuan_hoa(bang_tam: pd.DataFrame) -> pd.DataFrame:
    """Thêm phone_norm, name_norm, error_code vào bảng tạm (không đổi cột *_raw)."""
    df = bang_tam.copy()
    df['phone_norm'] = df['phone_raw'].map(chuan_hoa_so_dien_thoai).astype(object)
    df['name_norm'] = df['full_name_raw'].map(chuan_hoa_ho_ten).astype(object)
    df['error_code'] = [gan_ma_loi(r, p, n) for r, p, n in
                        zip(df['phone_raw'], df['phone_norm'], df['name_norm'])]
    return df


def phan_loai(df: pd.DataFrame, so_dang_hieu_luc: set[str]) -> pd.Series:
    """Trạng thái từng hồ sơ thô sau chuẩn hóa (FR-02, QT-01, QL7-04):

    ERROR       có mã lỗi → ở lại bảng tạm, không vào customer_clean, không tham gia so khớp.
    PENDING_DUP hồ sơ lặp: số đã thuộc một hồ sơ đang hiệu lực (đợt trước) HOẶC trùng số với một hồ sơ hợp lệ
                đứng trước trong cùng tệp → không tạo hồ sơ mới, chờ phát hiện cặp (UC3) và quyết định (UC5).
    CLEAN       hồ sơ hợp lệ còn lại → vào customer_clean.
    "Đứng trước" theo row_no: hồ sơ nạp sớm nhất của mỗi số là hồ sơ được giữ, khớp QL7-02 và DQ-05.
    Hồ sơ lỗi không được tính là "hồ sơ nạp sớm hơn" (TD-08).
    """
    trang_thai = pd.Series('CLEAN', index=df.index, dtype=object)
    loi = df['error_code'].notna()
    trang_thai[loi] = 'ERROR'
    hop_le = df.loc[~loi].sort_values('row_no')
    lap = hop_le['phone_norm'].duplicated(keep='first') | hop_le['phone_norm'].isin(so_dang_hieu_luc)
    trang_thai[lap[lap].index] = 'PENDING_DUP'
    return trang_thai


# Độ dài tối đa của cột customer_clean (sql/001) – hẹp hơn cột *_raw của bảng tạm
DO_DAI_HO_SO_SACH = {'name_norm': 120, 'email_raw': 120, 'address_raw': 255}


def kiem_do_dai_ho_so_sach(df: pd.DataFrame) -> dict[str, list[int]]:
    """Hồ sơ hợp lệ có giá trị dài hơn cột của customer_clean → {cột: [row_no, …]}; rỗng là đạt.

    Kiểm TRƯỚC khi ghi CSDL để từ chối đợt bằng thông báo rõ dòng nào (mã thoát 2), thay vì để lệnh INSERT
    lỗi giữa chừng (mã thoát 1). Không cắt bớt giá trị vì như vậy là âm thầm làm mất dữ liệu.
    Kiểm mọi hồ sơ không có mã lỗi (không chỉ CLEAN) vì hồ sơ PENDING_DUP có thể thành hồ sơ gốc khi gộp (UC5).
    """
    hop_le = df[df['error_code'].isna()]
    vi_pham = {}
    for cot, toi_da in DO_DAI_HO_SO_SACH.items():
        dai = hop_le[cot].fillna('').str.strip().str.len() > toi_da
        if dai.any():
            vi_pham[cot] = hop_le.loc[dai, 'row_no'].tolist()
    return vi_pham


def thong_ke_chuan_hoa(df: pd.DataFrame) -> dict:
    """Số đếm để báo cáo 'trước → sau' của bước chuẩn hóa."""
    co_so = ~la_trong(df['phone_raw'])
    dung_dang_san = co_so & df['phone_raw'].str.strip().str.fullmatch(r'0[0-9]{9}')
    co_ten = ~la_trong(df['full_name_raw'])
    ten_doi = co_ten & (df['name_norm'].fillna('') != df['full_name_raw'])
    return {
        'so_co_gia_tri': int(co_so.sum()),
        'so_dung_dang_san': int(dung_dang_san.sum()),
        'so_da_chuan_hoa': int((co_so & ~dung_dang_san & df['phone_norm'].notna()).sum()),
        'so_khong_quy_doi_duoc': int((co_so & df['phone_norm'].isna()).sum()),
        'ten_duoc_sua_cach_viet': int(ten_doi.sum()),
        'ma_loi': {k: int((df['error_code'] == k).sum()) for k in LY_DO},
        'trang_thai': {k: int((df['status'] == k).sum()) for k in ('CLEAN', 'PENDING_DUP', 'ERROR')}
        if 'status' in df else {},
    }


def bang_ho_so_loi(df: pd.DataFrame) -> pd.DataFrame:
    """FR-10 / UC9: bảng hồ sơ lỗi kèm mã lỗi và lý do; giá trị là giá trị GỐC để cửa hàng tìm và sửa tại nguồn.
    Ghi ra CSV ở load_ops.xuat_csv_ho_so_loi."""
    loi = df[df['error_code'].notna()]
    return pd.DataFrame({
        'row_no': loi['row_no'], 'record_id': loi['source_record_id'], 'ho_ten': loi['full_name_raw'],
        'so_dien_thoai': loi['phone_raw'], 'email': loi['email_raw'], 'dia_chi': loi['address_raw'],
        'ngay_tao': loi['created_raw'], 'error_code': loi['error_code'],
        'ly_do': loi['error_code'].map(LY_DO),
    })
