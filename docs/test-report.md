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
| 1 | 07/11/2026 · commit `574bfd0` (vừa viết 12 test case) | môi trường thử Linux của Claude: `.venv` Python 3.11, PostgreSQL 16; làm lại trong Docker (mã nguồn `574bfd0` gắn vào ảnh của lần 2, test case bản đang kiểm) cho cùng kết quả | **10/12 PASS** – TC-09 FAIL (BUG-15), TC-12 FAIL (BUG-16) |
| 2 | 07/11/2026 · sau commit `a3566b0` (BUG-15) và `aab583b` (BUG-16); lần cuối ở commit `7242ae4` | môi trường thử như lần 1 và Docker (`docker compose run --rm pipeline …`) | **12/12 PASS** |
| 3 | 08/11/2026 · commit `c58cd79` (nhánh `main`) | **MacBook của em**, Docker Desktop – phép thử máy trắng từ thư mục trống, ảnh `docs/screenshots/` | lần 1 trên mã nguồn `574bfd0`: TC-09, TC-12 FAIL · lần cuối **12/12 PASS**; pytest 194 passed, 3 skipped |
| 4 | mỗi lần push · GitHub Actions | máy ảo Ubuntu mới, ảnh Docker thật từ Docker Hub | `pytest` 194 passed, 3 skipped (gồm 12 test case) – xanh ([lần chạy ở commit `c58cd79`](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/actions/runs/42408809600); [ở commit `e5139d4`](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/actions/runs/43636228453)) |
| 5 | 15/11/2026 · commit `e5139d4` (nhánh `main`, sau đối chiếu buổi 16) | môi trường thử Linux của Claude: phép thử máy trắng theo đúng lệnh của slide buổi 16 (mục 4.2) | 12 test case 12/12 PASS; pytest 194 passed, 3 skipped (cả `exec` vào dashboard lẫn `run --rm`) |

Ba test case được làm chặt hơn sau lượt rà soát, khi đối chiếu với bảng quy tắc nghiệp vụ của SRS mục 5: **TC-08**
nạp sẵn 414 dòng rồi mới đưa tệp thiếu cột (thấy được tệp hỏng không đụng tới dữ liệu đang có); **TC-02** kiểm thêm
QL7-01 (cặp điểm 100 vẫn chờ người xác nhận, không tự gộp); **TC-12** kiểm thêm QT-14 (phạm vi xem theo đơn vị) – quy
tắc đã hiện thực ở `src/doc_kho.py` nhưng trước đó chỉ có test đơn vị. Chạy bản mới trên mã nguồn `574bfd0`: TC-02,
TC-08 PASS; TC-12 vẫn FAIL ở bước 3 (BUG-16), bước QT-14 PASS – cột "Lần 1" không đổi.

Ảnh kết quả từng test case: `docs/screenshots/TC-01.png` … `TC-12.png`; ảnh lần chạy FAIL: `TC-09-lan1-FAIL.png`,
`TC-12-lan1-FAIL.png`; ảnh phép thử máy trắng và checklist bảo mật: `PT-01-hai-lenh.png` … `PT-08-pip-audit.png`. Nơi chạy và cách tạo
từng ảnh: `docs/screenshots/README.md`.

## 2. Tóm tắt và truy vết

| Mã | Test case | Loại | Truy vết | Ưu tiên | Lần 1 | Lần cuối |
|---|---|---|---|---|---|---|
| TC-01 | Chuẩn hóa số điện thoại về 0xxxxxxxxx | Luồng đúng | QT-02, FR-02 | Cao | PASS | PASS |
| TC-02 | Hồ sơ lặp số không tạo khách hàng mới, không tự gộp | Luồng đúng | QT-01, QL7-01, QL7-02 | Cao | PASS | PASS |
| TC-03 | Điểm tương đồng của cặp FUZZY | Luồng đúng | QL7-03 | Trung bình | PASS | PASS |
| TC-04 | Hồ sơ lỗi ở lại bảng tạm kèm lý do | Luồng đúng | QL7-04, FR-10 | Cao | PASS | PASS |
| TC-05 | Tệp 10 dòng khớp tính tay | Luồng đúng | QL7-06, QL7-04, QT-01 | Cao | PASS | PASS |
| TC-06 | Biên trên ngưỡng 85: điểm 85,43 tạo cặp | Giá trị biên | QL7-02, QL7-03 | Cao | PASS | PASS |
| TC-07 | Biên dưới ngưỡng 85: điểm 84,97 không tạo cặp | Giá trị biên | QL7-02, QL7-03 | Cao | PASS | PASS |
| TC-08 | Tệp thiếu cột bị từ chối cả tệp | Dữ liệu sai | AC1.3, FR-01 | Cao | PASS | PASS |
| TC-09 | Ngày tạo sai vào bảng reject kèm lý do | Dữ liệu sai | data-requirements mục 3, QL7-04 | Trung bình | **FAIL** → BUG-15 | PASS |
| TC-10 | Cố ý vi phạm ngưỡng – hệ thống phát hiện, báo | Chất lượng dữ liệu | D3, QL7-06 (DQ-01) | Cao | PASS | PASS |
| TC-11 | Chạy lại cùng tệp không nhân đôi | Tái lập | AC1.4, NFR-05 | Cao | PASS | PASS |
| TC-12 | Dashboard chỉ đọc được phần dữ liệu được phép | Bảo mật | NFR-07, QT-14, TD-19 | Cao | **FAIL** → BUG-16 | PASS |

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

