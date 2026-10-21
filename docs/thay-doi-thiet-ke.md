# Nhật ký thay đổi thiết kế

Sinh viên: Dương Diễm My – MSSV 2374802010318 · L7 – Chất lượng dữ liệu khách hàng · Track DA

Mỗi thay đổi có mã **TD-xx** để nhắc lại về sau và đủ bốn dòng: **phản hồi → quyết định → lý do → ảnh hưởng**.
Tệp này được nối tiếp ở BT2, BT3 (thêm mục mới vào cuối, không sửa mục cũ).
Các thay đổi trước BT1 (SRS 1.0 Buổi 4 → 1.1 Buổi 6, 17 thay đổi) ghi ở `docs/srs.md` mục 7.

---

## Sau phản hồi Bài tập 1 (buổi 8, ngày 19/10/2026)

Kết quả BT1: 8,5/10 (Đầy đủ 7 · Kỹ thuật 9,5 · Nhất quán 9,5 · Trình bày 7).
Giảng viên nêu 3 điểm cần khắc phục và 1 gợi ý cho BT2. Mỗi điểm có một mục dưới đây (TD-01 – TD-05).
Phần được ghi nhận là điểm tốt (star schema 2 fact dùng chung dimension, `dim_rule` SCD loại 2, GRAIN,
bốn câu lập luận có số đo, bảng truy vết 11/11 FR) **giữ nguyên**.

### TD-01  Nộp đúng định dạng: một tệp PDF tên `BT1_<MSSV>_<HoTen>.pdf`

- **Phản hồi của GV:** Em nộp file .docx, tên "BT1 Buổi 6 _..." không đúng mẫu `BT1_<MSSV>_<HoTen>.pdf`; đề yêu cầu 1 file PDF.
- **Quyết định:** SỬA.
- **Lý do:** Lỗi hình thức, không có lý do để giữ; sai tên và định dạng làm chậm việc chấm và bị trừ ở tiêu chí Trình bày.
- **Ảnh hưởng:** Xuất lại `BT1_2374802010318_DuongDiemMy.pdf` (bản rút gọn ở TD-03), lưu ở gốc repo đúng như ví dụ slide Buổi 6. README mục 5 thêm bước kiểm trước khi nộp: đúng tên tệp, một tệp PDF, mở lại được, link repo bấm được.

### TD-02  Repo phải mở được và chứa đủ tệp gốc

- **Phản hồi của GV:** Thầy không truy cập được repo `Duongmy2612/smartcrm-2374802010318-customer-data-quality` (private hoặc sai link), nên chưa kiểm được các file .drawio gốc và commit.
- **Quyết định:** SỬA.
- **Lý do:** Khi kiểm lại, em thấy có hai nguyên nhân.
  - (1) Lúc chấm, repo không mở được với tài khoản của thầy. Ngày 19/10, `git clone` không cần đăng nhập đã chạy được, tức là repo đang public.
  - (2) Quan trọng hơn: hồ sơ BT1 (`docs/srs.md`, 5 tệp `.drawio`, `notebooks/profiling_customers.py`) **chưa từng được đẩy lên**. Repo chỉ có 3 commit ngày 25/09 và chỉ có nhánh `dev`; trong đó lại có `.venv/` (23.251 tệp của môi trường ảo) và `.env` (thông tin kết nối CSDL; mật khẩu để trống). Như vậy là vi phạm checklist Buổi 2 ("không có .env trong repo", "có nhánh main và dev") và NFR-07 ("kết nối chỉ qua .env, không commit").
  - Vì vậy, dù mở được repo, thầy vẫn không thấy tệp gốc nào.
- **Ảnh hưởng:**
  - Commit `chore`: bỏ `.venv`, `.env`, `.DS_Store` khỏi repo; `.gitignore` chặn `.env`, `data/raw`, `data/processed`; `.env.example` đủ biến.
  - Commit `docs`: bổ sung hồ sơ BT1 đúng bản đã nộp (ảnh trong `docs/export/` trùng từng byte với ảnh trong bài).
  - Tạo nhánh `main` từ `dev` khi đẩy lên.
  - `.env` cũ vẫn còn trong lịch sử commit ngày 25/09 nhưng không có mật khẩu. Từ nay `.gitignore` chặn `.env`, nên mật khẩu điền sau này không bị commit.
  - Nếu sau này repo chuyển private thì mời giảng viên làm collaborator.

