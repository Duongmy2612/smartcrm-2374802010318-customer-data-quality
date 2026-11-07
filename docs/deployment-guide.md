# Deployment Guide – Smart CRM L7 Customer Data Quality prototype

Student: Dương Diễm My – 2374802010318 · Business flow L7 (customer data quality) · Track DA · Assignment 3, tag `v1.0`
Repository: https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality

The system is packaged with Docker Compose. A machine with only Docker and Git installed can build and start it
with **two commands** (section 2), check that it works (section 5) and run the full test suite with one command.
No Python or PostgreSQL is needed on the host. Messages printed by the system are in Vietnamese; this guide quotes
them exactly and gives the meaning in English.

## 1. Environment requirements

| Item | Requirement | How to check |
|---|---|---|
| Operating system | macOS 13 or later (Intel or Apple Silicon), Windows 10/11 with WSL 2, or Linux (x86_64 / arm64) | – |
| Docker | Docker Engine 24 or later with Docker Compose v2 (Docker Desktop 4.25 or later on macOS / Windows), running | `docker --version` · `docker compose version` |
| Git | 2.30 or later | `git --version` |
| Disk space | at least 3 GB free: images about 1.1 GB (application image about 0.8 GB, `postgres:16-alpine` about 0.3 GB) plus build cache | – |
| Memory | 2 GB available to Docker | Docker Desktop → Settings → Resources |
| Network port | **8501** must be free on the host (dashboard). PostgreSQL is not published, so a local PostgreSQL on 5432 does not conflict | macOS / Linux: `lsof -i :8501` (no output = free) |
| Internet | needed on the first build only: pull two base images from Docker Hub, install pinned Python packages from PyPI | – |

Runtime inside the containers: Python 3.11 (`python:3.11-slim`), PostgreSQL 16 (`postgres:16-alpine`), libraries
pinned with `==` in `requirements.txt` – every direct and indirect package, 47 in total (pandas 3.0.6,
SQLAlchemy 2.1.1, streamlit 1.67.0, pillow 13.0.0, …).

## 2. Build and start the system

Run each line in a terminal (macOS / Linux: Terminal; Windows: PowerShell). Lines 1 – 2 get the code; the system
itself starts with the **two commands** in lines 3 – 4.

| # | Command | What it does |
|---|---|---|
| 1 | `git clone --branch v1.0 https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality.git smartcrm` | Gets the submitted version (tag `v1.0`) into a new folder |
| 2 | `cd smartcrm` | Enters the project folder |
| 3 | `cp .env.example .env` (PowerShell: `Copy-Item .env.example .env`) | Creates the configuration file from the sample – no editing needed (section 3) |
| 4 | `docker compose up -d --build` | Builds the application image `smartcrm-l7:local` and starts the three services below |

The first run of command 4 takes about 3 – 6 minutes (it downloads the base images and builds); later runs take a
few seconds. Command 4 starts:

| Service | What it is | Correct state |
|---|---|---|
| `db` | PostgreSQL 16 with database `smartcrm` (schemas `ops`, `dwh`) and a separate test database `smartcrm_test`, created on the first start by `docker/initdb/01-tao-csdl-kiem-thu.sh` | `Up (healthy)` – healthcheck `pg_isready` |
| `pipeline` | One-shot batch job: loads the sample file, cleans it, measures quality, loads the warehouse, detects duplicate pairs (`python -m src.pipeline --tep data/mau/customers_mau.csv`) | `Exited (0)` – a finished batch job |
| `dashboard` | Streamlit dashboard K1 – K3 at http://localhost:8501; starts only after `pipeline` finished successfully | `Up (healthy)` – healthcheck `/_stcore/health` |

Stop the system: `docker compose down` (keeps the data) · remove everything including data: `docker compose down -v`.

## 3. Environment variables

`.env` is created from `.env.example` in step 3. It is ignored by Git (`.gitignore`) and is not copied into the image
(`.dockerignore`); Docker Compose reads it and passes the values to the containers. Every value in `.env.example` is
a **sample** – keep it for a local run, change both passwords for any shared or real deployment.

| Variable | Meaning | Sample value | Required |
|---|---|---|---|
| `DB_HOST` | PostgreSQL host for a run **without** Docker. Docker Compose ignores it and uses the service name `db` | `localhost` | No (Docker) |
| `DB_PORT` | PostgreSQL port for a run without Docker. Docker uses 5432 inside the network | `5432` | No (Docker) |
| `DB_NAME` | Main database (schemas `ops`, `dwh`) | `smartcrm` | No – default `smartcrm` |
| `DB_USER` | Account used by the pipeline and the tests. Empty → Docker uses `smartcrm` (the database owner); without Docker on macOS Homebrew, empty means the current macOS account | *(empty)* | No |
| `DB_PASSWORD` | Password of `DB_USER`. With Docker it is also the password given to PostgreSQL on its **first** start | `smartcrm_mau_doi_khi_trien_khai` | **Yes** – Compose stops with `required variable DB_PASSWORD is missing a value` |
| `DB_NAME_TEST` | Separate database for `pytest` and the 12 test cases; every test drops and recreates schemas there, never in `DB_NAME` | `smartcrm_test` | No – default `smartcrm_test` |
| `DASH_DB_USER` | Read-only account of the dashboard. The pipeline creates it and grants **SELECT on schema `dwh` only** (counts, no personal data); it has no privileges on schema `ops` (names, phone numbers) | `dash_reader` | **Yes** |
| `DASH_DB_PASSWORD` | Password of `DASH_DB_USER` | `dash_reader_mau_doi_khi_trien_khai` | **Yes** |

