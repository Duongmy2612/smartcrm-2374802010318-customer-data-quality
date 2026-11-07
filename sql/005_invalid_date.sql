-- Lớp ③ Lưu trữ – migration 005 (BT3, buổi 14, BUG-15, TD-37).
-- Ngày tạo sai (ví dụ '31/02/2026', '2026-02-30') trước đây vẫn thành hồ sơ CLEAN vì error_code chỉ có ba giá trị.
-- Thêm giá trị INVALID_DATE cho CSDL đã tạo trước BT3 (CSDL mới đã có sẵn ở sql/001).
-- Chạy lại an toàn: xóa rồi tạo lại đúng ràng buộc này (tên mặc định PostgreSQL đặt cho CHECK của cột error_code).

ALTER TABLE ops.stg_customer DROP CONSTRAINT IF EXISTS stg_customer_error_code_check;
ALTER TABLE ops.stg_customer ADD CONSTRAINT stg_customer_error_code_check
    CHECK (error_code IN ('MISSING_PHONE', 'INVALID_PHONE', 'MISSING_NAME', 'INVALID_DATE'));
