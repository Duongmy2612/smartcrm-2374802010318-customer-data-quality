"""Kiểm thử tích hợp UC1 với PostgreSQL thật: AC1.4, ROLLBACK (TD-09), NFR-04, DDL chạy lại được.

Dùng một CSDL RIÊNG cho kiểm thử (mặc định smartcrm_test, đổi bằng biến DB_NAME_TEST) – mỗi test xóa và tạo lại
schema ops trong CSDL đó, KHÔNG đụng tới CSDL smartcrm đang dùng. Tạo một lần: `createdb smartcrm_test`.
Không kết nối được (chưa có PostgreSQL, chưa tạo CSDL test, thiếu .env) → các test này tự bỏ qua (skip).
"""
import os

import pytest
from sqlalchemy import text

from src import db, pipeline
from src.etl import transform
from tests.test_pipeline import TEP


@pytest.fixture
def csdl_test(monkeypatch, tmp_path):
    from dotenv import load_dotenv
    load_dotenv(db.GOC / '.env')
    monkeypatch.setenv('DB_NAME', os.getenv('DB_NAME_TEST', 'smartcrm_test'))
    try:
        engine = db.tao_engine()
        with engine.begin() as conn:
            conn.exec_driver_sql('DROP SCHEMA IF EXISTS ops CASCADE')
    except Exception as e:                      # noqa: BLE001
        pytest.skip(f'không kết nối được CSDL kiểm thử: {type(e).__name__}')
    p = tmp_path / 'dot.csv'
    p.write_text(TEP, encoding='utf-8')
    yield engine, p, tmp_path
    engine.dispose()


def _chay(p, tmp_path, **kw):
    return pipeline.chay_uc1(p, 'TONG_HOP', 'my.marketing', in_ra=lambda *_: None, thu_muc_ra=tmp_path, **kw)


def _dem(engine, sql):
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar_one()


def test_nap_tep_ghi_dung_bang(csdl_test):
    engine, p, tmp = csdl_test
    _chay(p, tmp)
    assert _dem(engine, 'SELECT count(*) FROM ops.load_batch') == 1
    assert _dem(engine, 'SELECT row_count FROM ops.load_batch') == 4
    assert _dem(engine, "SELECT count(*) FROM ops.stg_customer WHERE status = 'CLEAN' AND customer_id IS NOT NULL") == 2
    assert _dem(engine, "SELECT count(*) FROM ops.stg_customer WHERE status = 'PENDING_DUP' AND customer_id IS NULL") == 1
    assert _dem(engine, "SELECT count(*) FROM ops.stg_customer WHERE error_code = 'MISSING_PHONE'") == 1
    assert _dem(engine, 'SELECT count(*) FROM ops.dq_result') == 12          # 6 quy tắc × 2 giai đoạn
    assert _dem(engine, "SELECT full_name FROM ops.customer_clean WHERE phone = '0901234567'") == 'Nguyễn Văn An'


def test_ac14_nap_lai_bi_tu_choi_roi_xac_nhan(csdl_test):
    engine, p, tmp = csdl_test
    _chay(p, tmp)
    with pytest.raises(pipeline.TuChoi, match='đã được nạp'):
        _chay(p, tmp)
    assert _dem(engine, 'SELECT count(*) FROM ops.load_batch') == 1          # bảng tạm không đổi
    _chay(p, tmp, nap_lai=True)                                               # có xác nhận → đợt 2
    assert _dem(engine, "SELECT count(*) FROM ops.stg_customer WHERE batch_id = 2 AND status = 'PENDING_DUP'") == 3
    assert _dem(engine, 'SELECT count(*) FROM ops.customer_clean') == 2      # QT-01: không tạo hồ sơ mới


def test_loi_giua_chung_thi_rollback_ca_dot(csdl_test, monkeypatch):
    engine, p, tmp = csdl_test

    def hong(conn, batch_id):
        raise RuntimeError('giả lập mất kết nối khi ghi customer_clean')
    monkeypatch.setattr(transform, 'ghi_customer_clean', hong)
    with pytest.raises(RuntimeError):
        _chay(p, tmp)
    with engine.connect() as conn:          # DDL cũng nằm trong giao dịch nên schema ops có thể chưa tồn tại
        co_bang = conn.execute(text("SELECT to_regclass('ops.load_batch')")).scalar_one()
        assert co_bang is None or conn.execute(text('SELECT count(*) FROM ops.load_batch')).scalar_one() == 0


def test_nfr04_so_dang_hieu_luc_dung_mau_va_khong_trung(csdl_test):
    engine, p, tmp = csdl_test
    _chay(p, tmp)
    _chay(p, tmp, nap_lai=True)
    assert _dem(engine, "SELECT count(*) - count(DISTINCT phone) FROM ops.customer_clean WHERE is_active") == 0
    assert _dem(engine, "SELECT count(*) FROM ops.customer_clean WHERE phone !~ '^0[0-9]{9}$'") == 0


def test_ddl_chay_lai_khong_loi(csdl_test):
    engine, _, _ = csdl_test
    with engine.begin() as conn:
        db.khoi_tao_csdl(conn)
        db.khoi_tao_csdl(conn)
        assert conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'ops'")).scalar_one() == 6
