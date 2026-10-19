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