### TD-03  Rút gọn bản PDF; chi tiết để trong repo

- **Phản hồi của GV:** Bài dài 27 trang, gấp ba mức gợi ý; khung K4 và Phụ lục A, B nên rút gọn hoặc để trong repo.
- **Quyết định:** SỬA.
- **Lý do:** Slide Buổi 6: "Repo là nơi giữ bản gốc; PDF là bản để chấm". Phần nào đã có đầy đủ trong repo thì PDF chỉ cần dẫn đường dẫn. Riêng K4 vẫn là minh chứng cho phép kiểm 6 (mỗi luồng ngoại lệ của UC5 có chỗ hiển thị thông báo), nên giữ trong repo và giữ một câu dẫn ở mục 5.
- **Ảnh hưởng:**
  - PDF còn 13 trang (dưới một nửa bản cũ), kể cả trang bìa và phụ lục khai báo AI. Không ép xuống ít hơn vì sẽ phải thu nhỏ sơ đồ tới mức chữ trong hình không đọc được.
  - Phụ lục A chuyển sang `docs/data-requirements.md` mục 5.1, nơi đã có sẵn đủ 6 bảng.
  - Phụ lục B: B.1, B.2 và Bảng 4.2 của bản 09/10 (soi 5 lỗi ERD) chuyển sang `docs/ra-soat-bt1.md`; B.3, B.4 chuyển sang `docs/srs.md` mục 7.
  - Bảng chỉ số tính trong view (`v_rule_rate`, `v_batch_score`) và quy tắc nạp kho chuyển sang `docs/data-requirements.md` mục 5.2.
  - Khung K4 chuyển sang `docs/wireframe.drawio` trang 4 và `docs/export/wf_k4.png`.
  - Bảng thuật ngữ, FR, NFR, quy tắc nghiệp vụ viết gọn lại; câu đầy đủ ở `docs/srs.md`.
  - Bỏ Bảng 2.1 (trùng với sơ đồ Use Case và bảng truy vết); Bảng 3.1 chỉ giữ thứ tự gọi các mô-đun theo use case (Hình 3.1 dẫn chiếu tới bảng này).
  - **Không đổi** bảng, cột, FR, NFR hay quy tắc nào. SRS lên 1.2 chỉ để ghi lịch sử.

### TD-04  Thứ tự hiện thực: ưu tiên `match.py` và `load_dwh.py` cho BT2

- **Phản hồi của GV (gợi ý cho BT2):** Hiện thực trước `match.py` và `load_dwh.py`; đo lại NFR-01 và precision/recall NFR-03 trên tập 300 cặp gán nhãn.
- **Quyết định:** SỬA kế hoạch hiện thực: `match.py`, `load_dwh.py` là ưu tiên số 1 ngay sau phần nền bắt buộc của buổi 8. Thiết kế không đổi.
- **Lý do:**
  - Hai mô-đun này mang rủi ro lớn nhất. NFR-01 (phần phát hiện cặp ≤ 120 giây) và NFR-03 chỉ đo được khi `match.py` chạy. Lược đồ kho, phần được ghi nhận là điểm mạnh, chỉ có giá trị khi `load_dwh.py` nạp được dữ liệu.
  - Hai mô-đun này lại phụ thuộc phần nền: `match.py` cần `phone_norm` do `transform.py` ghi vào `stg_customer`; `load_dwh.py` cần `dq_result` do `dq_evaluate.py` ghi.
  - Vì vậy Sprint 1 làm phần nền trước, đúng nhiệm vụ track DA của buổi 8, rồi Sprint 2 dành trọn cho hai mô-đun thầy gợi ý.
- **Ảnh hưởng (kế hoạch, ghi ở README mục 6):**

  | Sprint | Buổi | Mô-đun | Đo NFR |
  |---|---|---|---|
  | 1 | 8 | `extract.py`, `transform.py`, `dq_evaluate.py`, DDL schema `ops`, `pipeline.py` | NFR-01 phần 1: nạp và chuẩn hóa 8.000 dòng ≤ 60 giây |
  | 2 | 9 – 10 | **`match.py`, `load_dwh.py`**, DDL schema `dwh` | NFR-01 phần 2: phát hiện cặp trên 8.000 hồ sơ ≤ 120 giây · **NFR-03** trên 300 cặp em tự gán nhãn |
  | 3 | 11 – 12 | `merge_service.py`, `dashboard/app.py`, `dashboard/report.py` | NFR-06, NFR-08 |