Changing `DB_PASSWORD` after the first start: PostgreSQL keeps the first password in the data volume, so run
`docker compose down -v` before `docker compose up -d` (this deletes the loaded data; the pipeline loads it again).

## 4. Sample data

The `pipeline` service loads the sample data automatically during step 4 – nothing to do by hand.

- File: `data/mau/customers_mau.csv`, 414 rows × 6 columns, **fake data** generated by `scripts/sinh_du_lieu_mau.py`
  with seed 42 (no real personal data). It deliberately contains the error types of the real LMS file: 24 missing
  phone numbers, 115 badly formatted numbers, 5 numbers that cannot be fixed, 2 missing names, 40 repeated numbers.
- Expected row counts after loading (`docker compose logs pipeline` prints the same table):

| Table | Rows | Note |
|---|---:|---|
| `ops.load_batch` | 1 | one load batch |
| `ops.stg_customer` | 414 | CLEAN 343 · PENDING_DUP 40 · ERROR 31 (MISSING_PHONE 24, INVALID_PHONE 5, MISSING_NAME 2, INVALID_DATE 0) |
| `ops.customer_clean` | 343 | clean customer records |
| `ops.dq_result` | 12 | 6 quality rules × 2 stages (before / after cleaning) |
| `ops.dup_candidate` | 43 | EXACT_PHONE 40 · FUZZY 3 |
| `dwh.dim_batch` · `dwh.fact_dq_check` · `dwh.fact_dup_pair` | 1 · 12 · 43 | warehouse matches `ops` |

  Cleanliness index: before **88.41** → after **95.79** (grade "Tốt" = Good).
- Loading again is safe: `docker compose up -d` runs the pipeline again on the same file; it prints the warning
  `CẢNH BÁO (AC1.4): tệp này đã nạp …` ("this file was already loaded") and every table stays the same (+0).
- Real data (optional, not in the repository): put the LMS file `customers_raw.csv` in `data/raw/`, then run
  `docker compose run --rm -v "$(pwd)/data/raw:/app/data/raw:ro" pipeline python -m src.pipeline --tep data/raw/customers_raw.csv`
  → 67,037 rows, cleanliness index 87.20 → 94.76, 11,637 duplicate pairs.

## 5. How to check the system is running correctly

Run these commands in the project folder after step 4. Each line gives the exact result to expect.

| # | Command | Expected result |
|---|---|---|
| 1 | `docker compose ps -a` | `db` and `dashboard`: `Up … (healthy)`; `pipeline`: `Exited (0)` |
| 2 | `curl -s http://localhost:8501/_stcore/health` (PowerShell: `curl.exe -s …`) | `ok` |
| 3 | Open http://localhost:8501 in a browser | Title "Mức độ sạch dữ liệu khách hàng"; tab K1 shows **95,79** (after) and **88,41** (before), 414 records; tabs K2, K3 show the 6 rules and 43 pairs |
| 4 | `docker compose logs pipeline` | Line `Số dòng: tệp 414 → bảng tạm 414 = sạch 343 + chờ quyết định 40 + lỗi 31` and the table of row counts of section 4 |
| 5 | `docker compose exec db psql -U smartcrm -d smartcrm -c "SELECT status, count(*) FROM ops.stg_customer GROUP BY status ORDER BY status"` | `CLEAN 343` · `ERROR 31` · `PENDING_DUP 40` |
| 6 | `docker compose run --rm pipeline python -m pytest -q` (**test suite, one command**) | `194 passed, 3 skipped` and a table of the five test types. The 3 skipped tests need real data that is not in the repository (the LMS file and an 8,000-row sample of it) |
| 7 | `docker compose run --rm pipeline python -m tests.tc_bt3 TC-06` (any of TC-01 … TC-12; no argument = all 12) | The eight columns of the test case and `Kết quả : PASS` ("Result: PASS") |
| 8 | `docker compose up -d` then `docker compose logs pipeline` | Last line `Kết quả lần chạy lại: mọi bảng +0 – không nhân đôi dữ liệu.` ("re-run: every table +0 – no duplicated data") |

Common problems:

| Message or symptom | Cause | Fix |
|---|---|---|
| `required variable DB_PASSWORD is missing a value` | `.env` was not created | Run step 3, then step 4 again |
| `Bind for 0.0.0.0:8501 failed: port is already allocated` | Another program (often a dashboard started with `streamlit run`) uses port 8501 | Stop that program, then `docker compose up -d` |
| `pipeline` shows `Exited (1)`; log has `password authentication failed` | `DB_PASSWORD` was changed after the first start | `docker compose down -v`, then `docker compose up -d` |
| `required variable DASH_DB_PASSWORD is missing a value` | `.env` was created from an older `.env.example` (before `v1.0`) that has no dashboard account | Copy the `DASH_DB_USER` and `DASH_DB_PASSWORD` lines from `.env.example` into `.env`, then step 4 again |
| Run without Docker: the dashboard shows "Chưa cấu hình tài khoản chỉ đọc của dashboard" ("the dashboard's read-only account is not configured") | `DASH_DB_USER` or `DASH_DB_PASSWORD` is empty in `.env` | Copy both lines from `.env.example`, run the pipeline once (it creates the account), restart the dashboard |
| `pull access denied for smartcrm-l7` | An older copy of `docker-compose.yml`; the dashboard must reuse the image built by `pipeline` | Use the file of tag `v1.0` (it sets `pull_policy: never` on `dashboard`) and run step 4 with `--build` |
