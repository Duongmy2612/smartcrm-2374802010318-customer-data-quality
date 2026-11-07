# Pipeline documentation – L7 Customer Data Quality

Student: Dương Diễm My – 2374802010318 · Track DA · Assignment 3 (tag `v1.0`). This document describes what the code
in this repository does **today**; every number below comes from a real run (sample file in Docker, real LMS file on
the test machine, 07/11/2026). Column-level details: `docs/data-dictionary.md`.

## 1. Phases of the pipeline

One command runs everything: `python -m src.pipeline --tep <file>` (in Docker: service `pipeline`). Extract (E),
transform (T) and load (L) live in separate modules; only `src/pipeline.py` calls all three, and 14 tests in
`tests/test_ranh_gioi_lop.py` keep the boundaries (E and T never touch the database, L never calls E or T).

```
 customers_*.csv / .xlsx
          │
 [1] EXTRACT   src/etl/extract.py ─ read file, check required columns, encoding, sizes, SHA-256
          │     └─ file rejected (missing column, empty, unreadable) → exit 2, nothing written
          │     └─ completeness of every column vs. its own threshold (D3, src/etl/dq_evaluate.py)
 [2] TRANSFORM src/etl/transform.py ─ normalise phone (QT-02) and name (FR-03), assign error code,
          │     classify CLEAN / PENDING_DUP (QT-01) / ERROR (QL7-04)
 [3] QUALITY   src/etl/dq_evaluate.py ─ 6 rule functions DQ-01 … DQ-06, BEFORE and AFTER cleaning,
          │     cleanliness index (QL7-06)
 [L] LOAD ops  src/etl/load_ops.py ─ ops.load_batch, stg_customer, customer_clean, dq_result     ┐ transaction 1
 [4] LOAD dwh  src/etl/load_dwh.py ─ dim_date, dim_batch, dim_rule (SCD 2), fact_dq_check        ┘ (UC1)
 [5] MATCH     src/etl/match.py ─ EXACT_PHONE + FUZZY pairs (blocking, score ≥ 85)               ┐ transaction 2
          │     load_ops → ops.dup_candidate · load_dwh → dwh.fact_dup_pair · reconciliation      ┘ (UC3)
          ▼
 dashboard/report.py (Streamlit, account dash_reader, SELECT on dwh only) ─ K1, K2, K3
```

Transaction 1 (UC1) is all-or-nothing: any error rolls back, so a half-loaded batch never exists. Transaction 2 (UC3)
can be re-run alone with `python -m src.pipeline --dot <batch_id>`. Exit codes: 0 success · 1 technical error
(unreadable file, database down) · 2 data rejected.

## 2. Data sources

| Source | Where | Rows × columns | Notes |
|---|---|---|---|
| Customer file of a store / channel | any `.csv` (UTF-8) or `.xlsx` given with `--tep` | – | Required columns `ho_ten`, `so_dien_thoai`; optional `record_id`, `email`, `dia_chi`, `ngay_tao` |
| Real data `customers_raw.csv` | LMS "Dataset Smart CRM"; not in Git (`data/raw/` is ignored) | 67,037 × 6 | Contains personal data |
| Sample data `customers_mau.csv` | `data/mau/`, committed | 414 × 6 | Fake data from `scripts/sinh_du_lieu_mau.py`, seed 42; loaded automatically in Docker |
| Rule configuration | `ops.dq_rule` (seeded from `src/etl/dq_evaluate.py`), `configs/config.yaml` | 6 rules | Weights, thresholds, users and their units, completeness thresholds |

## 3. Targets and grain

| Target | Grain (one row = …) | Load rule |
|---|---|---|
| `ops.load_batch` | one load of one file | insert; same SHA-256 again → warning AC1.4, no new batch |
| `ops.stg_customer` | one raw record of a file (raw values kept in `*_raw`) | insert; then update normalised values, error code, status |
| `ops.customer_clean` | one clean customer (active or merged) | insert CLEAN records; unique active phone (QT-01) |
| `ops.dq_result` | one rule × one batch × one stage × one measurement | insert counts only (no stored rates) |
| `ops.dup_candidate` | one suspected duplicate pair | insert if the pair does not exist (QL7-05) |
| `dwh.dim_date` · `dwh.dim_batch` · `dwh.dim_rule` | one day · one batch · one version of one rule (SCD type 2) | business key, `ON CONFLICT DO NOTHING` |
| `dwh.fact_dq_check` | one rule version × one batch × one stage × one measurement | business key `result_id` |
| `dwh.fact_dup_pair` | one pair, latest status (accumulating snapshot) | business key `pair_id`, upsert |
| `ops.v_reject` · `dwh.v_rule_rate` · `dwh.v_batch_score` | views: one rejected row · one fact row with rates · one batch × stage × measurement with the index | computed, never stored |

