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

---

## Trong Sprint 2 (buổi 10, ngày 24/10/2026) – module mở rộng track DA

Buổi 10 yêu cầu track DA nạp kho dữ liệu và dựng dashboard ≥ 2 biểu đồ, luồng chính chạy end-to-end. Các quyết định dưới đây phát sinh khi hiện thực `match.py`, `load_dwh.py`, `sql/002_dwh_schema.sql`, `dashboard/report.py` và khi ghép luồng.

### TD-14  Phạm vi Sprint 2 và phần cắt

- **Nguồn:** Slide buổi 10: "Cắt phạm vi có ghi nhận là quyết định kỹ thuật có trách nhiệm". Được cắt: màn hình thứ tư trở đi, biểu đồ thứ ba trở đi, chức năng ngoài luồng chính. Không được cắt: luồng chính, ba trạng thái, test, README mục 3. TD-04 xếp Sprint 2 gồm `match.py`, `load_dwh.py` và đo NFR-01, NFR-03.
- **Quyết định:**
  - **Làm trong Sprint 2:**
    - `match.py` (FR-04, UC3);
    - `load_dwh.py` và `sql/002_dwh_schema.sql` (FR-09; 5 bảng, 2 view);
    - `dashboard/report.py`: khung K1 – K3 (UC8), ba trạng thái, QT-14;
    - đo NFR-01 phần 2.
  - **Hoãn sang Sprint 3:**
    - `merge_service.py` (UC5 – Gộp/Giữ riêng, FR-05, FR-06, FR-11);
    - `dashboard/app.py` (K4, UC4 – UC6, UC9);
    - tài khoản chỉ đọc `dash_reader` (TD-19);
    - phần K2, K3 cần quyết định của UC5 (TD-20);
    - NFR-02 (200 dòng gán nhãn) và **NFR-03** (300 cặp gán nhãn) – TD-04 xếp NFR-03 vào Sprint 2, nay dời.
- **Lý do:**
  - UC5 cần người quyết định từng cặp nên không nằm trong lệnh chạy end-to-end. Luồng tự động (UC1 → UC3 → kho → dashboard) chạy đủ mà không cần UC5.
  - NFR-03 cần em tự gán nhãn 300 cặp bằng tay; không giao việc gán nhãn cho AI vì đó chính là phép kiểm chứng độc lập của thuật toán.
  - Dashboard K1 – K3 là phần bắt buộc của track DA; K4 là màn hình tác nghiệp, thuộc UC5.
- **Ảnh hưởng:**
  - Mọi cặp trong kho đang ở trạng thái Chờ xử lý. DQ-05 SAU dừng ở 81,52%, chỉ số mức độ sạch SAU dừng ở 94,76, cho tới khi có UC5.
  - Ngưỡng 85 chưa được kiểm chứng bằng precision/recall.
  - README mục 6.3 ghi việc còn lại.

### TD-15  `dim_date` được bổ sung ngày còn thiếu khi nạp

- **Nguồn:** `docs/data-requirements.md` mục 5.2 ghi "dim_date sinh sẵn một lần" (01/01/2024 – 31/12/2027, 1.461 dòng).
- **Quyết định:** GIỮ sinh sẵn 1.461 ngày trong `sql/002_dwh_schema.sql`. Trước khi nạp fact, `load_dwh` thêm các ngày đo, ngày phát hiện, ngày quyết định chưa có trong `dim_date` (`ON CONFLICT DO NOTHING`).
- **Lý do:** `fact_dq_check.date_key` và `fact_dup_pair.detected_date_key` là khóa ngoại tới `dim_date`. Một ngày nằm ngoài khoảng sinh sẵn (chạy sau 2027, hoặc đồng hồ máy sai) sẽ làm hỏng cả giao dịch nạp. Đây đúng là triệu chứng "số dòng fact ít hơn staging" mà slide buổi 10 nêu.
- **Ảnh hưởng:** `dim_date` vẫn là SCD loại 0: chỉ thêm, không sửa dòng cũ. Lần nạp bình thường in `dim_date (thêm ngày) +0`.

### TD-16  Thời điểm đo lấy theo đồng hồ của CSDL (lỗi hợp đồng dữ liệu khi ghép `dq_evaluate` → `load_dwh`)

