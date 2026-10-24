"""Kiểm thử load_dwh.py – FR-09, SCD loại 2 của dim_rule, nạp lại không nhân đôi (NFR-05).

Bốn test đầu là hàm thuần (không cần CSDL). Hai test cuối là tích hợp với PostgreSQL – dùng CSDL kiểm thử riêng
(fixture csdl_test ở tests/conftest.py); không kết nối được thì tự bỏ qua.
"""
from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import text

from src.etl.load_dwh import doi_soat, nap_kho, quyet_dinh_scd2
from tests.test_pipeline_csdl import _chay, _dem

T0, T1 = datetime(2026, 10, 1, 8, 0), datetime(2026, 10, 20, 9, 30)


def _qt(**doi):
    q = dict(rule_code='DQ-01', rule_name='Số điện thoại không trống', rule_type='COMPLETENESS',
             field_name='phone', weight=Decimal('0.25'), pass_threshold=Decimal('98.00'), is_active=True,
             updated_at=T0)
    return {**q, **doi}


def _phien_ban(**doi):
    p = {k: v for k, v in _qt().items() if k != 'updated_at'}
    return {**p, 'rule_key': 7, 'valid_from': T0, **doi}


def test_scd2_quy_tac_moi_tao_phien_ban_dau_tien():
    """Kho chưa có quy tắc → thêm phiên bản đầu, không đóng gì. [luồng đúng]"""
    dong, them = quyet_dinh_scd2({}, [_qt()])
    assert dong == [] and [q['rule_code'] for q in them] == ['DQ-01']


def test_scd2_doi_nguong_dong_phien_ban_cu_them_phien_ban_moi():
    """UC6 đổi ngưỡng 98 → 95: phiên bản cũ đóng tại updated_at, phiên bản mới bắt đầu từ đó. [luồng đúng]"""
    dong, them = quyet_dinh_scd2({'DQ-01': _phien_ban()}, [_qt(pass_threshold=95, updated_at=T1)])
    assert dong == [{'rule_key': 7, 'valid_to': T1}]
    assert them[0]['pass_threshold'] == 95 and them[0]['updated_at'] == T1


def test_scd2_luu_lai_cung_cau_hinh_khong_sinh_phien_ban():
    """Bấm Lưu mà không đổi gì (chỉ updated_at đổi; 0.25 dạng float, 98 dạng int) → không sinh phiên bản. [biên]"""
    assert quyet_dinh_scd2({'DQ-01': _phien_ban()}, [_qt(weight=0.25, pass_threshold=98, updated_at=T1)]) == ([], [])


def test_scd2_cau_hinh_doi_ma_thoi_diem_khong_tien_len_bi_tu_choi():
    """Cấu hình đổi nhưng updated_at không sau valid_from → không thể đóng phiên bản đúng thứ tự. [dữ liệu sai]"""
    with pytest.raises(ValueError, match='không sau valid_from'):
        quyet_dinh_scd2({'DQ-01': _phien_ban(valid_from=T1)}, [_qt(weight=0.30, updated_at=T0)])


def test_nap_kho_lan_hai_khong_nhan_doi_dong(csdl_test):
    """Phép thử nạp lại của buổi 10: chạy load_dwh lần hai → không thêm dòng nào; đối soát ops ↔ dwh khớp hết.
    [luồng đúng]"""
    engine, p, tmp = csdl_test
    _chay(p, tmp)                                     # UC1 → UC3 → kho
    dem = lambda: [_dem(engine, f'SELECT count(*) FROM dwh.{b}') for b in   # noqa: E731
                   ('dim_batch', 'dim_rule', 'fact_dq_check', 'fact_dup_pair')]
    truoc = dem()
    assert truoc == [1, 6, 12, 1]                     # 1 đợt · 6 quy tắc · 6 × 2 kết quả đo · 1 cặp cùng số
    with engine.begin() as conn:
        assert set(nap_kho(conn).values()) == {0}
        assert all(r['khop'] for r in doi_soat(conn))
    assert dem() == truoc


def test_doi_quy_tac_lan_do_cu_giu_phien_ban_cu(csdl_test):
    """SCD loại 2 (lập luận 3, NFR-05): đổi ngưỡng DQ-01 rồi nạp đợt mới – lần đo cũ vẫn gắn ngưỡng 98,
    lần đo mới gắn ngưỡng 95; chỉ số của đợt cũ không bị tính lại. [luồng đúng]"""
    engine, p, tmp = csdl_test
    _chay(p, tmp)
    with engine.begin() as conn:
        conn.execute(text("UPDATE ops.dq_rule SET pass_threshold = 95, updated_by = 'ql.mm001', "
                          "updated_at = clock_timestamp() WHERE rule_code = 'DQ-01'"))
    _chay(p, tmp, nap_lai=True)                       # đợt 2 đo bằng cấu hình mới
    assert _dem(engine, "SELECT count(*) FROM dwh.dim_rule WHERE rule_code = 'DQ-01'") == 2
    sql = ("SELECT v.pass_threshold FROM dwh.v_rule_rate v WHERE v.rule_code = 'DQ-01' AND v.batch_id = {} "
           "AND v.measure_stage = 'SAU'")
    assert _dem(engine, sql.format(1)) == 98 and _dem(engine, sql.format(2)) == 95


def test_sua_tay_quy_tac_khong_ghi_updated_at_van_nap_duoc(csdl_test):
    """TD-21: sửa ngưỡng bằng một câu UPDATE không ghi updated_at (như sửa tay bằng psql) → trigger đặt updated_at
    theo giờ CSDL, lần nạp sau vẫn chạy và sinh phiên bản mới, không dừng với lỗi. [dữ liệu sai]"""
    engine, p, tmp = csdl_test
    _chay(p, tmp)
    with engine.begin() as conn:
        conn.execute(text("UPDATE ops.dq_rule SET pass_threshold = 90 WHERE rule_code = 'DQ-06'"))
    _chay(p, tmp, nap_lai=True)
    assert _dem(engine, "SELECT count(*) FROM dwh.dim_rule WHERE rule_code = 'DQ-06'") == 2
    assert _dem(engine, "SELECT count(*) FROM dwh.dim_rule WHERE rule_code = 'DQ-06' AND valid_to IS NULL") == 1
