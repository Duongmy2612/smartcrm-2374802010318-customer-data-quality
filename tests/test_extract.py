"""Kiểm thử extract.py – FR-01, AC1.3 (thiếu cột → từ chối cả đợt), AC1.4 (băm SHA-256)."""
import hashlib

import pytest

from src.etl.extract import TepBiTuChoi, bam_sha256, doc_tep, ho_so_tep, sang_bang_tam


def _ghi(tmp_path, noi_dung, ten='tep.csv'):
    p = tmp_path / ten
    p.write_text(noi_dung, encoding='utf-8')
    return p


def test_ac13_thieu_cot_bat_buoc_bi_tu_choi(tmp_path):
    p = _ghi(tmp_path, 'record_id,ho_ten,email\n1,An,a@b.vn\n')
    with pytest.raises(TepBiTuChoi, match='so_dien_thoai'):
        doc_tep(p)


def test_ac13_bao_du_ten_cac_cot_thieu(tmp_path):
    p = _ghi(tmp_path, 'record_id,email\n1,a@b.vn\n')
    with pytest.raises(TepBiTuChoi, match='ho_ten, so_dien_thoai'):
        doc_tep(p)


def test_giu_nguyen_gia_tri_tho_va_so_0_dau(tmp_path):
    p = _ghi(tmp_path, 'ho_ten,so_dien_thoai\n  an  ,0901234567\nBình,\n')
    bt = sang_bang_tam(doc_tep(p))
    assert bt['full_name_raw'].tolist() == ['  an  ', 'Bình']      # không strip, không đổi hoa thường
    assert bt['phone_raw'].tolist() == ['0901234567', '']          # không mất số 0, ô trống là chuỗi rỗng
    assert bt['row_no'].tolist() == [1, 2]
    assert bt['email_raw'].tolist() == ['', '']                    # cột không bắt buộc vắng mặt → trống


def test_ho_so_tep_dem_o_trong(tmp_path):
    p = _ghi(tmp_path, 'ho_ten,so_dien_thoai\nAn,0901234567\nBình,  \n')
    hs = ho_so_tep(doc_tep(p))
    assert hs['so_dong'] == 2 and hs['so_cot'] == 2
    assert hs['o_trong']['so_dien_thoai'] == (1, 0.5)


def test_ac14_bam_sha256_theo_noi_dung(tmp_path):
    a = _ghi(tmp_path, 'ho_ten,so_dien_thoai\nAn,0901234567\n', 'a.csv')
    b = _ghi(tmp_path, 'ho_ten,so_dien_thoai\nAn,0901234567\n', 'b_doi_ten.csv')
    assert bam_sha256(a) == bam_sha256(b) == hashlib.sha256(a.read_bytes()).hexdigest()


def test_khong_nhan_dinh_dang_khac(tmp_path):
    with pytest.raises(TepBiTuChoi):
        doc_tep(_ghi(tmp_path, 'x', 'tep.txt'))


def test_doc_duoc_tep_excel(tmp_path):
    import pandas as pd
    p = tmp_path / 'cua_hang.xlsx'
    pd.DataFrame({'ho_ten': ['An'], 'so_dien_thoai': ['0901234567']}).to_excel(p, index=False)
    bt = sang_bang_tam(doc_tep(p))
    assert bt['phone_raw'].tolist() == ['0901234567']