- **Nguồn:** Bước 4 của sáu bước tích hợp (slide buổi 10): với mỗi chỗ đứt gãy, xác định là lỗi hợp đồng dữ liệu hay lỗi logic.
- **Vấn đề:** Hai bên hiểu khác nhau về "thời điểm", nên đây là lỗi hợp đồng dữ liệu, không phải lỗi logic.
  - Ở Sprint 1, `measured_at` do Python ghi theo giờ của máy chạy Python.
  - `dq_rule.updated_at` (= `dim_rule.valid_from`) và `load_batch.loaded_at` do PostgreSQL ghi theo múi giờ của CSDL.
  - `load_dwh` gắn mỗi lần đo với phiên bản quy tắc có `valid_from ≤ measured_at < valid_to`. Nếu giờ CSDL đi trước giờ Python, lần đo "xảy ra trước" phiên bản đầu tiên và không tìm được phiên bản. Ví dụ: CSDL đặt múi giờ +07 còn Python chạy trong container UTC, như khi đóng gói Docker ở buổi 11.
- **Quyết định:**
  - `measured_at` = `clock_timestamp()` của PostgreSQL, đọc trong cùng giao dịch. Dùng `clock_timestamp()` (giờ thật lúc đo), không dùng `now()` (giờ bắt đầu giao dịch).
  - Phòng hờ: không tìm được phiên bản bao phủ thì gán phiên bản sớm nhất của quy tắc, không làm rơi dòng fact.
  - Đối soát có thêm một dòng đếm số fact phải gán phòng hờ như vậy. Số này phải bằng 0.
- **Ảnh hưởng:** Không đổi bảng hay cột. Khi chạy `--khong-ghi-csdl` (không có kho), lần đo vẫn dùng giờ máy.

### TD-17  Luồng chính một lệnh, hai giao dịch: UC1 rồi UC3

- **Nguồn:** BT1 Bảng 3.1: UC1 nạp xong thì UC3 phát hiện cặp tự động. TD-09: cả UC1 nằm trong một giao dịch. Slide buổi 10: luồng chính chạy end-to-end, không có bước thao tác tay.
- **Quyết định:** `python -m src.pipeline --tep …` chạy hai giao dịch nối tiếp:
  - **Giao dịch 1 (UC1):** extract → transform → dq_evaluate → load_dwh.
  - **Giao dịch 2 (UC3):** match → load_dwh → đối soát.
  - **UC3 lỗi:** giao dịch 2 ROLLBACK, đợt nạp của giao dịch 1 vẫn còn. Lệnh trả mã 1 và in lệnh chạy lại riêng UC3: `python -m src.etl.match --dot <n>`.
  - `--khong-phat-hien-cap` chỉ chạy UC1.
- **Lý do:**
  - UC3 là use case riêng, không phải phần «include» của UC1.
  - Gói chung một giao dịch thì một lỗi lúc so khớp làm mất cả đợt đã chuẩn hóa và đo xong. Trên tệp đầy đủ (môi trường thử), UC1 mất khoảng 9 giây và UC3 khoảng 7 giây.
- **Ảnh hưởng:**
  - `test_uc3_loi_thi_dot_nap_van_con_va_chi_lenh_chay_lai` kiểm luồng ngoại lệ này.
  - TD-09 vẫn đúng cho UC1.

### TD-18  FUZZY chỉ so hồ sơ đại diện của mỗi số điện thoại

- **Nguồn:** `docs/data-requirements.md` mục 7, bước 2 – 6: blocking 5 số đầu/cuối; cùng số → EXACT_PHONE (k − 1 cặp); khác số và điểm ≥ 85 → FUZZY.
- **Vấn đề khi chạy trên tệp đầy đủ:** Nếu so mọi hồ sơ, số A có 2 hồ sơ và số B gần giống A sẽ sinh 2 cặp FUZZY cho cùng hai số. Đo được 21 cặp FUZZY nhưng chỉ ứng với 12 cặp số khác nhau. Marketing sẽ phải quyết định lặp cho cùng một khách.
- **Quyết định:** SỬA cách hiện thực, không đổi quy tắc.
  - FUZZY chỉ so giữa **hồ sơ đại diện** của mỗi số: hồ sơ nạp sớm nhất, cũng là hồ sơ mà các bản lặp đã ghép vào bằng cặp EXACT_PHONE.
  - Công thức điểm (QL7-03), ngưỡng 85 và blocking giữ nguyên.
