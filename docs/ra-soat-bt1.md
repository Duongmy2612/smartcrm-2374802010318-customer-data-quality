# Rà soát hồ sơ BT1 – tự kiểm, sáu phép kiểm nhất quán, năm lỗi ERD

Sinh viên: Dương Diễm My – MSSV 2374802010318 · L7 · Track DA

Nội dung này là Phụ lục B.1, B.2 và Bảng 4.2 của bản BT1 nộp ngày 09/10/2026. Theo phản hồi BT1, chúng được chuyển từ PDF vào repo (TD-03 trong `docs/thay-doi-thiet-ke.md`); nội dung không đổi.
Nhật ký thay đổi Buổi 4 → Buổi 6 (Phụ lục B.3) và ánh xạ User Story (Phụ lục B.4) nằm ở `docs/srs.md` mục 7.
Số mục, số bảng trong tệp này theo bản 09/10. Trong bản nộp lại 21/10 (9 trang): GRAIN là Bảng 4.1, từ điển dữ liệu kho là Bảng 4.2, cùng ở mục 4.2 (TD-13).

## 1. Tự kiểm theo bảng tiêu chí kỹ thuật tối thiểu (Phụ lục B.1)

| Nhóm | Mục kiểm chứng | Kết quả | Minh chứng |
|---|---|---|---|
| Chung | Có đủ 5 đầu mục: SRS, Use Case, kiến trúc, mô hình dữ liệu, wireframe | Đạt | Mục 1 – 5 của PDF |
| Chung | Mỗi yêu cầu chức năng truy vết tới ít nhất 1 User Story | Đạt | Bảng truy vết: 11/11 FR có User Story, không ô trống |
| Chung | Mọi sơ đồ có chú thích, đọc được không cần giải thích thêm | Đạt | Use Case, kiến trúc, data flow, ERD, star schema, K1 – K4 đều có khung ký hiệu hoặc ghi chú nguồn dữ liệu |
| Chung | Thuật ngữ nhất quán giữa SRS và các sơ đồ | Đạt | Bảng thuật ngữ; soát bằng Ctrl+F (phép 1) |
| Chung | ≥ 3 câu giải thích lựa chọn kiến trúc, gắn NFR và có đánh đổi | Đạt | Mục 3.2: 4 câu (NFR-01, NFR-06, NFR-05, NFR-04) |
| Chung | Mọi yêu cầu phi chức năng có ngưỡng số đo được | Đạt | 8/8 NFR |
| Chung | Có bảng khai báo sử dụng công cụ AI | Đạt | Phụ lục khai báo AI; `docs/ai-disclosure.md` |
| DA | Có ≥ 1 bảng fact + 2 bảng dimension | Đạt | 2 fact (`fact_dq_check`, `fact_dup_pair`) + 3 dimension (`dim_date`, `dim_batch`, `dim_rule`) |
| DA | Mỗi cột ghi rõ kiểu dữ liệu và ý nghĩa | Đạt | Từ điển kho trong PDF mục 4.4; tầng tác nghiệp ở `docs/data-requirements.md` mục 5.1 |
| DA | Phát biểu rõ GRAIN của bảng fact | Đạt | Bảng GRAIN mục 4.4; ghi lại trên hình star schema |
| DA | Có sơ đồ data flow từ nguồn đến kho dữ liệu | Đạt | `docs/dataflow.drawio` |
| DA | Nêu loại SCD cho dimension thay đổi theo thời gian, kèm lý do | Đạt | `dim_rule` loại 2; `dim_batch`, `dim_date` loại 0 |
| DA | Giải thích chọn star hay snowflake và lý do | Đạt | Mục 4.4 – ba lý do chọn lược đồ hình sao |

## 2. Sáu phép kiểm nhất quán (Phụ lục B.2)

