"""Dữ liệu mẫu trong repo (data/mau/, sinh bằng scripts/sinh_du_lieu_mau.py, seed 42) – BT2 TP4.

Chạy phần tính toán của luồng chính (không cần CSDL) trên tệp mẫu đã commit và kiểm đúng các con số README
mục 5 ghi ("Kết quả đúng"), để người chấm biết chạy ra số khác là có gì sai.
"""
import pathlib

import pytest

from src import pipeline
from src.etl import extract

GOC = pathlib.Path(__file__).resolve().parent.parent
MAU = GOC / 'data' / 'mau' / 'customers_mau.csv'


@pytest.mark.luong_dung
def test_du_lieu_mau_ra_dung_so_lieu_readme(tmp_path):
    """Tệp mẫu 414 dòng → CLEAN 343 · PENDING_DUP 40 · ERROR 31; chỉ số 88,41 → 95,79; EXACT_PHONE 40 · FUZZY 3.
    [luồng đúng]"""
    bc = pipeline.chay_uc1(MAU, 'TONG_HOP', 'my.marketing', ghi_csdl=False, in_ra=lambda *_: None,
                           thu_muc_ra=tmp_path)
    assert bc['so_dong_tep'] == 414
    assert bc['chuan_hoa']['trang_thai'] == {'CLEAN': 343, 'PENDING_DUP': 40, 'ERROR': 31}
    assert bc['chuan_hoa']['ma_loi'] == {'MISSING_PHONE': 24, 'INVALID_PHONE': 5, 'MISSING_NAME': 2}
    assert bc['chi_so'] == {'TRUOC': 88.41, 'SAU': 95.79}
    assert (bc['so_khop']['exact'], bc['so_khop']['fuzzy']) == (40, 3)


def test_tep_mau_sinh_lai_dung_tung_byte(tmp_path, monkeypatch):
    """NFR-05: chạy lại script sinh mẫu (seed 42) cho đúng tệp đã commit."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('sinh', GOC / 'scripts' / 'sinh_du_lieu_mau.py')
    sinh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sinh)
    dong, _ = sinh.sinh()
    sinh.ghi(dong, tmp_path / 'mau.csv')
    assert (tmp_path / 'mau.csv').read_bytes() == MAU.read_bytes()


@pytest.mark.du_lieu_sai
def test_tep_mau_thieu_cot_bi_tu_choi_ma_thoat_2():
    """AC1.3: tệp mẫu thiếu cột so_dien_thoai → từ chối cả đợt, thông báo tên cột thiếu, mã thoát 2. [dữ liệu sai]"""
    tep = GOC / 'data' / 'mau' / 'customers_thieu_cot.csv'
    with pytest.raises(extract.TepBiTuChoi, match='so_dien_thoai'):
        extract.doc_tep(tep)
    assert pipeline.main(['--tep', str(tep), '--khong-ghi-csdl']) == pipeline.MA_TU_CHOI
