"""Kiểm nhanh môi trường (buổi 1): phiên bản Python, thư viện, và kết nối PostgreSQL theo .env.

    python scripts/check_env.py

Dùng đúng hàm kết nối của hệ thống (src/db.tao_engine) nên kết quả giống khi chạy pipeline: DB_USER để trống
thì dùng tài khoản hệ điều hành (TD-31). Lỗi chỉ in loại lỗi, không in chuỗi kết nối hay mật khẩu (NFR-07).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pandas as pd                     # noqa: E402
from sqlalchemy import text            # noqa: E402

from src import db                      # noqa: E402

print(f'Python {sys.version.split()[0]} · pandas {pd.__version__}')
try:
    with db.tao_engine().connect() as conn:
        print('CSDL OK:', conn.execute(text('SELECT version()')).scalar())
except Exception as e:                  # noqa: BLE001
    print(f'Chưa kết nối được CSDL ({type(e).__name__}) – kiểm tra PostgreSQL đang chạy, đã createdb smartcrm và .env')