| Phép kiểm | Phát hiện ở bản Buổi 4 và cách đã sửa |
|---|---|
| **1 – Thuật ngữ** | Bổ sung các thuật ngữ mới dùng ở mục 3 – 5 (đơn vị nguồn, hồ sơ thô, hồ sơ lỗi, hồ sơ lặp, khóa tên, lần đo, kho dữ liệu, Chờ xử lý); tên kỹ thuật của "chỉ số mức độ sạch" đổi từ `dq_result` sang view `v_batch_score`; wireframe dùng "hồ sơ nghi trùng" thay cho "bản dư thừa"; tên cột nguồn dùng đúng header thật (`ho_ten`, `so_dien_thoai`). |
| **2 – Truy vết** | Bản Buổi 4 có 11 User Story, vượt giới hạn 5 – 7 → gộp còn 7; US10 thành mục WON'T W1; US11 thành ràng buộc QT-15. Bảng truy vết thêm cột bảng dữ liệu và khung màn hình; 0 ô trống, kể cả hàng WON'T. |
| **3 – Kiến trúc ↔ dữ liệu** | 11 tên bảng ở lớp lưu trữ (sơ đồ kiến trúc) khớp 100% với ERD tầng tác nghiệp và lược đồ kho. |
| **4 – Wireframe ↔ dữ liệu** | Mọi trường trên K1 – K4 có cột nguồn; 11/11 bảng xuất hiện ở ít nhất một khung hoặc báo cáo. |
| **5 – Lập luận ↔ yêu cầu** | 4 câu lập luận đều có mã NFR, ngưỡng số, quyết định và đánh đổi (mục 3.2). |
| **6 – Ngoại lệ ↔ giao diện** | 6 luồng ngoại lệ của UC5 (3a, 3b, 5a, 8a, 8b, 9a) đều có chỗ hiển thị ở vùng thông báo của K4 (`docs/wireframe.drawio` trang 4); dashboard có thông báo trạng thái rỗng (K1). |

## 3. Soi năm lỗi ERD trên tầng tác nghiệp (Bảng 4.2 của bản 09/10)

| Lỗi cần soi | Kết quả và cách xử lý |
|---|---|
| **Bảng cô lập** | Không có: 6/6 bảng nối với nhau bằng 8 khóa ngoại (`stg_customer.batch_id`, `stg_customer.customer_id`, `customer_clean.merged_into`, `dup_candidate.stg_id_a`, `stg_id_b`, `survivor_stg_id`, `dq_result.batch_id`, `dq_result.rule_id`). |
| **Thiếu bảng lịch sử** | Đã có: quyết định Gộp/Giữ riêng lưu ở `dup_candidate` (`decided_by`, `decided_at`, `note`); mỗi lần đo là một dòng mới ở `dq_result`; hồ sơ bị gộp giữ lại với `is_active = false` và `merged_into`; lịch sử cấu hình quy tắc lưu ở `dim_rule` (SCD loại 2). |
| **Lưu giá trị tính được** | Đã sửa: bỏ `pass_rate`, `weighted_score` và "dòng tổng" (`rule_id` NULL) khỏi `dq_result`; bỏ `phone_sim`, `name_sim`, `batch_id` khỏi `dup_candidate`. Ngoại lệ có chủ đích: `phone_norm`, `name_norm`, `name_key` là kết quả bước chuẩn hóa, cần chỉ mục cho so khớp và ràng buộc duy nhất; `score` là bằng chứng tại thời điểm quyết định (NFR-08); `row_count` là tổng kiểm soát số dòng đọc từ tệp. |
| **Thiếu chỉ mục** | Đã thêm: `stg_customer(batch_id)`, `stg_customer(phone_norm)`, `load_batch(file_hash)`, `dup_candidate(status, score DESC)` cho danh sách UC4 (FR-05), `dq_result(batch_id, measured_at)`, `UNIQUE(phone) WHERE is_active` trên `customer_clean`. |
| **Khóa nghiệp vụ làm khóa chính** | Không: mọi khóa chính là khóa thay thế tự tăng; khóa nghiệp vụ (`phone`, `rule_code`, `file_hash`, (`batch_id`, `row_no`), (`stg_id_a`, `stg_id_b`)) chỉ là UNIQUE hoặc chỉ mục. |