The warehouse contains **counts only**: no names, phone numbers or e-mails (D4). After every load the pipeline checks
`ops` against `dwh` (batches, results, pairs, raw rows vs. DQ-01 denominator) and prints ✔ or ✘ per line.

## 4. Cleaning rules and rows rejected

| Rule | What it does | Sample file (414 rows) | Real file (67,037 rows) |
|---|---|---:|---:|
| QT-02 phone normalisation | remove spaces, dots, hyphens; `+84` / `84` → `0`; must end as `0` + 9 digits | 115 fixed | 19,041 fixed |
| FR-03 name normalisation | trim, single spaces, capital first letters, Unicode NFC | 25 changed | 5,930 changed |
| QL7-04 `MISSING_PHONE` | empty phone → row stays in staging (ERROR) | **24 rejected** | **4,133 rejected** |
| QL7-04 `INVALID_PHONE` | phone cannot be normalised | **5 rejected** | 0 |
| QL7-04 `MISSING_NAME` | empty name | **2 rejected** | 0 |
| QL7-04 `INVALID_DATE` | `ngay_tao` present but not a real `yyyy-mm-dd` date (BUG-15) | 0 | 0 |
| QT-01 repeated phone | phone already active or earlier in the file → PENDING_DUP, no new customer | 40 held | 11,625 held |
| QL7-02 / QL7-03 pairs | EXACT_PHONE for same phone; FUZZY when score = 0.6 × phone similarity + 0.4 × name similarity ≥ 85 | 40 + 3 pairs | 11,625 + 12 pairs |
| File-level rejection | missing required column, empty / header-only file, wrong encoding, too-long value | whole file, exit 2 | – |

Result: sample 414 = 343 clean + 40 held + 31 rejected, index 88.41 → 95.79; real 67,037 = 51,279 + 11,625 + 4,133,
index 87.20 → 94.76. Every rejected row is listed with a sentence explaining why in `ops.v_reject` and in
`data/processed/ho_so_loi_dot_N.csv`.

**Quality measured on three dimensions.** The six rules of `ops.dq_rule` (seeded from `src/etl/dq_evaluate.py`) cover
completeness, validity and uniqueness; each is measured BEFORE and AFTER cleaning and stored in `ops.dq_result` /
`dwh.fact_dq_check`. Pass rate = records passing / records in the rule's scope (sample file, values printed by the
pipeline and stored in the database):

| Rule | Dimension | Weight | Threshold | Sample BEFORE → AFTER |
|---|---|---:|---:|---|
| DQ-01 phone not empty | Completeness | 0.25 | 98 % | 94.20 % → 94.20 % (cleaning cannot invent a missing number) |
| DQ-02 phone matches `^0[0-9]{9}$` | Validity | 0.25 | 95 % | 69.23 % → 98.72 % (QT-02) |
| DQ-03 name not empty | Completeness | 0.15 | 99 % | 99.52 % → 99.52 % |
| DQ-04 name 2 – 120 characters, no digits | Validity | 0.10 | 97 % | 100 % → 100 % |
| DQ-05 phone not repeated | Uniqueness | 0.20 | 98 % | 89.61 % → 89.61 % (needs UC5 decisions) |
| DQ-06 e-mail well-formed | Validity | 0.05 | 95 % | 94.12 % → 94.12 % |

Completeness is also measured **for every column against its own threshold** (`nguong_day_du` in
`configs/config.yaml`, TD-38), printed at step [1/5] of every run. Sample file: `record_id` 100.00 % (≥ 100 %) ·
`ho_ten` 99.52 % (≥ 99 %) · `so_dien_thoai` 94.20 % (< 98 %, NOT MET) · `email` 45.17 % (< 50 %, NOT MET) ·
`dia_chi` 91.79 % (≥ 90 %) · `ngay_tao` 100.00 % (≥ 99 %). TC-10 checks that a deliberate violation is reported.

