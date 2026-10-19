"""Mã nguồn prototype L7 – Chất lượng dữ liệu khách hàng (Smart CRM · Mekong Mobile).

Ánh xạ thư mục ↔ lớp trong sơ đồ kiến trúc (docs/architecture.drawio, Hình 3.1 của BT1):
    dashboard/        lớp ① Trình bày (Streamlit)
    src/etl/          lớp ② Xử lý – nghiệp vụ: 6 mô-đun, mỗi mô-đun một bước xử lý và một nhóm FR
    src/pipeline.py   thứ tự gọi các mô-đun của lớp ② theo từng use case (Bảng 3.1 của BT1)
    src/db.py         mũi tên ② ↔ ③: kết nối PostgreSQL qua SQLAlchemy, thông tin đọc từ .env
    src/config.py     đọc configs/config.yaml (người dùng, vai trò, ngưỡng)
    sql/              lớp ③ Lưu trữ: DDL schema ops (tác nghiệp) và dwh (kho dữ liệu)
"""
