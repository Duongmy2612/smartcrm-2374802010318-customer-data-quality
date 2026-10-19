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
