"""Kiểm thử dq_evaluate.py – FR-07, FR-08, QL7-06 và hồi quy với số liệu đã nộp ở mục 4.5 BT1 (NFR-05)."""
import pathlib

import pandas as pd
import pytest

from src.etl import dq_evaluate as dq
from src.etl.extract import doc_tep, sang_bang_tam
from src.etl.transform import chuan_hoa, phan_loai

GOC = pathlib.Path(__file__).resolve().parent.parent


def _dot(phones, names, emails=None):
    bt = pd.DataFrame({'row_no': range(1, len(phones) + 1), 'phone_raw': phones, 'full_name_raw': names,
                       'email_raw': emails or [''] * len(phones)})
    df = chuan_hoa(bt)
    df['status'] = phan_loai(df, set())
    return df


def _do(df, ma, gd):
    k = dq.do_quy_tac(df, ma, gd)
    return k.pass_count, k.total_records


def test_mau_so_theo_pham_vi_ap_dung():
    df = _dot(['0901234567', '84901234567', '', '0912 345 678'], ['An', 'Bình', 'Chi', 'Dũng'])
    assert _do(df, 'DQ-01', 'TRUOC') == (3, 4)          # mọi hồ sơ
    assert _do(df, 'DQ-02', 'TRUOC') == (1, 3)          # chỉ hồ sơ CÓ số: thiếu số không bị phạt lần hai
    assert _do(df, 'DQ-02', 'SAU') == (3, 3)            # sau chuẩn hóa cả 3 số đều đúng mẫu
    assert _do(df, 'DQ-05', 'TRUOC') == (2, 3)          # 0901234567 xuất hiện 2 lần → 1 hồ sơ lặp
    assert _do(df, 'DQ-05', 'SAU') == (2, 3)            # DQ-05 so theo phone_norm ở cả hai giai đoạn


def test_dq04_truoc_do_tren_gia_tri_tho_sau_tren_name_norm():
    df = _dot(['0901234567', '0911111111'], ['An2', 'B'])
    assert _do(df, 'DQ-04', 'TRUOC') == (0, 2)          # có chữ số; 1 ký tự
    assert _do(df, 'DQ-03', 'TRUOC') == (2, 2)


@pytest.mark.gia_tri_bien
def test_khong_co_email_thi_ti_le_bang_1():
    k = dq.do_quy_tac(_dot(['0901234567'], ['An']), 'DQ-06', 'SAU')
    assert (k.total_records, k.ti_le) == (0, 1.0)      # QL7-06: mẫu số 0 → tỉ lệ đạt = 1


def test_tong_trong_so_phai_bang_1():
    lech = [dict(q) for q in dq.QUY_TAC_MAC_DINH]
    lech[0]['weight'] = 0.30
    with pytest.raises(ValueError, match='1,00'):
        dq.kiem_trong_so(lech)
    dq.kiem_trong_so(dq.QUY_TAC_MAC_DINH)


def test_chi_so_va_xep_loai():
    kq = [dq.KetQua(q['rule_code'], 'SAU', 10, 10) for q in dq.QUY_TAC_MAC_DINH]
    assert dq.chi_so_muc_do_sach(kq, dq.QUY_TAC_MAC_DINH, 'SAU') == pytest.approx(100)
    assert [dq.xep_loai(x) for x in (90, 89.99, 75, 74.99)] == ['Tốt', 'Chấp nhận được', 'Chấp nhận được', 'Kém']


@pytest.mark.parametrize('tep, truoc, sau', [
    ('data/raw/customers_raw.csv', 87.20, 94.76),          # mục 4.5 BT1, toàn bộ tệp
    ('data/processed/mau_cum_8000.csv', 87.34, 94.87),     # mẫu theo cụm do profiling_customers.py sinh
])
def test_hoi_quy_khop_so_lieu_bt1(tep, truoc, sau):
    p = GOC / tep
    if not p.exists():
        pytest.skip(f'chưa có {tep} (dữ liệu không commit) – đặt tệp vào đúng chỗ để chạy test này')
    df = chuan_hoa(sang_bang_tam(doc_tep(p)))
    df['status'] = phan_loai(df, set())
    kq = dq.do_mot_lan(df, dq.QUY_TAC_MAC_DINH)
    assert round(dq.chi_so_muc_do_sach(kq, dq.QUY_TAC_MAC_DINH, 'TRUOC'), 2) == truoc
    assert round(dq.chi_so_muc_do_sach(kq, dq.QUY_TAC_MAC_DINH, 'SAU'), 2) == sau