### TD-05  Tự giải thích được từng phần AI hỗ trợ soạn nháp

- **Phản hồi của GV (gợi ý cho BT2):** Em cần tự giải thích được từng phần mà AI hỗ trợ soạn nháp.
- **Quyết định:** SỬA.
- **Lý do:** Giảng viên có thể hỏi bất kỳ dòng nào; khai báo chung chung "AI hỗ trợ soạn bản nháp mục 3, 4, 5" không cho thấy em đã kiểm chứng gì.
- **Ảnh hưởng:**
  - Khai báo AI tách theo từng phần cụ thể, mỗi dòng có cột "đã kiểm chứng gì" (`docs/ai-disclosure.md`, README mục 7).
  - Mỗi mô-đun và hàm nghiệp vụ trong `src/etl/` có docstring ghi FR/QT nó thực hiện và lý do chọn cách làm.
  - Các quy tắc đã hiện thực (QT-01, QT-02, QL7-04, QL7-06, FR-03, AC1.2 – AC1.4) đều có test em tự chạy được (`pytest -q`).
  - Có test hồi quy đối chiếu kết quả với đúng các con số đã nộp ở mục 4.5 BT1 (87,20 → 94,76).

---

## Trong Sprint 1 (buổi 8, ngày 19/10/2026) – quyết định khi hiện thực

### TD-06  Giữ cấu trúc `src/etl/` 6 mô-đun theo sơ đồ kiến trúc

- **Nguồn:** Slide buổi 8 gợi ý track DA dựng `src/extract/`, `src/transform/`, `src/quality/`, `src/load/` + `pipeline.py` như repo mẫu. Checklist buổi 8 lại yêu cầu `src/` ánh xạ một–một với sơ đồ kiến trúc **đã nộp**.
- **Quyết định:** GIỮ NGUYÊN.
- **Lý do:**
  - Sơ đồ kiến trúc (Hình 3.1) và cấu trúc track DA của Buổi 2 (`src/etl/`) đã chốt `src/etl/` gồm 6 mô-đun, mỗi mô-đun một nhóm FR.
  - Bốn pha của gợi ý vẫn có đủ: extract → `extract.py`, transform → `transform.py`, quality → `dq_evaluate.py`, load → `load_dwh.py`. Hai mô-đun còn lại (`match.py`, `merge_service.py`) là nghiệp vụ riêng của L7 mà repo mẫu (L6) không có.
  - Đổi sang cấu trúc của repo mẫu sẽ làm Hình 3.1 và Bảng 3.1 không còn khớp mã nguồn.
- **Ảnh hưởng:** Không đổi sơ đồ.
  - `src/pipeline.py` hiện thực đúng dòng "UC1: extract → transform → dq_evaluate → load_dwh" của Bảng 3.1.
  - `src/db.py` là mũi tên ② ↔ ③; `sql/` là lớp ③.
  - Ghi ở README mục 4.

### TD-07  Không thêm bảng reject riêng

- **Nguồn:** Slide buổi 8 (DA): "Ghi bảng reject cho dòng không quy đổi được, kèm lý do"; repo mẫu có bảng `reject_rows`.
- **Quyết định:** GIỮ NGUYÊN thiết kế (không thêm bảng).
- **Lý do:**
  - QL7-04 đã quy định hồ sơ lỗi ở lại bảng tạm `stg_customer` kèm `error_code`; đó chính là "bảng reject" của L7. Thêm một bảng thứ hai chứa cùng các dòng đó sẽ trùng dữ liệu.
  - Lý do dạng câu chữ suy ra được từ `error_code` nên không lưu, tránh lỗi ERD "lưu giá trị tính được". Câu lý do được sinh khi xuất CSV hồ sơ lỗi (FR-10).
- **Ảnh hưởng:** `transform.py` (`LY_DO`, `xuat_ho_so_loi`) ghi `data/processed/ho_so_loi_dot_<n>.csv` có cột `ly_do`. ERD không đổi.

