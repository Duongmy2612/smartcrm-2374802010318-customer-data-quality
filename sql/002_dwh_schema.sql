-- Lớp ③ Lưu trữ – schema dwh (kho dữ liệu hình sao), theo docs/erd.drawio trang 2 và
-- docs/data-requirements.md mục 5.2 (BT1). Sprint 2 (buổi 10), nạp bằng src/etl/load_dwh.py.
-- Chạy lại an toàn: IF NOT EXISTS, CREATE OR REPLACE VIEW, ON CONFLICT DO NOTHING.
--
-- GRAIN
--   fact_dq_check : 1 dòng = kết quả kiểm 1 quy tắc (đúng phiên bản đang hiệu lực) trên 1 đợt nạp,
--                   ở 1 giai đoạn đo (TRUOC/SAU), tại 1 lần đo.
--   fact_dup_pair : 1 dòng = 1 cặp nghi trùng, cập nhật theo trạng thái mới nhất (accumulating snapshot).
-- Kho chỉ chứa số đếm: không có họ tên, số điện thoại (lập luận 2 của BT1, NFR-07).

CREATE SCHEMA IF NOT EXISTS dwh;

-- dim_date – SCD loại 0 – 1 dòng = 1 ngày. Sinh sẵn 01/01/2024 – 31/12/2027; ngày ngoài khoảng này
-- được load_dwh.py thêm khi cần (TD-15) để không dòng fact nào bị rơi khi JOIN.
CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_key     INT      PRIMARY KEY,                       -- yyyymmdd, ví dụ 20261024
    full_date    DATE     NOT NULL UNIQUE,
    day_of_month SMALLINT NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    month        SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_label  CHAR(7)  NOT NULL,                          -- MM/YYYY trên trục biểu đồ
    quarter      SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year         SMALLINT NOT NULL
);
INSERT INTO dwh.dim_date (date_key, full_date, day_of_month, month, month_label, quarter, year)
SELECT TO_CHAR(d, 'YYYYMMDD')::INT, d::DATE, EXTRACT(DAY FROM d), EXTRACT(MONTH FROM d),
       TO_CHAR(d, 'MM/YYYY'), EXTRACT(QUARTER FROM d), EXTRACT(YEAR FROM d)
FROM   generate_series(DATE '2024-01-01', DATE '2027-12-31', INTERVAL '1 day') AS d
ON CONFLICT (date_key) DO NOTHING;

-- dim_batch – SCD loại 0 – 1 dòng = 1 đợt nạp. Khóa nghiệp vụ: batch_id.
CREATE TABLE IF NOT EXISTS dwh.dim_batch (
    batch_key   SERIAL       PRIMARY KEY,
    batch_id    BIGINT       NOT NULL UNIQUE,                -- = ops.load_batch.batch_id
    file_name   VARCHAR(255) NOT NULL,
    source_unit VARCHAR(50)  NOT NULL,                       -- bộ lọc theo quyền xem (QT-14)
    loaded_by   VARCHAR(50)  NOT NULL,
    loaded_at   TIMESTAMP    NOT NULL
);

-- dim_rule – SCD loại 2 – 1 dòng = 1 phiên bản của 1 quy tắc. Khóa nghiệp vụ: (rule_code, valid_from).
CREATE TABLE IF NOT EXISTS dwh.dim_rule (
    rule_key       SERIAL       PRIMARY KEY,
    rule_code      VARCHAR(10)  NOT NULL,
    rule_name      VARCHAR(100) NOT NULL,
    rule_type      VARCHAR(20)  NOT NULL CHECK (rule_type IN ('COMPLETENESS', 'VALIDITY', 'UNIQUENESS')),
    field_name     VARCHAR(30)  NOT NULL,
    weight         NUMERIC(3,2) NOT NULL CHECK (weight BETWEEN 0 AND 1),
    pass_threshold NUMERIC(5,2) NOT NULL CHECK (pass_threshold BETWEEN 0 AND 100),
    is_active      BOOLEAN      NOT NULL,
    valid_from     TIMESTAMP    NOT NULL,                    -- = ops.dq_rule.updated_at
    valid_to       TIMESTAMP,                                -- NULL = phiên bản hiện hành
    CONSTRAINT uq_dim_rule_version UNIQUE (rule_code, valid_from),
    CONSTRAINT ck_dim_rule_range CHECK (valid_to IS NULL OR valid_to >= valid_from)
);
-- Mỗi quy tắc có đúng một phiên bản hiện hành
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_rule_current ON dwh.dim_rule (rule_code) WHERE valid_to IS NULL;

