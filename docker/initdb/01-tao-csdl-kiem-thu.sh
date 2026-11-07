#!/bin/sh
# Ảnh postgres chính thức chạy tệp này MỘT lần, khi volume dữ liệu còn trống (lần dựng đầu tiên).
# Tạo CSDL kiểm thử riêng cho `pytest` và các test case BT3 – không đụng CSDL chính (BT3, TD-35).
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
     -c "CREATE DATABASE \"${DB_NAME_TEST:-smartcrm_test}\""
