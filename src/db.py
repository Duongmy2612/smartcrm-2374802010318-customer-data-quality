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
# DB_USER để trống thì thư viện libpq dùng tên tài khoản hệ điều hành – đúng mặc định của PostgreSQL cài bằng Homebrew
# trên macOS, nên README bước 6 chỉ còn một lệnh `cp .env.example .env` (TD-31).
BIEN_BAT_BUOC = ('DB_HOST', 'DB_PORT', 'DB_NAME')


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
        username=os.getenv('DB_USER') or None,         # trống → tài khoản hệ điều hành (TD-31)
        password=os.getenv('DB_PASSWORD') or None,   # URL.create tự mã hóa ký tự đặc biệt trong mật khẩu
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        database=os.getenv('DB_NAME'),
    )
    # values_plus_batch: psycopg2 gửi UPDATE nhiều dòng theo lô thay vì từng dòng một (NFR-01)
    return create_engine(url, executemany_mode='values_plus_batch')


MAU_TEN_TAI_KHOAN = re.compile(r'[a-z_][a-z0-9_]{0,62}')   # tên tài khoản PostgreSQL đưa vào câu lệnh – chặn chèn SQL


def tai_khoan_dashboard() -> tuple[str, str]:
    """(DASH_DB_USER, DASH_DB_PASSWORD) – bắt buộc từ BT3 (BUG-16, TD-36): dashboard KHÔNG còn dùng chung tài khoản
    của pipeline, vì tài khoản đó đọc được họ tên, số điện thoại ở schema ops."""
    load_dotenv(GOC / '.env')
    ten = (os.getenv('DASH_DB_USER') or '').strip()
    mat_khau = os.getenv('DASH_DB_PASSWORD') or ''
    if not ten or not mat_khau:
        raise ThieuCauHinhCSDL(
            'Chưa cấu hình tài khoản chỉ đọc của dashboard: điền DASH_DB_USER và DASH_DB_PASSWORD trong .env (mẫu ở '
            '.env.example) rồi chạy lại luồng chính một lần – luồng chính tạo tài khoản và cấp quyền chỉ đọc kho dwh.')
    if not MAU_TEN_TAI_KHOAN.fullmatch(ten):
        raise ThieuCauHinhCSDL('DASH_DB_USER chỉ được gồm chữ thường không dấu, chữ số và dấu gạch dưới, ví dụ dash_reader.')
    return ten, mat_khau


def tao_engine_chi_doc():
    """Kết nối cho dashboard (lớp ①): tài khoản riêng DASH_DB_USER chỉ có quyền SELECT trên schema dwh (kho chỉ có số
    đếm, không có dữ liệu cá nhân) – đọc schema ops bị PostgreSQL từ chối (NFR-07, TD-36). Phiên làm việc vẫn đặt
    default_transaction_read_only = on như TD-19: hai lớp chặn ghi.
    """
    load_dotenv(GOC / '.env')
    thieu = [k for k in BIEN_BAT_BUOC if not os.getenv(k)]
    if thieu:
        raise ThieuCauHinhCSDL(f"Thiếu biến {', '.join(thieu)} trong .env")
    ten, mat_khau = tai_khoan_dashboard()
    url = URL.create(
        'postgresql+psycopg2', username=ten, password=mat_khau,
        host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')), database=os.getenv('DB_NAME'),
    )
    return create_engine(url, pool_pre_ping=True, pool_size=2, max_overflow=2,
                         connect_args={'options': '-c default_transaction_read_only=on', 'connect_timeout': 5})


def _co_lenh(sql: str) -> bool:
    """True nếu tệp .sql còn lệnh sau khi bỏ chú thích (tệp chỉ có chú thích thì bỏ qua)."""
    return bool(re.sub(r'--[^\n]*', '', sql).strip())


def khoi_tao_csdl(conn) -> list[str]:
    """Chạy lần lượt sql/0*.sql (DDL viết IF NOT EXISTS nên chạy lại không lỗi), rồi cấp quyền cho tài khoản của
    dashboard. Trả về tên tệp đã chạy."""
    da_chay = []
    for tep in sorted(THU_MUC_SQL.glob('0*.sql')):
        sql = tep.read_text(encoding='utf-8')
        if _co_lenh(sql):
            conn.exec_driver_sql(sql)
            da_chay.append(tep.name)
    cap_quyen_dashboard(conn)
    return da_chay


def cap_quyen_dashboard(conn) -> str | None:
    """Tạo (hoặc đồng bộ mật khẩu) tài khoản DASH_DB_USER và cấp ĐÚNG quyền đọc schema dwh; thu hồi mọi quyền trên
    schema ops (BUG-16, TD-36). Chạy lại an toàn. Chưa cấu hình DASH_DB_USER → bỏ qua (pipeline vẫn chạy; dashboard
    sẽ báo thiếu cấu hình). Trả về tên tài khoản đã cấp quyền, hoặc None.

    Mật khẩu truyền dạng tham số (psycopg2 tự đặt trong dấu nháy) nên không chèn được câu lệnh; tên tài khoản và tên
    CSDL được kiểm bằng MAU_TEN_TAI_KHOAN / quote của SQLAlchemy.
    """
    try:
        ten, mat_khau = tai_khoan_dashboard()
    except ThieuCauHinhCSDL:
        return None
    from sqlalchemy.exc import DBAPIError
    q = conn.dialect.identifier_preparer.quote
    tk = q(ten)
    co = conn.exec_driver_sql('SELECT 1 FROM pg_roles WHERE rolname = %(t)s', {'t': ten}).first()
    lenh = 'ALTER' if co else 'CREATE'
    try:
        with conn.begin_nested():
            conn.exec_driver_sql(f'{lenh} ROLE {tk} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %(p)s',
                                 {'p': mat_khau})
    except DBAPIError as e:
        raise ThieuCauHinhCSDL(
            f'Tài khoản DB_USER không tạo / sửa được tài khoản {ten} của dashboard ({type(e.orig).__name__}). Nhờ quản '
            f'trị CSDL tạo tài khoản đó, hoặc để trống DASH_DB_USER nếu chỉ chạy pipeline không mở dashboard.') from None
    csdl = conn.exec_driver_sql('SELECT current_database()').scalar_one()
    conn.exec_driver_sql(
        f'GRANT CONNECT ON DATABASE {q(csdl)} TO {tk};'
        f'GRANT USAGE ON SCHEMA dwh TO {tk};'
        f'GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO {tk};'
        f'REVOKE ALL ON ALL TABLES IN SCHEMA ops FROM {tk};'
        f'REVOKE ALL ON SCHEMA ops FROM {tk};')
    return ten
