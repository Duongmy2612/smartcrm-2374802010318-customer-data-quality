# Data Requirements – L7: Chất lượng dữ liệu khách hàng (track DA)

Sinh viên: Dương Diễm My – 2374802010318 · Track DA · Phiên bản 1.1 (Buổi 6), thay cho `data-requirement-spec.md` (Buổi 4). Đi kèm `docs/srs.md` và mục 4 của file BT1.

> Mọi con số dưới đây được **đo** trên `data/raw/customers_raw.csv` bằng `notebooks/profiling_customers.py` (seed = 42), không ước đoán. Chạy lại: `python notebooks/profiling_customers.py data/raw/customers_raw.csv`.

## 1. Bảng nguồn dữ liệu

| Hệ thống nguồn | Tệp / định dạng | Tần suất cập nhật | Khối lượng (đo) | Ghi chú |
|---|---|---|---|---|
| Hồ sơ khách hàng thô hợp nhất từ Excel từng cửa hàng, Zalo, sổ tay bảo hành (V1) | `customers_raw.csv` (UTF-8, CSV) | Nạp theo đợt, theo yêu cầu (đề xuất hằng tháng) | 67.037 dòng × 6 cột; mẫu phát triển 8.000 dòng trích theo cụm | Dữ liệu mô phỏng, cố ý có lỗi. `data/raw/` và `data/processed/` không commit; mẫu sinh lại bằng script với seed 42 |
| Tệp Excel khách hàng của cửa hàng (nếu bổ sung) | `.xlsx` | Theo đợt | Vài trăm đến vài nghìn dòng/tệp | Phải có cột `ho_ten`, `so_dien_thoai` |

## 2. Từ điển dữ liệu nguồn (`customers_raw.csv`, header thật)

| Cột | Kiểu | Ý nghĩa | Ánh xạ vào stg_customer | Giá trị hợp lệ | Tỉ lệ thiếu (đo) |
|---|---|---|---|---|---|
| `record_id` | Số nguyên (văn bản trong CSV) | Mã dòng trong tệp nguồn | `source_record_id` | Duy nhất trong một tệp | 0% |
| `ho_ten` | Văn bản | Họ tên khách | `full_name_raw` | 2–120 ký tự, không chứa chữ số | 0% |
| `so_dien_thoai` | Văn bản | Số điện thoại, 5 dạng ghi | `phone_raw` | Sau chuẩn hóa khớp `^0\d{9}$` | 6,17% (4.133) |
| `email` | Văn bản | Thư điện tử | `email_raw` | Đúng mẫu email; có thể trống | 44,99% (30.157) |
| `dia_chi` | Văn bản | Địa chỉ liên hệ | `address_raw` | ≤ 255 ký tự; có thể trống | 8,98% (6.023) |
| `ngay_tao` | Văn bản yyyy-mm-dd | Ngày ghi nhận hồ sơ | `created_raw` | Ngày hợp lệ | 0% |

So với giả định ở Buổi 4 (`full_name, phone, address, source, created_at`): tệp thật dùng tên cột tiếng Việt không dấu, không có cột `source`; `ngay_tao` 100% dạng `yyyy-mm-dd` (2024-01-01 → 2026-08-28), không lẫn 3 định dạng.

## 3. Kết quả profiling

**Dạng ghi số điện thoại (67.037 dòng)**

| Dạng | Số dòng | Tỉ lệ | Cách chuẩn hóa (QT-02) |
|---|---|---|---|
| Chuẩn 0xxxxxxxxx | 43.863 | 65,43% | Giữ nguyên |
| Tiền tố 84… | 6.309 | 9,41% | 84 → 0 |
| Có dấu cách (0xxx xxx xxx) | 5.195 | 7,75% | Bỏ dấu cách |
| Tiền tố +84… | 5.027 | 7,50% | +84 → 0 |
| Có dấu chấm (0xxx.xxx.xxx) | 2.510 | 3,74% | Bỏ dấu chấm |
| Trống | 4.133 | 6,17% | MISSING_PHONE – không sửa được bằng làm sạch, xuất cho cửa hàng (UC9) |

