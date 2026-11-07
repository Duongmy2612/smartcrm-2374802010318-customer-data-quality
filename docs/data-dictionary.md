# Data dictionary – L7 Customer Data Quality

Student: Dương Diễm My – 2374802010318 · Track DA · Assignment 3 (tag `v1.0`). Every column of every target table of the
pipeline – 11 tables in schemas `ops` (operational) and `dwh` (star-schema warehouse) – and of the 3 views the
reject list and the dashboard read: 147 columns. Eight of the 11 tables receive rows on every load (the pipeline
prints their row counts before → after, and a re-run must leave all eight at +0); the other three hold the rule
configuration (`ops.dq_rule`, `dwh.dim_rule`) and the calendar (`dwh.dim_date`, pre-filled for 2024 – 2027).
Types and nullability are copied from `information_schema` of a database built by the pipeline;
`tests/test_tai_lieu.py` fails if a column exists in the database but not here.
DDL: `sql/001` – `sql/005`. How the tables are loaded: `docs/pipeline-doc.md`.

Classification used below:

| Class | Meaning | Where it may appear |
|---|---|---|
| Personal data (confidential) | Identifies or contacts a customer: name, phone, e-mail, address and their normalised forms | Schema `ops` only; never in `dwh`, logs, reports or the dashboard (D4) |
| Internal | Operational metadata: identifiers, file names, codes, timestamps | `ops`; non-personal copies in `dwh` |
| Internal – staff login | Login name of a staff member (`my.marketing`, `ql.mm001`) – not customer data | `ops`, `dwh.dim_batch` |
| Configuration | Quality rules, weights, thresholds | `ops.dq_rule`, `dwh.dim_rule` |
| Aggregate, non-personal | Counts, rates, dates, scores | `ops.dq_result`, `dwh` facts and views |

Access in short: the pipeline account owns both schemas; the dashboard account `dash_reader` has `SELECT` on `dwh`
only (BUG-16, TD-36), so every "Personal data" column below is unreachable from the dashboard.

## Tables in schema `ops`

### `ops.load_batch`

Grain: one load of one file.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `batch_id` | BIGINT | Load batch identifier (one run of one file) | ≥ 1, sequence | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `file_name` | VARCHAR(255) | File name as given to `--tep` (without folder) | text ≤ 255 | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `file_hash` | CHAR(64) | SHA-256 of the file content – detects the same file loaded again (AC1.4) | 64 hex characters | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `source_unit` | VARCHAR(50) | Unit that produced the file – basis of dashboard scoping (QT-14) | store code (e.g. `MM001`) or `TONG_HOP` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `row_count` | INTEGER | Rows read from the file – control total, must equal rows written to `stg_customer` | ≥ 0 (CHECK) | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `loaded_by` | VARCHAR(50) | Login of the person who loaded the file (role MARKETING) | login in `configs/config.yaml` | no | Internal – staff login | Staff login (not customer data); `ops` – pipeline account only |
| `loaded_at` | TIMESTAMP | Load time (database clock) | timestamp, default `now()` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |

### `ops.stg_customer`

Grain: one raw record of a loaded file.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `stg_id` | BIGINT | Staging row identifier | ≥ 1, sequence | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `batch_id` | BIGINT | Batch of the row → `ops.load_batch` | existing batch (FK) | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `customer_id` | BIGINT | Clean customer created from this row → `ops.customer_clean` | existing customer (FK) or NULL (ERROR / PENDING_DUP) | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `row_no` | INTEGER | Data row number in the file (header not counted) – lets the store find the row | ≥ 1; unique with `batch_id` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `source_record_id` | VARCHAR(20) | Value of column `record_id` in the source file | text ≤ 20 | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `full_name_raw` | VARCHAR(200) | Name exactly as in the file (column `ho_ten`) | any text ≤ 200 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `phone_raw` | VARCHAR(30) | Phone exactly as in the file (column `so_dien_thoai`) | any text ≤ 30 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `email_raw` | VARCHAR(200) | E-mail exactly as in the file | any text ≤ 200 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `address_raw` | VARCHAR(300) | Address exactly as in the file (column `dia_chi`) | any text ≤ 300 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `created_raw` | VARCHAR(30) | Creation date exactly as in the file (column `ngay_tao`) | text ≤ 30; valid = real `yyyy-mm-dd` date (else INVALID_DATE) | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `phone_norm` | CHAR(10) | Phone after normalisation (QT-02) | `^0[0-9]{9}$` or NULL when it cannot be normalised | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `name_norm` | VARCHAR(120) | Name after normalisation (FR-03) | text 2 – 120 or NULL | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `name_key` | VARCHAR(120) | Name without accents, lower case – matching key (QL7-03) | text ≤ 120 or NULL | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `error_code` | VARCHAR(20) | Main reason the row is not usable (one code by priority) | `MISSING_PHONE`, `INVALID_PHONE`, `MISSING_NAME`, `INVALID_DATE` or NULL (CHECK) | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `status` | VARCHAR(12) | Processing state of the row | `LOADED`, `CLEAN`, `PENDING_DUP`, `MERGED`, `ERROR` (CHECK) | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |

