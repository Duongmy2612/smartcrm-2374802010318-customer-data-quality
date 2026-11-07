# Security checklist – Smart CRM L7 prototype (Assignment 3)

Student: Dương Diễm My – 2374802010318 · checked on 07/11/2026 by RUNNING each check (commands below), on the
Docker system of `docs/deployment-guide.md` and on the Git repository. Values: **DONE** · **NOT DONE** · **N/A**.

| # | Item | Value | Evidence (one line) |
|---|---|---|---|
| 1 | No secret in the repository | **DONE** | `git grep -nE "(PASSWORD\|SECRET\|TOKEN\|API_KEY)\s*=" -- ':!*.md'` → only the two sample values in `.env.example`; history scan below |
| 2 | Input is validated in the application layer | **DONE** | TC-04, TC-08, TC-09 PASS: missing column / empty file / wrong encoding → whole file rejected (exit 2); bad phone, missing name, invalid date → row goes to `ops.v_reject` with a reason |
| 3 | Access control by owner | **DONE** | TC-12 PASS: dashboard account `dash_reader` reads only schema `dwh` – `SELECT … FROM ops.stg_customer` → "permission denied for schema ops"; TC-12 step 4: store manager `ql.mm001` sees only unit MM001, and choosing MM002 returns no batch (QT-14) |
| 4 | Passwords and sensitive data are hashed or encrypted | **NOT DONE** | Passwords: hashed by PostgreSQL (`pg_authid.rolpassword` starts with `SCRAM-SHA-256$`). Names and phone numbers in schema `ops` are stored in plain text |
| 5 | Error messages do not reveal internal structure | **DONE** | Stopped `db` and ran the pipeline / opened the dashboard: one Vietnamese sentence + fix, no traceback, no password or connection string (`test_mat_ket_noi_*`, TC-08); dashboard shows only the error type |
| 6 | Logs do not record secrets or unneeded personal data | **DONE** | `docker compose logs \| grep -cE "0[0-9]{9}\|@example\|@gmail"` → `0`; pipeline output and `reports/*.md` contain counts only |
| 7 | Dependencies are pinned and checked for known vulnerabilities | **DONE** | `requirements.txt` pins all 47 packages with `==`; `pip-audit -r requirements.txt` → "No known vulnerabilities found" (after BUG-17); CI repeats it on every push |

## Details

**1 · Secrets.** `.env` is in `.gitignore` and `.dockerignore`, so it is neither committed nor copied into the image;
containers get values as environment variables at run time. History scan:
`git log --all -p -- . ':(exclude).venv' | grep -E "^\+[A-Z_]*(PASSWORD|SECRET|TOKEN)=[^ ]+"` → only the two sample
values of `.env.example`. A `.env` file was committed once (commit `39020f3`, 25/09/2026) and removed (`ef28fe3`,
19/10/2026); it held only `DB_HOST=localhost`, `DB_NAME`, `DB_USER` (the macOS account name), `APP_PORT` and an empty
`DB_PASSWORD`, so there was no credential to rotate. The history was not rewritten to erase it: rewriting would change
every commit hash and break the commit links of the Bug Log and the tag `v0.2`. This is why the self-check marks C7
("`.env` never committed") as only partly met. The two values in `.env.example`
(`smartcrm_mau_doi_khi_trien_khai`, `dash_reader_mau_doi_khi_trien_khai`) are samples for a local machine; the
Deployment Guide (section 3) says to change both for any shared deployment.

**2 · Input validation.** File level (`src/etl/extract.py`): required columns `ho_ten`, `so_dien_thoai`; empty file,
header-only file, wrong encoding, broken structure and values longer than the staging columns are rejected before
anything is written (AC1.3, TD-28). Row level (`src/etl/transform.py`): phone must normalise to `0xxxxxxxxx`, name
must not be empty, creation date must be a real `yyyy-mm-dd` date (BUG-15). Configuration: `DASH_DB_USER` must match
`[a-z_][a-z0-9_]*` before it is used in `CREATE ROLE`; passwords are passed as query parameters.

**3 · Access control.** Database level: the pipeline account owns `ops` and `dwh`; the dashboard connects as
`dash_reader` (NOSUPERUSER) with `USAGE` + `SELECT` on `dwh` only and every right on `ops` revoked
(`src/db.py: cap_quyen_dashboard`, BUG-16), and its session is also read-only (`default_transaction_read_only=on`).
The warehouse holds counts only – no names or phone numbers. Application level: a store manager (`ql.mm001`) sees only
batches of unit `MM001` (QT-14, `src/doc_kho.py: don_vi_duoc_xem`), checked by TC-12 step 4. Containers run as a normal user (`USER app`, uid
10001), not root. Known limit: the prototype has no login – the viewer is chosen from a list (see
`docs/pipeline-doc.md`, section 6).

**4 · Hashing / encryption – why NOT DONE.** Database passwords are stored as SCRAM-SHA-256 hashes
(`password_encryption = scram-sha-256`), and the prototype stores no application passwords (no login). But names and
phone numbers in `ops.stg_customer` and `ops.customer_clean` are plain text, and the disk / volume is not encrypted.
They cannot simply be hashed: duplicate detection compares phone digits and names with a similarity score (QL7-03),
and store staff need the original values to fix rejected rows (FR-10). Current mitigations: personal data never
reaches the warehouse or the dashboard (D4), the error CSV with personal data stays in `data/processed/` (git-ignored,
not in the image). Next step (Phase 4): column encryption with `pgcrypto` for `email`, `address`, and an encrypted
volume for a real deployment.

**5 · Error messages.** Test performed: `docker compose stop db` → `docker compose run --rm --no-deps pipeline` →
`LỖI: LoiKetNoiCSDL: Không kết nối được PostgreSQL ở db:5432, CSDL smartcrm (OperationalError). Đang chạy trong Docker:
kiểm tra dịch vụ db bằng docker compose ps -a …` (exit code 1). The sentence names the service and the fix, never the
password or the connection URL; before BUG-18 it advised Homebrew commands that do not exist in Docker. Rejected
files print `TỪ CHỐI: …` with exit code 2 and no Python traceback (TC-08). The dashboard error state prints
"Loại lỗi: OperationalError" and a Retry button only.

**6 · Logs.** The pipeline prints counts, rule results, a SHA-256 prefix of the input file and table sizes – no names,
phone numbers or e-mails. `reports/*.md` contains the same counts. The rejected-rows CSV
(`data/processed/ho_so_loi_dot_N.csv`) does contain personal data on purpose (FR-10: the store must find and fix the
row); it is a data output, not a log, and is git-ignored and excluded from the image.

**7 · Dependencies.** `requirements.txt` is a full lock (direct and indirect packages, `==`), produced by `pip freeze` in
a clean virtual environment. `pip-audit` found pillow 12.3.0 with 39 published vulnerabilities (BUG-17); after the
upgrade: "No known vulnerabilities found". GitHub Actions runs `pip-audit` on every push. Base images use version tags
(`python:3.11-slim`, `postgres:16-alpine`), not digests – a known limit.