- 19.041 số sai dạng (28,40% tổng số dòng; 30,27% số dòng có số) đều chuẩn hóa được; sau chuẩn hóa 62.904/62.904 số có giá trị khớp `^0\d{9}$`, 0 số không quy về được.
- **Trùng theo số điện thoại chuẩn hóa:** 51.279 số khác nhau; 10.239 nhóm có từ 2 hồ sơ trở lên (8.854 nhóm 2 hồ sơ, 1.384 nhóm 3, 1 nhóm 4) = 19,97% số khách; 11.625 hồ sơ lặp (18,48% hồ sơ có số) → theo QL7-02 sinh 11.625 cặp EXACT_PHONE.
- **Không tự động gộp được:** 4 nhóm cùng số điện thoại nhưng khác họ tên và ngày ghi nhận (hai người khác nhau) → bằng chứng cho luồng 3a của UC5 và quyết định W1.
- **Họ tên không làm khóa được:** 10.080 trên 10.484 khóa tên không dấu được dùng chung bởi ít nhất 2 số điện thoại khác nhau (nhiều nhất 16 số cho một tên) → họ tên chỉ dùng để chấm điểm trong khối đã chặn theo số điện thoại. Hệ quả là giới hạn đã biết của L7: hai hồ sơ của cùng một khách nhưng số điện thoại khác hẳn nhau (kiểu “ba số khác nhau” của V1) không được phát hiện tự động.
- **Họ tên:** IN HOA 2.651, chữ thường 1.933, thừa khoảng trắng 1.346; 0 ô trống; 0 chứa chữ số; dài 9 – 19 ký tự.
- **Email:** 36.880 dòng có giá trị, 100% đúng mẫu. **Địa chỉ:** khác nhau giữa các hồ sơ của cùng một khách → không dùng để so khớp.

## 4. Cách trích mẫu phát triển

| Cách trích (seed 42) | Số dòng | Hồ sơ có số | Hồ sơ lặp | Tỉ lệ lặp | Kết luận |
|---|---|---|---|---|---|
| Ngẫu nhiên theo dòng (script Buổi 4) | 6.000 | 5.608 | 92 | 1,64% | Không dùng được: hai hồ sơ của cùng một khách hiếm khi cùng được chọn → không kiểm được US3, US4 |
| Theo cụm số điện thoại (bản 1.1) | 8.000 | 7.506 | 1.347 | 17,95% | Dùng làm mẫu phát triển: 1.193 nhóm trùng (1.039 nhóm 2, 154 nhóm 3), thiếu số 6,18% – sát dữ liệu gốc |

Trích theo cụm: chọn ngẫu nhiên các số điện thoại chuẩn hóa (seed 42), lấy **mọi** hồ sơ của số đó cho tới khi đủ phần hồ sơ có số, rồi cộng thêm hồ sơ thiếu số theo đúng tỉ lệ gốc. Kết quả ghi ở `data/processed/mau_cum_8000.csv`.

## 5. Mô hình dữ liệu

### 5.1. Tầng tác nghiệp (schema `ops`) – 6 bảng, 8 khóa ngoại
Bốn bảng đã đăng ký ở Buổi 2 (`stg_customer`, `customer_clean`, `dq_rule`, `dq_result`) cộng hai bảng bổ sung `load_batch`, `dup_candidate`. Sơ đồ: `docs/erd.drawio` trang 1.

**`load_batch`** – đợt nạp – 1 dòng = 1 lần nạp một tệp khách hàng thô

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `batch_id` | BIGSERIAL | PK | Mã đợt nạp. |
| `file_name` | VARCHAR(255) | NOT NULL | Tên tệp khách hàng thô đã nạp. |
| `file_hash` | CHAR(64) | NOT NULL, INDEX | Giá trị băm SHA-256 của tệp, dùng cảnh báo nạp lại (FR-01). |
| `source_unit` | VARCHAR(50) | NOT NULL | Đơn vị nguồn (mã cửa hàng/kênh) – căn cứ lọc theo QT-14. |
| `row_count` | INT | NOT NULL, ≥ 0 | Số dòng đọc được từ tệp – tổng kiểm soát để đối chiếu với số hồ sơ thô đã ghi. |
| `loaded_by` | VARCHAR(50) | NOT NULL | Tên đăng nhập người nạp. |
| `loaded_at` | TIMESTAMP | NOT NULL, mặc định now() | Thời điểm nạp. |