### `ops.customer_clean`

Grain: one clean customer.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `customer_id` | BIGINT | Clean customer identifier | ≥ 1, sequence | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `full_name` | VARCHAR(120) | Normalised name | text 2 – 120 | no | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `phone` | CHAR(10) | Normalised phone – unique among active customers (QT-01) | `^0[0-9]{9}$` (CHECK); unique where `is_active` | no | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `email` | VARCHAR(120) | E-mail | text ≤ 120 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `address` | VARCHAR(255) | Address | text ≤ 255 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `is_active` | BOOLEAN | Soft delete flag (QT-13); FALSE after a merge | TRUE / FALSE, default TRUE | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `merged_into` | BIGINT | Surviving customer after a merge (UC5, not implemented yet – always NULL) | existing customer (FK) or NULL | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `created_at` | TIMESTAMP | Time the clean record was created (load time, not `ngay_tao`) | timestamp, default `now()` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `updated_at` | TIMESTAMP | Time of the last change | timestamp, default `now()` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |

### `ops.dup_candidate`

Grain: one suspected duplicate pair.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `pair_id` | BIGINT | Suspected duplicate pair identifier | ≥ 1, sequence | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `stg_id_a` | BIGINT | Earlier-loaded row of the pair → `stg_customer` | existing row (FK); `stg_id_a < stg_id_b` (CHECK) | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `stg_id_b` | BIGINT | Later-loaded row of the pair → `stg_customer` | existing row (FK); pair unique | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `match_type` | VARCHAR(12) | How the pair was found (QL7-02) | `EXACT_PHONE`, `FUZZY` (CHECK) | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `score` | NUMERIC(5,2) | Similarity score 0.6 × phone + 0.4 × name (QL7-03) – evidence for the decision | 0 – 100 (CHECK); FUZZY ≥ 85 | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `status` | VARCHAR(15) | Decision state (Pending / Merge / Keep separate) | `PENDING`, `MERGED`, `KEEP_SEPARATE` (CHECK), default PENDING | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `survivor_stg_id` | BIGINT | Row kept after a merge (UC5, not implemented – NULL) | `stg_id_a` or `stg_id_b` (CHECK) or NULL | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `detected_at` | TIMESTAMP | Detection time | timestamp, default `now()` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `decided_by` | VARCHAR(50) | Login of the person who decided (UC5 – NULL until implemented) | login or NULL | yes | Internal – staff login | Staff login (not customer data); `ops` – pipeline account only |
| `decided_at` | TIMESTAMP | Decision time (NULL while pending) | timestamp or NULL | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `note` | VARCHAR(255) | Reason of the decision (optional) | text ≤ 255 or NULL | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |

### `ops.dq_rule`

Grain: one quality rule (current configuration).

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `rule_id` | INTEGER | Rule identifier | ≥ 1, sequence | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `rule_code` | VARCHAR(10) | Business code of the rule | `DQ-01` … `DQ-06`, unique | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `rule_name` | VARCHAR(100) | Rule name (Vietnamese) | text ≤ 100 | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `rule_type` | VARCHAR(20) | Quality dimension | `COMPLETENESS`, `VALIDITY`, `UNIQUENESS` (CHECK) | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `field_name` | VARCHAR(30) | Checked field | `phone`, `full_name`, `email` | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `weight` | NUMERIC(3,2) | Weight in the cleanliness index (QL7-06); active weights sum to 1.00 (FR-07) | 0 – 1 (CHECK) | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `pass_threshold` | NUMERIC(5,2) | Minimum pass rate in % for the rule to pass | 0 – 100 (CHECK) | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `is_active` | BOOLEAN | Rule is measured | TRUE / FALSE | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `updated_by` | VARCHAR(50) | Login of the last editor (UC6) | login or NULL | yes | Internal – staff login | Staff login (not customer data); `ops` – pipeline account only |
| `updated_at` | TIMESTAMP | Last change; set by trigger (TD-21); becomes `dim_rule.valid_from` | timestamp | no | Configuration | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |

