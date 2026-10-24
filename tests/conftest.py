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
    monkeypatch.setenv('DB_NAME', os.getenv('DB_NAME_TEST', 'smartcrm_test'))
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
