"""Kiểm thử phần quy tắc của dashboard (src/doc_kho.py) – QT-14, khoảng điểm K3, câu giải thích khi rỗng.

Không cần Streamlit hay CSDL: dashboard/report.py chỉ hiển thị, quy tắc nằm ở src/doc_kho.py.
"""
from datetime import date

import pytest

from src.doc_kho import cau_giai_thich_rong, don_vi_duoc_xem, khoang_diem, loc_don_vi, ly_do_rong, vi_tri_nguong

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
@pytest.mark.gia_tri_bien
def test_khoang_diem_k3_bien_thuoc_khoang_tren(diem, khoang):
    """Khoảng điểm của K3 (docs/data-requirements.md mục 5.2): đúng 85 nằm ở khoảng 85 – <90. [biên]"""
    assert khoang_diem(diem) == khoang


def test_qt14_chon_don_vi_ngoai_pham_vi_van_khong_xem_duoc():
    """Bộ lọc đơn vị không vượt được QT-14: Quản lý MM001 chọn MM002 → không truy vấn đơn vị nào. [dữ liệu sai]"""
    assert loc_don_vi(['MM001'], ['MM002']) == []
    assert loc_don_vi(['MM001'], []) == ['MM001'] and loc_don_vi(None, []) is None


@pytest.mark.parametrize('nguong, x', [(85, 0.5), (87.5, 1.0), (90, 1.5), (95, 2.5), (100, 3.5), (70, -0.5)],
                         ids=['85', '87.5', '90', '95', '100', '70'])
def test_duong_nguong_k3_dung_cho_khi_doi_nguong(nguong, x):
    """Đường ngưỡng ở K3 nằm đúng ranh giới cột (85 → giữa '< 85' và '85 – <90'), ngưỡng khác thì nội suy. [biên]"""
    assert vi_tri_nguong(nguong) == pytest.approx(x)


@pytest.mark.parametrize('tham, ly_do', [
    ((False, None, 0, 0, 0, 0), 'kho_rong'),
    ((True, [], 3, 0, 0, 0), 'khong_quyen'),
    ((True, ['MM001'], 3, 0, 0, 0), 'qt14'),               # có đợt trong khoảng ngày nhưng của đơn vị khác
    ((True, ['MM001'], 0, 0, 0, 0), 'khoang_ngay'),        # không đơn vị nào có đợt trong khoảng ngày
    ((True, None, 3, 3, 0, 0), 'chua_chon_don_vi'),        # bỏ chọn hết đơn vị nguồn
    ((True, None, 3, 3, 2, 0), 'chua_chon_dot'),           # bỏ chọn hết đợt nạp
    ((True, None, 3, 3, 2, 1), None),
], ids=['kho-rong', 'khong-quyen', 'qt14', 'khoang-ngay', 'chua-chon-don-vi', 'chua-chon-dot', 'co-du-lieu'])
def test_ly_do_rong_dung_nguyen_nhan(tham, ly_do):
    """Mỗi nguyên nhân rỗng cho đúng một lý do – câu giải thích không đổ lỗi sai chỗ. [trạng thái rỗng]"""
    assert ly_do_rong(*tham) == ly_do


def test_bo_loc_rong_noi_ro_vi_sao_va_nen_lam_gi():
    """Câu giải thích nêu đơn vị, khoảng ngày, QT-14 và việc nên làm. [trạng thái rỗng]"""
    cau = cau_giai_thich_rong('qt14', ['MM001'], date(2026, 10, 1), date(2026, 10, 24))
    assert 'MM001' in cau and '01/10/2026 – 24/10/2026' in cau and 'QT-14' in cau and 'Thử mở rộng' in cau
    assert 'đơn vị khác' not in cau_giai_thich_rong('khoang_ngay', ['MM001'], date(2026, 10, 1), date(2026, 10, 24))


def test_kho_chua_co_du_lieu_chi_lenh_chay_luong_chinh():
    """Kho rỗng thì hướng dẫn chạy luồng chính trước, không nói chung chung 'không có dữ liệu'. [trạng thái rỗng]"""
    assert 'python -m src.pipeline' in cau_giai_thich_rong('kho_rong', None, None, None)
