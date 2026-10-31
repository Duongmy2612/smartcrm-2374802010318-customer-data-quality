"""Kiểm thử pipeline UC1 ở chế độ --khong-ghi-csdl (không cần PostgreSQL)."""
import pytest

from src import pipeline

TEP = ('record_id,ho_ten,so_dien_thoai,email,dia_chi,ngay_tao\n'
       '1,nguyễn văn an,0901 234 567,an@gmail.com,1 Lê Lợi,2025-01-01\n'
       '2,NGUYỄN VĂN AN,+84901234567,,,2025-02-01\n'           # cùng số với dòng 1 → hồ sơ lặp
       '3,Trần Bình,,binh@gmail.com,,2025-03-01\n'             # thiếu số → MISSING_PHONE
       '4,Lê Chi,0912.345.678,,,2025-04-01\n')


def _tep(tmp_path, noi_dung=TEP):
    p = tmp_path / 'dot.csv'
    p.write_text(noi_dung, encoding='utf-8')
    return p


@pytest.mark.luong_dung
def test_chay_thu_khong_ghi_csdl(tmp_path):
    bc = pipeline.chay_uc1(_tep(tmp_path), 'TONG_HOP', 'my.marketing', ghi_csdl=False,
                           in_ra=lambda *_: None, thu_muc_ra=tmp_path)
    assert bc['chuan_hoa']['trang_thai'] == {'CLEAN': 2, 'PENDING_DUP': 1, 'ERROR': 1}
    assert (tmp_path / 'ho_so_loi_dot_thu.csv').read_text(encoding='utf-8-sig').count('MISSING_PHONE') == 1
    assert 0 <= bc['chi_so']['TRUOC'] <= bc['chi_so']['SAU'] <= 100
    assert bc['so_khop']['exact'] == 1 and bc['so_khop']['fuzzy'] == 0   # UC3 chạy thử trong bộ nhớ


def test_chi_nhan_vien_marketing_duoc_nap_tep(tmp_path):
    with pytest.raises(pipeline.TuChoi, match='MARKETING|Marketing'):
        pipeline.chay_uc1(_tep(tmp_path), 'MM001', 'ql.mm001', ghi_csdl=False, in_ra=lambda *_: None)


@pytest.mark.du_lieu_sai
def test_gia_tri_qua_dai_bi_tu_choi_ca_dot(tmp_path):
    p = _tep(tmp_path, 'ho_ten,so_dien_thoai\n' + 'A' * 130 + ',0901234567\n')
    with pytest.raises(pipeline.TuChoi, match='name_norm > 120'):
        pipeline.chay_uc1(p, 'TONG_HOP', 'my.marketing', ghi_csdl=False, in_ra=lambda *_: None)


@pytest.mark.du_lieu_sai
def test_ma_thoat(tmp_path):
    assert pipeline.main(['--tep', str(_tep(tmp_path, 'ho_ten\nAn\n')), '--khong-ghi-csdl']) == pipeline.MA_TU_CHOI
    assert pipeline.main(['--tep', str(tmp_path / 'khong_co.csv'), '--khong-ghi-csdl']) == pipeline.MA_LOI_KY_THUAT


def test_mat_ket_noi_csdl_bao_ro_va_khong_lo_mat_khau(tmp_path, monkeypatch, capsys):
    """Suy giảm có kiểm soát: PostgreSQL không chạy → mã thoát 1, câu báo lỗi chỉ cách sửa, không in mật khẩu
    hay chuỗi kết nối (NFR-07), không ghi gì."""
    for k, v in {'DB_HOST': '127.0.0.1', 'DB_PORT': '1', 'DB_NAME': 'smartcrm', 'DB_USER': 'u',
                 'DB_PASSWORD': 'MatKhauBiMat123'}.items():
        monkeypatch.setenv(k, v)
    assert pipeline.main(['--tep', str(_tep(tmp_path))]) == pipeline.MA_LOI_KY_THUAT
    loi = capsys.readouterr().err
    assert 'Không kết nối được PostgreSQL' in loi and 'brew services start' in loi
    assert 'MatKhauBiMat123' not in loi and 'postgresql+psycopg2://' not in loi
