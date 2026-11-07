# Test Report – Bài tập 3

Dương Diễm My – 2374802010318 · L7 – Chất lượng dữ liệu khách hàng · Track DA · kế hoạch: `docs/test-plan.md`

Mỗi test case chạy lại được bằng một lệnh, in đủ tám cột dưới đây (định nghĩa ở `tests/tc_bt3.py`):

    docker compose run --rm pipeline python -m tests.tc_bt3 TC-06     # Docker (docs/deployment-guide.md)
    python -m tests.tc_bt3 TC-06                                      # máy có .venv (README mục 3)

Tiền điều kiện chung của cả 12 test case: CSDL kiểm thử `smartcrm_test` được làm sạch (xóa schema `ops`, `dwh`) ngay
trước test case – viết tắt **[CSDL sạch]** trong bảng.

## 1. Các lần chạy

| Lần | Ngày · phiên bản | Môi trường | Kết quả |
|---|---|---|---|
| 1 | 07/11/2026 · commit `574bfd0` (vừa viết 12 test case) | môi trường thử Linux của Claude: `.venv` Python 3.11, PostgreSQL 16; làm lại trong Docker (mã nguồn `574bfd0` gắn vào ảnh của lần 2) cho cùng kết quả | **10/12 PASS** – TC-09 FAIL (BUG-15), TC-12 FAIL (BUG-16) |
| 2 | 07/11/2026 · sau commit `a3566b0` (BUG-15) và `aab583b` (BUG-16); lần cuối ở commit ghi trên nhãn ảnh `TC-xx.png` | môi trường thử như lần 1 và Docker (`docker compose run --rm pipeline …`) | **12/12 PASS** |
| 3 | mỗi lần push · GitHub Actions | máy ảo Ubuntu mới, ảnh Docker thật từ Docker Hub | `pytest` 194 passed, 3 skipped (gồm 12 test case) – xanh ([lần chạy ở commit `e3c7a28`](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/actions/runs/42376678386)) |

TC-08 được làm chặt hơn sau rà soát: nạp sẵn 414 dòng rồi mới đưa tệp thiếu cột, để thấy tệp hỏng không đụng tới dữ
liệu đang có. Bản mới chạy trên mã nguồn `574bfd0` vẫn PASS, nên cột "Lần 1" không đổi.

Ảnh kết quả từng test case: `docs/screenshots/TC-01.png` … `TC-12.png`; ảnh lần chạy FAIL: `TC-09-lan1-FAIL.png`,
`TC-12-lan1-FAIL.png`; ảnh phép thử máy trắng: `PT-01-hai-lenh.png` … `PT-07-mat-csdl.png`. Nơi chạy và cách tạo
từng ảnh: `docs/screenshots/README.md`.

## 2. Tóm tắt và truy vết

| Mã | Test case | Loại | Truy vết | Ưu tiên | Lần 1 | Lần cuối |
|---|---|---|---|---|---|---|
| TC-01 | Chuẩn hóa số điện thoại về 0xxxxxxxxx | Luồng đúng | QT-02, FR-02 | Cao | PASS | PASS |
| TC-02 | Hồ sơ lặp số không tạo khách hàng mới | Luồng đúng | QT-01, QL7-02 | Cao | PASS | PASS |
| TC-03 | Điểm tương đồng của cặp FUZZY | Luồng đúng | QL7-03 | Trung bình | PASS | PASS |
| TC-04 | Hồ sơ lỗi ở lại bảng tạm kèm lý do | Luồng đúng | QL7-04, FR-10 | Cao | PASS | PASS |
| TC-05 | Tệp 10 dòng khớp tính tay | Luồng đúng | QL7-06, QL7-04, QT-01 | Cao | PASS | PASS |
| TC-06 | Biên trên ngưỡng 85: điểm 85,43 tạo cặp | Giá trị biên | QL7-02, QL7-03 | Cao | PASS | PASS |
| TC-07 | Biên dưới ngưỡng 85: điểm 84,97 không tạo cặp | Giá trị biên | QL7-02, QL7-03 | Cao | PASS | PASS |
| TC-08 | Tệp thiếu cột bị từ chối cả tệp | Dữ liệu sai | AC1.3, FR-01 | Cao | PASS | PASS |
| TC-09 | Ngày tạo sai vào bảng reject kèm lý do | Dữ liệu sai | data-requirements mục 3, QL7-04 | Trung bình | **FAIL** → BUG-15 | PASS |
| TC-10 | Cố ý vi phạm ngưỡng – hệ thống phát hiện, báo | Chất lượng dữ liệu | D3, QL7-06 (DQ-01) | Cao | PASS | PASS |
| TC-11 | Chạy lại cùng tệp không nhân đôi | Tái lập | AC1.4, NFR-05 | Cao | PASS | PASS |
| TC-12 | Tài khoản dashboard không đọc được dữ liệu cá nhân | Bảo mật | NFR-07, TD-19 | Cao | **FAIL** → BUG-16 | PASS |