### TC-02 · Hồ sơ lặp số không tạo khách hàng mới, không tự gộp (QT-01, QL7-01)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch] |
| Các bước | 1. `python -m src.pipeline --tep tests/du_lieu_tc/tc02_ho_so_lap.csv` · 2. đếm `customer_clean`, trạng thái `stg_customer`, cặp `dup_candidate` và trạng thái cặp |
| Dữ liệu thử | 3 hồ sơ; dòng 1 `0912345678` và dòng 2 `0912 345 678` là cùng một số |
| Kết quả mong đợi | `customer_clean` 0 → 2 (không phải 3); CLEAN 2 · PENDING_DUP 1; 1 cặp EXACT_PHONE dòng 1 ↔ dòng 2 ở trạng thái PENDING dù điểm 100, không hồ sơ nào MERGED (QL7-01: không tự động gộp) |
| Ưu tiên | Cao |
| Kết quả thực tế | mã thoát 0; `ops.customer_clean` 0 → 2 (tệp 3 dòng); trạng thái CLEAN 2 · PENDING_DUP 1; cặp dòng 1 ↔ dòng 2 EXACT_PHONE 100,00, trạng thái cặp PENDING; hồ sơ MERGED: 0 |
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

### TC-12 · Dashboard chỉ đọc được phần dữ liệu được phép (NFR-07, QT-14)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | [CSDL sạch]; `.env` theo `.env.example`; nạp `tc01_chuan_hoa_so.csv` cho đơn vị MM001 và `tc02_ho_so_lap.csv` cho đơn vị MM002 (`--don-vi`) |
| Các bước | 1. mở kết nối đúng như dashboard: `db.tao_engine_chi_doc()` · 2. `SELECT batch_key, measure_stage, clean_index FROM dwh.v_batch_score` · 3. `SELECT full_name_raw, phone_raw FROM ops.stg_customer` · 4. `doc_kho.doc_dot()` – hàm dashboard dùng – cho người xem `my.marketing`, `ql.mm001`, và `ql.mm001` tự chọn đơn vị MM002 |
| Dữ liệu thử | kho có 2 đợt: tc01 (MM001), tc02 (MM002); người xem và đơn vị trong `configs/config.yaml` |
| Kết quả mong đợi | đọc được kho `dwh` (2 đợt × 2 lần đo = 4 dòng); bị PostgreSQL từ chối khi đọc `ops.stg_customer` (permission denied); QT-14: `my.marketing` (văn phòng) thấy MM001, MM002 · `ql.mm001` chỉ thấy MM001 · `ql.mm001` chọn MM002 → không đợt nào |
| Ưu tiên | Cao |
| Kết quả thực tế | **Lần 1 (mã nguồn `574bfd0`):** kết nối dùng tài khoản của pipeline (`postgres` ở `.venv`, `smartcrm` trong Docker); kho ĐỌC ĐƯỢC; `ops.stg_customer` (họ tên, số điện thoại): **ĐỌC ĐƯỢC** → ghi BUG-16. **Lần cuối (sau `aab583b`):** tài khoản `dash_reader`; kho: ĐỌC ĐƯỢC 4 dòng; `ops.stg_customer`: bị từ chối – "permission denied for schema ops"; QT-14: `my.marketing` thấy MM001, MM002 · `ql.mm001` thấy MM001 · `ql.mm001` chọn MM002 → không đợt nào |
| PASS/FAIL | **FAIL → PASS** · `docs/screenshots/TC-12-lan1-FAIL.png`, `TC-12.png` |