- **Lý do:** Các hồ sơ cùng số đã được nối với hồ sơ đại diện bằng cặp EXACT_PHONE, nên một cặp FUZZY giữa hai đại diện đủ để Marketing thấy cả hai nhóm.
- **Ảnh hưởng:**
  - Tệp đầy đủ: FUZZY 21 → 12 cặp. Mẫu 8.000 dòng: 0 cặp FUZZY.
  - "Cặp ứng viên" in ra giờ đếm giữa hồ sơ đại diện của hai số khác nhau: 6.911 trên mẫu, 483.124 trên tệp đầy đủ. Số này khác số 11.858 đo ở BT1 (`data-requirements.md` mục 7), vì số BT1 đếm mọi cặp hồ sơ trong cùng khối, kể cả 1.501 cặp cùng số. Không sửa số đo của BT1; ghi chú ở `data-requirements.md` mục 7.
  - `test_fuzzy_chi_so_ho_so_dai_dien_cua_moi_so` giữ quyết định này.

### TD-19  Dashboard dùng kết nối chỉ đọc; tài khoản `dash_reader` để Sprint 3

- **Nguồn:** BT1 (kiến trúc, NFR-04, NFR-07): dashboard chỉ đọc schema `dwh` qua tài khoản riêng `dash_reader`.
- **Quyết định:**
  - Sprint 2: `src/db.tao_engine_chi_doc()` mở phiên PostgreSQL với `default_transaction_read_only=on`, dùng `DASH_DB_USER` nếu có trong `.env`, để trống thì dùng `DB_USER`. Mọi lệnh ghi từ dashboard bị PostgreSQL từ chối.
  - Tài khoản riêng `dash_reader` (chỉ quyền SELECT trên `dwh`) tạo ở Sprint 3, cùng việc bỏ quyền DELETE của tài khoản ứng dụng.
- **Lý do:**
  - Tạo role cần quyền quản trị PostgreSQL. Cách làm khác nhau giữa máy em (Homebrew) và máy người chấm, nên thêm bước dễ làm hỏng README mục 3.
  - Chế độ chỉ đọc của phiên chặn được ghi nhầm, nhưng **không** thay được phân quyền. Người cố ý vẫn có thể mở lại quyền ghi trong phiên.
- **Ảnh hưởng:** `.env.example` để trống `DASH_DB_USER`, có chú thích. Dashboard chỉ in loại lỗi, không in chuỗi kết nối (NFR-07).

### TD-20  Dashboard K1 – K3 so với wireframe BT1

- **Nguồn:** Wireframe K1 – K3 (`docs/export/wf_k1.png` … `wf_k3.png`). Slide buổi 10: ≥ 2 biểu đồ, mỗi biểu đồ gắn một câu hỏi phân tích, có mốc tham chiếu, dòng ghi nguồn và thời điểm dữ liệu.
- **Quyết định – giữ đúng wireframe:**
  - Ba tab K1 · K2 · K3.
  - K1: năm thẻ chỉ số, đường chỉ số mức độ sạch theo đợt nạp (SAU nét liền, TRƯỚC nét đứt), mốc 90 · Tốt và 75 · Kém, bảng các đợt nạp.
  - K2: hai biểu đồ như wireframe – tỉ lệ đạt theo quy tắc có vạch ngưỡng đạt (thanh chưa đạt tô đỏ), và điểm bị mất từng quy tắc; bảng chi tiết.
  - K3: năm thẻ (tổng, Chờ xử lý, Gộp, Giữ riêng, tỉ lệ đã xử lý); phân bố cặp theo khoảng điểm < 85 · 85 – <90 · 90 – <95 · ≥ 95.
  - Dòng ghi nguồn dưới mỗi biểu đồ.
  - Bộ lọc đơn vị nguồn theo QT-14.
