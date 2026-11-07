"""12 test case hệ thống của BT3 (tests/tc_bt3.py) chạy trong bộ pytest – `python -m pytest -q` chạy cả bộ.

Mỗi test case gắn marker theo năm loại của đề BT3 mục 2.2 (pytest.ini); bảng tóm tắt cuối lần chạy đếm theo loại.
Chưa có CSDL kiểm thử (DB_NAME_TEST, mặc định smartcrm_test) → 12 test case tự bỏ qua, không báo lỗi.
Xem đủ tám cột của một test case: python -m tests.tc_bt3 TC-06
"""
import pytest

from tests import tc_bt3


@pytest.fixture(scope='module')
def moi_truong():
    try:
        mt = tc_bt3.MoiTruong()
        mt.lam_sach()
    except Exception as e:                      # noqa: BLE001
        pytest.skip(f'không kết nối được CSDL kiểm thử: {type(e).__name__}')
    yield mt
    mt.engine.dispose()


@pytest.mark.parametrize('ca', [pytest.param(c, marks=getattr(pytest.mark, c.loai), id=c.ma) for c in tc_bt3.TCS])
def test_tc_bt3(ca, moi_truong):
    thuc_te, dat = tc_bt3.chay_mot(ca, moi_truong)
    assert dat, f'{ca.ma} FAIL – mong đợi: {ca.mong_doi} | thực tế: ' + ' | '.join(thuc_te)