## 5. Schedule and back-fill

- **Trigger:** on demand, one run per received file (a store or channel sends a file). There is no scheduler in the
  prototype; in Docker the `pipeline` service runs once at start-up with the sample file.
- **Re-run is safe:** the same file (same SHA-256) is detected, nothing is inserted again, the warehouse and pairs are
  re-synchronised – every table +0 (TC-11). `--nap-lai` forces a new batch on purpose.
- **Back-fill:** run the old files in the order they were produced; each becomes its own batch, and duplicates against
  earlier batches are detected because matching compares the new batch with all earlier valid records. If matching
  failed after loading, re-run only UC3: `python -m src.pipeline --dot <batch_id>`.
- **Run time:** real file 67,037 rows → about 11.5 s on the test machine (extract 2.6 s, transform 3.7 s, quality 0.1 s,
  matching + warehouse 5.1 s); NFR-01 limits are 60 s and 120 s for 8,000 rows.

## 6. Known limitations and data latency

Each limitation is stated with what it means for the business user and what is done about it now.

| Limitation | Business impact | Now / plan |
|---|---|---|
| **Latency:** the dashboard is as fresh as the last pipeline run plus a 60-second cache; data arrive file by file, no streaming | Store managers and Marketing see the state of the last loaded file, not of today's sales; fine for a weekly data-quality review, not for live operations | Every chart prints the time of the last measurement; run the pipeline as soon as a file arrives (section 5) |
| **UC5 Merge / Keep separate is not implemented** (TD-27, TD-41): every pair stays PENDING | The 11,625 repeated-phone records of the real file stay held (PENDING_DUP): they create no duplicate customer (QT-01), but whatever newer name, email or address they carry is not merged into the existing customer. DQ-05 and the AFTER index stop at 94.76 on real data, short of the +10-point target (estimated 98.46 with UC5) | Dashboard K3 shows how many pairs wait and in which score band; deciding pair by pair needs UC5 (Phase 4) – until then the pairs stay in `ops.dup_candidate` |
| **FUZZY false positives at threshold 85:** on 300 hand-labelled real pairs precision is 91.43 % and recall 96.97 % (NFR-03, TD-32); the 12 false positives are exactly the 12 FUZZY pairs of the real file, scores 85 – 89.56 | Every FUZZY pair proposed on the real file joins two different customers: reviewers would spend time on them, and merging any of them would join two real people | No automatic merge (QL7-01, tested by TC-02); raising the threshold to 90 (precision 100 %, same recall on the sample) is a Phase 4 decision |
| **Records without a phone are never matched** (QL7-04) | 4,133 real records (6.2 %) cannot be called, texted or de-duplicated; a person present twice, once without phone, is missed (4 pairs of tier T4 in the NFR-03 sample) | Each run writes the rejected rows with a reason sentence to a CSV in `data/processed/` (`ops.v_reject` in the database), so the store knows which rows to complete and send again |
| **No login:** the dashboard viewer is chosen from a list in `configs/config.yaml` | Unit scoping (QT-14) is applied but not authenticated – anyone who can open the page can pick another viewer and see another store's counts | Counts only: the account `dash_reader` cannot read any personal data (TC-12); run the dashboard on the internal network only; SSO is out of scope (BT1) |
| **Personal data in `ops` is not encrypted** (security checklist item 4) | Whoever holds the pipeline database account or the disk can read names and phone numbers | Only the pipeline account can read `ops`; passwords stay in `.env`; `pgcrypto` for `email`, `address` and an encrypted disk in Phase 4 |
| **One error code per row:** only the first problem by priority is shown (MISSING_PHONE > INVALID_PHONE > MISSING_NAME > INVALID_DATE) | A store fixes the reported problem and the row can be rejected again for the next one | The reason sentence in `v_reject` names the field; the next load shows the next problem |
| **Date of creation is validated but not loaded:** `customer_clean.created_at` is the load time, not `ngay_tao` | A report of "new customers by creation date" would count by load date | No chart uses it today (K1 – K3 count by batch); load `ngay_tao` when a chart needs it |