### TD-08  Làm rõ hai quy tắc khi hiện thực: mã lỗi chính, hồ sơ lặp và DQ-05

- **Nguồn:** Khi viết `transform.py` và `dq_evaluate.py`, có hai chỗ SRS chưa nói rõ:
  - (a) Một hồ sơ có nhiều lỗi thì cột `error_code` (chỉ một giá trị) ghi mã nào?
  - (b) Hồ sơ lỗi nhưng có số hợp lệ (MISSING_NAME) có được tính là "hồ sơ nạp sớm hơn" khi xác định hồ sơ lặp không?
- **Quyết định:** SỬA (làm rõ quy tắc; không đổi bảng, cột).
- **Lý do:**
  - (a) Thứ tự ưu tiên MISSING_PHONE > INVALID_PHONE > MISSING_NAME, vì số điện thoại là khóa so khớp và không sửa được bằng làm sạch.
  - (b) Không tính. Hồ sơ lỗi không vào `customer_clean` nên không thể là hồ sơ được giữ. Nếu tính nó, hồ sơ hợp lệ đứng sau sẽ bị treo ở PENDING_DUP mà không có hồ sơ đang hiệu lực nào để gộp vào.
  - Hệ quả cho DQ-05: "đạt" = hồ sơ có số hợp lệ và không ở trạng thái PENDING_DUP.
  - `customers_raw.csv` có 0 hồ sơ MISSING_NAME nên số đo không đổi (DQ-05 = 81,52% như BT1).
- **Ảnh hưởng:**
  - Mã nguồn: `transform.gan_ma_loi`, `transform.phan_loai`, `dq_evaluate.do_quy_tac`.
  - Test: `test_ma_loi_theo_thu_tu_uu_tien`, `test_ho_so_loi_o_lai_bang_tam_va_khong_chan_ho_so_sau`.
  - Tài liệu: `docs/data-requirements.md` mục 6 (ghi chú hiện thực).

### TD-09  Cả UC1 trong một giao dịch; đo chất lượng không chặn việc nạp

- **Nguồn:** Repo mẫu (L6) dừng pipeline khi một phép đo dưới ngưỡng. Thiết kế của em: UC1 «include» UC2, UC7.
- **Quyết định:** SỬA cách hiện thực (thiết kế không đổi):
  - extract → transform → dq_evaluate chạy trong **một** giao dịch.
  - Quy tắc dưới ngưỡng **không** làm dừng việc nạp.
- **Lý do:**
  - Lỗi ở bất kỳ bước nào thì ROLLBACK, không còn đợt nạp dở. Test `test_loi_giua_chung_thi_rollback_ca_dot` giả lập lỗi khi ghi `customer_clean` và kiểm `load_batch` không có thêm dòng nào.
  - Phân biệt hai loại: quy tắc **dưới ngưỡng** là kết quả đo, không chặn việc nạp. **Cấu hình quy tắc sai** (tổng trọng số ≠ 1,00, quy tắc chưa có cách đo) là lỗi kỹ thuật, nên ROLLBACK, mã thoát 1.
  - Với L7, kết quả đo là **sản phẩm đầu ra** (FR-08), và dữ liệu bẩn chính là đầu vào cần làm sạch. DQ-01 chắc chắn dưới ngưỡng 98% vì 6,17% hồ sơ thiếu số; nếu dừng khi dưới ngưỡng thì không bao giờ nạp được.
- **Ảnh hưởng:** `src/pipeline.py` (mã thoát 0 / 1 / 2); `tests/test_pipeline_csdl.py`; README mục 5.

### TD-10  Phương án dự phòng khi chưa có PostgreSQL: `--khong-ghi-csdl`, không đổi sang SQLite

- **Nguồn:** Slide buổi 8: SQLite thay PostgreSQL là phương án dự phòng hợp lệ.
- **Quyết định:** SỬA: thêm tùy chọn `--khong-ghi-csdl`; vẫn giữ PostgreSQL là CSDL của thiết kế.
- **Lý do:**
  - DDL dùng những tính năng PostgreSQL mà thiết kế cần: chỉ mục duy nhất từng phần `WHERE is_active` (QT-01), CHECK bằng biểu thức chính quy (QT-02), hai schema `ops`/`dwh`. SQLite không có schema và không có toán tử regex, nên sẽ phải viết thêm một bộ DDL thứ hai.
  - `--khong-ghi-csdl` vẫn chạy đủ extract, transform, dq_evaluate, xuất CSV hồ sơ lỗi và báo cáo trên mọi máy.
