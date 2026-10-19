-- Lớp ③ Lưu trữ – schema ops (tầng tác nghiệp), 6 bảng, 8 khóa ngoại.
-- Nguồn: ERD docs/erd.drawio trang 1 và từ điển dữ liệu docs/data-requirements.md mục 5.1 (BT1).
-- Chạy lại an toàn: mọi lệnh có IF NOT EXISTS, nên pipeline gọi tệp này ở mỗi lần chạy.

CREATE SCHEMA IF NOT EXISTS ops;

-- Đợt nạp – 1 dòng = 1 lần nạp một tệp khách hàng thô (FR-01)
CREATE TABLE IF NOT EXISTS ops.load_batch (
    batch_id     BIGSERIAL    PRIMARY KEY,
    file_name    VARCHAR(255) NOT NULL,
    file_hash    CHAR(64)     NOT NULL,                       -- SHA-256: cảnh báo nạp lại (AC1.4)
    source_unit  VARCHAR(50)  NOT NULL,                       -- căn cứ lọc theo QT-14
    row_count    INT          NOT NULL CHECK (row_count >= 0), -- tổng kiểm soát số dòng đọc từ tệp
    loaded_by    VARCHAR(50)  NOT NULL,
    loaded_at    TIMESTAMP    NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_load_batch_file_hash ON ops.load_batch (file_hash);

-- Hồ sơ đã làm sạch – 1 dòng = 1 hồ sơ (đang hiệu lực hoặc đã ngừng sử dụng).
-- Tạo trước stg_customer vì stg_customer.customer_id trỏ tới bảng này.
CREATE TABLE IF NOT EXISTS ops.customer_clean (
    customer_id  BIGSERIAL    PRIMARY KEY,
    full_name    VARCHAR(120) NOT NULL,
    phone        CHAR(10)     NOT NULL CHECK (phone ~ '^0[0-9]{9}$'),   -- QT-02, NFR-04
    email        VARCHAR(120),
    address      VARCHAR(255),
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,                  -- QT-13: xóa mềm
    merged_into  BIGINT       REFERENCES ops.customer_clean (customer_id),
    created_at   TIMESTAMP    NOT NULL DEFAULT now(),
    updated_at   TIMESTAMP    NOT NULL DEFAULT now()
);
-- QT-01, NFR-04: số điện thoại duy nhất trong các hồ sơ ĐANG HIỆU LỰC (chỉ mục duy nhất từng phần)
CREATE UNIQUE INDEX IF NOT EXISTS ux_customer_clean_phone_active
    ON ops.customer_clean (phone) WHERE is_active;

-- Bảng tạm – 1 dòng = 1 hồ sơ thô. Giữ nguyên giá trị gốc ở cột *_raw (NFR-05, lập luận 3).
CREATE TABLE IF NOT EXISTS ops.stg_customer (
    stg_id           BIGSERIAL    PRIMARY KEY,
    batch_id         BIGINT       NOT NULL REFERENCES ops.load_batch (batch_id),
    customer_id      BIGINT       REFERENCES ops.customer_clean (customer_id),
    row_no           INT          NOT NULL,                   -- dòng dữ liệu thứ n của tệp (không tính tiêu đề)
    source_record_id VARCHAR(20),
    full_name_raw    VARCHAR(200),
    phone_raw        VARCHAR(30),
    email_raw        VARCHAR(200),
    address_raw      VARCHAR(300),
    created_raw      VARCHAR(30),
    phone_norm       CHAR(10),
    name_norm        VARCHAR(120),
    name_key         VARCHAR(120),                            -- match.py ghi ở Sprint 2 (FR-04)
    error_code       VARCHAR(20)
                     CHECK (error_code IN ('MISSING_PHONE', 'INVALID_PHONE', 'MISSING_NAME')),
    status           VARCHAR(12)  NOT NULL DEFAULT 'LOADED'
                     CHECK (status IN ('LOADED', 'CLEAN', 'PENDING_DUP', 'MERGED', 'ERROR')),
    CONSTRAINT uq_stg_customer_batch_row UNIQUE (batch_id, row_no)
);
CREATE INDEX IF NOT EXISTS ix_stg_customer_batch ON ops.stg_customer (batch_id);
CREATE INDEX IF NOT EXISTS ix_stg_customer_phone_norm ON ops.stg_customer (phone_norm);

-- Cặp nghi trùng – 1 dòng = 1 cặp hồ sơ thô (match.py ghi ở Sprint 2)
CREATE TABLE IF NOT EXISTS ops.dup_candidate (
    pair_id          BIGSERIAL    PRIMARY KEY,
    stg_id_a         BIGINT       NOT NULL REFERENCES ops.stg_customer (stg_id),  -- hồ sơ nạp sớm hơn
    stg_id_b         BIGINT       NOT NULL REFERENCES ops.stg_customer (stg_id),
    match_type       VARCHAR(12)  NOT NULL CHECK (match_type IN ('EXACT_PHONE', 'FUZZY')),
    score            NUMERIC(5,2) NOT NULL CHECK (score BETWEEN 0 AND 100),         -- bằng chứng NFR-08
    status           VARCHAR(15)  NOT NULL DEFAULT 'PENDING'
                     CHECK (status IN ('PENDING', 'MERGED', 'KEEP_SEPARATE')),
    survivor_stg_id  BIGINT       REFERENCES ops.stg_customer (stg_id),
    detected_at      TIMESTAMP    NOT NULL DEFAULT now(),
    decided_by       VARCHAR(50),
    decided_at       TIMESTAMP,
    note             VARCHAR(255),
    CONSTRAINT uq_dup_candidate_pair UNIQUE (stg_id_a, stg_id_b),
    CONSTRAINT ck_dup_candidate_order CHECK (stg_id_a < stg_id_b),
    CONSTRAINT ck_dup_candidate_survivor
        CHECK (survivor_stg_id IS NULL OR survivor_stg_id IN (stg_id_a, stg_id_b))
);
CREATE INDEX IF NOT EXISTS ix_dup_candidate_status_score ON ops.dup_candidate (status, score DESC);  -- FR-05

-- Quy tắc chất lượng (cấu hình hiện hành) – 1 dòng = 1 quy tắc; lịch sử phiên bản ở dwh.dim_rule
CREATE TABLE IF NOT EXISTS ops.dq_rule (
    rule_id        SERIAL       PRIMARY KEY,
    rule_code      VARCHAR(10)  NOT NULL UNIQUE,
    rule_name      VARCHAR(100) NOT NULL,
    rule_type      VARCHAR(20)  NOT NULL CHECK (rule_type IN ('COMPLETENESS', 'VALIDITY', 'UNIQUENESS')),
    field_name     VARCHAR(30)  NOT NULL,
    weight         NUMERIC(3,2) NOT NULL CHECK (weight BETWEEN 0 AND 1),
    pass_threshold NUMERIC(5,2) NOT NULL CHECK (pass_threshold BETWEEN 0 AND 100),
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    updated_by     VARCHAR(50),
    updated_at     TIMESTAMP    NOT NULL DEFAULT now()
);

-- Kết quả đo – 1 dòng = 1 quy tắc × 1 đợt nạp × 1 giai đoạn × 1 lần đo.
-- Không lưu tỉ lệ hay chỉ số (giá trị tính được) – chỉ lưu số kiểm và số đạt.
CREATE TABLE IF NOT EXISTS ops.dq_result (
    result_id     BIGSERIAL  PRIMARY KEY,
    batch_id      BIGINT     NOT NULL REFERENCES ops.load_batch (batch_id),
    rule_id       INT        NOT NULL REFERENCES ops.dq_rule (rule_id),
    measure_stage VARCHAR(5) NOT NULL CHECK (measure_stage IN ('TRUOC', 'SAU')),
    measured_at   TIMESTAMP  NOT NULL,
    total_records INT        NOT NULL CHECK (total_records >= 0),
    pass_count    INT        NOT NULL,
    CONSTRAINT ck_dq_result_pass CHECK (pass_count BETWEEN 0 AND total_records)
);
CREATE INDEX IF NOT EXISTS ix_dq_result_batch_measured ON ops.dq_result (batch_id, measured_at);