## 3. Chi tiết 12 test case (tám cột)

### TC-01 · Chuẩn hóa số điện thoại về 0xxxxxxxxx (QT-02)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc01_chuan_hoa_so.csv` · 2. `SELECT phone_raw, phone_norm, status FROM ops.stg_customer` |
| Dữ liệu thử | 4 hồ sơ, 4 cách viết số: `+84 912 345 678` · `0987.654.321` · `84903111222` · `0933-444-555` |
| Kết quả mong đợi | mã thoát 0; `phone_norm` = 0912345678 · 0987654321 · 0903111222 · 0933444555; 4 CLEAN; `customer_clean` 0 → 4 |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0; `ops.customer_clean` 0 → 4; "+84 912 345 678" → 0912345678 (CLEAN) · "0987.654.321" → 0987654321 (CLEAN) · "84903111222" → 0903111222 (CLEAN) · "0933-444-555" → 0933444555 (CLEAN) |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-01.png` |

### TC-02 · Hồ sơ lặp số không tạo khách hàng mới (QT-01)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc02_ho_so_lap.csv` · 2. đếm `customer_clean`, trạng thái `stg_customer`, cặp `dup_candidate` |
| Dữ liệu thử | 3 hồ sơ; dòng 1 `0912345678` và dòng 2 `0912 345 678` là cùng một số |
| Kết quả mong đợi | `customer_clean` 0 → 2 (không phải 3); CLEAN 2 · PENDING_DUP 1; 1 cặp EXACT_PHONE dòng 1 ↔ dòng 2 |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0; `ops.customer_clean` 0 → 2 (tệp 3 dòng); trạng thái CLEAN 2 · PENDING_DUP 1; cặp dòng 1 ↔ dòng 2 EXACT_PHONE 100,00 |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-02.png` |

### TC-03 · Điểm tương đồng của cặp FUZZY (QL7-03)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc03_diem_tuong_dong.csv` · 2. `SELECT match_type, score FROM ops.dup_candidate` |
| Dữ liệu thử | "Nguyễn Thanh Tâm" 0912345678 và "Nguyễn Thanh Tâm" 0912345670 (khác một chữ số cuối) |
| Kết quả mong đợi | 1 cặp FUZZY, điểm = 0,6 × 90 + 0,4 × 100 = **94,00** |
| Ưu tiên | Trung bình |
| Kết quả thực tế | mã thoát 0; cặp dòng 1 ↔ dòng 2 FUZZY 94,00 |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-03.png` |

### TC-04 · Hồ sơ lỗi ở lại bảng tạm, có lý do cho người đọc (QL7-04)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc04_ho_so_loi.csv` · 2. `SELECT row_no, error_code, ly_do FROM ops.v_reject` |
| Dữ liệu thử | 4 hồ sơ: thiếu số · số `12345` · thiếu họ tên · 1 hồ sơ đúng |
| Kết quả mong đợi | mã thoát 0; `v_reject` 3 dòng: 1 MISSING_PHONE, 2 INVALID_PHONE, 3 MISSING_NAME, mỗi dòng một câu lý do; `customer_clean` 0 → 1 |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0; `ops.customer_clean` 0 → 1; `ops.v_reject` 3 dòng: dòng 1 MISSING_PHONE "Thiếu số điện thoại – không sửa được bằng làm sạch, cửa hàng cần bổ sung tại nguồn" · dòng 2 INVALID_PHONE "Số điện thoại không quy về được dạng 0xxxxxxxxx (…)" · dòng 3 MISSING_NAME "Thiếu họ tên – hồ sơ đã làm sạch bắt buộc có họ tên" |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-04.png` |

### TC-05 · Tệp nhỏ 10 dòng: số dòng và chỉ số mức độ sạch khớp tính tay (QL7-06)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc05_tep_nho_10_dong.csv` · 2. `SELECT measure_stage, clean_index FROM dwh.v_batch_score` |
| Dữ liệu thử | 10 hồ sơ: 1 thiếu số, 2 số viết sai dạng nhưng chuẩn hóa được, 1 số `12345`, 1 hồ sơ lặp số, 3 email (1 sai) |
| Kết quả mong đợi | CLEAN 7 · PENDING_DUP 1 · ERROR 2; `customer_clean` 7; 1 cặp EXACT_PHONE dòng 1 ↔ 6; chỉ số TRƯỚC 85,00 → SAU 90,56 (tính tay: Test Plan mục 4) |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0; CLEAN 7 · ERROR 2 · PENDING_DUP 1; `ops.customer_clean` 7; cặp dòng 1 ↔ dòng 6 EXACT_PHONE 100,00; kho `dwh.v_batch_score`: TRƯỚC 85,00 → SAU 90,56 |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-05.png` |

### TC-06 · Biên ngưỡng 85 – phía trên (QL7-02)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc06_bien_tren_85.csv` · 2. `SELECT match_type, score FROM ops.dup_candidate` |
| Dữ liệu thử | "Nguyễn Thanh Tâm" 0912345678 · "Lê Thanh Tâm" 0912345670 |
| Kết quả mong đợi | 1 cặp FUZZY điểm **85,43** (≥ 85) |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0; blocking: 1 cặp ứng viên được so; `ops.dup_candidate` 1 cặp: dòng 1 ↔ dòng 2 FUZZY 85,43 |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-06.png` |

### TC-07 · Biên ngưỡng 85 – phía dưới (QL7-02)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc07_bien_duoi_85.csv` · 2. `SELECT count(*) FROM ops.dup_candidate` |
| Dữ liệu thử | "Nguyễn Thanh Tâm" 0912345678 · "Nguyễn Văn Tuấn" 0912345670 |
| Kết quả mong đợi | 1 cặp ứng viên được so (cùng 5 số đầu) nhưng **0 cặp** được tạo vì 84,97 < 85 |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0; blocking: 1 cặp ứng viên được so; `ops.dup_candidate` 0 cặp |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-07.png` |

### TC-08 · Tệp thiếu cột bắt buộc bị từ chối cả tệp (AC1.3)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch], rồi nạp sẵn dữ liệu mẫu 414 dòng (bước 1) – để thấy tệp hỏng không đụng tới dữ liệu đang có |
| Các bước | 1. `python -m src.pipeline --tep data/mau/customers_mau.csv` · 2. `python -m src.pipeline --tep data/mau/customers_thieu_cot.csv` · 3. đếm 8 bảng đích trước / sau bước 2 |
| Dữ liệu thử | `data/mau/customers_thieu_cot.csv` – không có cột `so_dien_thoai` |
| Kết quả mong đợi | mã thoát 2; câu "TỪ CHỐI: …" nêu tên cột thiếu, không có Traceback; 8 bảng đích không đổi (`load_batch` 1 → 1, `stg_customer` 414 → 414) |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 2; `ops.load_batch` 1 → 1; `ops.stg_customer` 414 → 414; `ops.customer_clean` 343 → 343 – 8 bảng đích không bảng nào đổi; "TỪ CHỐI: Thiếu cột bắt buộc: so_dien_thoai – từ chối cả đợt, bảng tạm không thay đổi" |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-08.png` |