-- fact_dq_check – kết quả đo. Khóa nghiệp vụ result_id: nạp lại không sinh trùng (NFR-05).
CREATE TABLE IF NOT EXISTS dwh.fact_dq_check (
    check_id      BIGSERIAL  PRIMARY KEY,
    date_key      INT        NOT NULL REFERENCES dwh.dim_date (date_key),
    batch_key     INT        NOT NULL REFERENCES dwh.dim_batch (batch_key),
    rule_key      INT        NOT NULL REFERENCES dwh.dim_rule (rule_key),
    result_id     BIGINT     NOT NULL UNIQUE,                -- = ops.dq_result.result_id (thuộc tính suy biến)
    measure_stage VARCHAR(5) NOT NULL CHECK (measure_stage IN ('TRUOC', 'SAU')),
    measured_at   TIMESTAMP  NOT NULL,
    total_records INT        NOT NULL CHECK (total_records >= 0),   -- số đo: mẫu số
    pass_count    INT        NOT NULL,                              -- số đo: số đạt
    CONSTRAINT ck_fact_dq_check_pass CHECK (pass_count BETWEEN 0 AND total_records)
);
CREATE INDEX IF NOT EXISTS ix_fact_dq_check_batch ON dwh.fact_dq_check (batch_key, measure_stage, measured_at);

-- fact_dup_pair – cặp nghi trùng (accumulating snapshot). Khóa nghiệp vụ pair_id.
-- dim_date đóng hai vai trò: ngày phát hiện và ngày quyết định.
CREATE TABLE IF NOT EXISTS dwh.fact_dup_pair (
    pair_key          BIGSERIAL    PRIMARY KEY,
    pair_id           BIGINT       NOT NULL UNIQUE,          -- = ops.dup_candidate.pair_id
    batch_key         INT          NOT NULL REFERENCES dwh.dim_batch (batch_key),  -- đợt của hồ sơ nạp sau
    detected_date_key INT          NOT NULL REFERENCES dwh.dim_date (date_key),
    decided_date_key  INT          REFERENCES dwh.dim_date (date_key),            -- NULL khi còn Chờ xử lý
    match_type        VARCHAR(12)  NOT NULL CHECK (match_type IN ('EXACT_PHONE', 'FUZZY')),
    status            VARCHAR(15)  NOT NULL CHECK (status IN ('PENDING', 'MERGED', 'KEEP_SEPARATE')),
    score             NUMERIC(5,2) NOT NULL CHECK (score BETWEEN 0 AND 100)          -- không cộng
);
CREATE INDEX IF NOT EXISTS ix_fact_dup_pair_batch ON dwh.fact_dup_pair (batch_key, status);

-- v_rule_rate – 1 dòng / 1 dòng fact_dq_check: tỉ lệ đạt, số không đạt, điểm bị mất (K2).
-- Tính trong view, không lưu (giá trị tính được).
CREATE OR REPLACE VIEW dwh.v_rule_rate AS
SELECT f.check_id, f.result_id,
       b.batch_key, b.batch_id, b.file_name, b.source_unit, b.loaded_at,
       f.measure_stage, f.measured_at, d.full_date AS measured_date,
       r.rule_key, r.rule_code, r.rule_name, r.rule_type, r.field_name, r.weight, r.pass_threshold, r.is_active,
       f.total_records, f.pass_count,
       f.total_records - f.pass_count                                             AS fail_count,
       ROUND(COALESCE(f.pass_count::NUMERIC / NULLIF(f.total_records, 0), 1), 4)  AS pass_rate,
       ROUND(r.weight * (1 - COALESCE(f.pass_count::NUMERIC / NULLIF(f.total_records, 0), 1)) * 100, 2)
                                                                                  AS lost_points,
       COALESCE(f.pass_count::NUMERIC / NULLIF(f.total_records, 0), 1) * 100 >= r.pass_threshold
                                                                                  AS is_pass
FROM   dwh.fact_dq_check f
JOIN   dwh.dim_rule  r ON r.rule_key  = f.rule_key
JOIN   dwh.dim_batch b ON b.batch_key = f.batch_key
JOIN   dwh.dim_date  d ON d.date_key  = f.date_key;

-- v_batch_score – 1 dòng / (đợt nạp, giai đoạn, lần đo): chỉ số mức độ sạch QL7-06, xếp loại, lần đo mới nhất (K1).
CREATE OR REPLACE VIEW dwh.v_batch_score AS
WITH lan_do AS (
    SELECT f.batch_key, f.measure_stage, f.measured_at, f.date_key,
           SUM(r.weight * COALESCE(f.pass_count::NUMERIC / NULLIF(f.total_records, 0), 1)) * 100 AS diem,
           COUNT(*) AS so_quy_tac
    FROM   dwh.fact_dq_check f
    JOIN   dwh.dim_rule r ON r.rule_key = f.rule_key
    WHERE  r.is_active
    GROUP  BY f.batch_key, f.measure_stage, f.measured_at, f.date_key
)
SELECT b.batch_key, b.batch_id, b.file_name, b.source_unit, b.loaded_by, b.loaded_at,
       l.measure_stage, l.measured_at, d.full_date AS measured_date, l.so_quy_tac,
       ROUND(l.diem, 2) AS clean_index,
       CASE WHEN ROUND(l.diem, 2) >= 90 THEN 'Tốt'
            WHEN ROUND(l.diem, 2) >= 75 THEN 'Chấp nhận được'
            ELSE 'Kém' END AS grade,
       l.measured_at = MAX(l.measured_at) OVER (PARTITION BY l.batch_key, l.measure_stage) AS is_latest
FROM   lan_do l
JOIN   dwh.dim_batch b ON b.batch_key = l.batch_key
JOIN   dwh.dim_date  d ON d.date_key  = l.date_key;