**`stg_customer`** – bảng tạm – 1 dòng = 1 hồ sơ thô

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `stg_id` | BIGSERIAL | PK | Mã hồ sơ thô. |
| `batch_id` | BIGINT | FK → load_batch, NOT NULL | Đợt nạp chứa hồ sơ. |
| `customer_id` | BIGINT | FK → customer_clean, NULL được | Hồ sơ đã làm sạch mà hồ sơ thô thuộc về; NULL khi là hồ sơ lỗi hoặc đang chờ quyết định trùng. |
| `row_no` | INT | NOT NULL; UNIQUE(batch_id, row_no) | Số thứ tự dòng trong tệp. |
| `source_record_id` | VARCHAR(20) | NULL được | Giá trị cột record_id của tệp nguồn (chỉ để đối chiếu). |
| `full_name_raw` | VARCHAR(200) | NULL được | Họ tên như trong tệp (cột ho_ten). |
| `phone_raw` | VARCHAR(30) | NULL được | Số điện thoại như trong tệp (cột so_dien_thoai). |
| `email_raw` | VARCHAR(200) | NULL được | Email như trong tệp. |
| `address_raw` | VARCHAR(300) | NULL được | Địa chỉ như trong tệp (cột dia_chi). |
| `created_raw` | VARCHAR(30) | NULL được | Ngày ghi nhận như trong tệp (cột ngay_tao). |
| `phone_norm` | CHAR(10) | NULL được, INDEX | Số điện thoại sau chuẩn hóa (QT-02); NULL khi thiếu hoặc không hợp lệ. |
| `name_norm` | VARCHAR(120) | NULL được | Họ tên sau chuẩn hóa (bỏ khoảng trắng thừa, viết hoa chữ cái đầu). |
| `name_key` | VARCHAR(120) | NULL được | Họ tên không dấu, chữ thường – khóa so khớp (QL7-03). |
| `error_code` | VARCHAR(20) | NULL được; MISSING_PHONE / INVALID_PHONE / MISSING_NAME | Mã lỗi chính khiến hồ sơ không vào customer_clean. |
| `status` | VARCHAR(12) | NOT NULL; LOADED / CLEAN / PENDING_DUP / MERGED / ERROR | Bước xử lý hiện tại của hồ sơ thô. |

**`customer_clean`** – hồ sơ đã làm sạch – 1 dòng = 1 hồ sơ (đang hiệu lực hoặc đã ngừng sử dụng)

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `customer_id` | BIGSERIAL | PK | Mã hồ sơ đã làm sạch. |
| `full_name` | VARCHAR(120) | NOT NULL | Họ tên đã chuẩn hóa. |
| `phone` | CHAR(10) | NOT NULL; CHECK ~ `'^0[0-9]{9}$'`; UNIQUE WHERE is_active | Số điện thoại chính (QT-01, QT-02). |
| `email` | VARCHAR(120) | NULL được | Email. |
| `address` | VARCHAR(255) | NULL được | Địa chỉ liên hệ. |
| `is_active` | BOOLEAN | NOT NULL, mặc định true | false = ngừng sử dụng, đã được gộp vào hồ sơ khác (QT-13). |
| `merged_into` | BIGINT | FK → customer_clean, NULL được | Hồ sơ được giữ lại (đang hiệu lực) đã nhận hồ sơ này khi gộp. |
| `created_at` | TIMESTAMP | NOT NULL | Thời điểm tạo hồ sơ. |
| `updated_at` | TIMESTAMP | NOT NULL | Thời điểm cập nhật gần nhất. |

**`dup_candidate`** – cặp nghi trùng – 1 dòng = 1 cặp hồ sơ thô

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `pair_id` | BIGSERIAL | PK | Mã cặp nghi trùng. |
| `stg_id_a` | BIGINT | FK → stg_customer, NOT NULL | Hồ sơ thứ nhất của cặp (hồ sơ nạp sớm hơn). |
| `stg_id_b` | BIGINT | FK → stg_customer, NOT NULL; UNIQUE(stg_id_a, stg_id_b); CHECK stg_id_a < stg_id_b | Hồ sơ thứ hai của cặp. |
| `match_type` | VARCHAR(12) | NOT NULL; EXACT_PHONE / FUZZY | Loại so khớp đã tạo ra cặp. |
| `score` | NUMERIC(5,2) | NOT NULL, 0–100; INDEX(status, score) | Điểm tương đồng lúc phát hiện (QL7-03) – lưu làm bằng chứng quyết định (NFR-08). |
| `status` | VARCHAR(15) | NOT NULL, mặc định PENDING; PENDING / MERGED / KEEP_SEPARATE | Trạng thái: Chờ xử lý / Gộp / Giữ riêng. |
| `survivor_stg_id` | BIGINT | FK → stg_customer, NULL được; thuộc {stg_id_a, stg_id_b} | Hồ sơ gốc được chọn khi Gộp. |
| `detected_at` | TIMESTAMP | NOT NULL | Thời điểm phát hiện cặp. |
| `decided_by` | VARCHAR(50) | NULL được | Người quyết định Gộp/Giữ riêng. |
| `decided_at` | TIMESTAMP | NULL được | Thời điểm quyết định. |
| `note` | VARCHAR(255) | NULL được | Lý do quyết định (tùy chọn). |