### TC-09 · Ngày tạo sai định dạng vào bảng reject kèm lý do (data-requirements mục 3)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc09_ngay_sai.csv` · 2. `SELECT row_no, created_raw, error_code, ly_do FROM ops.v_reject` |
| Dữ liệu thử | 3 hồ sơ, ngày tạo: `2026-01-05` (đúng) · `31/02/2026` · `2026-02-30` |
| Kết quả mong đợi | mã thoát 0 (luồng không dừng); `v_reject` 2 dòng INVALID_DATE (dòng 2, 3) có lý do; `customer_clean` 0 → 1 |
| Ưu tiên | Trung bình |
| Kết quả thực tế | **Lần 1 (commit `574bfd0`):** mã thoát 0; `ops.customer_clean` 0 → **3**; `ops.v_reject` **0 dòng** – dòng 2 "31/02/2026" CLEAN, dòng 3 "2026-02-30" CLEAN → ghi BUG-15. **Lần 2 (sau `a3566b0`):** mã thoát 0; `ops.customer_clean` 0 → 1; `ops.v_reject` 2 dòng: dòng 2 "31/02/2026" INVALID_DATE, dòng 3 "2026-02-30" INVALID_DATE, lý do "Ngày tạo không phải ngày hợp lệ dạng yyyy-mm-dd (ví dụ 2026-01-31) – cửa hàng cần sửa tại nguồn" |
| PASS/FAIL | **FAIL → PASS** · `docs/screenshots/TC-09-lan1-FAIL.png`, `TC-09.png` |

