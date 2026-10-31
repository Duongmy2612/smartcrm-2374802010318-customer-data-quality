"""Fixture dùng chung cho các test cần PostgreSQL (tests/test_pipeline_csdl.py, tests/test_load_dwh.py).

csdl_test: kết nối CSDL kiểm thử RIÊNG (mặc định smartcrm_test, đổi bằng biến DB_NAME_TEST), xóa schema ops, dwh
trước mỗi test và ghi tệp mẫu 4 dòng. Không kết nối được (chưa có PostgreSQL, chưa tạo CSDL test, thiếu .env)
→ test tự bỏ qua (skip), không báo lỗi.
"""
import os

import pytest

from src import db
from tests.test_pipeline import TEP


@pytest.fixture
def csdl_test(monkeypatch, tmp_path):
    from dotenv import load_dotenv
    load_dotenv(db.GOC / '.env')
    monkeypatch.setenv('DB_NAME', os.getenv('DB_NAME_TEST') or 'smartcrm_test')
    try:
        engine = db.tao_engine()
        with engine.begin() as conn:
            conn.exec_driver_sql('DROP SCHEMA IF EXISTS dwh CASCADE; DROP SCHEMA IF EXISTS ops CASCADE')
    except Exception as e:                      # noqa: BLE001
        pytest.skip(f'không kết nối được CSDL kiểm thử: {type(e).__name__}')
    p = tmp_path / 'dot.csv'
    p.write_text(TEP, encoding='utf-8')
    yield engine, p, tmp_path
    engine.dispose()


# ------------------------------------------------------------------ tóm tắt theo ba loại kiểm thử của BT2
LOAI = {'luong_dung': '1. luồng đúng', 'gia_tri_bien': '2. giá trị biên', 'du_lieu_sai': '3. dữ liệu sai'}
_dem_loai = {k: {'passed': 0, 'failed': 0, 'skipped': 0} for k in LOAI}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    ket_qua = (yield).get_result()
    if ket_qua.when == 'call' or (ket_qua.when == 'setup' and not ket_qua.passed):
        for m in LOAI:
            if item.get_closest_marker(m):
                _dem_loai[m][ket_qua.outcome] += 1


def pytest_terminal_summary(terminalreporter):
    """In cuối mỗi lần chạy: số test PASS theo ba loại (pytest.ini) – minh chứng C4 trong một lệnh."""
    if not any(sum(v.values()) for v in _dem_loai.values()):
        return
    terminalreporter.section('Ba loại kiểm thử của BT2 (đánh dấu trong pytest.ini)')
    for m, ten in LOAI.items():
        d = _dem_loai[m]
        them = ''.join(f' · {d[k]} {k}' for k in ('failed', 'skipped') if d[k])
        terminalreporter.write_line(f'  {ten:<17} {d["passed"]:>3} passed{them}')