**`dq_rule`** – quy tắc chất lượng dữ liệu (cấu hình hiện hành) – 1 dòng = 1 quy tắc

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `rule_id` | SERIAL | PK | Mã quy tắc. |
| `rule_code` | VARCHAR(10) | NOT NULL, UNIQUE | Mã nghiệp vụ DQ-01 … DQ-06. |
| `rule_name` | VARCHAR(100) | NOT NULL | Tên quy tắc. |
| `rule_type` | VARCHAR(20) | NOT NULL; COMPLETENESS / VALIDITY / UNIQUENESS | Loại tiêu chí chất lượng. |
| `field_name` | VARCHAR(30) | NOT NULL | Trường được kiểm (phone, full_name, email). |
| `weight` | NUMERIC(3,2) | NOT NULL, 0–1 | Trọng số trong chỉ số mức độ sạch (tổng các quy tắc đang bật = 1,00). |
| `pass_threshold` | NUMERIC(5,2) | NOT NULL, 0–100 | Ngưỡng đạt (%) của quy tắc. |
| `is_active` | BOOLEAN | NOT NULL | Quy tắc đang bật hay tắt. |
| `updated_by` | VARCHAR(50) | NULL được | Người sửa cấu hình gần nhất (UC6). |
| `updated_at` | TIMESTAMP | NOT NULL | Thời điểm sửa gần nhất – dùng làm valid_from của phiên bản mới ở dim_rule. |

**`dq_result`** – kết quả đo – 1 dòng = 1 quy tắc × 1 đợt nạp × 1 giai đoạn × 1 lần đo

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `result_id` | BIGSERIAL | PK | Mã kết quả đo. |
| `batch_id` | BIGINT | FK → load_batch, NOT NULL | Đợt nạp được đo. |
| `rule_id` | INT | FK → dq_rule, NOT NULL | Quy tắc được đo. |
| `measure_stage` | VARCHAR(5) | NOT NULL; TRUOC / SAU | Giai đoạn đo: trước hay sau làm sạch. |
| `measured_at` | TIMESTAMP | NOT NULL; INDEX(batch_id, measured_at) | Thời điểm của lần đo. |
| `total_records` | INT | NOT NULL, ≥ 0 | Số hồ sơ thuộc phạm vi áp dụng của quy tắc (mẫu số). |
| `pass_count` | INT | NOT NULL; 0 ≤ pass_count ≤ total_records | Số hồ sơ đạt quy tắc. |

### 5.2. Kho dữ liệu (schema `dwh`) – lược đồ hình sao
Sơ đồ: `docs/erd.drawio` trang 2; luồng nạp: `docs/dataflow.drawio`.

**GRAIN**

| Bảng fact | GRAIN |
|---|---|
| `fact_dq_check` | 1 dòng = kết quả kiểm **1 quy tắc** (đúng phiên bản đang hiệu lực) trên toàn bộ hồ sơ thuộc phạm vi áp dụng của **1 đợt nạp**, ở **1 giai đoạn đo** (TRUOC hoặc SAU), tại **1 lần đo**. Mỗi lần đo sinh 6 dòng (6 quy tắc đang bật). |
| `fact_dup_pair` | 1 dòng = **1 cặp nghi trùng**, được cập nhật theo trạng thái mới nhất (accumulating snapshot: Chờ xử lý → Gộp hoặc Giữ riêng). |

**`dim_date`** – dimension ngày (SCD loại 0) – 1 dòng = 1 ngày

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `date_key` | INT | PK | Khóa ngày dạng yyyymmdd (ví dụ 20261009). |
| `full_date` | DATE | NOT NULL, UNIQUE | Ngày dương lịch; sinh sẵn 01/01/2024 – 31/12/2027 (1.461 dòng). |
| `day_of_month` | SMALLINT | 1–31 | Ngày trong tháng. |
| `month` | SMALLINT | 1–12 | Tháng – gom nhóm theo tháng. |
| `month_label` | CHAR(7) | NOT NULL | Nhãn tháng dạng MM/YYYY trên trục biểu đồ. |
| `quarter` | SMALLINT | 1–4 | Quý. |
| `year` | SMALLINT | NOT NULL | Năm. |