### TC-10 · Cố ý vi phạm ngưỡng chất lượng – hệ thống phát hiện và báo (D3)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc10_vi_pham_nguong.csv` · 2. `SELECT measure_stage, pass_rate, is_pass FROM dwh.v_rule_rate WHERE rule_code = 'DQ-01'` |
| Dữ liệu thử | 10 hồ sơ: 2 thiếu số điện thoại (80%), 3 thiếu địa chỉ (70%) |
| Kết quả mong đợi | mã thoát 0; màn hình: `so_dien_thoai 80,00% < 98% CHƯA ĐẠT`, `dia_chi 70,00% < 90% CHƯA ĐẠT`, DQ-01 chưa đạt; kho: DQ-01 `is_pass = false` ở cả TRƯỚC và SAU |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0 (lỗi chất lượng được báo, không làm dừng luồng); màn hình: `so_dien_thoai 80,00% < 98% CHƯA ĐẠT` · `dia_chi 70,00% < 90% CHƯA ĐẠT` · `DQ-01 0,25 ≥ 98% 80,00% chưa đạt 80,00% chưa đạt 2 (20,00%)`; kho `dwh.v_rule_rate` DQ-01: TRUOC 80,00% is_pass=False · SAU 80,00% is_pass=False |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-10.png` |

### TC-11 · Chạy lại cùng tệp lần hai không lỗi, không nhân đôi (AC1.4)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep data/mau/customers_mau.csv` · 2. chạy lại đúng lệnh ở bước 1 · 3. đếm 8 bảng đích sau mỗi lần |
| Dữ liệu thử | `data/mau/customers_mau.csv` (414 dòng, dữ liệu giả) |
| Kết quả mong đợi | cả hai lần mã thoát 0; lần 2 có "CẢNH BÁO (AC1.4)"; 8 bảng đích sau lần 2 giống hệt sau lần 1 (`stg_customer` 414, `dup_candidate` 43) |
| Ưu tiên | Cao |
| Kết quả thực tế | lần 1: mã thoát 0; lần 2: mã thoát 0; "CẢNH BÁO (AC1.4): tệp này đã nạp ở đợt 1 (customers_mau.csv, …) → không tạo đợt mới"; sau lần 1 → sau lần 2: load_batch 1→1 · stg_customer 414→414 · customer_clean 343→343 · dq_result 12→12 · dup_candidate 43→43 · dim_batch 1→1 · fact_dq_check 12→12 · fact_dup_pair 43→43 |
| PASS/FAIL | **PASS** · `docs/screenshots/TC-11.png` |