## 4. PT-01 – phép thử máy trắng (kiểm thử đầu-cuối của gói đóng gói)

Làm theo các bước của đề BT3 mục 2.4: xóa sạch Docker, clone repo vào thư mục trống, `cp .env.example .env`,
`docker compose up -d --build`, rồi các bước kiểm tra ở Deployment Guide mục 5 (lúc đó tám bước; bước 9 thêm ngày 15/11 –
mục 4.2), cộng ba bước kiểm checklist bảo mật.
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
([run 42376678386](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/actions/runs/42376678386)); ở commit `c58cd79` (commit em clone để chụp ảnh trên MacBook): mọi bước xanh,
pytest 194 passed, 3 skipped, pip-audit 0 lỗ hổng, đủ bản dựng sẵn cho linux/arm64 ([run 42408809600](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/actions/runs/42408809600)).

**Lần chạy cuối của PT-01 – trên MacBook của em** (08/11/2026, commit `c58cd79`, cùng buổi với 12 test case – ảnh
`PT-01-hai-lenh.png` … `PT-08-pip-audit.png`): hai lệnh dựng xong, `smartcrm-l7:local` Built; `db`, `dashboard` Up (healthy), `pipeline` Exited (0); `ok`; 414 = 343 +
40 + 31, chỉ số 88,41 → 95,79; pytest 194 passed, 3 skipped; 12/12 test case PASS; chạy lại `up -d` mọi bảng +0;
dừng `db`: câu báo chỉ lệnh `docker compose`, không lộ mật khẩu; `pip-audit`: "No known vulnerabilities found".

### 4.1. Sáu lỗi hay gặp khi gói chạy trên máy sinh viên mà không chạy trên máy khác (slide buổi 16)

Kiểm ngày 15/11/2026 trên repo (môi trường Linux của Claude), mỗi lỗi một lệnh kiểm như slide:

| Lỗi hay gặp | Lệnh kiểm | Kết quả |
|---|---|---|
| Quên commit tệp cần thiết, `.gitignore` chặn nhầm | `git status --ignored` | Chỉ bị bỏ qua: `.env`, `.venv/`, `.pytest_cache/`, `__pycache__/`, `data/raw/customers_raw.csv` (dữ liệu thật), `data/processed/ho_so_loi_dot_*.csv` (có dữ liệu cá nhân), `reports/*.md` (sinh ra khi chạy) – không tệp nào hệ thống cần để dựng; clone mới dựng được (mục 4, 4.2) |
| Đường dẫn tuyệt đối trong mã | `grep -rnF -e 'C:\' -e '/home/' -e '/Users/' src/ dashboard/ tests/ scripts/ configs/ sql/ docker/` | Không có dòng nào: mọi đường dẫn tính từ thư mục gốc repo (`db.GOC`) hoặc lấy từ `--tep`, `.env` |
| Tên tệp sai hoa/thường | `git ls-files` lọc tên có chữ hoa | Mọi tệp mã, cấu hình, SQL, dữ liệu mẫu viết thường (chỉ `Dockerfile`, `README.md` viết hoa theo quy ước); import khớp tên tệp – CI chạy trên Linux (phân biệt hoa/thường) ở mỗi lần push |
| Script `.sh` xuống dòng kiểu Windows (CRLF) | `git ls-files --eol` · `.gitattributes` | 100 tệp văn bản đều lưu LF (`i/lf`), 66 tệp ảnh / PDF nhị phân, 0 tệp CRLF; `.gitattributes` buộc `*.sh`, `*.sql`, `*.yml`, `Dockerfile`, `.env.example` giữ LF kể cả khi clone trên Windows |
| Thiếu bước khởi tạo CSDL hoặc dữ liệu mẫu | `docker compose down -v` rồi `docker compose up -d --build` | `docker/initdb/01-tao-csdl-kiem-thu.sh` tạo `smartcrm_test` khi volume còn trống; pipeline tự tạo schema `ops`, `dwh` (`sql/001` – `005`) rồi nạp `data/mau/customers_mau.csv`: 414 dòng, 8 bảng đích có dữ liệu |
| Thứ tự khởi động, cổng bị chiếm | healthcheck · `APP_PORT=8502` trong `.env` | `db` healthy → `pipeline` chạy (`service_healthy`) → `dashboard` mở khi `pipeline` thoát 0 (`service_completed_successfully`). Với `APP_PORT=8502`: `docker compose ps` hiện `0.0.0.0:8502->8501/tcp`, `curl -s http://localhost:8502/_stcore/health` → `ok`, cổng 8501 để trống |