- **Khác wireframe:**

  | Khung | Wireframe | Sprint 2 | Lý do |
  |---|---|---|---|
  | K2 | Biểu đồ điểm bị mất không có mốc tham chiếu | Thêm đường 10 điểm: tổng điểm được mất tối đa để đợt còn mức Tốt (≥ 90, QL7-06) | Slide buổi 10 yêu cầu mỗi biểu đồ có mốc tham chiếu |
  | K2 | Bộ lọc lần đo, loại quy tắc; ghi chú "Hiệu quả chuẩn hóa" (Q6) | Lần đo mới nhất của đợt; không lọc loại quy tắc; số liệu Q6 nằm trong báo cáo mỗi lần chạy (`reports/`) | Mỗi đợt hiện chỉ có một lần đo (đo lại khi đổi quy tắc là UC6 – Sprint 3) |
  | K3 | Số cặp theo trạng thái theo đợt; tỉ lệ gộp theo khoảng điểm; số cặp quyết định theo ngày | Một biểu đồ: số cặp theo khoảng điểm, tách EXACT_PHONE / FUZZY, thang log, mốc ngưỡng 85; trạng thái ở 5 thẻ (Q4) | Tỉ lệ gộp và ngày quyết định cần quyết định của UC5 (Sprint 3). Hiện mọi cặp đang Chờ xử lý nên tách theo trạng thái không cho thêm thông tin; tách theo loại so khớp cho thấy ngưỡng chỉ áp cho FUZZY. Thang log để 12 cặp sát ngưỡng vẫn thấy được cạnh 11.620 cặp ≥ 95 |
  | Chung | Người xem là người đăng nhập | Chọn người xem ở thanh bên (hoặc `?nguoi_xem=` trên địa chỉ trang) để áp QT-14 | Đăng nhập/SSO ngoài phạm vi (BT1 mục 1); đây là mô phỏng vai trò, không phải xác thực |

- **Ảnh hưởng:** Sprint 3 bổ sung phần K3 còn thiếu sau khi có `merge_service.py`; README mục 6.3.

### TD-21  `dq_rule.updated_at` tự cập nhật khi quy tắc bị sửa (trigger)

- **Nguồn:** Rà soát độc lập trước khi nộp. Sửa ngưỡng DQ-06 bằng một câu UPDATE không ghi `updated_at` (như sửa tay bằng psql) thì lần nạp kho sau dừng với lỗi "updated_at … không sau valid_from". Mọi lần chạy luồng chính sau đó ROLLBACK cả UC1.
- **Quyết định:** Thêm migration `sql/003_dq_rule_updated_at.sql`.
  - Trigger BEFORE UPDATE trên `ops.dq_rule`: câu UPDATE không tự ghi `updated_at` thì trigger đặt `updated_at = clock_timestamp()`.
  - Giữ lỗi trong `quyet_dinh_scd2` cho trường hợp `updated_at` bị ghi lùi về trước.
  - Không sửa `sql/001_ops_schema.sql` đã nộp ở Sprint 1.
- **Lý do:**
  - `valid_from` của phiên bản mới phải là thời điểm cấu hình đổi, tức là trước mọi lần đo dùng cấu hình mới.
  - Nếu lấy thời điểm nạp kho làm `valid_from`, lần đo ngay sau khi sửa sẽ bị gắn nhầm phiên bản cũ: trong UC1, việc đo chạy trước bước nạp kho, cùng một giao dịch.
  - Trigger ghi đúng thời điểm sửa, cùng đồng hồ với `measured_at` (TD-16). UC6 (Sprint 3) vẫn ghi `updated_at` như thiết kế.
- **Ảnh hưởng:**
  - Không đổi bảng hay cột.
  - `CREATE OR REPLACE TRIGGER` cần PostgreSQL 14 trở lên, đúng yêu cầu ở README mục 2.
  - Test `test_sua_tay_quy_tac_khong_ghi_updated_at_van_nap_duoc` (không có trigger thì test này lỗi); test DDL kiểm có trigger.

---

## Bài tập 2 (buổi 12, ngày 31/10/2026) – hiện thực so với thiết kế BT1

Đề BT2 yêu cầu ghi **mọi sai lệch so với thiết kế BT1, mỗi thay đổi ba dòng: thay đổi gì · vì sao · ảnh hưởng tới
thành phần nào**. TD-01 – TD-21 ở trên vẫn đúng. Các mục dưới đây phát sinh khi đối chiếu repo với bảng tiêu chí
kỹ thuật của BT2 (đề mục 4.2: C1 – C7, D1 – D4).