**`dim_batch`** – dimension đợt nạp (SCD loại 0) – 1 dòng = 1 đợt nạp

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `batch_key` | SERIAL | PK | Khóa thay thế của đợt nạp trong kho. |
| `batch_id` | BIGINT | NOT NULL, UNIQUE | Khóa tự nhiên = ops.load_batch.batch_id. |
| `file_name` | VARCHAR(255) | NOT NULL | Tên tệp khách hàng thô của đợt. |
| `source_unit` | VARCHAR(50) | NOT NULL | Đơn vị nguồn – bộ lọc theo quyền xem (QT-14). |
| `loaded_by` | VARCHAR(50) | NOT NULL | Người nạp. |
| `loaded_at` | TIMESTAMP | NOT NULL | Thời điểm nạp – cột Ngày nạp ở K1. |

**`dim_rule`** – dimension quy tắc chất lượng (SCD loại 2) – 1 dòng = 1 phiên bản của 1 quy tắc

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `rule_key` | SERIAL | PK | Khóa thay thế; mỗi phiên bản quy tắc một khóa. |
| `rule_code` | VARCHAR(10) | NOT NULL; UNIQUE(rule_code, valid_from) | Khóa tự nhiên DQ-01 … DQ-06. |
| `rule_name` | VARCHAR(100) | NOT NULL | Tên quy tắc. |
| `rule_type` | VARCHAR(20) | NOT NULL | COMPLETENESS / VALIDITY / UNIQUENESS – bộ lọc ở K2. |
| `field_name` | VARCHAR(30) | NOT NULL | Trường dữ liệu được kiểm. |
| `weight` | NUMERIC(3,2) | NOT NULL, 0–1 | Trọng số của phiên bản. |
| `pass_threshold` | NUMERIC(5,2) | NOT NULL, 0–100 | Ngưỡng đạt (%) của phiên bản. |
| `is_active` | BOOLEAN | NOT NULL | Quy tắc bật/tắt trong phiên bản. |
| `valid_from` | TIMESTAMP | NOT NULL | Bắt đầu hiệu lực (= ops.dq_rule.updated_at). |
| `valid_to` | TIMESTAMP | NULL được | Hết hiệu lực; NULL = phiên bản hiện hành. |

**`fact_dq_check`** – bảng fact kết quả đo – GRAIN ở bảng trên

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `check_id` | BIGSERIAL | PK | Khóa thay thế. |
| `date_key` | INT | FK → dim_date, NOT NULL | Ngày đo (lấy từ measured_at). |
| `batch_key` | INT | FK → dim_batch, NOT NULL | Đợt nạp được đo. |
| `rule_key` | INT | FK → dim_rule, NOT NULL | Phiên bản quy tắc có valid_from ≤ measured_at < valid_to. |
| `result_id` | BIGINT | NOT NULL, UNIQUE | Thuộc tính suy biến = ops.dq_result.result_id; giúp nạp lại không sinh trùng (NFR-05). |
| `measure_stage` | VARCHAR(5) | NOT NULL; TRUOC/SAU | Giai đoạn đo – thuộc tính suy biến. |
| `measured_at` | TIMESTAMP | NOT NULL | Thời điểm lần đo – chọn lần đo mới nhất. |
| `total_records` | INT | NOT NULL, ≥ 0 | Số đo: số hồ sơ thuộc phạm vi áp dụng (mẫu số). |
| `pass_count` | INT | NOT NULL, ≤ total_records | Số đo: số hồ sơ đạt quy tắc. |

**`fact_dup_pair`** – bảng fact cặp nghi trùng – GRAIN ở bảng trên

