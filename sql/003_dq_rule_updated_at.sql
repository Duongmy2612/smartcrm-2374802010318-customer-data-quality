-- Lớp ③ Lưu trữ – migration 003 (buổi 10, TD-21).
-- ops.dq_rule.updated_at tự lấy giờ của CSDL mỗi khi cấu hình quy tắc bị sửa mà câu UPDATE không tự ghi
-- updated_at (ví dụ sửa tay bằng psql). load_dwh.py dùng updated_at làm valid_from của phiên bản mới trong
-- dwh.dim_rule (SCD loại 2), nên giá trị này phải tiến lên sau mỗi lần sửa; nếu không, lần nạp kho sau
-- sẽ dừng với lỗi "updated_at … không sau valid_from".
-- Chạy lại an toàn: CREATE OR REPLACE (CREATE OR REPLACE TRIGGER cần PostgreSQL 14 trở lên).

CREATE OR REPLACE FUNCTION ops.dq_rule_dat_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.updated_at IS NOT DISTINCT FROM OLD.updated_at THEN   -- câu UPDATE không tự ghi updated_at
        NEW.updated_at := clock_timestamp();                      -- cùng đồng hồ với measured_at (TD-16)
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_dq_rule_updated_at
    BEFORE UPDATE ON ops.dq_rule
    FOR EACH ROW EXECUTE FUNCTION ops.dq_rule_dat_updated_at();
