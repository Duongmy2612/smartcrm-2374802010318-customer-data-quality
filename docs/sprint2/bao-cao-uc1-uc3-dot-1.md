# Báo cáo UC1 – đợt nạp 1

- Tệp: `data/raw/customers_raw.csv` · SHA-256 `f5a84bdf5da67ea932d729f5c6ab6527ad7d0df9097a3a93558fc891c154117a`
- Đơn vị nguồn: TONG_HOP · Người nạp: my.marketing · Bắt đầu: 2026-10-24T01:48:42
- Ghi CSDL: có

## 1. Extract – 67.037 dòng × 6 cột

| Cột | Ô trống | Tỉ lệ |
|---|---:|---:|
| record_id | 0 | 0,00% |
| ho_ten | 0 | 0,00% |
| so_dien_thoai | 4.133 | 6,17% |
| email | 30.157 | 44,99% |
| dia_chi | 6.023 | 8,98% |
| ngay_tao | 0 | 0,00% |

## 2. Transform – số dòng trước → sau

| Hạng mục | Số hồ sơ |
|---|---:|
| Số điện thoại đúng dạng sẵn | 43.863 |
| Số điện thoại sai dạng đã chuẩn hóa | 19.041 |
| Số điện thoại không quy đổi được (INVALID_PHONE) | 0 |
| Họ tên được sửa cách viết | 5.930 |
| **CLEAN** – vào customer_clean | 51.279 |
| **PENDING_DUP** – hồ sơ lặp chờ quyết định | 11.625 |
| **ERROR** – ở lại bảng tạm | 4.133 |
| &nbsp;&nbsp;MISSING_PHONE | 4.133 |
| &nbsp;&nbsp;INVALID_PHONE | 0 |
| &nbsp;&nbsp;MISSING_NAME | 0 |

Tệp hồ sơ lỗi kèm lý do: `data/processed/ho_so_loi_dot_1.csv` (có dữ liệu cá nhân, không commit).

## 3. Chất lượng TRƯỚC / SAU (FR-08, QL7-06)

| Quy tắc | Tên | Trọng số | Ngưỡng | TRƯỚC (đạt/kiểm) | SAU (đạt/kiểm) |
|---|---|---:|---:|---|---|
| DQ-01 | Số điện thoại không trống | 0,25 | ≥ 98% | 93,83% chưa đạt (62.904/67.037) | 93,83% chưa đạt (62.904/67.037) |
| DQ-02 | Số điện thoại đúng mẫu 0xxxxxxxxx | 0,25 | ≥ 95% | 69,73% chưa đạt (43.863/62.904) | 100,00% đạt (62.904/62.904) |
| DQ-03 | Họ tên không trống | 0,15 | ≥ 99% | 100,00% đạt (67.037/67.037) | 100,00% đạt (67.037/67.037) |
| DQ-04 | Họ tên 2–120 ký tự, không chứa chữ số | 0,10 | ≥ 97% | 100,00% đạt (67.037/67.037) | 100,00% đạt (67.037/67.037) |
| DQ-05 | Số điện thoại không trùng | 0,20 | ≥ 98% | 81,52% chưa đạt (51.279/62.904) | 81,52% chưa đạt (51.279/62.904) |
| DQ-06 | Email đúng mẫu | 0,05 | ≥ 95% | 100,00% đạt (36.880/36.880) | 100,00% đạt (36.880/36.880) |

**Chỉ số mức độ sạch:** TRƯỚC 87,20 (Chấp nhận được) → SAU 94,76 (Tốt), +7,56 điểm.

## 4. UC3 – phát hiện cặp nghi trùng (FR-04)

- Hồ sơ tham gia so khớp: 62.904 hồ sơ có số hợp lệ (51.279 số khác nhau); cặp ứng viên sau blocking (giữa hồ sơ đại diện của hai số khác nhau): 483.124; ngưỡng FUZZY 85.
- Cặp mới: EXACT_PHONE 11.625 · FUZZY 12.

## 5. Nạp kho và đối soát staging (ops) ↔ kho (dwh)

| Mục | ops | dwh | Khớp | Giải thích |
|---|---:|---:|---|---|
| Đợt nạp | 1 | 1 | có | cùng GRAIN: 1 dòng = 1 đợt |
| Kết quả đo | 12 | 12 | có | cùng GRAIN: 1 dòng = 1 quy tắc × 1 đợt × 1 giai đoạn × 1 lần đo |
| Cặp nghi trùng | 11.637 | 11.637 | có | cùng GRAIN: 1 dòng = 1 cặp |
| Hồ sơ thô ↔ mẫu số DQ-01 (lần đo mới nhất) | 67.037 | 67.037 | có | khác GRAIN: kho không lưu từng hồ sơ; mẫu số của DQ-01 là mọi hồ sơ của đợt nên phải bằng số hồ sơ thô |
| Hồ sơ lặp chờ quyết định ↔ cặp EXACT_PHONE chờ xử lý | 11.625 | 11.625 | có | QL7-02: mỗi hồ sơ lặp sinh đúng một cặp EXACT_PHONE với hồ sơ nạp sớm nhất của cùng số |
| Lần đo trước phiên bản quy tắc đầu tiên (gán phiên bản sớm nhất) | 0 | 0 | có | phải bằng 0; khác 0 là đồng hồ hai máy lệch (TD-16) |

## 6. Thời gian (NFR-01)

| Bước | Giây |
|---|---:|
| extract | 4,22 |
| transform | 5,13 |
| dq_evaluate | 0,15 |
| load_dwh | 0,01 |
| match | 7,44 |