| Cột | Kiểu | Ràng buộc | Ý nghĩa / nguồn |
|---|---|---|---|
| `pair_key` | BIGSERIAL | PK | Khóa thay thế. |
| `pair_id` | BIGINT | NOT NULL, UNIQUE | Thuộc tính suy biến = ops.dup_candidate.pair_id (khóa để cập nhật). |
| `batch_key` | INT | FK → dim_batch, NOT NULL | Đợt nạp của hồ sơ nạp sau trong cặp (stg_id_b). |
| `detected_date_key` | INT | FK → dim_date, NOT NULL | Ngày phát hiện cặp (vai trò 1 của dim_date). |
| `decided_date_key` | INT | FK → dim_date, NULL được | Ngày quyết định (vai trò 2); NULL khi còn Chờ xử lý. |
| `match_type` | VARCHAR(12) | NOT NULL | EXACT_PHONE / FUZZY – thuộc tính suy biến. |
| `status` | VARCHAR(15) | NOT NULL | PENDING / MERGED / KEEP_SEPARATE – cập nhật khi có quyết định. |
| `score` | NUMERIC(5,2) | NOT NULL, 0–100 | Số đo: điểm tương đồng (lấy trung bình hoặc chia khoảng, không cộng). |

**Loại SCD**

| Dimension | Thuộc tính thay đổi theo thời gian? | Loại SCD | Lý do |
|---|---|---|---|
| `dim_rule` | Có: rule_name, rule_type, field_name, weight, pass_threshold, is_active đổi khi Quản lý cửa hàng lưu cấu hình (UC6, FR-07). | Loại 2 – thêm dòng mới với valid_from/valid_to, giữ dòng cũ. | Lần đo cũ phải được tính bằng trọng số đang hiệu lực lúc đo; ghi đè (loại 1) sẽ làm chỉ số mức độ sạch và đường xu hướng ở K1 bị tính lại hồi tố, vi phạm NFR-05. |
| `dim_batch` | Không: tên tệp, đơn vị nguồn, người nạp, thời điểm cố định sau khi nạp. | Loại 0 – không cập nhật. | Đợt nạp là sự kiện đã xảy ra; muốn sửa thì nạp đợt mới. |
| `dim_date` | Không. | Loại 0. | Lịch tĩnh, sinh sẵn. |

Chọn **lược đồ hình sao (star)**, không chọn bông tuyết (snowflake), vì ba lý do:

(1) Ba dimension đều nhỏ – dim_rule khoảng 6 dòng cho mỗi phiên bản cấu hình, dim_batch tối đa 24 đợt trong phạm vi NFR-06, dim_date 1.461 dòng – nên tách tiếp (đơn vị nguồn, loại quy tắc, tháng/quý ra bảng riêng) chỉ tiết kiệm vài trăm byte nhưng mỗi biểu đồ phải nối thêm 1–2 bảng.

(2) Mỗi biểu đồ ở K1–K3 chỉ cần nối fact với tối đa 3 dimension một bước, dễ viết truy vấn cho dashboard Streamlit và giữ thời gian tải ≤ 5 giây (NFR-06).

(3) Hai fact dùng chung dim_date và dim_batch (conformed dimension) nên một bộ lọc ngày – đơn vị nguồn – đợt nạp áp dụng được cho cả K1, K2, K3; tổng thể là hai ngôi sao dùng chung dimension, mỗi ngôi sao vẫn phẳng.

**Chỉ số tính trong view (không lưu vào bảng)**

| View / truy vấn | Mức chi tiết | Công thức | Dùng ở |
|---|---|---|---|
| v_rule_rate | 1 dòng / 1 dòng fact_dq_check | pass_rate NUMERIC(5,4) = COALESCE(pass_count::NUMERIC / NULLIF(total_records, 0), 1); fail_count INT = total_records − pass_count; lost_points NUMERIC(5,2) = weight × (1 − pass_rate) × 100; is_pass BOOLEAN = pass_rate × 100 ≥ pass_threshold. | K2 |
| v_batch_score | 1 dòng / (đợt nạp, giai đoạn, lần đo) | clean_index NUMERIC(5,2) = Σ weight × pass_rate × 100 trên các quy tắc is_active; grade VARCHAR(15) = Tốt / Chấp nhận được / Kém (QL7-06); is_latest BOOLEAN = lần đo có measured_at lớn nhất theo (đợt, giai đoạn). | K1 |
| Tỉ lệ gộp (truy vấn của K3) | theo khoảng điểm hoặc đợt | merge_rate NUMERIC(5,4) = MERGED / (MERGED + KEEP_SEPARATE); khoảng điểm < 85, 85 – <90, 90 – <95, ≥ 95 tính từ score. | K3 |

