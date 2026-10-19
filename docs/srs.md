# SRS – Smart CRM Mekong Mobile · L7: Chất lượng dữ liệu khách hàng

| Mục | Nội dung |
|---|---|
| Sinh viên | Dương Diễm My – MSSV 2374802010318 |
| Track | DA (Data Analytics) |
| Học phần | Chuyên đề tốt nghiệp 1 (71ITGR40203) – Trường ĐH Văn Lang |
| Luồng nghiệp vụ | L7 – Chất lượng dữ liệu khách hàng |
| Phiên bản | 1.1 (Buổi 6 – nộp kèm Bài tập 1); thay đổi so với 1.0 (Buổi 4) ở mục 7 |
| Tài liệu liên quan | `docs/usecase.drawio`, `docs/architecture.drawio`, `docs/dataflow.drawio`, `docs/erd.drawio`, `docs/wireframe.drawio` / `docs/wireframe.png`, `docs/data-requirements.md`, `docs/ai-disclosure.md` |

**Phạm vi một câu:** Nạp tệp khách hàng thô, chuẩn hóa số điện thoại và họ tên, phát hiện cặp hồ sơ nghi trùng bằng so khớp mờ để Nhân viên Marketing xác nhận gộp hoặc giữ riêng, rồi đo và báo cáo chỉ số mức độ sạch dữ liệu theo từng đợt nạp.

---

## 1. Giới thiệu

### 1.1. Mục đích
Tài liệu đặc tả yêu cầu cho luồng L7 của hệ thống Smart CRM Mekong Mobile: phát hiện hồ sơ lặp, hồ sơ thiếu hoặc sai định dạng trong dữ liệu khách hàng; chuẩn hóa dữ liệu; đo và báo cáo mức độ sạch theo thời gian. Luồng giải quyết vấn đề **V1** của case study. Đây là bản nguồn của Mục 1 – 2 trong file BT1 (PDF).

### 1.2. Phạm vi

**Làm**
- Nạp tệp khách hàng thô (CSV/Excel) theo đợt nạp; chuẩn hóa số điện thoại và họ tên (UC1, UC2).
- Phát hiện cặp nghi trùng bằng so khớp mờ; Nhân viên Marketing xem và xác nhận Gộp hoặc Giữ riêng từng cặp (UC3, UC4, UC5).
- Cấu hình bộ quy tắc chất lượng dữ liệu; đo chỉ số mức độ sạch của từng đợt trước và sau làm sạch (UC6, UC7).
- Dashboard mức độ sạch theo thời gian và xuất danh sách hồ sơ lỗi để cửa hàng sửa tại nguồn (UC8, UC9).

