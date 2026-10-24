"""Mũi tên ② ↔ ③ của Hình 3.1: kết nối PostgreSQL qua SQLAlchemy + psycopg2.

- Thông tin kết nối đọc từ .env (không commit – NFR-07); mẫu ở .env.example.
- Mọi thao tác ghi của một use case nằm trong MỘT giao dịch: `with engine.begin() as conn:` tự COMMIT
  khi khối lệnh xong và tự ROLLBACK khi có lỗi (đặc tả UC5 – luồng 9a; TD-09).
"""
import os
import re

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

from src.config import GOC

THU_MUC_SQL = GOC / 'sql'
BIEN_BAT_BUOC = ('DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER')


class ThieuCauHinhCSDL(RuntimeError):
    pass


def tao_engine():
    load_dotenv(GOC / '.env')
    thieu = [k for k in BIEN_BAT_BUOC if not os.getenv(k)]
    if thieu:
        raise ThieuCauHinhCSDL(
            f"Thiếu biến {', '.join(thieu)} trong .env – chép .env.example thành .env rồi điền thông tin "
            'kết nối PostgreSQL, hoặc chạy thử không ghi CSDL bằng --khong-ghi-csdl.')
    url = URL.create(
        'postgresql+psycopg2',
        username=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD') or None,   # URL.create tự mã hóa ký tự đặc biệt trong mật khẩu
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        database=os.getenv('DB_NAME'),
    )
    # values_plus_batch: psycopg2 gửi UPDATE nhiều dòng theo lô thay vì từng dòng một (NFR-01)
    return create_engine(url, executemany_mode='values_plus_batch')


def tao_engine_chi_doc():
    """Kết nối cho dashboard (lớp ①): chỉ SELECT được (NFR-06, NFR-07).

    Có DASH_DB_USER trong .env → dùng tài khoản riêng đó. Để trống → dùng DB_USER nhưng phiên làm việc đặt
    default_transaction_read_only = on, nên mọi lệnh ghi đều bị PostgreSQL từ chối (TD-19).
    """
    load_dotenv(GOC / '.env')
    thieu = [k for k in BIEN_BAT_BUOC if not os.getenv(k)]
    if thieu:
        raise ThieuCauHinhCSDL(f"Thiếu biến {', '.join(thieu)} trong .env")
    rieng = (os.getenv('DASH_DB_USER') or '').strip()
    url = URL.create(
        'postgresql+psycopg2',
        username=rieng or os.getenv('DB_USER'),
        password=(os.getenv('DASH_DB_PASSWORD') if rieng else os.getenv('DB_PASSWORD')) or None,
        host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), database=os.getenv('DB_NAME'),
    )
    return create_engine(url, pool_pre_ping=True, pool_size=2, max_overflow=2,
                         connect_args={'options': '-c default_transaction_read_only=on', 'connect_timeout': 5})


def _co_lenh(sql: str) -> bool:
    """True nếu tệp .sql còn lệnh sau khi bỏ chú thích (tệp chỉ có chú thích thì bỏ qua)."""
    return bool(re.sub(r'--[^\n]*', '', sql).strip())


def khoi_tao_csdl(conn) -> list[str]:
    """Chạy lần lượt sql/0*.sql (DDL viết IF NOT EXISTS nên chạy lại không lỗi). Trả về tên tệp đã chạy."""
    da_chay = []
    for tep in sorted(THU_MUC_SQL.glob('0*.sql')):
        sql = tep.read_text(encoding='utf-8')
        if _co_lenh(sql):
            conn.exec_driver_sql(sql)
            da_chay.append(tep.name)
    return da_chay
