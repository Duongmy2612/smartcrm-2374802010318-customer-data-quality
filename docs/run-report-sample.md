> **Sample run report** – copied unchanged (below the line) from `reports/uc1-dot-1-20261114_200758.md`, written by
> the `pipeline` service on a fresh `docker compose up -d --build` (empty volume, sample file, 15/11/2026, Claude's
> Linux test environment, code of tag `v1.0`). Times are the container clock (UTC): 14/11 20:07 UTC = 15/11 03:07 in
> Vietnam. Get the same report yourself: Deployment Guide section 5 step 9. The report is generated in Vietnamese;
> section 2 lists the rows rejected per rule, section 6 the row counts of the eight target tables.

---

# Báo cáo UC1 – đợt nạp 1

- Tệp: `data/mau/customers_mau.csv` · SHA-256 `56a2841ed7da0279a87b7d22f45b7ae190d5b31ebda116cd6647723e26df24a7`
- Đơn vị nguồn: TONG_HOP · Người nạp: my.marketing · Bắt đầu: 2026-11-14T20:07:57
- Ghi CSDL: có

## 1. Extract – 414 dòng × 6 cột

| Cột | Ô trống | Có giá trị (độ đầy đủ) | Ngưỡng riêng (D3) | Kết quả |
|---|---:|---:|---:|---|
| record_id | 0 | 100,00% | ≥ 100% | đạt |
| ho_ten | 2 | 99,52% | ≥ 99% | đạt |
| so_dien_thoai | 24 | 94,20% | ≥ 98% | CHƯA ĐẠT |
| email | 227 | 45,17% | ≥ 50% | CHƯA ĐẠT |
| dia_chi | 34 | 91,79% | ≥ 90% | đạt |
| ngay_tao | 0 | 100,00% | ≥ 99% | đạt |

## 2. Transform – số dòng trước → sau

| Hạng mục | Số hồ sơ |
|---|---:|
| Số điện thoại đúng dạng sẵn | 270 |
| Số điện thoại sai dạng đã chuẩn hóa | 115 |
| Số điện thoại không quy đổi được (INVALID_PHONE) | 5 |
| Họ tên được sửa cách viết | 25 |
| **CLEAN** – vào customer_clean | 343 |
| **PENDING_DUP** – hồ sơ lặp chờ quyết định | 40 |
| **ERROR** – ở lại bảng tạm | 31 |
| &nbsp;&nbsp;MISSING_PHONE | 24 |
| &nbsp;&nbsp;INVALID_PHONE | 5 |
| &nbsp;&nbsp;MISSING_NAME | 2 |
| &nbsp;&nbsp;INVALID_DATE | 0 |

Tệp hồ sơ lỗi kèm lý do: `data/processed/ho_so_loi_dot_1.csv` (có dữ liệu cá nhân, không commit).

## 3. Chất lượng TRƯỚC / SAU (FR-08, QL7-06)

| Quy tắc | Tên | Trọng số | Ngưỡng | TRƯỚC (đạt/kiểm) | SAU (đạt/kiểm) | Dòng lỗi SAU (tỉ lệ) |
|---|---|---:|---:|---|---|---:|
| DQ-01 | Số điện thoại không trống | 0,25 | ≥ 98% | 94,20% chưa đạt (390/414) | 94,20% chưa đạt (390/414) | 24 (5,80%) |
| DQ-02 | Số điện thoại đúng mẫu 0xxxxxxxxx | 0,25 | ≥ 95% | 69,23% chưa đạt (270/390) | 98,72% đạt (385/390) | 5 (1,28%) |
| DQ-03 | Họ tên không trống | 0,15 | ≥ 99% | 99,52% đạt (412/414) | 99,52% đạt (412/414) | 2 (0,48%) |
| DQ-04 | Họ tên 2–120 ký tự, không chứa chữ số | 0,10 | ≥ 97% | 100,00% đạt (412/412) | 100,00% đạt (412/412) | 0 (0,00%) |
| DQ-05 | Số điện thoại không trùng | 0,20 | ≥ 98% | 89,61% chưa đạt (345/385) | 89,61% chưa đạt (345/385) | 40 (10,39%) |
| DQ-06 | Email đúng mẫu | 0,05 | ≥ 95% | 94,12% chưa đạt (176/187) | 94,12% chưa đạt (176/187) | 11 (5,88%) |

**Chỉ số mức độ sạch:** TRƯỚC 88,41 (Chấp nhận được) → SAU 95,79 (Tốt), +7,38 điểm.

## 4. UC3 – phát hiện cặp nghi trùng (FR-04)

- Hồ sơ tham gia so khớp: 383 hồ sơ có số hợp lệ (343 số khác nhau); cặp ứng viên sau blocking (giữa hồ sơ đại diện của hai số khác nhau): 53; ngưỡng FUZZY 85.
- Cặp mới: EXACT_PHONE 40 · FUZZY 3.

## 5. Nạp kho và đối soát staging (ops) ↔ kho (dwh)

| Mục | ops | dwh | Khớp | Giải thích |
|---|---:|---:|---|---|
| Đợt nạp | 1 | 1 | có | cùng GRAIN: 1 dòng = 1 đợt |
| Kết quả đo | 12 | 12 | có | cùng GRAIN: 1 dòng = 1 quy tắc × 1 đợt × 1 giai đoạn × 1 lần đo |
| Cặp nghi trùng | 43 | 43 | có | cùng GRAIN: 1 dòng = 1 cặp |
| Hồ sơ thô ↔ mẫu số DQ-01 (lần đo mới nhất) | 414 | 414 | có | khác GRAIN: kho không lưu từng hồ sơ; mẫu số của DQ-01 là mọi hồ sơ của đợt nên phải bằng số hồ sơ thô |
| Hồ sơ lặp chờ quyết định ↔ cặp EXACT_PHONE chờ xử lý | 40 | 40 | có | QL7-02: mỗi hồ sơ lặp sinh đúng một cặp EXACT_PHONE với hồ sơ nạp sớm nhất của cùng số |
| Lần đo trước phiên bản quy tắc đầu tiên (gán phiên bản sớm nhất) | 0 | 0 | có | phải bằng 0; khác 0 là đồng hồ hai máy lệch (TD-16) |

## 6. Số dòng bảng đích trước → sau

| Bảng | Trước | Sau | Thêm |
|---|---:|---:|---:|
| ops.load_batch | 0 | 1 | +1 |
| ops.stg_customer | 0 | 414 | +414 |
| ops.customer_clean | 0 | 343 | +343 |
| ops.dq_result | 0 | 12 | +12 |
| ops.dup_candidate | 0 | 43 | +43 |
| dwh.dim_batch | 0 | 1 | +1 |
| dwh.fact_dq_check | 0 | 12 | +12 |
| dwh.fact_dup_pair | 0 | 43 | +43 |

## 7. Thời gian (NFR-01)

| Bước | Giây |
|---|---:|
| extract | 0,06 |
| transform | 0,06 |
| dq_evaluate | 0,01 |
| load_dwh | 0,01 |
| match | 0,09 |
