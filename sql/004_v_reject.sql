-- Lớp ③ Lưu trữ – migration 004 (BT2, buổi 12, TD-23).
-- Bảng reject của pha load: hồ sơ bị loại (status = ERROR, QL7-04) kèm LÝ DO VIẾT CHO NGƯỜI ĐỌC.
-- Là VIEW, không phải bảng thứ hai: hồ sơ lỗi vẫn chỉ nằm ở ops.stg_customer (TD-07 – không lưu trùng dữ liệu,
-- không lưu giá trị tính được). Ba câu lý do giống hệt transform.LY_DO (câu trong CSV hồ sơ lỗi, FR-10);
-- test_ly_do_trong_view_reject_khop_transform giữ hai nơi khớp nhau.
-- Xem nhanh:  psql -d smartcrm -c "SELECT batch_id, row_no, phone_raw, error_code, ly_do FROM ops.v_reject LIMIT 5"
-- Chạy lại an toàn: CREATE OR REPLACE VIEW.

CREATE OR REPLACE VIEW ops.v_reject AS
SELECT s.batch_id,
       s.row_no,                          -- dòng thứ n của tệp nguồn (không tính tiêu đề): cửa hàng tìm để sửa
       s.source_record_id,
       s.full_name_raw,
       s.phone_raw,                       -- giá trị GỐC, chưa chuẩn hóa
       s.email_raw,
       s.error_code,
       CASE s.error_code
           WHEN 'MISSING_PHONE' THEN 'Thiếu số điện thoại – không sửa được bằng làm sạch, cửa hàng cần bổ sung tại nguồn'
           WHEN 'INVALID_PHONE' THEN 'Số điện thoại không quy về được dạng 0xxxxxxxxx (sau khi bỏ dấu cách, chấm, gạch và đổi +84/84 thành 0)'
           WHEN 'MISSING_NAME'  THEN 'Thiếu họ tên – hồ sơ đã làm sạch bắt buộc có họ tên'
       END                     AS ly_do,
       b.file_name,
       b.loaded_at
FROM   ops.stg_customer s
JOIN   ops.load_batch   b ON b.batch_id = s.batch_id
WHERE  s.status = 'ERROR';
