"""Mã nguồn prototype L7 – Chất lượng dữ liệu khách hàng (Smart CRM · Mekong Mobile).

Ánh xạ thư mục ↔ lớp trong sơ đồ kiến trúc (docs/architecture.drawio, Hình 3.1 của BT1):
    dashboard/        lớp ① Trình bày (Streamlit)
    src/etl/          lớp ② Xử lý – nghiệp vụ, ba pha E / T / L (xem src/etl/__init__.py, TD-22)
    src/pipeline.py   thứ tự gọi các mô-đun của lớp ② theo từng use case (Bảng 3.1 của BT1) – nơi duy nhất gọi cả ba pha
    src/doc_kho.py    truy vấn CHỈ ĐỌC kho dwh cho lớp ①
    src/db.py         mũi tên ② ↔ ③: kết nối PostgreSQL qua SQLAlchemy, thông tin đọc từ .env
    src/config.py     đọc configs/config.yaml (người dùng, vai trò, ngưỡng)
    sql/              lớp ③ Lưu trữ: DDL schema ops (tác nghiệp) và dwh (kho dữ liệu)
"""
