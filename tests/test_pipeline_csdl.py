"""Kiểm thử tích hợp luồng chính (UC1 → UC3 → kho) với PostgreSQL thật: AC1.4, ROLLBACK (TD-09), NFR-04,
DDL chạy lại được.

Dùng một CSDL RIÊNG cho kiểm thử (fixture csdl_test ở tests/conftest.py; mặc định smartcrm_test, đổi bằng biến
DB_NAME_TEST) – mỗi test xóa và tạo lại schema ops, dwh trong CSDL đó, KHÔNG đụng tới CSDL smartcrm đang dùng.
Tạo một lần: `createdb smartcrm_test`.
Không kết nối được (chưa có PostgreSQL, chưa tạo CSDL test, thiếu .env) → các test này tự bỏ qua (skip).
"""
import pytest
from sqlalchemy import text

from src import db, pipeline
from src.etl import load_ops, transform


def _chay(p, tmp_path, **kw):
    return pipeline.chay_uc1(p, 'TONG_HOP', 'my.marketing', in_ra=lambda *_: None, thu_muc_ra=tmp_path, **kw)


def _dem(engine, sql):
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar_one()


@pytest.mark.luong_dung
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
    # UC3: hồ sơ lặp (dòng 2) ghép với hồ sơ nạp sớm nhất cùng số (dòng 1) → 1 cặp EXACT_PHONE, đã nạp vào kho
    assert _dem(engine, "SELECT count(*) FROM ops.dup_candidate WHERE match_type = 'EXACT_PHONE'") == 1
    assert _dem(engine, 'SELECT count(*) FROM dwh.fact_dup_pair') == 1
    assert _dem(engine, "SELECT clean_index FROM dwh.v_batch_score WHERE measure_stage = 'SAU'") > 0


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
    monkeypatch.setattr(load_ops, 'ghi_customer_clean', hong)
    with pytest.raises(RuntimeError):
        _chay(p, tmp)
    with engine.connect() as conn:          # DDL cũng nằm trong giao dịch nên schema ops có thể chưa tồn tại
        co_bang = conn.execute(text("SELECT to_regclass('ops.load_batch')")).scalar_one()
        assert co_bang is None or conn.execute(text('SELECT count(*) FROM ops.load_batch')).scalar_one() == 0


def test_uc3_loi_thi_dot_nap_van_con_va_chi_lenh_chay_lai(csdl_test, monkeypatch):
    """TD-17: hai giao dịch. UC3 lỗi → đợt nạp và lần đo của UC1 vẫn còn, không có cặp dở dang; thông báo chỉ
    đúng lệnh chạy lại riêng UC3, chạy lệnh đó thì kho đủ và đối soát khớp. [luồng ngoại lệ]"""
    engine, p, tmp = csdl_test
    that = pipeline.chay_uc3

    def hong(conn, batch_id, nguong):
        raise RuntimeError('giả lập mất kết nối khi so khớp')
    monkeypatch.setattr(pipeline, 'chay_uc3', hong)
    with pytest.raises(pipeline.LoiUC3, match='python -m src.pipeline --dot 1'):
        _chay(p, tmp)
    assert _dem(engine, 'SELECT count(*) FROM ops.load_batch') == 1
    assert _dem(engine, 'SELECT count(*) FROM dwh.fact_dq_check') == 12
    assert _dem(engine, 'SELECT count(*) FROM ops.dup_candidate') == 0
    monkeypatch.setattr(pipeline, 'chay_uc3', that)
    assert pipeline.main(['--dot', '1']) == 0
    assert _dem(engine, 'SELECT count(*) FROM dwh.fact_dup_pair') == 1
    assert pipeline.main(['--dot', '9']) == pipeline.MA_TU_CHOI               # đợt không tồn tại


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
        dem = "SELECT count(*) FROM information_schema.tables WHERE table_schema = :s AND table_type = :t"
        assert conn.execute(text(dem), {'s': 'ops', 't': 'BASE TABLE'}).scalar_one() == 6
        assert conn.execute(text(dem), {'s': 'dwh', 't': 'BASE TABLE'}).scalar_one() == 5
        assert conn.execute(text(dem), {'s': 'dwh', 't': 'VIEW'}).scalar_one() == 2
        assert conn.execute(text('SELECT count(*) FROM dwh.dim_date')).scalar_one() == 1461   # 2024 – 2027
        assert conn.execute(text("SELECT count(*) FROM pg_trigger WHERE tgname = 'trg_dq_rule_updated_at'")).scalar_one() == 1