| Mã | Tóm tắt | Mục BT2 liên quan |
|---|---|---|
| TD-22 | Tách mọi lệnh đọc/ghi CSDL ra pha load `src/etl/load_ops.py`; E / T / quality chỉ còn hàm thuần | C2 (CỐT LÕI), D1 |
| TD-23 | Bảng reject là view `ops.v_reject` có cột `ly_do` viết thành câu | D3 |
| TD-24 | Sáu hàm kiểm chất lượng riêng (DQ-01 … DQ-06), mỗi hàm trả về số dòng lỗi và tỉ lệ lỗi | D2 |
| TD-25 | Chạy lại cùng tệp: cảnh báo AC1.4, không tạo đợt mới, mọi bảng +0, mã thoát 0 | C5 (CỐT LÕI) |
| TD-26 | Dữ liệu mẫu giả `data/mau/` (414 dòng, seed 42) được commit; README chạy trên dữ liệu mẫu | C1 (CỐT LÕI), TP4 |
| TD-27 | Phạm vi BT2: hoãn UC5 Gộp/Giữ riêng, K4, `dash_reader`, NFR-02, NFR-03, Docker sang Giai đoạn 3 | Phạm vi đề mục 1 |

### TD-22  Tách pha load: `src/etl/load_ops.py` giữ mọi lệnh đọc/ghi schema ops

- **Thay đổi gì:** Các hàm có `conn` trong `extract.py` (`tim_dot_cung_tep`, `ghi_dot_nap`, `ghi_ho_so_tho`),
  `transform.py` (`lay_so_dang_hieu_luc`, `ghi_ket_qua_chuan_hoa`, `ghi_customer_clean`), `dq_evaluate.py`
  (`khoi_tao_quy_tac`, `doc_quy_tac_dang_bat`, `ghi_ket_qua`) và phần CSDL của `match.phat_hien_cap` chuyển sang
  `src/etl/load_ops.py`. `transform.xuat_ho_so_loi` tách hai: `transform.bang_ho_so_loi` (lập bảng, thuần) và
  `load_ops.xuat_csv_ho_so_loi` (ghi tệp). Thứ tự gọi UC3 chuyển vào `src/pipeline.chay_uc3`; lệnh chạy lại riêng
  UC3 đổi từ `python -m src.etl.match --dot 1` thành `python -m src.pipeline --dot 1`.
- **Vì sao:** Đề BT2 kiểm C2 bằng cách "mở tệp transform và kiểm tra ranh giới lớp – không có dấu vết của lớp khác
  lẫn vào", và D1 "ba pha tách ở ba nơi". Ở Sprint 1 – 2, mỗi mô-đun có một phần "đọc / ghi CSDL" ở cuối tệp
  (quy ước ghi ở `src/etl/__init__.py`), nên `transform.py` vẫn `import sqlalchemy` và có câu `INSERT INTO
  ops.customer_clean`. Theo cách chấm của BT2, đó là lớp load lẫn vào pha transform.
- **Ảnh hưởng:**
  - Pha E = `extract.py`; pha T = `transform.py`, `dq_evaluate.py`, `match.py`; pha L = `load_ops.py`,
    `load_dwh.py`. Chỉ `src/pipeline.py` gọi cả ba pha.
  - `tests/test_ranh_gioi_lop.py` (11 test, đọc mã bằng `ast`) giữ ranh giới: E/T không import `sqlalchemy`,
    `src.db` và không có câu SQL; L không gọi E/T; dashboard không gọi `src/etl`.
  - Không đổi bảng, cột, quy tắc hay con số nào: 95 test cũ vẫn PASS sau khi đổi tên hàm trong test.
  - TD-06 (giữ `src/etl/`, mỗi mô-đun một nhóm FR) vẫn đúng: thêm một mô-đun, không đổi thư mục.

### TD-23  Bảng reject: view `ops.v_reject` (bổ sung TD-07)

- **Thay đổi gì:** Migration `sql/004_v_reject.sql` tạo view `ops.v_reject`: hồ sơ `status = 'ERROR'` của
  `ops.stg_customer` kèm `row_no`, giá trị gốc, `error_code` và cột `ly_do` viết thành câu cho cửa hàng đọc.
  Hàm đọc: `load_ops.doc_reject`.
