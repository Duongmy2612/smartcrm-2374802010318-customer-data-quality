"""② transform.py – FR-02, FR-03, FR-10 (UC2, UC9).

1. Chuẩn hóa số điện thoại về 0xxxxxxxxx (QT-02) và họ tên (FR-03) – hàm THUẦN, kiểm thử ở tests/.
2. Gắn mã lỗi chính cho hồ sơ không dùng được (MISSING_PHONE / INVALID_PHONE / MISSING_NAME).
3. Phân loại hồ sơ: ERROR (ở lại bảng tạm – QL7-04), CLEAN (vào customer_clean), PENDING_DUP (hồ sơ lặp,
   không tạo hồ sơ mới mà chờ quyết định ở UC5 – QT-01).
4. Ghi kết quả vào CSDL bằng câu lệnh SQL theo tập (UPDATE … FROM, INSERT … SELECT) thay vì từng dòng.
5. Xuất CSV hồ sơ lỗi kèm lý do (FR-10) để cửa hàng sửa tại nguồn.

name_key KHÔNG tạo ở đây: theo thay đổi số 2 của SRS 1.1, khóa tên thuộc FR-04 (match.py – Sprint 2).
"""
import re
import unicodedata

import pandas as pd
from sqlalchemy import text

from src.etl.extract import la_trong

KY_TU_BO = re.compile(r'[\s.\-]')          # QT-02: bỏ dấu cách, dấu chấm, dấu gạch
MAU_SO_CHUAN = re.compile(r'0[0-9]{9}')    # 10 chữ số ASCII, bắt đầu bằng 0 – khớp CHECK '^0[0-9]{9}$' ở sql/001
#   (không dùng \d: trong Python \d nhận cả chữ số Unicode như '９', CSDL sẽ từ chối)

# Lý do dạng câu chữ được sinh từ error_code khi xuất CSV, KHÔNG lưu vào CSDL (tránh lưu giá trị tính được – TD-07)
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


def xuat_ho_so_loi(df: pd.DataFrame, duong_dan) -> int:
    """FR-10 / UC9: CSV hồ sơ lỗi kèm mã lỗi và lý do; giá trị là giá trị GỐC để cửa hàng tìm và sửa tại nguồn.
    utf-8-sig để Excel mở đúng tiếng Việt. Tệp có dữ liệu cá nhân → nằm trong data/processed (không commit)."""
    loi = df[df['error_code'].notna()]
    out = pd.DataFrame({
        'row_no': loi['row_no'], 'record_id': loi['source_record_id'], 'ho_ten': loi['full_name_raw'],
        'so_dien_thoai': loi['phone_raw'], 'email': loi['email_raw'], 'dia_chi': loi['address_raw'],
        'ngay_tao': loi['created_raw'], 'error_code': loi['error_code'],
        'ly_do': loi['error_code'].map(LY_DO),
    })
    out.to_csv(duong_dan, index=False, encoding='utf-8-sig')
    return len(out)


# ------------------------------------------------------------------ đọc / ghi CSDL
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