- **Ảnh hưởng:** `src/pipeline.py`; README mục 2, 5.

### TD-11  Kiểm độ dài trước khi ghi `customer_clean`; số điện thoại chỉ nhận chữ số ASCII

- **Nguồn:** Rà soát độc lập Sprint 1 (19/10) tìm ra hai trường hợp biên làm lệnh INSERT lỗi giữa chừng (mã thoát 1), thay vì báo rõ cho người dùng.
  - Cột `customer_clean` hẹp hơn cột `*_raw`: họ tên 120 so với 200, email 120 so với 200, địa chỉ 255 so với 300.
  - Mẫu `\d` của Python nhận cả chữ số Unicode (ví dụ `０９０…`), trong khi CHECK `^0[0-9]{9}$` của CSDL thì không.
- **Quyết định:** SỬA (không đổi bảng, cột).
- **Lý do:**
  - Từ chối cả đợt TRƯỚC khi ghi CSDL, báo rõ cột và số dòng (mã thoát 2), để cửa hàng sửa tại nguồn.
  - Không cắt bớt giá trị, vì cắt là âm thầm làm mất dữ liệu.
  - Mẫu số điện thoại dùng `[0-9]` cho khớp đúng CHECK của CSDL.
  - Trên `customers_raw.csv` không có trường hợp nào như vậy (họ tên dài nhất 21 ký tự, địa chỉ 38), nên số đo không đổi.
- **Ảnh hưởng:** `transform.kiem_do_dai_ho_so_sach`, `MAU_SO_CHUAN`; `dq_evaluate.MAU_SO_CHUAN`; test `test_kiem_do_dai_truoc_khi_ghi_customer_clean`, `test_chu_so_unicode_khong_duoc_chap_nhan`, `test_gia_tri_qua_dai_bi_tu_choi_ca_dot`.

### TD-12  Hàm chuẩn hóa đầu tiên là số điện thoại, không phải ngày

- **Nguồn:** Slide buổi 8 (DA): "Viết hàm chuẩn hoá ĐẦU TIÊN: xử lý ba định dạng ngày trong cột ngay". Ví dụ này lấy từ repo mẫu L6, nơi tệp đơn hàng `orders_2024_2026.csv` có ba định dạng ngày.
- **Quyết định:** SỬA nhiệm vụ cho đúng dữ liệu của L7.
  - Hàm chuẩn hóa đầu tiên là `transform.chuan_hoa_so_dien_thoai` (QT-02); hàm thứ hai là `transform.chuan_hoa_ho_ten` (FR-03).
  - Không viết hàm quy đổi ngày.
- **Lý do:**
  - Tệp nguồn của L7 là `customers_raw.csv`, không phải tệp đơn hàng. Cột ngày duy nhất là `ngay_tao`, đã đo ở BT1 mục 4.1: 67.037/67.037 giá trị dạng `yyyy-mm-dd` (2024-01-01 → 2026-08-28), không ô nào trống. Không có gì để quy đổi.
  - Cột "nhiều định dạng" thật của L7 là số điện thoại: 5 dạng ghi, 28,40% hồ sơ ghi số sai dạng. Số điện thoại cũng là khóa so khớp của `match.py` (Sprint 2), nên phải chuẩn hóa trước.
  - Kết quả quan sát được tương đương dòng "ngày đọc được 302/302" của ví dụ slide: "19.041 sai dạng đã chuẩn hóa · 0 không quy đổi được" (`docs/sprint1/ket-qua-pipeline.png`).
- **Ảnh hưởng:**
  - Không đổi thiết kế. `ngay_tao` giữ nguyên giá trị gốc ở `stg_customer.created_raw` (NFR-05); chỉ dùng để hiển thị "ngày ghi nhận" ở K4 (UC5) và xuất CSV hồ sơ lỗi.
  - Nếu sau này tệp của cửa hàng lẫn định dạng ngày thì thêm hàm quy đổi vào `transform.py`, kèm test, và ghi một TD mới.