- **Vì sao:** D3 yêu cầu "có bảng reject và có dòng trong đó, lý do viết cho người đọc". TD-07 đã quyết định
  không lưu bảng thứ hai (tránh trùng dữ liệu, tránh lưu giá trị tính được), nên lý do trước đây chỉ có trong
  tệp CSV. View giữ đúng TD-07 (không lưu thêm gì) mà vẫn cho xem bảng reject ngay trong CSDL.
- **Ảnh hưởng:** ERD không đổi (view không phải bảng). Ba câu lý do viết ở hai nơi (`transform.LY_DO` cho CSV và
  `sql/004`), `test_ly_do_trong_view_reject_khop_transform` giữ hai nơi khớp nhau.
  `test_ddl_chay_lai_khong_loi` kiểm thêm schema `ops` có 1 view.

### TD-24  Sáu hàm kiểm chất lượng thay cho một hàm nhiều nhánh

- **Thay đổi gì:** `dq_evaluate.do_quy_tac` (một hàm, 6 nhánh `if/elif`) tách thành 6 hàm
  `kiem_dq01_so_dien_thoai_khong_trong` … `kiem_dq06_email_dung_mau`, đăng ký trong `HAM_KIEM`; `do_quy_tac`
  chỉ tra bảng `HAM_KIEM`. `KetQua` có thêm `so_loi` (số dòng lỗi) và `ti_le_loi`. Pipeline in thêm cột
  "Dòng lỗi SAU (tỉ lệ lỗi)"; báo cáo `reports/` có thêm cột này.
- **Vì sao:** D2 yêu cầu "≥ 5 hàm kiểm chất lượng, mỗi hàm trả về số đo được" và ví dụ ở đề mục 2.1 nói rõ "mỗi
  hàm trả về số dòng lỗi và tỉ lệ lỗi". Công thức, phạm vi áp dụng (mẫu số) và ngưỡng của từng quy tắc giữ
  nguyên như `docs/data-requirements.md` mục 6.
- **Ảnh hưởng:** `src/etl/dq_evaluate.py`, `src/pipeline.py` (in bảng). Quy tắc mới ở UC6 phải có hàm kiểm trong
  `HAM_KIEM` (thay câu "đã có cách đo trong dq_evaluate.py"). Test mới:
  `test_sau_ham_kiem_tra_ve_so_dong_loi_va_ti_le_loi`, `test_dq04_bien_2_va_120_ky_tu`.

### TD-25  Chạy lại cùng tệp: cảnh báo AC1.4, mọi bảng +0, mã thoát 0 (thay "từ chối, mã thoát 2")

- **Thay đổi gì:** Trước đây chạy lại `python -m src.pipeline --tep <cùng tệp>` thì in `TỪ CHỐI: Tệp này đã được nạp…`
  và trả mã thoát 2. Nay lệnh in `CẢNH BÁO (AC1.4): tệp này đã nạp ở đợt n → không tạo đợt mới, không ghi lại hồ sơ`,
  bỏ qua bước 2 – 3, vẫn chạy nạp kho và UC3 cho đợt n (đều theo khóa nghiệp vụ nên +0), in bảng số dòng 8 bảng
  đích trước → sau, rồi trả mã thoát 0. Muốn nạp thành đợt mới vẫn dùng `--nap-lai` như cũ. Mọi lần chạy đều in
  bảng số dòng bảng đích.
- **Vì sao:**
  - C5 (CỐT LÕI) kiểm "chạy lại lần thứ hai **không lỗi** và không nhân đôi dữ liệu". Mã thoát 2 kèm chữ "TỪ CHỐI"
    dễ bị đọc là lỗi, dù dữ liệu không nhân đôi.
  - AC1.4 chỉ yêu cầu "cảnh báo tệp đã được nạp ở đợt nào và chỉ nạp khi người dùng xác nhận", không yêu cầu báo
    lỗi. Cách mới vẫn cảnh báo, vẫn không nạp khi chưa xác nhận.
  - Nếu lần trước UC3 lỗi (TD-17), lần chạy lại tự làm nốt phần còn thiếu thay vì bắt người dùng nhớ lệnh khác.