Cùng ngày, đối chiếu tài liệu track với hệ thống thật như slide chặng 4: từ điển dữ liệu so với `\d <bảng>` trong psql
– tên và kiểu khớp cả 147 cột, NULL khớp mọi cột của 11 bảng (cột của view thì `\d` luôn báo có thể NULL, từ điển ghi
rõ cách hiểu); `tests/test_tai_lieu.py` nay lặp lại phép so này ở mỗi lần chạy test và đã được thử cố ý sửa sai một
kiểu, một NULL trong từ điển → test FAIL đúng dòng đó. Số dòng bị loại theo từng quy tắc ở `docs/pipeline-doc.md`
mục 4 trùng với báo cáo lần chạy (`docs/run-report-sample.md`, mục 2 của báo cáo).

### 4.2. Phép thử máy trắng theo đúng các lệnh trên slide buổi 16

15/11/2026, môi trường thử Linux của Claude (Docker 29), commit `e5139d4` – nội dung mã nguồn của tag `v1.0` (commit sau
chỉ thêm mục này vào Test Report). Tag do em gắn và đẩy (môi trường của Claude không đẩy được tag), nên bước clone dùng
nhánh `main` đúng như slide cho phép khi tag chưa có; khi đã có tag, bước 2 dùng `--branch v1.0` (Deployment Guide mục 2).

| Bước trên slide | Lệnh | Thực tế |
|---|---|---|
| 1 – xóa dấu vết lần trước | `docker compose down -v` (trong thư mục làm việc cũ) | container và volume `smartcrm-l7_pgdata` đã xóa |
| 2 – clone vào thư mục hoàn toàn mới | `cd /tmp && rm -rf kiem-tra && mkdir kiem-tra && cd kiem-tra` · `git clone --branch main https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality.git .` | mã thoát 0; `git log -1` = `e5139d4` |
| 3 – làm đúng Guide | `cp .env.example .env` · `docker compose up -d --build` | mã thoát 0; `pipeline` Exited, `dashboard` Started |
| 4 – Verify it works | `docker compose ps` | `dashboard` Up (healthy) `0.0.0.0:8501->8501/tcp` · `db` Up (healthy) `5432/tcp` (`ps -a`: `pipeline` Exited (0)) |
| | `curl -s http://localhost:8501/_stcore/health` | `ok` |
| | `docker compose exec dashboard python -m pytest -q` · `docker compose run --rm pipeline python -m pytest -q` | cả hai: `194 passed, 3 skipped`, bảng năm loại 23 · 35 · 42 · 3 · 7 |
| | test case chọn ngẫu nhiên: `docker compose run --rm pipeline python -m tests.tc_bt3 TC-07` | `Kết quả : PASS` |
| | cả 12 test case: `docker compose run --rm pipeline python -m tests.tc_bt3` | `Tổng: TC-01 PASS · … · TC-12 PASS → 12/12 PASS` |
| 5 – chạy lại lần hai (C8) | `docker compose run --rm pipeline` | tám bảng đích +0; `Kết quả lần chạy lại: mọi bảng +0 – không nhân đôi dữ liệu.` |
| Guide bước 9 – báo cáo lần chạy | `docker compose cp pipeline:/app/reports/. reports/` | `reports/uc1-dot-1-…md`: mọi con số trùng `docs/run-report-sample.md` (chỉ khác giờ bắt đầu và số giây ở mục 7; SHA-256 của tệp giống nhau) |
| Chặng 4 bước 6 – kiểm nội dung | `git ls-tree -r HEAD --name-only docs/` | đủ `test-plan`, `test-report`, `bug-log`, `deployment-guide`, `checklist-bao-mat`, `pipeline-doc`, `data-dictionary`, `ai-disclosure`, `run-report-sample`, `thay-doi-thiet-ke` và 22 ảnh `screenshots/` |

Ảnh chụp của phép thử máy trắng vẫn là 22 ảnh trên MacBook của em ngày 08/11/2026 (mục 4, `docs/screenshots/`):
các bước 4 – 5 ở trên trùng các ảnh `PT-02`, `PT-04`, `TC-xx`, `PT-05` (ảnh `PT-05` chạy lại bằng `docker compose up -d`,
Guide bước 8 ghi cả hai cách). Lần này cũng chạy trên GitHub Actions (lần 4).