**Quy tắc nạp kho (`load_dwh.py`)**
- Thời điểm chạy: sau mỗi lần phát hiện cặp (UC3), mỗi lần đo (UC7) và mỗi lần lưu cấu hình quy tắc (UC6); thêm dòng mới bằng INSERT…SELECT, dùng UPDATE khi đóng phiên bản dim_rule và khi cập nhật trạng thái fact_dup_pair.
- dim_rule: so sánh ops.dq_rule với phiên bản hiện hành theo rule_code; khác thì đóng phiên bản cũ (valid_to = updated_at) và thêm phiên bản mới (SCD loại 2).
- dim_batch: thêm các đợt nạp chưa có (theo batch_id); không cập nhật dòng cũ (loại 0). dim_date sinh sẵn một lần.
- fact_dq_check: thêm các dòng ops.dq_result chưa có (theo result_id); rule_key = phiên bản có valid_from ≤ measured_at < valid_to (valid_to NULL coi như vô hạn).
- fact_dup_pair: thêm cặp mới; với cặp đã có (theo pair_id) chỉ cập nhật status và decided_date_key khi có quyết định.

## 6. Quy tắc chất lượng dữ liệu (nội dung `dq_rule` / `dim_rule`)

| Mã | Loại | Kiểm tra | Phạm vi áp dụng (mẫu số) | Trọng số | Ngưỡng đạt | TRƯỚC (đo) | SAU chuẩn hóa (đo) |
|---|---|---|---|---|---|---|---|
| DQ-01 | COMPLETENESS | Số điện thoại không trống | Mọi hồ sơ của đợt | 0,25 | ≥ 98% | 93,83% | 93,83% |
| DQ-02 | VALIDITY | Số điện thoại khớp `^0\d{9}$` (TRƯỚC: giá trị thô; SAU: phone_norm) | Hồ sơ có số điện thoại | 0,25 | ≥ 95% | 69,73% | 100% |
| DQ-03 | COMPLETENESS | Họ tên không trống | Mọi hồ sơ của đợt | 0,15 | ≥ 99% | 100% | 100% |
| DQ-04 | VALIDITY | Họ tên 2–120 ký tự, không chứa chữ số | Hồ sơ có họ tên | 0,10 | ≥ 97% | 100% | 100% |
| DQ-05 | UNIQUENESS | Số điện thoại không trùng (so theo phone_norm ở cả hai giai đoạn): trong mỗi nhóm cùng số, hồ sơ nạp sớm nhất đạt; hồ sơ khác chỉ đạt khi cặp của nó đã Gộp hoặc Giữ riêng | Hồ sơ có số hợp lệ | 0,20 | ≥ 98% | 81,52% | 81,52% → 100% khi xử lý hết cặp |
| DQ-06 | VALIDITY | Email đúng mẫu | Hồ sơ có email | 0,05 | ≥ 95% | 100% | 100% |
| | | **Tổng trọng số** | | **1,00** | | | |

**Công thức (QL7-06):** chỉ số mức độ sạch của một đợt tại một lần đo = Σ (trọng số × tỉ lệ đạt) × 100, tỉ lệ đạt = số hồ sơ đạt / số hồ sơ thuộc phạm vi áp dụng của quy tắc. Mẫu số theo phạm vi giúp hồ sơ thiếu số chỉ bị trừ điểm một lần (ở DQ-01), không bị phạt lại ở DQ-02, DQ-05.

**Mục tiêu chung:** chỉ số mức độ sạch SAU ≥ 90 (loại *Tốt*) và cao hơn chỉ số TRƯỚC ít nhất 10 điểm.

| Thời điểm | Chỉ số mức độ sạch |
|---|---|
| Chỉ số mức độ sạch TRƯỚC làm sạch (đo) | 87,20 – Chấp nhận được |
| SAU chuẩn hóa, chưa có quyết định trùng (đo) | 94,76 – Tốt (+7,56 điểm) |
| SAU khi xử lý hết cặp nghi trùng (ước tính) | 98,46 – Tốt (+11,26 điểm so với TRƯỚC) |
| Mẫu 8.000 dòng theo cụm (đo; giá trị cuối là ước tính) | 87,34 → 94,87 → 98,46 (cùng xu hướng) |