### `ops.dq_result`

Grain: one rule × one batch × one stage × one measurement.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `result_id` | BIGINT | Measurement result identifier | ≥ 1, sequence | no | Aggregate, non-personal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `batch_id` | BIGINT | Measured batch → `load_batch` | existing batch (FK) | no | Aggregate, non-personal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `rule_id` | INTEGER | Measured rule → `dq_rule` | existing rule (FK) | no | Aggregate, non-personal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `measure_stage` | VARCHAR(5) | Stage: before or after cleaning | `TRUOC`, `SAU` (CHECK) | no | Aggregate, non-personal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `measured_at` | TIMESTAMP | Measurement time (database clock, TD-16) | timestamp | no | Aggregate, non-personal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `total_records` | INTEGER | Denominator: rows in the rule scope | ≥ 0 (CHECK) | no | Aggregate, non-personal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `pass_count` | INTEGER | Rows that pass the rule (rates are computed, not stored) | 0 – `total_records` (CHECK) | no | Aggregate, non-personal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |

## Tables in schema `dwh`

### `dwh.dim_date`

Grain: one calendar day (SCD 0).

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `date_key` | INTEGER | Date key `yyyymmdd` | e.g. 20261107; 01/01/2024 – 31/12/2027 pre-filled, others added when needed (TD-15) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `full_date` | DATE | Calendar date | unique date | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `day_of_month` | SMALLINT | Day of month | 1 – 31 (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `month` | SMALLINT | Month | 1 – 12 (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `month_label` | CHAR(7) | Month label on chart axes | `MM/YYYY` | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `quarter` | SMALLINT | Quarter | 1 – 4 (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `year` | SMALLINT | Year | e.g. 2026 | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |

### `dwh.dim_batch`

Grain: one load batch (SCD 0).

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `batch_key` | INTEGER | Surrogate key | ≥ 1, sequence | no | Internal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `batch_id` | BIGINT | Business key = `ops.load_batch.batch_id` | unique | no | Internal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `file_name` | VARCHAR(255) | Loaded file name | text ≤ 255 | no | Internal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `source_unit` | VARCHAR(50) | Unit of the batch – filter of dashboard scope (QT-14) | store code or `TONG_HOP` | no | Internal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `loaded_by` | VARCHAR(50) | Login of the loader | login | no | Internal – staff login | Staff login (not customer data); readable by `dash_reader` |
| `loaded_at` | TIMESTAMP | Load time | timestamp | no | Internal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |

### `dwh.dim_rule`

Grain: one version of one rule (SCD 2).

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `rule_key` | INTEGER | Surrogate key of one rule version | ≥ 1, sequence | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `rule_code` | VARCHAR(10) | Rule business code | `DQ-01` … `DQ-06` | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `rule_name` | VARCHAR(100) | Rule name | text ≤ 100 | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `rule_type` | VARCHAR(20) | Quality dimension | `COMPLETENESS`, `VALIDITY`, `UNIQUENESS` (CHECK) | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `field_name` | VARCHAR(30) | Checked field | `phone`, `full_name`, `email` | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `weight` | NUMERIC(3,2) | Weight of this version | 0 – 1 (CHECK) | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `pass_threshold` | NUMERIC(5,2) | Pass threshold of this version (%) | 0 – 100 (CHECK) | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `is_active` | BOOLEAN | Rule active in this version | TRUE / FALSE | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `valid_from` | TIMESTAMP | Start of validity (SCD type 2) = `ops.dq_rule.updated_at` | timestamp; unique with `rule_code` | no | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `valid_to` | TIMESTAMP | End of validity; NULL = current version (one per rule) | timestamp ≥ `valid_from` (CHECK) or NULL | yes | Configuration | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |

### `dwh.fact_dq_check`

Grain: one rule version × one batch × one stage × one measurement.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `check_id` | BIGINT | Surrogate key | ≥ 1, sequence | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `date_key` | INTEGER | Measurement date → `dim_date` | existing date (FK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `batch_key` | INTEGER | Batch → `dim_batch` | existing batch (FK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `rule_key` | INTEGER | Rule version valid at measurement time → `dim_rule` | existing version (FK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `result_id` | BIGINT | Business key = `ops.dq_result.result_id` (degenerate dimension) – reload never duplicates | unique | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `measure_stage` | VARCHAR(5) | Stage | `TRUOC`, `SAU` (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `measured_at` | TIMESTAMP | Measurement time | timestamp | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `total_records` | INTEGER | Measure: denominator | ≥ 0 (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `pass_count` | INTEGER | Measure: rows passing | 0 – `total_records` (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |

### `dwh.fact_dup_pair`

Grain: one pair, latest status (accumulating snapshot).

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `pair_key` | BIGINT | Surrogate key | ≥ 1, sequence | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `pair_id` | BIGINT | Business key = `ops.dup_candidate.pair_id` | unique | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `batch_key` | INTEGER | Batch of the later-loaded row → `dim_batch` | existing batch (FK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `detected_date_key` | INTEGER | Detection date → `dim_date` | existing date (FK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `decided_date_key` | INTEGER | Decision date → `dim_date` (NULL while pending) | existing date (FK) or NULL | yes | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `match_type` | VARCHAR(12) | How the pair was found | `EXACT_PHONE`, `FUZZY` (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `status` | VARCHAR(15) | Latest decision state (accumulating snapshot) | `PENDING`, `MERGED`, `KEEP_SEPARATE` (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |
| `score` | NUMERIC(5,2) | Similarity score – not additive | 0 – 100 (CHECK) | no | Aggregate, non-personal | Readable by `dash_reader` (SELECT only, read-only session); written only by the pipeline |

## Views

### `ops.v_reject`

Grain: one rejected row (status ERROR) – view.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `batch_id` | BIGINT | = `ops.stg_customer.batch_id` | existing batch (FK) | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `row_no` | INTEGER | = `ops.stg_customer.row_no` | ≥ 1; unique with `batch_id` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `source_record_id` | VARCHAR(20) | = `ops.stg_customer.source_record_id` | text ≤ 20 | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `full_name_raw` | VARCHAR(200) | = `ops.stg_customer.full_name_raw` | any text ≤ 200 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `phone_raw` | VARCHAR(30) | = `ops.stg_customer.phone_raw` | any text ≤ 30 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `email_raw` | VARCHAR(200) | = `ops.stg_customer.email_raw` | any text ≤ 200 | yes | Personal data (confidential) | Kept only in `ops`; `dash_reader` has no privileges on `ops` (BUG-16); never copied to `dwh`; not printed in logs; exported only to git-ignored `data/processed/*.csv` |
| `error_code` | VARCHAR(20) | = `ops.stg_customer.error_code` | `MISSING_PHONE`, `INVALID_PHONE`, `MISSING_NAME`, `INVALID_DATE` or NULL (CHECK) | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `ly_do` | TEXT | Reason written as a sentence for the store, from `error_code` (same text as `transform.LY_DO`) | one of 4 sentences | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `file_name` | VARCHAR(255) | = `ops.load_batch.file_name` | text ≤ 255 | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `loaded_at` | TIMESTAMP | = `ops.load_batch.loaded_at` | timestamp, default `now()` | no | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |
| `created_raw` | VARCHAR(30) | = `ops.stg_customer.created_raw` | text ≤ 30; valid = real `yyyy-mm-dd` date (else INVALID_DATE) | yes | Internal | Readable and writable by the pipeline account only; `dash_reader` has no privileges on `ops` |

### `dwh.v_rule_rate`

Grain: one `fact_dq_check` row with computed rates – view.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `check_id` | BIGINT | = `dwh.fact_dq_check.check_id` | ≥ 1, sequence | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `result_id` | BIGINT | = `dwh.fact_dq_check.result_id` | unique | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `batch_key` | INTEGER | = `dwh.dim_batch.batch_key` | ≥ 1, sequence | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `batch_id` | BIGINT | = `dwh.dim_batch.batch_id` | unique | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `file_name` | VARCHAR(255) | = `dwh.dim_batch.file_name` | text ≤ 255 | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `source_unit` | VARCHAR(50) | = `dwh.dim_batch.source_unit` | store code or `TONG_HOP` | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `loaded_at` | TIMESTAMP | = `dwh.dim_batch.loaded_at` | timestamp | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `measure_stage` | VARCHAR(5) | = `dwh.fact_dq_check.measure_stage` | `TRUOC`, `SAU` (CHECK) | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `measured_at` | TIMESTAMP | = `dwh.fact_dq_check.measured_at` | timestamp | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `measured_date` | DATE | Measurement date (`dim_date.full_date`) | date | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `rule_key` | INTEGER | = `dwh.dim_rule.rule_key` | ≥ 1, sequence | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `rule_code` | VARCHAR(10) | = `dwh.dim_rule.rule_code` | `DQ-01` … `DQ-06` | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `rule_name` | VARCHAR(100) | = `dwh.dim_rule.rule_name` | text ≤ 100 | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `rule_type` | VARCHAR(20) | = `dwh.dim_rule.rule_type` | `COMPLETENESS`, `VALIDITY`, `UNIQUENESS` (CHECK) | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `field_name` | VARCHAR(30) | = `dwh.dim_rule.field_name` | `phone`, `full_name`, `email` | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `weight` | NUMERIC(3,2) | = `dwh.dim_rule.weight` | 0 – 1 (CHECK) | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `pass_threshold` | NUMERIC(5,2) | = `dwh.dim_rule.pass_threshold` | 0 – 100 (CHECK) | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `is_active` | BOOLEAN | = `dwh.dim_rule.is_active` | TRUE / FALSE | no | Configuration | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `total_records` | INTEGER | = `dwh.fact_dq_check.total_records` | ≥ 0 (CHECK) | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `pass_count` | INTEGER | = `dwh.fact_dq_check.pass_count` | 0 – `total_records` (CHECK) | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `fail_count` | INTEGER | `total_records − pass_count` | ≥ 0 | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `pass_rate` | NUMERIC | Pass rate; empty scope counts as 1 (QL7-06) | 0 – 1, 4 decimals | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `lost_points` | NUMERIC | Index points lost by the rule = weight × (1 − pass rate) × 100 (chart K2) | 0 – 100 | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `is_pass` | BOOLEAN | Rule passes: pass rate × 100 ≥ `pass_threshold` | TRUE / FALSE | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |

### `dwh.v_batch_score`

Grain: one batch × stage × measurement with the index – view.

| Column | Type | Meaning | Valid values | Null | Classification | Security handling |
|---|---|---|---|---|---|---|
| `batch_key` | INTEGER | = `dwh.dim_batch.batch_key` | ≥ 1, sequence | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `batch_id` | BIGINT | = `dwh.dim_batch.batch_id` | unique | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `file_name` | VARCHAR(255) | = `dwh.dim_batch.file_name` | text ≤ 255 | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `source_unit` | VARCHAR(50) | = `dwh.dim_batch.source_unit` | store code or `TONG_HOP` | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `loaded_by` | VARCHAR(50) | = `dwh.dim_batch.loaded_by` | login | no | Internal – staff login | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `loaded_at` | TIMESTAMP | = `dwh.dim_batch.loaded_at` | timestamp | no | Internal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `measure_stage` | VARCHAR(5) | = `dwh.fact_dq_check.measure_stage` | `TRUOC`, `SAU` (CHECK) | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `measured_at` | TIMESTAMP | = `dwh.fact_dq_check.measured_at` | timestamp | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `measured_date` | DATE | Measurement date | date | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `so_quy_tac` | BIGINT | Number of active rules in the measurement | ≥ 1 | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `clean_index` | NUMERIC | Cleanliness index Σ weight × pass rate × 100 (QL7-06, chart K1) | 0 – 100, 2 decimals | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `grade` | TEXT | Grade of the index | `Tốt` ≥ 90 · `Chấp nhận được` 75 – < 90 · `Kém` < 75 | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
| `is_latest` | BOOLEAN | TRUE for the latest measurement of the batch and stage | TRUE / FALSE | no | Aggregate, non-personal | Computed by the view, not stored; readable by `dash_reader` (SELECT only) |