---

## Nộp lại Bài tập 1 (21/10/2026)

Giảng viên cho nộp lại BT1 để chấm lại. Bản 13 trang ở TD-03 vẫn dài hơn mức gợi ý 6–9 trang.

### TD-13  Rút bản PDF nộp lại còn 9 trang

- **Phản hồi của GV:** Bài dài 27 trang, gấp ba mức gợi ý; khung K4 và Phụ lục A, B nên rút gọn hoặc để trong repo (cùng phản hồi với TD-03).
- **Quyết định:** SỬA tiếp. PDF nộp lại còn 9 trang, kể cả trang bìa và phụ lục khai báo AI. Thay ý "không ép xuống ít hơn 13 trang" của TD-03.
- **Lý do:**
  - Đề Buổi 6 ghi khung trang cho từng mục: SRS 2–3 trang, Use Case 1–2, kiến trúc 1, mô hình dữ liệu 1–2, wireframe 1. Bản 13 trang vẫn vượt mức này.
  - Lo ngại ở TD-03 là sơ đồ thu nhỏ sẽ không đọc được. Bản 9 trang xử lý lo ngại đó bằng ba cách:
    - PDF nhúng ảnh ở đúng độ phân giải của ảnh xuất trong `docs/export/`, không nén mất dữ liệu, nên phóng to vẫn đọc rõ.
    - Ảnh gốc vẫn ở `docs/export/`.
    - Tệp `.drawio` gốc vẫn ở `docs/`.
- **Ảnh hưởng:**
  - **Dàn trang:**
    - Hình và phần giải thích đặt hai cột: Hình 2.1, 3.1, 4.3, 5.1 – 5.3.
    - Hình 4.1 (data flow) và Hình 4.2 (ERD tầng tác nghiệp) đặt cạnh nhau.
  - **Bảng chuyển thành chữ:**
    - Các bảng sau của bản 13 trang viết thành đoạn văn, giữ đúng các con số cũ: bảng nguồn dữ liệu (Bảng 4.1), bảng SCD (Bảng 4.4), bảng chỉ số mức độ sạch (Bảng 4.6).
    - Bảng 5.1 của bản 13 trang viết thành phần chữ cạnh từng khung K1 – K3.
  - **Đánh số lại mục 4:**

    | Bản 9 trang | Bản 09/10 |
    |---|---|
    | 4.1 Dữ liệu nguồn, luồng dữ liệu, tầng tác nghiệp | 4.1 – 4.3 |
    | 4.2 Kho dữ liệu: Bảng 4.1 GRAIN, Bảng 4.2 từ điển dữ liệu kho | 4.4 |
    | 4.3 Quy tắc chất lượng: Bảng 4.3 | 4.5 |

    Các tài liệu khác trong repo vẫn ghi số mục theo bản 09/10.
  - **Giữ đủ trong PDF:**
    - bảng thuật ngữ có cột tên trong CSDL;
    - bảng truy vết 11/11 FR;
    - 4 câu lập luận có số đo;
    - GRAIN;
    - `dim_rule` SCD loại 2;
    - từ điển dữ liệu kho (kiểu, ràng buộc, ý nghĩa từng cột).
  - **Đối chiếu lại với đề bài BT1**, chỉ đổi cách ghi, không đổi nội dung:
    - đặc tả UC5 ghi tách các mục "Actor chính", "User Story liên quan" như đề yêu cầu;
    - tên Mục 4 ghi đúng như đề: "Mô hình dữ liệu theo chuyên ngành";
    - mục 3 ghi thêm dòng "Ngoài phạm vi" (khớp khung nét đứt trong Hình 3.1);
    - mục 5 ghi rõ mỗi khung nối về UC8 và mọi trường hiển thị là cột của kho hoặc chỉ số tính trong view.
  - **Không đổi** bảng, cột, FR, NFR, quy tắc hay con số nào. Đã đối chiếu tự động mọi con số của bản 9 trang với bản 09/10 và bản 13 trang.
  - Repo chỉ giữ một tệp `BT1_2374802010318_DuongDiemMy.pdf`: bản nộp lại 9 trang.
