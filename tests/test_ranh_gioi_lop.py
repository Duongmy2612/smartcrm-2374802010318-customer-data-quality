"""Kiểm ranh giới lớp (BT2 – C2, D1; TD-22): ba pha E / T / L tách ở ba nơi và không gọi chéo sai chiều.

Đọc mã nguồn bằng ast (không chạy mã), nên test chạy được trên mọi máy, không cần CSDL.

    pha E   src/etl/extract.py                                 – chỉ đọc tệp nguồn
    pha T   src/etl/transform.py, dq_evaluate.py, match.py,
            danh_gia_match.py (NFR-03 – TD-32)                  – hàm thuần: không CSDL, không gọi pha E, pha L
    dùng chung src/etl/tien_ich.py                             – hàm thuần không thuộc pha nào (TD-29)
    pha L   src/etl/load_ops.py, load_dwh.py                    – chỉ chạy lệnh SQL: không gọi pha E / T
    điều phối  src/pipeline.py                                  – nơi DUY NHẤT gọi cả ba pha
               src/kiem_chung_nfr03.py                          – chỉ gọi pha E, T; không đọc/ghi CSDL (TD-32)
    lớp ①   dashboard/report.py                                 – chỉ đọc kho qua src/doc_kho.py (không gọi src/etl)
"""
import ast
import pathlib

import pytest

GOC = pathlib.Path(__file__).resolve().parent.parent
THU_VIEN_CSDL = {'sqlalchemy', 'psycopg2', 'src.db'}
PHA_E = ['src/etl/extract.py']
PHA_T = ['src/etl/transform.py', 'src/etl/dq_evaluate.py', 'src/etl/match.py', 'src/etl/danh_gia_match.py']
PHA_L = ['src/etl/load_ops.py', 'src/etl/load_dwh.py']


def _import(tep: str) -> set[str]:
    """Mọi module mà tệp import (kể cả import nằm trong hàm)."""
    cay = ast.parse((GOC / tep).read_text(encoding='utf-8'))
    ra = set()
    for nut in ast.walk(cay):
        if isinstance(nut, ast.Import):
            ra.update(a.name for a in nut.names)
        elif isinstance(nut, ast.ImportFrom) and nut.module:
            ra.add(nut.module)
            ra.update(f'{nut.module}.{a.name}' for a in nut.names)
    return ra


def _cham(imports: set[str], cam: set[str]) -> set[str]:
    return {m for m in imports for c in cam if m == c or m.startswith(c + '.')}


@pytest.mark.parametrize('tep', PHA_E + PHA_T)
def test_pha_e_va_t_khong_cham_csdl(tep):
    """Mở transform.py (hoặc extract, dq_evaluate, match): không có dấu vết của lớp lưu trữ. [luồng đúng]"""
    assert not _cham(_import(tep), THU_VIEN_CSDL), f'{tep} không được đọc/ghi CSDL – chuyển sang load_ops.py'
    nguon = (GOC / tep).read_text(encoding='utf-8')
    for lenh in ('INSERT INTO', 'UPDATE ops', 'DELETE FROM', 'CREATE TEMP'):
        assert lenh not in nguon, f'{tep} có câu SQL "{lenh}"'


@pytest.mark.parametrize('tep', PHA_T)
def test_pha_t_khong_goi_pha_e_va_l(tep):
    """Pha T không gọi pha E (đọc tệp) và pha L (ghi CSDL); hàm dùng chung lấy từ src/etl/tien_ich.py (TD-29)."""
    cam = {'src.etl.extract', 'src.etl.load_ops', 'src.etl.load_dwh', 'src.pipeline'}
    assert not _cham(_import(tep), cam), f'{tep} gọi sang pha khác – chỉ src/pipeline.py được nối các pha'


@pytest.mark.parametrize('tep', PHA_L)
def test_pha_l_khong_goi_pha_e_t(tep):
    """Pha load chỉ ghi dữ liệu đã tính sẵn, không tự chuẩn hóa / đo / so khớp."""
    cam = {'src.etl.extract', 'src.etl.transform', 'src.etl.dq_evaluate', 'src.etl.match', 'src.pipeline'}
    assert not _cham(_import(tep), cam)


def test_chi_pipeline_goi_ca_ba_pha():
    imp = _import('src/pipeline.py')
    assert {'src.etl.extract', 'src.etl.transform', 'src.etl.load_ops', 'src.etl.load_dwh'} <= imp


def test_kiem_chung_nfr03_khong_cham_csdl():
    """Phép kiểm chứng NFR-03 dựng khung cặp từ tệp nguồn bằng hàm thuần: không kết nối CSDL, không gọi pha L,
    nên chạy được trên máy chưa có PostgreSQL và không thay đổi dữ liệu đã nạp (TD-32)."""
    cam = THU_VIEN_CSDL | {'src.etl.load_ops', 'src.etl.load_dwh', 'src.pipeline'}
    assert not _cham(_import('src/kiem_chung_nfr03.py'), cam)


def test_dashboard_chi_doc_kho():
    """Lớp ① không gọi lớp ② xử lý và không ghi CSDL; truy vấn kho nằm ở src/doc_kho.py (chỉ SELECT)."""
    assert not _cham(_import('dashboard/report.py'), {'src.etl', 'src.pipeline'})
    nguon = (GOC / 'src/doc_kho.py').read_text(encoding='utf-8').upper()
    for lenh in ('INSERT ', 'UPDATE ', 'DELETE ', 'DROP ', 'TRUNCATE '):
        assert lenh not in nguon
