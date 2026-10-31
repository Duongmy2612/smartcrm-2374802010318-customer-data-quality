"""Kiểm thử lớp nghiệp vụ transform.py – các tiêu chí chấp nhận AC1.2 (docs/srs.md mục 3.1.2), QT-01, QT-02, FR-03."""
import pandas as pd
import pytest

from src.etl.transform import (chuan_hoa, chuan_hoa_ho_ten, chuan_hoa_so_dien_thoai, gan_ma_loi,
                                kiem_do_dai_ho_so_sach, phan_loai)


# ---------------------------------------------------------------- AC1.2: bốn dạng ghi → cùng một số
@pytest.mark.parametrize('tho', ['+84901234567', '84901234567', '0901 234 567', '0901.234.567',
                                 '0901-234-567', ' 0901234567 ', '+84 901 234 567'])
@pytest.mark.luong_dung
def test_ac12_cac_dang_ghi_quy_ve_mot_so(tho):
    assert chuan_hoa_so_dien_thoai(tho) == '0901234567'


@pytest.mark.parametrize('tho', ['', '   ', None])
def test_so_trong_tra_ve_none(tho):
    assert chuan_hoa_so_dien_thoai(tho) is None


@pytest.mark.parametrize('tho', ['090123456',      # 9 chữ số
                                 '09012345678',    # 11 chữ số bắt đầu bằng 0
                                 '8490123456',     # 84 nhưng chỉ 10 chữ số → không đổi tiền tố
                                 '849012345678',   # 84 + 10 chữ số → 12 chữ số
                                 '(090) 123 4567', # dấu ngoặc không thuộc QT-02
                                 '1901234567'])    # không bắt đầu bằng 0
@pytest.mark.du_lieu_sai
def test_so_khong_quy_doi_duoc(tho):
    assert chuan_hoa_so_dien_thoai(tho) is None


# ---------------------------------------------------------------- FR-03: họ tên
@pytest.mark.parametrize('tho, ky_vong', [
    ('  NGUYỄN   văn  an ', 'Nguyễn Văn An'),
    ('dương quang trung', 'Dương Quang Trung'),
    ('ĐẶNG VĂN NGÂN', 'Đặng Văn Ngân'),
    ('Hoang Kim Ha', 'Hoang Kim Ha'),                 # tên mất dấu từ nguồn: giữ nguyên, không đoán dấu
    ('nguyễn an', 'Nguyễn An'),           # dấu rời (NFD) → gộp NFC, không viết hoa nhầm
])
def test_fr03_chuan_hoa_ho_ten(tho, ky_vong):
    assert chuan_hoa_ho_ten(tho) == ky_vong


def test_ho_ten_trong_tra_ve_none():
    assert chuan_hoa_ho_ten('   ') is None


# ---------------------------------------------------------------- mã lỗi chính (TD-08)
def test_ma_loi_theo_thu_tu_uu_tien():
    assert gan_ma_loi('', None, None) == 'MISSING_PHONE'          # thiếu cả số lẫn tên → lỗi số
    assert gan_ma_loi('12345', None, 'An') == 'INVALID_PHONE'
    assert gan_ma_loi('0901234567', '0901234567', None) == 'MISSING_NAME'
    assert gan_ma_loi('0901234567', '0901234567', 'An') is None


# ---------------------------------------------------------------- phân loại: QT-01, QL7-04
def _bang(phones, names=None):
    names = names or ['An'] * len(phones)
    n = len(phones)
    return chuan_hoa(pd.DataFrame({'row_no': range(1, n + 1), 'phone_raw': phones, 'full_name_raw': names,
                                   'email_raw': [''] * n, 'address_raw': [''] * n}))


def test_ho_so_nap_som_nhat_vao_customer_clean_ho_so_sau_cho_quyet_dinh():
    df = _bang(['0901234567', '84901234567', '+84901234567', '0911111111'])
    assert phan_loai(df, set()).tolist() == ['CLEAN', 'PENDING_DUP', 'PENDING_DUP', 'CLEAN']


def test_so_da_co_trong_customer_clean_khong_tao_ho_so_moi():
    df = _bang(['0901234567', '0922222222'])
    assert phan_loai(df, {'0901234567'}).tolist() == ['PENDING_DUP', 'CLEAN']


def test_ho_so_loi_o_lai_bang_tam_va_khong_chan_ho_so_sau():
    df = _bang(['', '0901234567', '0901234567'], names=['An', '  ', 'Bình'])
    # dòng 2 thiếu tên (ERROR) nên không được tính là "hồ sơ nạp sớm hơn" của dòng 3
    assert df['error_code'].tolist()[:2] == ['MISSING_PHONE', 'MISSING_NAME']
    assert phan_loai(df, set()).tolist() == ['ERROR', 'ERROR', 'CLEAN']


@pytest.mark.du_lieu_sai
def test_chu_so_unicode_khong_duoc_chap_nhan():
    # '０９０…' là chữ số toàn chiều rộng: Python \d nhận, nhưng CHECK '^0[0-9]{9}$' của CSDL thì không
    assert chuan_hoa_so_dien_thoai('０９０１２３４５６７') is None


def test_kiem_do_dai_truoc_khi_ghi_customer_clean():
    from src.etl.transform import kiem_do_dai_ho_so_sach
    df = _bang(['0901234567', '0911111111', ''], names=['A' * 121, 'Bình', 'C' * 150])
    # dòng 1 hợp lệ nhưng tên 121 ký tự > 120 của customer_clean.full_name; dòng 3 là hồ sơ lỗi nên không xét
    assert kiem_do_dai_ho_so_sach(df) == {'name_norm': [1]}


@pytest.mark.gia_tri_bien
@pytest.mark.parametrize('tho, ky_vong', [
    ('0901234567', '0901234567'),       # đúng 10 chữ số → hợp lệ
    ('090123456', None),                # 9 chữ số (thiếu 1) → không quy đổi được
    ('09012345678', None),              # 11 chữ số bắt đầu bằng 0 (thừa 1) → không quy đổi được
    ('84901234567', '0901234567'),      # 84 + 9 chữ số = đúng 11 ký tự → đổi tiền tố
    ('8490123456', None),               # 84… chỉ 10 ký tự → KHÔNG đổi tiền tố, và không bắt đầu bằng 0
], ids=['10-chu-so', '9-chu-so', '11-chu-so', '84-du-11', '84-chi-10'])
def test_bien_do_dai_so_dien_thoai(tho, ky_vong):
    """QT-02 ở đúng ranh giới độ dài: 10 chữ số là hợp lệ; tiền tố 84 chỉ đổi khi có đúng 11 chữ số. [giá trị biên]"""
    assert chuan_hoa_so_dien_thoai(tho) == ky_vong


@pytest.mark.gia_tri_bien
def test_bien_120_ky_tu_cua_customer_clean():
    """Họ tên đúng 120 ký tự (bằng độ rộng cột full_name) được nhận; 121 ký tự bị từ chối kèm số dòng.
    [giá trị biên]"""
    bt = pd.DataFrame({'row_no': [1, 2], 'phone_raw': ['0901234567', '0912345678'],
                       'full_name_raw': ['A' * 120, 'B' * 121], 'email_raw': ['', ''], 'address_raw': ['', '']})
    assert kiem_do_dai_ho_so_sach(chuan_hoa(bt)) == {'name_norm': [2]}
