"""Bảo mật của kết nối dashboard (BT3: BUG-16, TD-36; checklist bảo mật mục 3, 4).

Dashboard dùng tài khoản riêng DASH_DB_USER chỉ đọc được kho dwh. TC-12 (tests/tc_bt3.py) kiểm từ đầu tới cuối;
các test dưới đây giữ từng phần của bản sửa.
"""
import pytest
from sqlalchemy import text

from src import db


@pytest.mark.chat_luong_bao_mat
def test_dashboard_khong_con_dung_chung_tai_khoan_pipeline(monkeypatch):
    """Thiếu DASH_DB_USER → báo thiếu cấu hình, KHÔNG lặng lẽ dùng DB_USER (đọc được ops). [bảo mật]"""
    monkeypatch.setenv('DASH_DB_USER', '')
    with pytest.raises(db.ThieuCauHinhCSDL, match='DASH_DB_USER'):
        db.tao_engine_chi_doc()


@pytest.mark.du_lieu_sai
@pytest.mark.parametrize('ten', ['dash reader', 'x;DROP ROLE postgres', 'Dash', ''])
def test_ten_tai_khoan_la_chi_bi_tu_choi(monkeypatch, ten):
    """Tên tài khoản đi thẳng vào câu CREATE ROLE nên chỉ nhận chữ thường, số, gạch dưới. [dữ liệu sai]"""
    monkeypatch.setenv('DASH_DB_USER', ten)
    monkeypatch.setenv('DASH_DB_PASSWORD', 'mat_khau_thu')
    with pytest.raises(db.ThieuCauHinhCSDL):
        db.tai_khoan_dashboard()


@pytest.mark.tai_lap
def test_cap_quyen_chay_lai_khong_loi_va_khong_co_quyen_tren_ops(csdl_test, monkeypatch):
    """Khởi tạo CSDL hai lần: không lỗi; tài khoản dashboard có SELECT trên dwh, không có quyền gì trên ops. [tái lập]"""
    engine, _, _ = csdl_test
    monkeypatch.setenv('DASH_DB_USER', 'dash_reader_kiem_thu')
    monkeypatch.setenv('DASH_DB_PASSWORD', 'mat_khau_kiem_thu')
    for _ in range(2):
        with engine.begin() as conn:
            assert db.khoi_tao_csdl(conn)
    with engine.connect() as conn:
        q = ("SELECT has_schema_privilege('dash_reader_kiem_thu', :s, 'USAGE'), "
             "has_table_privilege('dash_reader_kiem_thu', :b, 'SELECT')")
        assert tuple(conn.execute(text(q), {'s': 'dwh', 'b': 'dwh.fact_dq_check'}).one()) == (True, True)
        assert tuple(conn.execute(text(q), {'s': 'ops', 'b': 'ops.stg_customer'}).one()) == (False, False)
        conn.execute(text('DROP OWNED BY dash_reader_kiem_thu; DROP ROLE dash_reader_kiem_thu'))
        conn.commit()