- **Ảnh hưởng:** `src/pipeline.py` (`_tep_da_nap`, `_in_bang_dich`), `src/etl/load_ops.py`
  (`dem_dong_bang_dich`). Mã thoát 2 nay chỉ còn cho dữ liệu sai thật (thiếu cột, người nạp sai vai trò, giá trị
  quá dài, đợt không tồn tại). Test: `test_ac14_chay_lai_cung_tep_canh_bao_va_khong_nhan_doi` (thay
  `test_ac14_nap_lai_bi_tu_choi_roi_xac_nhan`), `test_chay_lai_bang_lenh_tra_ma_0_va_khong_nhan_doi`.

### TD-26  Dữ liệu mẫu giả trong repo: `data/mau/`

- **Thay đổi gì:** `scripts/sinh_du_lieu_mau.py` (chỉ dùng thư viện chuẩn, `random.Random(42)`) sinh
  `data/mau/customers_mau.csv` – 414 dòng giả cùng 6 cột với `customers_raw.csv`, có đủ 5 dạng ghi số, hồ sơ lặp,
  cặp số gần giống, thiếu số, số sai, thiếu tên, email sai – và `data/mau/customers_thieu_cot.csv` (thiếu cột
  `so_dien_thoai`) để thử AC1.3. Hai tệp được commit. README mục 3 chạy trên dữ liệu mẫu; dữ liệu thật 67.037 dòng
  là bước tùy chọn.
- **Vì sao:** C1 (CỐT LÕI) và TP4 yêu cầu người khác dựng lại được "từ trạng thái ban đầu theo đúng README, không
  cần can thiệp ngoài hướng dẫn" và "có dữ liệu mẫu để hệ thống không lên trống trơn". `customers_raw.csv` lấy từ
  LMS và không commit (`.gitignore`), nên trước đây bước 8 cần một tệp nằm ngoài repo. Dữ liệu mẫu là dữ liệu giả,
  không có dữ liệu cá nhân nên commit được.
- **Ảnh hưởng:** README mục 3, 5; `test_du_lieu_mau_ra_dung_so_lieu_readme` kiểm đúng các số README ghi;
  `test_tep_mau_sinh_lai_dung_tung_byte` kiểm script sinh lại đúng tệp đã commit (NFR-05). Mọi số đo của BT1 và
  Sprint 1 – 2 trên dữ liệu thật giữ nguyên.

### TD-27  Phạm vi BT2 và phần chuyển sang Giai đoạn 3

- **Thay đổi gì:** Không làm trong BT2, chuyển sang Giai đoạn 3 (BT3, buổi 13 – 16):
  - `merge_service.py` (UC5 Gộp/Giữ riêng) và `dashboard/app.py` (K4, UC6, UC9) – TD-14 xếp vào Sprint 3;
  - tài khoản `dash_reader` và bỏ quyền DELETE của tài khoản ứng dụng (TD-19);
  - NFR-02 (200 dòng gán nhãn), NFR-03 (300 cặp gán nhãn), NFR-06 đo trên MacBook;
  - Dockerfile / docker-compose.
- **Vì sao:**
  - Đề BT2 mục 1: "làm thừa không được cộng điểm"; module cốt lõi của track DA là pipeline E/T/L, module mở rộng là
    kho + dashboard ≥ 2 biểu đồ. Cả hai đã chạy. Slide buổi 12: thiếu thời gian thì ưu tiên bốn mục CỐT LÕI,
    thêm tính năng là việc ít điểm nhất.
  - UC5 cần người quyết định từng cặp nên không nằm trong luồng tự động (TD-14).
  - Docker: môi trường thử không tải được ảnh `postgres`, `python` từ registry nên không kiểm chứng được tệp
    Dockerfile. Không đưa vào repo tệp chưa chạy thử; đề ghi đây là bước chuẩn bị cho BT3.
- **Ảnh hưởng:** Mọi cặp trong kho vẫn ở trạng thái Chờ xử lý; DQ-05 và chỉ số SAU dừng ở mức trước UC5 (dữ liệu
  thật 94,76; dữ liệu mẫu 95,79). README mục 8 ghi việc còn lại.
