"""Kiểm thử lớp nghiệp vụ match.py – FR-04, QL7-02 … QL7-05 (UC3). Không cần CSDL.

Mỗi test ghi loại ở cuối docstring: [luồng đúng] · [biên] · [dữ liệu sai] (yêu cầu BT2 / buổi 10).
"""
import pandas as pd
import pytest

from src.etl.match import diem_tuong_dong, la_cap_fuzzy, tao_name_key, tim_cap
from src.etl.transform import chuan_hoa_so_dien_thoai


def _ho_so(*dong):
    """dong = (stg_id, phone_norm, họ tên) – name_key tính như match.py."""
    return pd.DataFrame({'stg_id': [d[0] for d in dong], 'phone_norm': [d[1] for d in dong],
                         'name_key': [tao_name_key(d[2]) for d in dong]})


def _cap(df):
    return {(int(r.stg_id_a), int(r.stg_id_b), r.match_type) for r in df.itertuples()}


def test_name_key_bo_dau_chu_thuong_va_khoang_trang():
    """Khóa họ tên dùng để chấm điểm (QL7-03): bỏ dấu, kể cả đ/Đ; chữ thường; bỏ khoảng trắng thừa. [luồng đúng]"""
    assert tao_name_key('  Đặng   Văn  ĐỨC ') == 'dang van duc'
    assert tao_name_key('Nguyễn Văn An') == tao_name_key('NGUYEN VAN AN') == 'nguyen van an'
    assert tao_name_key('   ') is None and tao_name_key(None) is None


def test_diem_tuong_dong_theo_cong_thuc_ql7_03():
    """Điểm = 0,6 × độ giống số + 0,4 × độ giống họ tên. [luồng đúng]"""
    assert diem_tuong_dong('0901234567', '0901234567', 'nguyen van an', 'nguyen van an') == 100
    # khác đúng 1 chữ số → fuzz.ratio = 90; cùng họ tên → 100  ⇒ 0,6 × 90 + 0,4 × 100 = 94
    assert diem_tuong_dong('0901234567', '0901234568', 'nguyen van an', 'nguyen van an') == 94
    # thứ tự từ trong họ tên không ảnh hưởng (token_sort_ratio)
    assert diem_tuong_dong('0901234567', '0901234567', 'an nguyen van', 'nguyen van an') == 100


def test_cung_so_tao_k_tru_1_cap_ghep_voi_ho_so_nap_som_nhat():
    """QL7-02: nhóm 3 hồ sơ cùng số → 2 cặp EXACT_PHONE, cả hai ghép với hồ sơ nạp sớm nhất. [luồng đúng]"""
    hs = _ho_so((5, '0901234567', 'Nguyễn Văn An'), (2, '0901234567', 'NGUYỄN VĂN AN'),
                (9, '0901234567', 'nguyen van an'), (4, '0987654321', 'Lê Chi'))
    assert _cap(tim_cap(hs)) == {(2, 5, 'EXACT_PHONE'), (2, 9, 'EXACT_PHONE')}


def test_diem_bang_dung_nguong_van_tao_cap_fuzzy():
    """Điểm BẰNG ngưỡng thì tạo cặp, thấp hơn 0,01 điểm thì không (≥, không phải >). [biên]"""
    hs = _ho_so((1, '0901234567', 'Trần Thị Mai'), (2, '0901234576', 'Tran Thi Mai'))
    d = diem_tuong_dong('0901234567', '0901234576', 'tran thi mai', 'tran thi mai')
    assert la_cap_fuzzy(85, 85) and not la_cap_fuzzy(84.99, 85)
    assert _cap(tim_cap(hs, nguong=d)) == {(1, 2, 'FUZZY')}
    assert tim_cap(hs, nguong=d + 0.01).empty


def test_ho_so_khong_co_so_hop_le_khong_tham_gia_so_khop():
    """QL7-04: số trống / rác không quy đổi được → không tạo cặp, dù họ tên giống hệt. [dữ liệu sai]"""
    hs = _ho_so((1, chuan_hoa_so_dien_thoai(''), 'Lê Chi'),
                (2, chuan_hoa_so_dien_thoai('abc-xyz'), 'Lê Chi'),
                (3, chuan_hoa_so_dien_thoai('0912.345.678'), 'Lê Chi'))
    assert tim_cap(hs).empty


def test_blocking_khong_so_hai_so_khac_ca_nua_dau_lan_nua_cuoi():
    """Đánh đổi của lập luận (1): hai số không chung 5 số đầu, không chung 5 số cuối thì không được so,
    dù cùng họ tên – recall phải theo dõi bằng NFR-03. [biên]"""
    hs = _ho_so((1, '0901234567', 'Phạm Minh Tú'), (2, '0911234560', 'Phạm Minh Tú'))
    assert tim_cap(hs, nguong=0).empty                 # ngưỡng 0 vẫn rỗng: cặp này chưa từng được so


def test_cap_da_co_hoac_da_giu_rieng_khong_de_xuat_lai():
    """QL7-05 / luồng 3a của UC5: cặp đã Giữ riêng (đã có trong dup_candidate) không được tạo lại. [luồng ngoại lệ]"""
    hs = _ho_so((1, '0901234567', 'Võ Văn An'), (2, '0901234567', 'Hoàng Bảo Sơn'))
    assert _cap(tim_cap(hs)) == {(1, 2, 'EXACT_PHONE')}
    assert tim_cap(hs, cap_da_co={(1, 2)}).empty


def test_chi_tra_ve_cap_co_ho_so_cua_dot_moi():
    """Nạp đợt 2: chỉ sinh cặp có ít nhất một hồ sơ mới; cặp cũ giữa hai hồ sơ đợt 1 không sinh lại. [luồng đúng]"""
    hs = _ho_so((1, '0901234567', 'An'), (2, '0901234567', 'An'), (3, '0901234567', 'An'))
    assert _cap(tim_cap(hs, ho_so_moi={3})) == {(1, 3, 'EXACT_PHONE')}


def test_fuzzy_chi_so_ho_so_dai_dien_cua_moi_so():
    """TD-18: số A có 2 hồ sơ, số B gần giống A có 1 hồ sơ → 1 cặp FUZZY (đại diện của A với B), không phải 2. [luồng đúng]"""
    hs = _ho_so((1, '0892444295', 'Võ Văn An'), (2, '0892444295', 'Võ Văn An'), (3, '0892444296', 'Võ Văn An'))
    assert _cap(tim_cap(hs)) == {(1, 2, 'EXACT_PHONE'), (1, 3, 'FUZZY')}


@pytest.mark.parametrize('ten', ['', None])
def test_tim_cap_tren_bang_rong_khong_loi(ten):
    """Đợt không có hồ sơ hợp lệ nào → bảng cặp rỗng, không lỗi. [dữ liệu sai]"""
    assert tim_cap(_ho_so((1, None, ten))).empty