@pytest.mark.luong_dung
def test_sau_ham_kiem_tra_ve_so_dong_loi_va_ti_le_loi():
    """D2: ≥ 5 hàm kiểm chất lượng, mỗi hàm trả về số đo được – số dòng lỗi và tỉ lệ lỗi. [luồng đúng]"""
    assert len(dq.HAM_KIEM) == 6 and all(callable(h) for h in dq.HAM_KIEM.values())
    df = _dot(['0901234567', '84901234567', '', 'abc'], ['An', 'Bình', 'Chi', 'Dũng'])
    k = dq.kiem_dq01_so_dien_thoai_khong_trong(df, 'TRUOC')
    assert (k.so_loi, k.total_records, round(k.ti_le_loi, 4)) == (1, 4, 0.25)        # 1 hồ sơ thiếu số
    k = dq.kiem_dq02_so_dien_thoai_dung_mau(df, 'SAU')
    assert (k.so_loi, k.total_records) == (1, 3)                                    # 'abc' không quy đổi được
    k = dq.kiem_dq05_so_dien_thoai_khong_trung(df, 'SAU')
    assert (k.so_loi, k.total_records) == (1, 2)                                    # 84901234567 lặp 0901234567
    for ma, ham in dq.HAM_KIEM.items():
        k = ham(df, 'SAU')
        assert k.rule_code == ma and k.so_loi == k.total_records - k.pass_count
        assert 0 <= k.ti_le_loi <= 1


@pytest.mark.du_lieu_sai
def test_quy_tac_chua_co_ham_kiem_la_loi_cau_hinh():
    """Quy tắc đang bật mà chưa có hàm kiểm → lỗi cấu hình rõ ràng, không đo bừa. [dữ liệu sai]"""
    with pytest.raises(ValueError, match='DQ-99.*chưa có hàm kiểm'):
        dq.do_quy_tac(_dot(['0901234567'], ['An']), 'DQ-99', 'SAU')


@pytest.mark.gia_tri_bien
@pytest.mark.parametrize('ten, dat', [('An', 1), ('A', 0), ('A' * 120, 1), ('A' * 121, 0)],
                         ids=['2-ky-tu', '1-ky-tu', '120-ky-tu', '121-ky-tu'])
def test_dq04_bien_2_va_120_ky_tu(ten, dat):
    """DQ-04: họ tên 2–120 ký tự là đạt – kiểm đúng hai đầu mút và ngay ngoài mút. [giá trị biên]"""
    k = dq.kiem_dq04_ho_ten_hop_le(_dot(['0901234567'], [ten]), 'TRUOC')
    assert (k.pass_count, k.so_loi) == (dat, 1 - dat)


# ------------------------------------------------------------------ D3 (BT3, TD-38): độ đầy đủ theo từng cột
def _nguon(n_dong, n_trong, cot='so_dien_thoai'):
    return pd.DataFrame({'ho_ten': ['An'] * n_dong, cot: [''] * n_trong + ['0901234567'] * (n_dong - n_trong)})


@pytest.mark.gia_tri_bien
@pytest.mark.parametrize('n_dong, dat', [(50, True), (49, False)], ids=['98,00%-dat', '97,96%-chua-dat'])
def test_day_du_theo_cot_bien_nguong_98(n_dong, dat):
    """1 ô trống trên 50 dòng = 98,00% ≥ 98% là ĐẠT; trên 49 dòng = 97,96% là CHƯA ĐẠT. [giá trị biên]"""
    d = {x.cot: x for x in dq.do_day_du_theo_cot(_nguon(n_dong, 1), {'so_dien_thoai': 98})}
    assert d['so_dien_thoai'].dat is dat
    assert d['ho_ten'].nguong is None and d['ho_ten'].dat is None      # cột không có ngưỡng: chỉ đo


@pytest.mark.du_lieu_sai
def test_day_du_cot_co_nguong_ma_tep_khong_co_la_chua_dat():
    """Tệp bỏ mất cột có ngưỡng (email) → báo 0%, CHƯA ĐẠT, không im lặng bỏ qua. [dữ liệu sai]"""
    d = {x.cot: x for x in dq.do_day_du_theo_cot(_nguon(4, 0), {'email': 50})}
    assert (d['email'].co_cot, d['email'].so_co_gia_tri, d['email'].dat) == (False, 0, False)


@pytest.mark.luong_dung
def test_day_du_tren_du_lieu_mau_khop_o_trong_cua_extract():
    """Dữ liệu mẫu: số ô có giá trị của từng cột = số dòng − số ô trống mà extract đếm. [luồng đúng]"""
    from src import config
    from src.etl.extract import ho_so_tep
    df = doc_tep(GOC / 'data' / 'mau' / 'customers_mau.csv')
    d = {x.cot: x for x in dq.do_day_du_theo_cot(df, config.doc_cau_hinh()['nguong_day_du'])}
    assert {c: len(df) - k for c, (k, _) in ho_so_tep(df)['o_trong'].items()} == \
           {c: x.so_co_gia_tri for c, x in d.items()}
    assert [c for c, x in d.items() if x.dat is False] == ['so_dien_thoai', 'email']