**Chủ ý không làm (mức WON'T của MoSCoW)**

| Mã | Không làm | Lý do |
|---|---|---|
| W1 | Tự động gộp cặp nghi trùng có điểm tương đồng cao mà không cần xác nhận (US10 của bản Buổi 4). | Gộp nhầm hai người rất khó hoàn tác; đo được 4 nhóm hồ sơ cùng số điện thoại nhưng là hai người khác nhau (khác họ tên và ngày ghi nhận) – gộp tự động sẽ sai ngay trên dữ liệu mẫu (QL7-01). |
| W2 | Xử lý dữ liệu đơn hàng, bảo hành, kho linh kiện; phân khúc khách hàng (L1); dự báo khách rời bỏ (L9). | Thuộc luồng nghiệp vụ khác; L7 chỉ làm sạch dữ liệu khách hàng. |
| W3 | Gửi tin khuyến mãi/chiến dịch thực tế; tích hợp trực tiếp hệ thống bán hàng; đăng nhập một lần (SSO); triển khai máy chủ. | Ngoài phạm vi prototype của Chuyên đề tốt nghiệp 1. |

### 1.3. Bảng thuật ngữ
Mỗi khái niệm chỉ dùng **một tên** trong SRS, sơ đồ, ERD và wireframe.

| Thuật ngữ | Định nghĩa | Tên kỹ thuật |
|---|---|---|
| **Hồ sơ khách hàng** | Một bản ghi mô tả một khách hàng: họ tên, số điện thoại, email, địa chỉ. | `stg_customer, customer_clean` |
| **Tệp khách hàng thô** | Tệp CSV/Excel chưa làm sạch, mỗi dòng là một hồ sơ; cột bắt buộc ho_ten, so_dien_thoai (mẫu: customers_raw.csv). Trên Use Case, nơi cung cấp tệp là actor hệ thống ngoài “Tệp nguồn Excel/CSV”. | – |
| **Đợt nạp** | Một lần nạp một tệp khách hàng thô; có mã, thời điểm, người nạp và đơn vị nguồn. | `load_batch` |
| **Đơn vị nguồn** | Cửa hàng hoặc kênh cung cấp tệp của đợt nạp; căn cứ phân quyền xem dữ liệu (QT-14). | `source_unit` |
| **Bảng tạm** | Nơi lưu hồ sơ thô sau khi nạp, trước khi làm sạch. | `stg_customer` |
| **Hồ sơ thô** | Một dòng của tệp khách hàng thô đã nạp vào bảng tạm, giữ nguyên giá trị gốc. | `stg_customer (1 dòng)` |
| **Chuẩn hóa** | Đưa số điện thoại về dạng 0xxxxxxxxx (QT-02) và họ tên về một dạng thống nhất (FR-02, FR-03). | `phone_norm, name_norm` |
| **Khóa tên** | Họ tên không dấu, chữ thường, bỏ khoảng trắng thừa; tạo khi phát hiện cặp nghi trùng (FR-04) để chấm điểm tương đồng (QL7-03). | `name_key` |
| **Hồ sơ lỗi** | Hồ sơ thô có mã lỗi (thiếu hoặc sai số điện thoại, thiếu họ tên) nên không được đưa vào hồ sơ đã làm sạch. | `error_code` |
| **Hồ sơ đã làm sạch** | Hồ sơ đã chuẩn hóa, có số điện thoại hợp lệ và không trùng với hồ sơ đang hiệu lực nào khác. | `customer_clean` |
| **Cặp nghi trùng** | Hai hồ sơ có khả năng là một người; mỗi hồ sơ trong cặp gọi là hồ sơ nghi trùng. | `dup_candidate` |
| **Hồ sơ lặp** | Hồ sơ có cùng số điện thoại chuẩn hóa với một hồ sơ nạp sớm hơn; mỗi hồ sơ lặp sinh một cặp EXACT_PHONE (QL7-02). Tỉ lệ hồ sơ lặp = số hồ sơ lặp / số hồ sơ có số điện thoại. | – (đếm theo phone_norm) |
| **Điểm tương đồng** | Số từ 0 đến 100 đo mức giống nhau của hai hồ sơ trong cặp nghi trùng (QL7-03). | `score` |
| **Chờ xử lý / Gộp / Giữ riêng** | Ba trạng thái của cặp nghi trùng: chưa quyết định; đã hợp nhất thành một hồ sơ (có xác nhận); đã xác định là hai khách khác nhau. | `PENDING / MERGED / KEEP_SEPARATE` |
| **Hồ sơ gốc** | Hồ sơ được chọn khi gộp để lấy giá trị cho hồ sơ đã làm sạch sau gộp; trường trống được bổ sung từ hồ sơ còn lại. | `survivor_stg_id` |
| **Ngừng sử dụng** | Xóa mềm: đánh dấu không dùng nữa, giữ nguyên lịch sử (QT-13). | `is_active = false` |
| **Quy tắc chất lượng dữ liệu** | Một tiêu chí đánh giá hồ sơ (DQ-01 … DQ-06), có loại, trường áp dụng, trọng số và ngưỡng đạt. | `dq_rule / dim_rule` |
| **Lần đo** | Một lần đánh giá các quy tắc đang bật trên một đợt nạp, ở giai đoạn TRƯỚC (trên giá trị thô) hoặc SAU làm sạch; riêng quy tắc không trùng (DQ-05) luôn so theo số đã chuẩn hóa. | `dq_result / fact_dq_check` |
| **Chỉ số mức độ sạch** | Điểm 0–100 của một đợt nạp tại một lần đo = Σ(trọng số × tỉ lệ đạt) × 100 (QL7-06); tính trong view, không lưu. | `v_batch_score` |
| **Kho dữ liệu** | Schema dwh dạng lược đồ hình sao (bảng fact, bảng dimension) phục vụ dashboard; chỉ chứa số đếm, không chứa dữ liệu cá nhân. | `dwh` |

### 1.4. Tài liệu tham chiếu
- Case study Smart CRM – Mekong Mobile: Bảng 2.2 (V1, V5), Mục 7 (L7), Mục 8 (từ điển dữ liệu tham chiếu), Bảng 9.1 (quy tắc nghiệp vụ), Mục 11 (dữ liệu mẫu).
- Bài thực hành Buổi 2 (phiếu phạm vi đã duyệt), Buổi 4 (SRS 1.0, Use Case), slide Buổi 6 (Workshop thiết kế kiến trúc, mô hình dữ liệu và wireframe).
- `docs/data-requirements.md` – số đo trên `customers_raw.csv` (sinh bởi `notebooks/profiling_customers.py`, seed 42).

---

## 2. Mô tả tổng quan

### 2.1. Bối cảnh và vấn đề
Mekong Mobile (24 cửa hàng, 6 trung tâm bảo hành, khoảng 65.000 khách hàng) chưa có hệ thống CRM. Dữ liệu khách hàng nằm rải rác ở file Excel của từng cửa hàng, tin nhắn Zalo và sổ tay trung tâm bảo hành; một khách có thể tồn tại nhiều lần với nhiều số điện thoại (vấn đề V1 – case study ánh xạ tới L1, L7; ước tính 18–22% hồ sơ lặp). Marketing cũng chưa phân khúc được khách hàng nên phải gửi khuyến mãi cho toàn bộ danh sách (V5, thuộc L1, L9) – muốn phân khúc, trước hết mỗi khách phải là một hồ sơ duy nhất, đó là việc của L7. Đo trên tệp mẫu `customers_raw.csv` (67.037 dòng): 18,48% hồ sơ có số điện thoại là hồ sơ lặp của một khách đã có, 6,17% hồ sơ thiếu số điện thoại và 28,40% hồ sơ ghi số điện thoại sai dạng (84…, +84…, có dấu cách hoặc dấu chấm).

### 2.2. Actor

| Actor | Loại | Được làm | Không được làm |
|---|---|---|---|
| **Nhân viên Marketing** | Người dùng chính (Bộ phận Marketing, 5 người; thuộc văn phòng công ty nên phạm vi dữ liệu là toàn công ty) | Nạp tệp (UC1); chạy phát hiện cặp nghi trùng (UC3); xem danh sách và xác nhận Gộp/Giữ riêng (UC4, UC5); xem dashboard (UC8); xuất danh sách hồ sơ lỗi (UC9). | Không cấu hình quy tắc chất lượng (UC6); không xem số điện thoại đầy đủ (QT-15); không xóa hồ sơ (QT-13). |
| **Quản lý cửa hàng** | Người dùng (24 người) | Cấu hình quy tắc chất lượng dùng chung toàn công ty (UC6) – mỗi lần lưu ghi người sửa gần nhất (dq_rule.updated_by) và tạo phiên bản mới ở dim_rule (SCD loại 2); xem dashboard của đơn vị mình (UC8); xuất hồ sơ lỗi của đơn vị mình để sửa tại nguồn (UC9); xem số điện thoại đầy đủ. | Không quyết định Gộp/Giữ riêng (thuộc Marketing); không xem dữ liệu của đơn vị khác (QT-14); không xóa hồ sơ (QT-13). |
| **Tệp nguồn Excel/CSV** | Hệ thống ngoài (actor phụ) | Cung cấp hồ sơ thô cho UC1. | Không ghi trực tiếp vào CSDL; tệp thiếu cột ho_ten hoặc so_dien_thoai bị từ chối cả đợt. |

### 2.3. Luồng nghiệp vụ tổng thể (bắt đầu → kết thúc)
1. Nhân viên Marketing nạp tệp khách hàng thô của một đơn vị nguồn → hệ thống tạo đợt nạp (`load_batch`) và ghi hồ sơ thô vào `stg_customer` (UC1).
2. Hệ thống chuẩn hóa số điện thoại và họ tên, gắn mã lỗi (UC2). Hồ sơ hợp lệ có số chưa tồn tại → `customer_clean`; hồ sơ lặp (trùng số với hồ sơ có sẵn) không được tạo mới (QT-01) mà chờ quyết định; hồ sơ lỗi ở lại bảng tạm (QL7-04). Hệ thống đo chỉ số mức độ sạch giai đoạn TRƯỚC (trên giá trị thô) và SAU (UC7).
3. Nhân viên Marketing chạy phát hiện cặp nghi trùng (UC3) → `dup_candidate` ở trạng thái Chờ xử lý.
4. Nhân viên Marketing xem danh sách và quyết định Gộp hoặc Giữ riêng từng cặp (UC4, UC5); sau mỗi quyết định hệ thống đo lại chỉ số (UC7).
5. Sau mỗi lần phát hiện cặp, mỗi lần đo và mỗi lần Quản lý cửa hàng lưu cấu hình quy tắc (UC6), hệ thống nạp kho dữ liệu (schema `dwh`).
6. Quản lý cửa hàng và Nhân viên Marketing xem dashboard mức độ sạch theo thời gian (UC8), xuất danh sách hồ sơ lỗi để cửa hàng sửa tại nguồn (UC9). *Kết thúc.*

### 2.4. Ràng buộc và giả định
- Prototype chạy cục bộ: Python 3.11 (pandas, rapidfuzz), PostgreSQL, Streamlit; không tích hợp hệ thống thật của doanh nghiệp.
- Dữ liệu mô phỏng của case study; mẫu phát triển 8.000 dòng trích theo cụm số điện thoại với seed = 42 (`docs/data-requirements.md`, mục 4).
- “Làm từng phần, phần nào xong dùng phần đó” (Phó Tổng giám đốc): L7 được triển khai độc lập, không phụ thuộc luồng khác.
- Người dùng và vai trò khai báo trong cấu hình ứng dụng (prototype); tên đăng nhập được ghi vào loaded_by, decided_by, updated_by.
- Tệp nguồn bắt buộc có hai cột `ho_ten`, `so_dien_thoai` (header thật của `customers_raw.csv`: `record_id, ho_ten, so_dien_thoai, email, dia_chi, ngay_tao`); `email`, `dia_chi` có thể trống.
- Hồ sơ không có số điện thoại hợp lệ không vào `customer_clean` mà ở lại `stg_customer` kèm mã lỗi (QL7-04) và được liệt kê khi xuất danh sách hồ sơ lỗi (UC9).
- Giới hạn đã biết: hai hồ sơ của cùng một khách nhưng số điện thoại khác hẳn nhau không được phát hiện tự động, vì họ tên không làm khóa được (10.080 / 10.484 khóa tên dùng chung bởi ≥ 2 số).

### 2.5. Thực thể dữ liệu
Tầng tác nghiệp (schema `ops`): `load_batch`, `stg_customer`, `customer_clean`, `dup_candidate`, `dq_rule`, `dq_result`. Kho dữ liệu (schema `dwh`): `dim_date`, `dim_batch`, `dim_rule`, `fact_dq_check`, `fact_dup_pair`. Từ điển dữ liệu ở `docs/data-requirements.md`; sơ đồ ở `docs/erd.drawio` (2 trang) và `docs/dataflow.drawio`.

---

## 3. Yêu cầu chức năng

### 3.1. Danh sách User Story
Vai trò, mục tiêu, giá trị nối trực tiếp về vấn đề V1 ở Bảng 2.2 của case study (V1 được ánh xạ tới L1, L7). Bản 1.0 có 11 story, vượt giới hạn 5 – 7 nên được gộp còn 7 (ánh xạ ở mục 7).

| ID | User Story | MoSCoW |
|---|---|---|
| **US1** | Là **Nhân viên Marketing**, tôi muốn nạp tệp khách hàng thô (CSV/Excel) và nhận số điện thoại đã ở dạng chuẩn 0xxxxxxxxx để không phải sửa tay hàng nghìn số sai dạng (V1; đo được 28,40% hồ sơ ghi số sai dạng). | MUST |
| **US2** | Là **Nhân viên Marketing**, tôi muốn họ tên khách được chuẩn hóa về một dạng thống nhất để danh sách hiển thị gọn và gọi đúng tên khách (đo được 2.651 họ tên viết IN HOA, 1.933 viết thường, 1.346 thừa khoảng trắng). | SHOULD |
| **US3** | Là **Nhân viên Marketing**, tôi muốn hệ thống tự phát hiện các cặp hồ sơ nghi trùng kèm điểm tương đồng để không phải dò thủ công khoảng 18% hồ sơ lặp (V1). | MUST |
| **US4** | Là **Nhân viên Marketing**, tôi muốn xem danh sách cặp nghi trùng sắp theo điểm tương đồng và xác nhận Gộp hoặc Giữ riêng từng cặp để hồ sơ được hợp nhất đúng mà không gộp nhầm hai người khác nhau. | MUST |
| **US5** | Là **Quản lý cửa hàng**, tôi muốn cấu hình trọng số và ngưỡng của các quy tắc chất lượng dữ liệu để tiêu chí đánh giá phù hợp từng giai đoạn mà không cần sửa mã. | SHOULD |
| **US6** | Là **Quản lý cửa hàng**, tôi muốn xem chỉ số mức độ sạch của từng đợt nạp và xu hướng theo thời gian để biết dữ liệu đạt hay chưa và đang cải thiện hay xấu đi mà không phải đếm tay trên từng tệp Excel. | SHOULD |
| **US7** | Là **Quản lý cửa hàng**, tôi muốn xuất danh sách hồ sơ lỗi ra tệp CSV để cửa hàng bổ sung số điện thoại tại nguồn, vì 6,17% hồ sơ thiếu số không thể sửa bằng làm sạch. | COULD |

### 3.1.1. Kiểm tra INVEST

| ID | I | N | V | E | S | T | Ghi chú xử lý |
|---|---|---|---|---|---|---|---|
| US1 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | Chuẩn hóa số điện thoại là kết quả bắt buộc của bước nạp (QT-02) nên nằm cùng story; chuẩn hóa họ tên tách riêng ở US2. |
| US2 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | Quy tắc chuẩn hóa họ tên được định nghĩa cụ thể ở FR-03, không còn mơ hồ. |
| US3 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | Công thức điểm và ngưỡng ở FR-04, QL7-03; kiểm chứng bằng 300 cặp gán nhãn tay (NFR-03). |
| US4 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | Gộp US4 + US5 của bản 1.0: xem danh sách là bước bắt buộc của xác nhận (UC5 «include» UC4); Gộp/Giữ riêng là hai nhánh của một quyết định; dùng chung một màn hình (K4) nên vẫn đủ nhỏ. |
| US5 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | – |
| US6 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | Gộp US7 + US8 của bản 1.0: tính chỉ số (UC7) chỉ có giá trị khi được xem (UC8); mức chi tiết theo đợt nạp, ngày, quy tắc. |
| US7 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | – |

### 3.1.2. Tiêu chí chấp nhận (Given – When – Then) cho story MUST

**US1 – Nạp tệp khách hàng thô và chuẩn hóa số điện thoại**
- **AC1.1 (luồng chính)**: *Given* một tệp CSV hợp lệ có cột `ho_ten` và `so_dien_thoai`, 8.000 dòng; *When* Nhân viên Marketing chọn tệp, chọn đơn vị nguồn và bấm Nạp; *Then* hệ thống tạo một đợt nạp mới (tên tệp, giá trị băm SHA-256, đơn vị nguồn, người nạp, thời điểm, `row_count` = 8.000), ghi đủ 8.000 hồ sơ thô vào `stg_customer` và báo số dòng đã nạp.
- **AC1.2 (chuẩn hóa)**: *Given* các số `+84901234567`, `84901234567`, `0901 234 567`, `0901.234.567`; *When* đợt nạp được xử lý; *Then* `phone_norm` của cả bốn dòng là `0901234567`; dòng trống được gắn `MISSING_PHONE`, dòng không quy về được mẫu `^0\d{9}$` được gắn `INVALID_PHONE`.
- **AC1.3 (ngoại lệ – thiếu cột)**: *Given* tệp thiếu cột `so_dien_thoai` (hoặc `ho_ten`); *When* bấm Nạp; *Then* hệ thống từ chối cả đợt, thông báo tên cột thiếu; `load_batch` và `stg_customer` không thay đổi.
- **AC1.4 (ngoại lệ – nạp lại)**: *Given* tệp có giá trị băm trùng với một đợt đã nạp; *When* bấm Nạp; *Then* hệ thống cảnh báo tệp đã được nạp ở đợt nào và chỉ nạp khi người dùng xác nhận.

**US3 – Phát hiện cặp nghi trùng**
- **AC3.1 (cùng số)**: *Given* 3 hồ sơ có cùng `phone_norm`; *When* Nhân viên Marketing chạy phát hiện; *Then* hệ thống tạo 2 cặp `EXACT_PHONE` ở trạng thái Chờ xử lý, mỗi cặp ghép hồ sơ nạp sớm nhất với một hồ sơ còn lại (QL7-02), kèm điểm tương đồng.
- **AC3.2 (gần giống)**: *Given* hai hồ sơ có số điện thoại khác nhau đúng một chữ số và cùng `name_key`; *When* chạy phát hiện; *Then* cặp `FUZZY` được tạo với điểm tương đồng 0,6 × 90 + 0,4 × 100 = 94 ≥ 85.
- **AC3.3 (ngoại lệ – thiếu số)**: *Given* một hồ sơ không có số điện thoại hợp lệ; *When* chạy phát hiện; *Then* hồ sơ không tham gia so khớp (QL7-04) và không có cặp nào được tạo chỉ vì họ tên giống nhau.
- **AC3.4 (không đề xuất lại)**: *Given* một cặp đã Giữ riêng; *When* chạy phát hiện lần sau; *Then* cặp đó không được tạo lại (QL7-05).

**US4 – Xem và xác nhận Gộp / Giữ riêng cặp nghi trùng**
- **AC4.1 (danh sách – UC4)**: *Given* có cặp ở trạng thái Chờ xử lý; *When* Nhân viên Marketing mở màn hình Cặp nghi trùng; *Then* danh sách sắp theo điểm tương đồng giảm dần, lọc được theo trạng thái và khoảng điểm; chọn một cặp thì thấy hai hồ sơ cạnh nhau, các trường khác nhau được đánh dấu, số điện thoại ở dạng che (QT-15).
- **AC4.2 (Gộp – UC5)**: *Given* một cặp Chờ xử lý; *When* nhân viên chọn Gộp, chọn hồ sơ gốc (và số chính nếu hai số khác nhau – QL7-07) rồi Xác nhận; *Then* `customer_clean` còn đúng một hồ sơ đang hiệu lực mang giá trị của hồ sơ gốc (trường trống được bổ sung từ hồ sơ còn lại); nếu bên kia cũng có trong `customer_clean` thì chuyển sang ngừng sử dụng (`is_active = false`, `merged_into` = hồ sơ được giữ), nếu không thì hồ sơ thô của nó được gắn vào hồ sơ được giữ (`stg_customer.customer_id`); cặp chuyển `MERGED` kèm người quyết định, thời điểm, lý do; chỉ số mức độ sạch của đợt được đo lại (UC7).
- **AC4.3 (Giữ riêng – UC5, luồng 3a)**: *Given* một cặp `FUZZY` Chờ xử lý; *When* nhân viên chọn Giữ riêng; *Then* cặp chuyển `KEEP_SEPARATE`, hai hồ sơ không đổi, cặp không được đề xuất lại và chỉ số mức độ sạch được đo lại (UC7). Với cặp `EXACT_PHONE`, hệ thống yêu cầu nhập một số điện thoại hợp lệ khác cho một hồ sơ; bỏ trống thì không cho Giữ riêng (QT-01).
- **AC4.4 (không tự động gộp – QL7-01)**: *Given* một cặp có điểm tương đồng 100 chưa ai quyết định; *When* lượt phát hiện kết thúc; *Then* cặp vẫn ở trạng thái Chờ xử lý – hệ thống không tự động gộp.

### 3.2. Use Case Diagram
File gốc: **`docs/usecase.drawio`** (ảnh: `docs/export/usecase.png`). Ranh giới hệ thống: *Hệ thống Smart CRM – Mekong Mobile · L7 Chất lượng dữ liệu khách hàng*; mọi actor nằm ngoài ranh giới; sơ đồ có khung chú thích ký hiệu.

| UC | Tên use case | Actor | Quan hệ | User Story |
|---|---|---|---|---|
| **UC1** | Nạp tệp khách hàng thô | Nhân viên Marketing; Tệp nguồn Excel/CSV | «include» UC2, UC7 | US1 |
| **UC2** | Chuẩn hóa số điện thoại và họ tên | (UC1 gọi) | – | US1, US2 |
| **UC3** | Phát hiện cặp nghi trùng | Nhân viên Marketing | – | US3 |
| **UC4** | Xem danh sách cặp nghi trùng | Nhân viên Marketing | (UC5 gọi) | US4 |
| **UC5** | Xác nhận gộp hoặc giữ riêng cặp nghi trùng | Nhân viên Marketing | «include» UC4, UC7 | US4 |
| **UC6** | Cấu hình quy tắc chất lượng dữ liệu | Quản lý cửa hàng | – | US5 |
| **UC7** | Tính chỉ số mức độ sạch dữ liệu | (UC1, UC5 gọi) | – | US6 |
| **UC8** | Xem dashboard mức độ sạch theo thời gian | Nhân viên Marketing; Quản lý cửa hàng | – | US6 |
| **UC9** | Xuất danh sách hồ sơ lỗi | Nhân viên Marketing; Quản lý cửa hàng | – | US7 |

### 3.3. Đặc tả chi tiết UC5 – Xác nhận gộp hoặc giữ riêng cặp nghi trùng
Chọn UC5 vì đây là bước duy nhất hợp nhất hoặc ngừng sử dụng hồ sơ đã làm sạch và là điểm kiểm soát "không tự động gộp" (QL7-01).

| Mục | Nội dung |
|---|---|
| **Mã / Tên** | UC5 – Xác nhận gộp hoặc giữ riêng cặp nghi trùng |
| **Actor chính** | Nhân viên Marketing |
| **Mục tiêu** | Quyết định một cặp nghi trùng là cùng một khách (Gộp) hay hai khách khác nhau (Giữ riêng) và cập nhật hồ sơ đã làm sạch tương ứng. |
| **User Story liên quan** | US4 (tiêu chí chấp nhận AC4.2 – AC4.4 trong docs/srs.md) |
| **Điều kiện trước** | Người dùng đã đăng nhập với vai trò Nhân viên Marketing; UC3 đã chạy; có ít nhất một cặp ở trạng thái Chờ xử lý. |
| **Điều kiện sau (thành công)** | Cặp ở trạng thái Gộp hoặc Giữ riêng; customer_clean được cập nhật đúng; có đủ người quyết định, thời điểm, điểm tương đồng (NFR-08); không hồ sơ nào bị xóa vật lý (QT-13); chỉ số mức độ sạch của đợt được đo lại (UC7). |
| **Điều kiện sau (thất bại)** | Dữ liệu không đổi, cặp vẫn ở trạng thái Chờ xử lý. |
| **Quy tắc liên quan** | QT-01, QT-13, QT-15, QL7-01, QL7-05, QL7-07 |

**Luồng chính (Gộp)**
1. Nhân viên Marketing mở danh sách cặp nghi trùng (UC4) và chọn một cặp ở trạng thái Chờ xử lý.
2. Hệ thống hiển thị hai hồ sơ cạnh nhau (họ tên đã chuẩn hóa, số điện thoại che theo QT-15, email, địa chỉ, ngày ghi nhận), điểm tương đồng, loại so khớp và đánh dấu các trường khác nhau.
3. Nhân viên chọn quyết định Gộp.
4. Hệ thống yêu cầu chọn hồ sơ gốc.
5. Nhân viên chọn hồ sơ gốc.
6. Hệ thống hiển thị bản xem trước hồ sơ sau gộp: giữ giá trị của hồ sơ gốc, bổ sung trường trống từ hồ sơ còn lại.
7. Nhân viên bấm Xác nhận (có thể nhập lý do).
8. Hệ thống khóa cặp để ghi và kiểm tra lại: cặp vẫn ở trạng thái Chờ xử lý; số điện thoại của hồ sơ sau gộp không trùng với hồ sơ đang hiệu lực nào khác (QT-01).
9. Trong một giao dịch, hệ thống: giữ một hồ sơ trong customer_clean – của bên được chọn làm hồ sơ gốc, hoặc của bên duy nhất đã có trong customer_clean (cặp EXACT_PHONE) – và cập nhật nó theo giá trị của hồ sơ gốc, bổ sung trường trống từ hồ sơ còn lại; nếu bên kia cũng có trong customer_clean thì chuyển hồ sơ đó sang ngừng sử dụng (is_active = false, merged_into = hồ sơ được giữ), nếu không thì gắn hồ sơ thô của bên kia vào hồ sơ được giữ; chuyển cặp sang Gộp kèm hồ sơ gốc, người quyết định, thời điểm, lý do; sau đó gọi UC7 đo lại chỉ số mức độ sạch.
10. Hệ thống báo “Đã gộp” và quay lại danh sách. Kết thúc.

**Luồng ngoại lệ (đánh số theo bước)**
- **3a.** Nhân viên chọn Giữ riêng. Riêng cặp EXACT_PHONE: hai hồ sơ cùng số không thể cùng hiệu lực (QT-01) nên hệ thống yêu cầu nhập một số điện thoại hợp lệ khác cho một hồ sơ; nếu không có, từ chối Giữ riêng và quay lại bước 3 (dữ liệu mẫu có 4 nhóm như vậy). Khi lưu, hệ thống khóa cặp và kiểm tra cặp vẫn Chờ xử lý (nếu không → 8a), chuyển cặp sang Giữ riêng, ghi người quyết định, thời điểm, lý do, không đề xuất lại cặp này (QL7-05) và gọi UC7 đo lại chỉ số; kết thúc thành công.
- **3b.** Nhân viên chọn Để sau: cặp giữ trạng thái Chờ xử lý; quay lại danh sách.
- **5a.** Hai hồ sơ có số điện thoại khác nhau: hệ thống yêu cầu chọn số chính (QL7-07); tiếp tục bước 6.
- **8a.** Cặp đã được người khác xử lý trong lúc đang xem: hệ thống báo “Cặp này đã được xử lý”, làm mới danh sách và quay lại bước 1.
- **8b.** Số điện thoại sau gộp trùng với một hồ sơ thứ ba đang hiệu lực: hệ thống từ chối gộp, hiển thị hồ sơ thứ ba và gợi ý xử lý cặp liên quan trước; quay lại bước 1.
- **9a.** Lỗi ghi CSDL: hệ thống hoàn tác toàn bộ giao dịch (ROLLBACK) và báo lỗi; cặp vẫn Chờ xử lý; quay lại bước 1.

Nơi hiển thị thông báo của từng luồng ngoại lệ: vùng thông báo của màn hình K4 (`docs/wireframe.drawio`, trang 4).

### 3.4. Danh sách yêu cầu chức năng (FR)

| Mã | Yêu cầu chức năng | MoSCoW |
|---|---|---|
| **FR-01** | Hệ thống cho phép nạp tệp CSV/Excel vào bảng tạm; mỗi lần nạp tạo một đợt nạp ghi tên tệp, giá trị băm SHA-256, đơn vị nguồn, người nạp, thời điểm và số dòng; từ chối cả đợt khi thiếu cột ho_ten hoặc so_dien_thoai (báo tên cột thiếu, bảng tạm không đổi); cảnh báo khi tệp trùng giá trị băm với một đợt đã nạp. | MUST |
| **FR-02** | Hệ thống chuẩn hóa số điện thoại về 10 chữ số bắt đầu bằng 0 (QT-02): bỏ dấu cách, dấu chấm, dấu gạch; đổi tiền tố +84 hoặc 84 thành 0; gắn mã lỗi MISSING_PHONE khi trống, INVALID_PHONE khi không quy về được mẫu `^0\d{9}$` và MISSING_NAME khi họ tên trống; ghi hồ sơ không có mã lỗi và có số chưa thuộc hồ sơ đang hiệu lực nào vào customer_clean; hồ sơ lặp không tạo hồ sơ mới mà chờ quyết định (QT-01, QL7-04). | MUST |
| **FR-03** | Hệ thống chuẩn hóa họ tên để hiển thị thống nhất (name_norm): bỏ khoảng trắng thừa, viết hoa chữ cái đầu mỗi từ, giữ nguyên dấu tiếng Việt. | SHOULD |
| **FR-04** | Hệ thống phát hiện cặp nghi trùng: tạo khóa tên không dấu, chữ thường (name_key); chỉ so sánh hai hồ sơ cùng 5 số đầu hoặc cùng 5 số cuối của số điện thoại chuẩn hóa (blocking); tính điểm tương đồng theo QL7-03; ghi cặp ở trạng thái Chờ xử lý khi cùng số điện thoại (EXACT_PHONE) hoặc điểm ≥ ngưỡng 85 (FUZZY); không đề xuất lại cặp đã Giữ riêng (QL7-05). | MUST |
| **FR-05** | Hệ thống hiển thị danh sách cặp nghi trùng sắp theo điểm tương đồng giảm dần, lọc theo trạng thái và khoảng điểm, và cho xem hai hồ sơ cạnh nhau với các trường khác nhau được đánh dấu. | MUST |
| **FR-06** | Hệ thống cho phép xác nhận Gộp (chọn hồ sơ gốc) hoặc Giữ riêng từng cặp; khi gộp, trong cùng một giao dịch, giữ đúng một hồ sơ đang hiệu lực trong customer_clean mang giá trị của hồ sơ gốc và chuyển hồ sơ còn lại sang ngừng sử dụng (hoặc gắn hồ sơ thô của nó vào hồ sơ được giữ nếu nó chưa có trong customer_clean); ghi người quyết định, thời điểm, lý do; không bao giờ tự động gộp (QL7-01). | MUST |
| **FR-07** | Hệ thống cho phép thêm, sửa, tắt quy tắc chất lượng dữ liệu (loại, trường áp dụng, trọng số, ngưỡng đạt); chỉ lưu khi tổng trọng số các quy tắc đang bật bằng 1,00. | SHOULD |
| **FR-08** | Hệ thống đánh giá các quy tắc đang bật trên từng đợt nạp và ghi số hồ sơ được kiểm, số hồ sơ đạt cho mỗi quy tắc ở hai giai đoạn: TRƯỚC (trên giá trị thô của đợt; riêng DQ-05 so theo số đã chuẩn hóa) và SAU (sau chuẩn hóa; đo lại sau mỗi lần Gộp/Giữ riêng). | MUST |
| **FR-09** | Hệ thống hiển thị dashboard: chỉ số mức độ sạch theo đợt nạp và theo ngày (TRƯỚC/SAU), phân rã theo quy tắc, số cặp nghi trùng theo trạng thái và phân bố điểm; lọc theo khoảng ngày, đơn vị nguồn, đợt nạp. | SHOULD |
| **FR-10** | Hệ thống xuất danh sách hồ sơ lỗi của một đợt nạp (kèm mã lỗi) ra tệp CSV. | COULD |
| **FR-11** | Hệ thống che số điện thoại dạng `090****567` trên mọi màn hình với vai trò không phải Quản lý hoặc Ban giám đốc (QT-15). | MUST |

---

## 4. Yêu cầu phi chức năng (mỗi yêu cầu có ngưỡng đo được)

| Mã | Nhóm | Yêu cầu (ngưỡng đo được) | Cách kiểm chứng |
|---|---|---|---|
| **NFR-01** | Hiệu năng xử lý | Nạp và chuẩn hóa tệp 8.000 dòng ≤ 60 giây; phát hiện cặp nghi trùng trên 8.000 hồ sơ ≤ 120 giây. | Đo 3 lần trên máy phát triển, lấy giá trị lớn nhất. |
| **NFR-02** | Độ chính xác chuẩn hóa | ≥ 99% số điện thoại có giá trị được chuẩn hóa đúng trên tập 200 dòng gán nhãn tay có đủ 5 dạng ghi (chuẩn, 84…, +84…, dấu cách, dấu chấm). | Kiểm thử tự động so với nhãn tay. |
| **NFR-03** | Chất lượng phát hiện trùng | Trên tập 300 cặp gán nhãn tay, ở ngưỡng 85: precision ≥ 85% và recall ≥ 80%. | Tính precision/recall; chỉnh ngưỡng nếu chưa đạt. |
| **NFR-04** | Toàn vẹn dữ liệu | 100% số điện thoại của hồ sơ đang hiệu lực trong customer_clean khớp `^0\d{9}$` và không trùng nhau (QT-01, QT-02); 0 hồ sơ bị xóa vật lý (QT-13). | Truy vấn kiểm tra sau mỗi đợt nạp. |
| **NFR-05** | Tái lập | Nạp lại cùng tệp vào CSDL mới khởi tạo với cùng cấu hình quy tắc cho kết quả giống 100% (số cặp nghi trùng, chỉ số mức độ sạch trước khi có quyết định); chỉ số của các lần đo đã có không đổi khi cấu hình quy tắc thay đổi sau đó; mọi bước ngẫu nhiên đặt seed = 42 và ghi trong README. | So sánh kết quả hai lần chạy. |
| **NFR-06** | Hiệu năng dashboard | Mỗi khung dashboard tải xong ≤ 5 giây với ≤ 24 đợt nạp. | Đo thời gian tải từng khung. |
| **NFR-07** | Bảo mật | 0 thông tin bí mật (mật khẩu, khóa) trong repo, kết nối chỉ qua .env (không commit); 100% màn hình hiển thị số điện thoại che số với vai trò không phải Quản lý/Ban giám đốc (QT-15). | Quét repo; kiểm tra giao diện theo từng vai trò. |
| **NFR-08** | Truy vết | 100% quyết định Gộp/Giữ riêng có bản ghi người thực hiện, thời điểm và điểm tương đồng. | Đối chiếu dup_candidate với thao tác. |

---

## 5. Ràng buộc và quy tắc nghiệp vụ

**Quy tắc của case study áp dụng cho L7 (trích Bảng 9.1)**

| Mã | Quy tắc | Áp dụng ở |
|---|---|---|
| **QT-01** | Số điện thoại khách hàng là duy nhất; khi số đã tồn tại, hiển thị hồ sơ có sẵn thay vì tạo hồ sơ mới. | FR-02, FR-04, FR-06; UC5 (8b) |
| **QT-02** | Số điện thoại được chuẩn hóa về 10 chữ số bắt đầu bằng 0 trước khi lưu; các dạng +84…, 84…, có dấu cách, dấu chấm đều quy về dạng chuẩn. | FR-02, US1 |
| **QT-13** | Không xóa vật lý hồ sơ khách hàng; chỉ đánh dấu ngừng sử dụng và giữ nguyên lịch sử. | FR-06, NFR-04 |
| **QT-14** | Nhân viên chỉ xem dữ liệu của đơn vị mình; quản lý xem toàn bộ đơn vị mình phụ trách. | FR-09 (lọc theo đơn vị nguồn) |
| **QT-15** | Số điện thoại hiển thị dạng che với mọi vai trò trừ Quản lý và Ban giám đốc. | FR-11, NFR-07 |

**Quy tắc riêng của luồng L7**

| Mã | Quy tắc | Áp dụng ở |
|---|---|---|
| **QL7-01** | Không tự động gộp trong mọi trường hợp (kể cả điểm 100); mọi lần gộp cần Nhân viên Marketing xác nhận. | FR-06; UC5 |
| **QL7-02** | Tạo cặp nghi trùng khi hai hồ sơ cùng số điện thoại chuẩn hóa (EXACT_PHONE) hoặc có điểm tương đồng ≥ ngưỡng (mặc định 85, khai báo trong cấu hình ứng dụng) (FUZZY). Nhóm k hồ sơ cùng số tạo k − 1 cặp, mỗi cặp ghép hồ sơ nạp sớm nhất với một hồ sơ còn lại. | FR-04 |
| **QL7-03** | Điểm tương đồng = 0,6 × độ giống số điện thoại + 0,4 × độ giống họ tên. Độ giống số điện thoại = 100 nếu bằng nhau, ngược lại là tỉ lệ giống chuỗi 10 chữ số; độ giống họ tên tính trên name_key, không phân biệt hoa/thường, không phụ thuộc thứ tự từ. | FR-04 |
| **QL7-04** | Hồ sơ không có số điện thoại hợp lệ ở lại bảng tạm với mã lỗi, không vào customer_clean và không tham gia so khớp. | FR-02, FR-10 |
| **QL7-05** | Cặp đã Giữ riêng không được đề xuất lại. | FR-04; UC5 (3a) |
| **QL7-06** | Chỉ số mức độ sạch = Σ(trọng số × tỉ lệ đạt) × 100 trên các quy tắc đang bật (tổng trọng số = 1,00); tỉ lệ đạt = số hồ sơ đạt / số hồ sơ thuộc phạm vi áp dụng của quy tắc. Quy tắc có mẫu số bằng 0 trong đợt (ví dụ tệp không có email) được tính tỉ lệ đạt = 1. Phân loại: ≥ 90 Tốt; từ 75 đến dưới 90 Chấp nhận được; dưới 75 Kém. | FR-07, FR-08, FR-09 |
| **QL7-07** | Gộp hai hồ sơ khác số điện thoại phải chọn số chính; số còn lại vẫn lưu ở hồ sơ thô và hồ sơ ngừng sử dụng (không mất thông tin). | FR-06; UC5 (5a) |

---

## 6. Bảng truy vết yêu cầu

| FR | User Story | Use Case | MoSCoW | Bảng dữ liệu | Màn hình / khung |
|---|---|---|---|---|---|
| FR-01 | US1 | UC1 | MUST | load_batch, stg_customer → dim_batch | K1 (bộ lọc Đợt nạp, Số hồ sơ được đánh giá) |
| FR-02 | US1 | UC1, UC2 | MUST | stg_customer (phone_raw, phone_norm, error_code), customer_clean | K2 (DQ-01, DQ-02 trước/sau) |
| FR-03 | US2 | UC2 | SHOULD | stg_customer (name_norm) | K4 (họ tên hai hồ sơ) |
| FR-04 | US3 | UC3 | MUST | stg_customer (name_key); dup_candidate → fact_dup_pair | K3 (số cặp, phân bố điểm) |
| FR-05 | US4 | UC4 | MUST | dup_candidate, stg_customer | K4 (danh sách cặp) |
| FR-06 | US4 | UC5 | MUST | dup_candidate, customer_clean, stg_customer | K4 (Gộp / Giữ riêng); K3 (trạng thái) |
| FR-07 | US5 | UC6 | SHOULD | dq_rule → dim_rule | K2 (trọng số, ngưỡng) |
| FR-08 | US6 | UC7 | MUST | dq_result → fact_dq_check | K1, K2 |
| FR-09 | US6 | UC8 | SHOULD | fact_dq_check, fact_dup_pair, dim_date, dim_batch, dim_rule | K1, K2, K3 |
| FR-10 | US7 | UC9 | COULD | stg_customer (error_code) | Tệp CSV hồ sơ lỗi |
| FR-11 | US4 | UC4, UC5 | MUST | customer_clean, stg_customer (số điện thoại) | K4 (số điện thoại che) |
| W1 – tự động gộp (không có FR) | US10 (bản Buổi 4) | UC5 – chỉ gộp khi có xác nhận | WON'T | dup_candidate.status chỉ đổi khi có người quyết định (decided_by) | K4 – không có nút gộp tự động hay gộp hàng loạt |

Đọc theo hàng: 11/11 FR đều có User Story, use case, bảng dữ liệu và khung màn hình; hàng WON'T ghi cách hệ thống bảo đảm điều chủ ý không làm. Đọc theo cột: UC1 – UC9 và US1 – US7 đều xuất hiện ít nhất một lần; 11/11 bảng (6 bảng tác nghiệp, 5 bảng kho) đều phục vụ ít nhất một FR. Mức MoSCoW ghi theo FR: FR-08 là MUST dù US6 là SHOULD, vì UC7 là bước bắt buộc («include») của UC1 và UC5; phần SHOULD của US6 là dashboard (FR-09).

---

## 7. Lịch sử thay đổi (1.0 Buổi 4 → 1.1 Buổi 6)

| # | Thay đổi | Lý do / căn cứ | Vị trí trong BT1 |
|---|---|---|---|
| 1 | User Story 11 → 7: gộp US4 + US5 cũ thành US4; gộp US7 + US8 cũ thành US6; US10 → WON'T W1; US11 → ràng buộc QT-15 (FR-11, NFR-07); đánh số lại US1 – US7; bỏ dẫn chiếu V4 ở story báo cáo. | Đề bài yêu cầu 5 – 7 User Story; case study ánh xạ V4 tới L6, L10, không phải L7. | 1.3, B.4 |
| 2 | FR-05, FR-08, FR-11 nâng từ SHOULD lên MUST; việc tạo name_key chuyển từ FR-03 sang FR-04; mã lỗi MISSING_NAME và việc ghi hồ sơ hợp lệ vào customer_clean ghi rõ ở FR-02. | UC4, UC7 là bước bắt buộc («include») của use case MUST (UC5; UC1, UC5) nên xếp SHOULD là mâu thuẫn; FR-11 thực hiện quy tắc bắt buộc QT-15; FR-04 (MUST) chấm điểm trên name_key nên không được phụ thuộc FR-03 (SHOULD); customer_clean.full_name là NOT NULL nên kiểm MISSING_NAME phải thuộc bước MUST. | 1.3, 1.6 |
| 3 | Cột nguồn giả định (full_name, phone, address, source, created_at) → header thật record_id, ho_ten, so_dien_thoai, email, dia_chi, ngay_tao; FR-01 kiểm cột ho_ten, so_dien_thoai. | Đối chiếu header thật của customers_raw.csv (bản Buổi 4 ghi là giả định). | 1.3, 4.1 |
| 4 | Điền tỉ lệ thiếu từng cột bằng số đo thật: so_dien_thoai 6,17%, email 44,99%, dia_chi 8,98%, ho_ten 0%, ngay_tao 0%. | Việc còn dở ghi trong báo cáo Buổi 4. | 4.1 |
| 5 | Trích mẫu ngẫu nhiên theo dòng (6.000) → trích theo cụm số điện thoại (8.000 dòng, seed 42). | Đo: mẫu cũ chỉ còn 1,64% hồ sơ lặp nên không kiểm được US3, US4. | 4.1, Hình 4.1 |
| 6 | Bỏ khóa blocking “cùng tên gọi”, giữ “cùng 5 số đầu hoặc 5 số cuối”. | Đo: khóa tên gọi (44 giá trị) thêm 639.483 phép so sánh và chỉ tìm thêm 1 cặp dương tính giả. | FR-04, 3.2 |
| 7 | Sinh cặp EXACT_PHONE theo hồ sơ nạp sớm nhất (k − 1 cặp mỗi nhóm). | Tránh cặp phụ thuộc nhau khi gộp nhóm 3 hồ sơ. | QL7-02 |
| 8 | Use Case: thêm «include» UC5 → UC7, bố trí lại thành hai cột; đổi tên UC1, UC3, UC8 theo bảng thuật ngữ (tệp khách hàng thô, cặp nghi trùng, dashboard). Đặc tả UC5: thêm dòng “User Story liên quan”; bước 8 và luồng 3a khóa cặp, kiểm tra lại trạng thái (6a cũ thành 8a, 8a cũ thành 8b); 3a gọi UC7. | Khớp bước 9 của đặc tả và bảng thuật ngữ; đủ các mục đặc tả theo đề bài; tránh hai người cùng quyết định một cặp. | 2.1, 2.2 |
| 9 | Bảng actor thêm cột “Không được làm”. | Đề bài yêu cầu nêu việc mỗi vai trò không được làm. | 1.2 |
| 10 | dq_result: bỏ pass_rate, weighted_score và “dòng tổng” (rule_id NULL); thêm measure_stage. | Lỗi lưu giá trị tính được, trộn hai mức chi tiết; cần so TRƯỚC/SAU. | 4.3 |
| 11 | dup_candidate: record_a/record_b → stg_id_a/stg_id_b (khóa ngoại tới stg_customer); bỏ phone_sim, name_sim, batch_id; thêm detected_at. | Khóa ngoại phải trỏ về một bảng xác định; tránh giá trị tính được và phụ thuộc bắc cầu. | 4.3 |
| 12 | stg_customer: flags (nhiều giá trị trong một cột) → error_code; thêm customer_id, source_record_id, created_raw. customer_clean: UNIQUE(phone) chỉ trên hồ sơ đang hiệu lực. load_batch: thêm source_unit. dq_rule: thêm updated_by, updated_at. | Đạt 1NF; truy vết hồ sơ thô → hồ sơ đã làm sạch; gộp không vi phạm QT-01; phục vụ QT-14 và SCD loại 2. | 4.3, Phụ lục A |
| 13 | Thêm kho dữ liệu dwh: dim_date, dim_batch, dim_rule (SCD loại 2), fact_dq_check, fact_dup_pair và 2 view. | Sản phẩm bắt buộc của track DA; dashboard chỉ đọc kho (NFR-06). | 4.4 |
| 14 | Quy tắc DQ ghi rõ mẫu số (phạm vi áp dụng) từng quy tắc; DQ-02 tính trên hồ sơ có số điện thoại. | Tránh phạt hai lần hồ sơ thiếu số (đã tính ở DQ-01). | 4.5 |
| 15 | Câu hỏi phân tích Q6 diễn đạt lại: số điện thoại sai dạng đã sửa được nhờ chuẩn hóa và số hồ sơ thiếu số không sửa được. | Đo: sau chuẩn hóa không còn số nào sai dạng (0 số không quy về được). | K2; data-requirements.md |
| 16 | Đổi tên tệp: data-requirement-spec.md → data-requirements.md; usecase_L7.drawio → usecase.drawio; chuyển hồ sơ sang repo dự án (thư mục docs/). | Đúng cấu trúc thư mục tối thiểu của đề bài. | Repo |
| 17 | NFR-05 bổ sung: nạp lại vào CSDL mới khởi tạo; chỉ số của lần đo đã có không đổi khi cấu hình quy tắc thay đổi. | Nạp lại cùng tệp vào CSDL đang có sẽ sinh cặp trùng giữa hai đợt; căn cứ cho SCD loại 2 của dim_rule. | 1.4, 3.2 |

**Ánh xạ User Story 1.0 → 1.1**

| Bản 1.0 (Buổi 4) | Bản 1.1 (Buổi 6) | Ghi chú |
|---|---|---|
| US1 | US1 | Giữ nguyên |
| US2 | US2 | Giữ nguyên |
| US3 | US3 | Giữ nguyên |
| US4 + US5 | US4 | Gộp: xem danh sách là bước bắt buộc của xác nhận (UC5 «include» UC4) |
| US6 | US5 | Đánh số lại |
| US7 + US8 | US6 | Gộp: tính chỉ số (UC7) phục vụ trực tiếp việc xem dashboard (UC8) |
| US9 | US7 | Đánh số lại |
| US10 | W1 (WON'T) | Chuyển vào danh sách chủ ý không làm |
| US11 | QT-15 (FR-11, NFR-07) | Yêu cầu bảo mật từ quy tắc nghiệp vụ, không phải mục tiêu của actor |
