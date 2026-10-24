"""Kiểm thử phần quy tắc của dashboard (src/doc_kho.py) – QT-14, khoảng điểm K3, câu giải thích khi rỗng.

Không cần Streamlit hay CSDL: dashboard/report.py chỉ hiển thị, quy tắc nằm ở src/doc_kho.py.
"""
from datetime import date

import pytest

from src.doc_kho import cau_giai_thich_rong, don_vi_duoc_xem, khoang_diem

CAU_HINH = {'nguoi_dung': [{'ten_dang_nhap': 'my.marketing', 'vai_tro': 'MARKETING', 'don_vi': 'VAN_PHONG'},
                           {'ten_dang_nhap': 'ql.mm001', 'vai_tro': 'QUAN_LY_CUA_HANG', 'don_vi': 'MM001'}]}


def test_qt14_marketing_xem_toan_cong_ty_quan_ly_chi_xem_don_vi_minh():
    """QT-14 / Bảng 1.2. [luồng đúng]"""
    assert don_vi_duoc_xem(CAU_HINH, 'my.marketing') is None          # None = mọi đơn vị nguồn
    assert don_vi_duoc_xem(CAU_HINH, 'ql.mm001') == ['MM001']


def test_qt14_tai_khoan_khong_co_trong_cau_hinh_khong_xem_duoc_gi():
    """Không đoán quyền cho tài khoản lạ. [dữ liệu sai]"""
    assert don_vi_duoc_xem(CAU_HINH, 'ai.do') == []


@pytest.mark.parametrize('diem, khoang', [(84.99, '< 85'), (85, '85 – <90'), (89.99, '85 – <90'),
                                          (90, '90 – <95'), (95, '≥ 95'), (100, '≥ 95')],
                         ids=['84.99', '85', '89.99', '90', '95', '100'])
def test_khoang_diem_k3_bien_thuoc_khoang_tren(diem, khoang):
    """Khoảng điểm của K3 (docs/data-requirements.md mục 5.2): đúng 85 nằm ở khoảng 85 – <90. [biên]"""
    assert khoang_diem(diem) == khoang


def test_bo_loc_rong_noi_ro_vi_sao_va_nen_lam_gi():
    """Trạng thái rỗng: câu giải thích nêu đơn vị, khoảng ngày, QT-14 và việc nên làm. [trạng thái rỗng]"""
    cau = cau_giai_thich_rong(['MM001'], [], date(2026, 10, 1), date(2026, 10, 24), co_du_lieu_trong_kho=True)
    assert 'MM001' in cau and '01/10/2026 – 24/10/2026' in cau and 'QT-14' in cau and 'Thử mở rộng' in cau


def test_kho_chua_co_du_lieu_chi_lenh_chay_luong_chinh():
    """Kho rỗng thì hướng dẫn chạy luồng chính trước, không nói chung chung 'không có dữ liệu'. [trạng thái rỗng]"""
    assert 'python -m src.pipeline' in cau_giai_thich_rong(None, [], None, None, co_du_lieu_trong_kho=False)