### TC-12 · Tài khoản dashboard không đọc được dữ liệu cá nhân (NFR-07)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch]; đã chạy luồng chính trên `tc01_chuan_hoa_so.csv`; `.env` theo `.env.example` |
| Các bước | 1. mở kết nối đúng như dashboard: `db.tao_engine_chi_doc()` · 2. `SELECT count(*) FROM dwh.v_batch_score` · 3. `SELECT full_name_raw, phone_raw FROM ops.stg_customer` |
| Dữ liệu thử | kho sau khi nạp 4 hồ sơ của TC-01 |
| Kết quả mong đợi | đọc được kho `dwh`; bị PostgreSQL từ chối khi đọc `ops.stg_customer` (permission denied) |
| Ưu tiên | Cao |
| Kết quả thực tế | **Lần 1 (commit `574bfd0`):** kết nối dùng tài khoản `postgres` (tài khoản của pipeline); kho: ĐỌC ĐƯỢC 1 dòng; `ops.stg_customer` (họ tên, số điện thoại): **ĐỌC ĐƯỢC** → ghi BUG-16. **Lần 2 (sau `aab583b`):** tài khoản `dash_reader`; kho: ĐỌC ĐƯỢC 1 dòng; `ops.stg_customer`: bị từ chối – "permission denied for schema ops" |
| PASS/FAIL | **FAIL → PASS** · `docs/screenshots/TC-12-lan1-FAIL.png`, `TC-12.png` |

## 4. PT-01 – phép thử máy trắng (kiểm thử đầu-cuối của gói đóng gói)

Làm theo các bước của đề BT3 mục 2.4: xóa sạch Docker, clone repo vào thư mục trống, `cp .env.example .env`,
`docker compose up -d --build`, rồi tám bước kiểm tra ở Deployment Guide mục 5, cộng ba bước kiểm checklist bảo mật.
Khác biệt duy nhất ở môi trường của Claude: bước xóa dùng `docker builder prune -af` và xóa container, volume, ảnh của
hệ thống này, thay cho `docker system prune -af --volumes` – lệnh đó xóa luôn hai ảnh gốc dựng cục bộ mà môi trường
không tải lại được (registry bị chặn). GitHub Actions (máy ảo mới mỗi lần) và MacBook làm đúng lệnh của đề.

| Bước | Mong đợi | Thực tế (07/11/2026, Linux của Claude, commit `4ba61ab`) |
|---|---|---|
| Hai lệnh dựng hệ thống | mã thoát 0 | mã thoát 0 |
| `docker compose ps -a` | db, dashboard healthy; pipeline Exited (0) | `db` Up (healthy) · `dashboard` Up (healthy) · `pipeline` Exited (0) |
| `curl -s …/_stcore/health` | `ok` | `ok` |
| Log pipeline · đếm `stg_customer` | 414 = 343 + 40 + 31; 88,41 → 95,79 | `Số dòng: tệp 414 → bảng tạm 414 = sạch 343 + chờ quyết định 40 + lỗi 31`; chỉ số 88,41 → 95,79; `CLEAN 343` · `ERROR 31` · `PENDING_DUP 40` |
| `docker compose run --rm pipeline python -m pytest -q` | 0 failed | 190 passed, 3 skipped |
| Một test case (TC-06) · chạy lại `up -d` | PASS · mọi bảng +0 | PASS · "mọi bảng +0 – không nhân đôi dữ liệu" |
| Kiểm bảo mật: `pip-audit -r requirements.txt` | 0 lỗ hổng | **pillow 12.3.0: 39 lỗ hổng** → BUG-17 |
| Kiểm bảo mật: dừng `db`, chạy pipeline | câu báo đúng cách sửa, không lộ mật khẩu | không lộ mật khẩu, nhưng **khuyên `brew services` / `createdb`** – sai với Docker → BUG-18 |
| Kiểm bảo mật: quét secret trong repo và lịch sử | 0 secret | 0 secret (chi tiết: `docs/checklist-bao-mat.md` mục 1) |

Sau khi sửa BUG-17, BUG-18: pytest trong Docker **191 passed, 3 skipped**; `pip-audit` "No known vulnerabilities found";
câu báo mất CSDL chỉ lệnh `docker compose`. Môi trường Linux của Claude chặn registry Docker nên hai ảnh gốc ở lần
này là ảnh thay thế dựng cục bộ. Cùng các bước chạy lại trên **GitHub Actions với ảnh thật từ Docker Hub** ở mỗi lần
push (`.github/workflows/ci.yml`) – lần chạy đầu ở commit `1a315f9`: mọi bước xanh, pytest 191 passed, 3 skipped,
pip-audit 0 lỗ hổng ([run 42375421851](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/actions/runs/42375421851));
ở commit `e3c7a28` (đủ tài liệu và `tests/test_tai_lieu.py`): pytest **194 passed, 3 skipped**
([run 42376678386](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/actions/runs/42376678386)).