- Chuẩn hóa một mình chỉ tăng 7,56 điểm; mục tiêu chỉ đạt (+11,26) khi Marketing xử lý hết cặp nghi trùng – đó là lý do UC5/US4 là MUST.
- DQ-01 (93,83%) không thể đạt ngưỡng 98% bằng làm sạch vì số điện thoại bị thiếu thật; chỉ sửa được tại nguồn → US7/UC9 xuất danh sách 4.133 hồ sơ lỗi cho cửa hàng.
- DQ-03, DQ-04 đạt 100% trên dữ liệu mẫu nhưng vẫn giữ vì tệp thật của cửa hàng có thể thiếu hoặc ghi sai họ tên.

## 7. Thuật toán so khớp mờ (đặc tả, bản 1.1)

1. **Chuẩn bị:** `phone_norm` (QT-02); `name_key` = họ tên bỏ dấu, chữ thường, bỏ khoảng trắng thừa. Hồ sơ không có số hợp lệ không tham gia (QL7-04).
2. **Blocking** (NFR-01): chỉ so sánh hai hồ sơ cùng **5 số đầu** hoặc cùng **5 số cuối** của `phone_norm`. Đo trên mẫu 8.000 dòng (7.506 hồ sơ có số): so toàn bộ cần 28.166.265 cặp, blocking còn 11.858 cặp (0,042%) và vẫn chứa đủ 1.501 cặp cùng số. Khóa "cùng tên gọi" của bản 1.0 bị bỏ: thêm 639.483 phép so sánh nhưng chỉ tạo thêm 1 cặp, là dương tính giả (cùng họ tên, khác số, khác ngày ghi nhận).
3. **Độ giống số điện thoại:** 100 nếu bằng nhau; ngược lại `rapidfuzz.fuzz.ratio` trên hai chuỗi 10 chữ số.
4. **Độ giống họ tên:** `rapidfuzz.fuzz.token_sort_ratio` trên `name_key`.
5. **Điểm tương đồng** = 0,6 × độ giống số điện thoại + 0,4 × độ giống họ tên (QL7-03).
6. **Tạo cặp (QL7-02):** cùng `phone_norm` → `EXACT_PHONE`; nhóm k hồ sơ cùng số tạo k − 1 cặp, mỗi cặp ghép hồ sơ nạp sớm nhất với một hồ sơ còn lại (toàn bộ tệp: 11.625 cặp; mẫu: 1.347 cặp). Khác số và điểm ≥ 85 → `FUZZY`. Cặp đã Giữ riêng không tạo lại (QL7-05).
7. Ngưỡng 85 là giá trị khởi đầu, chỉnh theo precision/recall trên 300 cặp gán nhãn tay (NFR-03).

## 8. Câu hỏi phân tích và mức chi tiết báo cáo

| # | Câu hỏi phân tích | Truy vết User Story | Mức chi tiết | Khung dashboard |
|---|---|---|---|---|
| Q1 | Mỗi đợt nạp có bao nhiêu % hồ sơ thiếu số, sai dạng, nghi trùng? | US6 | Theo đợt nạp | K1 (thẻ chỉ số), K2 |
| Q2 | Chỉ số mức độ sạch thay đổi thế nào theo thời gian, TRƯỚC và SAU làm sạch? | US6 | Theo đợt nạp, ngày, tháng | K1 (biểu đồ đường) |
| Q3 | Quy tắc nào kéo chỉ số xuống nhiều nhất? | US5, US6 | Theo quy tắc DQ-01 … DQ-06 | K2 (điểm bị mất) |
| Q4 | Bao nhiêu cặp nghi trùng đã Gộp, Giữ riêng, còn Chờ xử lý? | US3, US4 | Theo đợt nạp, trạng thái | K3 |
| Q5 | Phân bố điểm tương đồng và tỉ lệ gộp theo khoảng điểm (để chỉnh ngưỡng)? | US3, US4 | Khoảng < 85, 85 – <90, 90 – <95, ≥ 95 | K3 |
| Q6 | Bao nhiêu số điện thoại sai dạng đã được sửa nhờ chuẩn hóa, và bao nhiêu hồ sơ thiếu số không sửa được (phải sửa tại nguồn)? | US1, US7 | Theo đợt nạp, loại lỗi | K2 (ghi chú hiệu quả chuẩn hóa), tệp CSV hồ sơ lỗi |

## 9. Tái lập (NFR-05)
- Seed = 42 cho mọi bước ngẫu nhiên (trích mẫu); ghi trong README.
- Lệnh: `python notebooks/profiling_customers.py data/raw/customers_raw.csv` → in số đo, ghi `data/processed/mau_cum_8000.csv` và `data/processed/profiling_result.json`.
