# Smart CRM – Chất lượng dữ liệu khách hàng (L7)

**Sinh viên:** Dương Diễm My – MSSV: 2374802010318
**Track:** DA (Data Analytics)
**Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang · HK1 2026 – 2027
**Bài tập 1:** `BT1_2374802010318_DuongDiemMy.pdf` – bản nộp lại theo nhận xét chấm (21/10/2026, 9 trang); nhật ký `docs/thay-doi-thiet-ke.md`

> Đánh số mục theo checklist: mục 2 – yêu cầu môi trường (buổi 8), mục 3 – các bước dựng hệ thống, mỗi bước một lệnh (buổi 10), mục 6 – trạng thái hiện tại.

## 1. Mô tả bài toán và phạm vi

Mekong Mobile chưa có CRM. Dữ liệu khách hàng rải rác ở Excel từng cửa hàng, Zalo và sổ tay bảo hành, nên một khách có thể tồn tại nhiều lần (vấn đề V1 của case study). Đo trên `customers_raw.csv` (67.037 dòng): 18,48% hồ sơ có số điện thoại là hồ sơ lặp, 6,17% thiếu số, 28,40% ghi số sai dạng.

**Luồng L7, từ bắt đầu đến kết thúc:**

1. Nhân viên Marketing nạp tệp khách hàng thô.
2. Hệ thống chuẩn hóa số điện thoại và họ tên, rồi phát hiện cặp hồ sơ nghi trùng bằng so khớp mờ.
3. Nhân viên Marketing xác nhận Gộp hoặc Giữ riêng từng cặp.
4. Hệ thống đo chỉ số mức độ sạch TRƯỚC/SAU làm sạch và nạp kho dữ liệu.
5. Quản lý cửa hàng xem dashboard và xuất danh sách hồ sơ lỗi để cửa hàng sửa tại nguồn.

- **Làm:** nạp và chuẩn hóa (UC1, UC2); phát hiện cặp nghi trùng, xác nhận Gộp/Giữ riêng (UC3 – UC5); cấu hình quy tắc, đo chỉ số TRƯỚC/SAU (UC6, UC7); dashboard và xuất hồ sơ lỗi (UC8, UC9).
- **Không làm:**
  - Tự động gộp mà không có người xác nhận (W1).
  - Đơn hàng, bảo hành, kho; phân khúc (L1); dự báo rời bỏ (L9).
  - Gửi chiến dịch thật, SSO, triển khai máy chủ.

**Luồng chính chạy end-to-end bằng một lệnh** (README mục 3, bước 9): bước 1 – 2 và nạp kho chạy tự động; bước 3 (UC5 – Gộp/Giữ riêng) cần người quyết định, thuộc Sprint 3; bước 5 là dashboard `dashboard/report.py`.

Đặc tả đầy đủ: `docs/srs.md`.

## 2. Yêu cầu môi trường

| Thành phần | Yêu cầu | Ghi chú |
|---|---|---|
| Python | **3.11 trở lên** | pandas 3 không chạy trên 3.10 trở xuống; máy phát triển dùng 3.11 (Homebrew) |
| Thư viện | `requirements.txt` | pandas, openpyxl, rapidfuzz, SQLAlchemy, psycopg2-binary, python-dotenv, PyYAML, pytest; Streamlit, Plotly (dashboard, buổi 10) |
| CSDL | **PostgreSQL 14 trở lên**, đang chạy (macOS: `brew services start postgresql@14`). Đã chạy trên 14 (MacBook của em) và 16 (môi trường thử) | Cần CSDL `smartcrm` và một tài khoản có quyền tạo schema trong CSDL đó. Luồng chính tự tạo schema `ops`, `dwh` (DDL chạy lại an toàn). Kiểm thử tích hợp dùng CSDL riêng `smartcrm_test`. |
| Biến môi trường | `.env` (chép từ `.env.example`) | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`; `DASH_DB_USER` để trống thì dashboard dùng `DB_USER` ở chế độ chỉ đọc (TD-19). `.env` **không commit** (NFR-07). |
| Dữ liệu | `data/raw/customers_raw.csv` | Lấy trong bộ "Dataset Smart CRM" trên LMS. **Không commit** vì có dữ liệu cá nhân. |
| Cổng | 8501 còn trống | Dashboard Streamlit; đổi bằng `--server.port`. |
| Không có PostgreSQL? | `--khong-ghi-csdl` | Vẫn chạy được extract, chuẩn hóa, đo chất lượng, so khớp trong bộ nhớ, xuất CSV và báo cáo (phương án dự phòng – TD-10); dashboard thì cần kho. |

**Công nghệ:** Python 3.11 · pandas (làm sạch, đo chất lượng) · rapidfuzz (so khớp mờ) · PostgreSQL – schema `ops` (tác nghiệp) và `dwh` (kho hình sao) · SQLAlchemy + psycopg2 · Streamlit + Plotly (dashboard) · draw.io (tệp gốc `.drawio` trong `docs/`).

## 3. Các bước dựng hệ thống – mỗi bước một lệnh

Các bước dưới đây đã được thử trên bản clone mới ở môi trường thử (Linux, 24/10/2026 – nhật ký `docs/sprint2/thu-clone-moi.txt`) và trên MacBook của em (25/10/2026, clone từ GitHub); những chỗ chưa rõ tìm ra khi thử đã sửa (README mục 6.2, dòng 9). Lệnh viết cho macOS/Linux; Windows ghi chú bên cạnh. Trước bước 1, PostgreSQL phải đang chạy (README mục 2).

| # | Việc | Lệnh |
|---|---|---|
| 1 | Lấy mã nguồn | `git clone https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality.git` |
| 2 | Vào thư mục repo | `cd smartcrm-2374802010318-customer-data-quality` |
| 3 | Tạo môi trường ảo | `python3.11 -m venv .venv` |
| 4 | Kích hoạt môi trường ảo | `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`) |
| 5 | Cài thư viện | `pip install -r requirements.txt` |
| 6 | Tạo tệp cấu hình kết nối, rồi mở `.env` điền `DB_USER`, `DB_PASSWORD` (PostgreSQL cài bằng Homebrew: `DB_USER` là tên tài khoản macOS, `DB_PASSWORD` để trống) | `cp .env.example .env` |
| 7 | Tạo CSDL rỗng. Không có lệnh `createdb` thì dùng `psql -d postgres -c 'CREATE DATABASE smartcrm;'`. Báo "already exists" nghĩa là máy đã có CSDL `smartcrm` từ lần chạy trước: dữ liệu cũ làm kết quả bước 9 khác với kết quả ghi bên dưới (hoặc bị từ chối nếu đã nạp đúng tệp này – AC1.4) – chạy `dropdb smartcrm` rồi làm lại bước này | `createdb smartcrm` |
| 8 | Chép dữ liệu nguồn vào `data/raw/`. Đổi `~/Downloads/Dataset` thành thư mục em đã giải nén bộ "Dataset Smart CRM" (LMS) | `cp ~/Downloads/Dataset/customers_raw.csv data/raw/` |
| 9 | **Chạy luồng chính end-to-end:** UC1 nạp – chuẩn hóa – đo – nạp kho, rồi UC3 phát hiện cặp – nạp kho | `python -m src.pipeline --tep data/raw/customers_raw.csv` |
| 10 | Mở dashboard K1 – K3, rồi mở trình duyệt vào http://localhost:8501. Gõ đúng `python -m streamlit`: lệnh `streamlit` trần có thể chạy nhầm Python ngoài `.venv` (pyenv, conda) và báo `ModuleNotFoundError`. Lệnh giữ cửa sổ Terminal (Ctrl+C để dừng); bước 11 – 12 làm ở một tab Terminal mới: `cd` vào thư mục repo rồi `source .venv/bin/activate` | `python -m streamlit run dashboard/report.py` |
| 11 | Tạo CSDL riêng cho kiểm thử (một lần; báo "already exists" là bình thường – mỗi test tự xóa và tạo lại schema) | `createdb smartcrm_test` |
| 12 | Chạy kiểm thử – màn hình in số test pass | `python -m pytest -q` |

**Kết quả đúng của bước 9** trên `customers_raw.csv` (5 bước in ra màn hình, mã thoát 0):

- `[2/5] transform`: CLEAN 51.279 · PENDING_DUP 11.625 · ERROR 4.133.
- `[3/5] dq_evaluate`: chỉ số mức độ sạch TRƯỚC 87,20 → SAU 94,76.
- `[5/5] match`: EXACT_PHONE 11.625 · FUZZY 12.
- Đối soát staging ↔ kho: 6 dòng, tất cả ✔.

**Bước 12:** làm đúng 12 bước trên một bản clone mới, kết quả là `93 passed, 1 skipped`. Test bị bỏ qua là test hồi quy trên mẫu 8.000 dòng: nó cần tệp `data/processed/mau_cum_8000.csv`, sinh bằng lệnh ở mục "Đo NFR-01" bên dưới. Sinh mẫu xong, chạy lại thì ra `94 passed`.

Thiếu CSDL `smartcrm_test` thì 9 test tích hợp cũng tự bỏ qua (`skipped`), không báo lỗi.

**Phép thử nạp lại** (nạp lần hai không nhân đôi dòng): `python -m src.etl.load_dwh`, chạy bao nhiêu lần cũng in `+0` ở mọi bảng và đối soát vẫn khớp.

**Chạy lại riêng UC3** cho một đợt đã nạp: `python -m src.etl.match --dot 1` (TD-17).

**Đo NFR-01** trên mẫu 8.000 dòng:
1. Sinh mẫu `data/processed/mau_cum_8000.csv` (seed 42): `python notebooks/profiling_customers.py data/raw/customers_raw.csv`.
2. Chạy `python -m src.pipeline --tep data/processed/mau_cum_8000.csv` trên CSDL mới.

## 4. Cấu trúc thư mục

Thư mục ánh xạ một–một với các lớp của sơ đồ kiến trúc `docs/architecture.drawio` (Hình 3.1 BT1); xem thêm TD-06.

```
dashboard/            ① TRÌNH BÀY  report.py – dashboard K1–K3 (UC8), chỉ đọc kho                ✔ Sprint 2
                                   app.py – ứng dụng tác nghiệp K4 (UC4–UC6, UC9)               – Sprint 3
src/etl/              ② XỬ LÝ – NGHIỆP VỤ, mỗi mô-đun một nhóm FR:
  extract.py              FR-01  đọc tệp, kiểm cột, SHA-256, ghi load_batch + stg_customer        ✔ Sprint 1
  transform.py            FR-02, FR-03, FR-10  chuẩn hóa, mã lỗi, customer_clean, CSV hồ sơ lỗi   ✔ Sprint 1
  dq_evaluate.py          FR-07, FR-08  quy tắc DQ-01…06, đo TRƯỚC/SAU, dq_result                 ✔ Sprint 1
  match.py                FR-04  name_key, blocking, điểm tương đồng, dup_candidate               ✔ Sprint 2
  load_dwh.py             FR-09  nạp kho dwh theo khóa nghiệp vụ, SCD loại 2, đối soát            ✔ Sprint 2
  merge_service.py        FR-05, FR-06, FR-11  Gộp / Giữ riêng trong một giao dịch                – Sprint 3
src/pipeline.py       luồng chính theo Bảng 3.1 – UC1: extract → transform → dq_evaluate → load_dwh;
                      UC3: match → load_dwh (hai giao dịch, TD-17)
src/doc_kho.py        truy vấn chỉ đọc kho dwh và quy tắc hiển thị (QT-14, khoảng điểm) cho dashboard
src/db.py             mũi tên ② ↔ ③: SQLAlchemy + psycopg2, kết nối đọc từ .env, giao dịch
src/config.py         đọc configs/config.yaml (người dùng, vai trò, ngưỡng – không có bí mật)
sql/                  ③ LƯU TRỮ  001_ops_schema.sql (6 bảng) ✔ · 002_dwh_schema.sql (5 bảng + 2 view) ✔
                                 003_dq_rule_updated_at.sql (trigger giữ updated_at của quy tắc, TD-21) ✔
tests/                94 test (pytest): 83 unit test, 2 test hồi quy cần dữ liệu, 9 test tích hợp cần PostgreSQL
                      (fixture CSDL kiểm thử ở conftest.py)
docs/                 srs.md, data-requirements.md, thay-doi-thiet-ke.md, ra-soat-bt1.md, ai-disclosure.md,
                      5 tệp .drawio + export/*.png, sprint1/, sprint2/ (ảnh kết quả chạy, báo cáo mẫu)
notebooks/            profiling_customers.py – sinh mọi con số ở mục 4 BT1 và mẫu 8.000 dòng (seed 42)
scripts/check_env.py  kiểm tra môi trường (Buổi 2)
.github/              mẫu issue peer review (buổi 10)
data/raw, processed/  dữ liệu – KHÔNG commit · reports/ – báo cáo số đếm sinh mỗi lần chạy, KHÔNG commit
```

## 5. Tùy chọn, mã thoát và tái lập

Tùy chọn của `src.pipeline`:

| Tùy chọn | Ý nghĩa |
|---|---|
| `--tep` | Tệp `.csv` hoặc `.xlsx`; bắt buộc có cột `ho_ten`, `so_dien_thoai` |
| `--don-vi` | Đơn vị nguồn (QT-14); mặc định `TONG_HOP` |
| `--nguoi-nap` | Tên đăng nhập vai trò `MARKETING` trong `configs/config.yaml` |
| `--nap-lai` | Xác nhận nạp tệp đã từng nạp; không có cờ này thì bị từ chối (AC1.4) |
| `--khong-ghi-csdl` | Chạy thử, không ghi CSDL (so khớp vẫn chạy trong bộ nhớ) |
| `--khong-phat-hien-cap` | Chỉ chạy UC1, bỏ UC3 (match) |

Mã thoát của lệnh:

| Mã | Ý nghĩa |
|---|---|
| 0 | Thành công |
| 1 | Lỗi kỹ thuật (không đọc được tệp, không kết nối được CSDL). Mọi ghi chép của lần chạy được ROLLBACK. |
| 2 | Bị từ chối theo quy tắc nghiệp vụ (thiếu cột, tệp đã nạp, người nạp sai vai trò). Bảng tạm không đổi. |

Mỗi lần chạy ghi:
- `reports/uc1-dot-<n>-<thời điểm>.md`: chỉ có số đếm – gồm cả UC3 và bảng đối soát staging ↔ kho;
- `data/processed/ho_so_loi_dot_<n>.csv`: hồ sơ lỗi kèm lý do (FR-10).

**Tái lập (NFR-05):** mọi bước ngẫu nhiên dùng `seed = 42`. Ba lần nạp mẫu 8.000 dòng vào ba CSDL mới cho cùng một kết quả. Trên `customers_raw.csv`, kết quả là CLEAN 51.279 · PENDING_DUP 11.625 · ERROR 4.133, chỉ số 87,20 → 94,76.
- `test_hoi_quy_khop_so_lieu_bt1` kiểm các con số này bằng phần tính toán (không cần CSDL).
- `tests/test_pipeline_csdl.py` kiểm phần ghi CSDL.

**Trước khi nộp bài tập (TD-01):**
- Một tệp PDF duy nhất, đúng tên `BT<số>_2374802010318_DuongDiemMy.pdf`.
- Mở lại tệp sau khi nộp; link repo ở trang bìa bấm được.
- Repo public (hoặc đã mời giảng viên làm collaborator) và đã `git push` đủ tệp gốc.

## 6. Trạng thái hiện tại (buổi 10 – 24/10/2026)

**Sprint 2 – đã hiện thực module mở rộng của track DA:** phát hiện cặp nghi trùng (`match.py`), nạp kho dữ liệu (`load_dwh.py`, `sql/002_dwh_schema.sql`) và dashboard K1 – K3 (`dashboard/report.py`). Luồng chính chạy bằng một lệnh (mục 3, bước 9). Phạm vi đã cắt và lý do: `docs/thay-doi-thiet-ke.md` TD-14.

### 6.1 Luồng chính – kết quả quan sát trên `customers_raw.csv`

Luồng lấy từ đặc tả UC1 «include» UC7 và UC3 của BT1 (Bảng 3.1). Bước 1 – 5 chạy trong lệnh của bước 9 mục 3, chia hai giao dịch (TD-17).

| # | Bước | Mô-đun | Đầu ra quan sát được |
|---|---|---|---|
| 1 | Nạp tệp, kiểm cột, ghi bảng tạm | `extract.py` | 67.037 dòng × 6 cột → `ops.stg_customer` +67.037 |
| 2 | Chuẩn hóa số điện thoại, họ tên; phân loại | `transform.py` | CLEAN 51.279 · PENDING_DUP 11.625 · ERROR 4.133 |
| 3 | Đo 6 quy tắc TRƯỚC/SAU làm sạch | `dq_evaluate.py` | chỉ số mức độ sạch 87,20 → 94,76 (Tốt) |
| 4 | Nạp kho – dimension trước, fact sau (hết giao dịch 1) | `load_dwh.py` | `dim_batch` +1 · `dim_rule` +6 · `fact_dq_check` +12 |
| 5 | Phát hiện cặp nghi trùng, nạp kho, đối soát (giao dịch 2) | `match.py`, `load_dwh.py` | 62.904 hồ sơ có số hợp lệ · 483.124 cặp ứng viên · EXACT_PHONE 11.625 · FUZZY 12 → `fact_dup_pair` +11.637; đối soát 6/6 ✔ |
| 6 | Xem dashboard K1 – K3 | `dashboard/report.py` | 4 biểu đồ (K2 có hai, như wireframe), mỗi biểu đồ gắn một câu hỏi phân tích (Q2, Q3, Q5); thẻ chỉ số K3 trả lời Q4 |

**Đối soát staging (`ops`) ↔ kho (`dwh`)** – in ở cuối bước 5 và khi chạy `python -m src.etl.load_dwh`:

| Mục | `ops` | `dwh` | Vì sao bằng / khác |
|---|---|---|---|
| Đợt nạp | 1 | 1 | cùng GRAIN: 1 dòng = 1 đợt |
| Kết quả đo | 12 | 12 | cùng GRAIN: 1 quy tắc × 1 đợt × 1 giai đoạn × 1 lần đo |
| Cặp nghi trùng | 11.637 | 11.637 | cùng GRAIN: 1 dòng = 1 cặp |
| Hồ sơ thô ↔ mẫu số DQ-01 | 67.037 | 67.037 | khác GRAIN: kho không lưu từng hồ sơ (67.037 dòng staging → 12 dòng fact); mẫu số DQ-01 là mọi hồ sơ của đợt nên phải bằng số hồ sơ thô |
| Hồ sơ lặp ↔ cặp EXACT_PHONE chờ xử lý | 11.625 | 11.625 | QL7-02: mỗi hồ sơ lặp sinh đúng một cặp với hồ sơ nạp sớm nhất cùng số |
| Lần đo trước phiên bản quy tắc đầu tiên | 0 | 0 | phải bằng 0 (TD-16) |

Fact không mất dòng nào khi nối dimension: `fact_dq_check` tìm phiên bản quy tắc bằng LEFT JOIN và có phương án dự phòng (TD-16), `dim_batch` được nạp trước trong cùng giao dịch.

### 6.2 Checklist buổi 10

| # | Mục kiểm chứng | | Minh chứng |
|---|---|---|---|
| 1 | Module mở rộng theo track đã hiện thực và chạy được | ✔ | `match.py`, `load_dwh.py`, `sql/002_dwh_schema.sql`, `dashboard/report.py` |
| 2 | Luồng chính chạy end-to-end, không lỗi treo | ✔ | mục 3 bước 9, mã thoát 0; `docs/sprint2/ket-qua-toan-luong.png` |
| 3 | Chạy trên dữ liệu mẫu thật | ✔ | `customers_raw.csv` (67.037 dòng) và mẫu `mau_cum_8000.csv` |
| 4 | Ảnh kết quả toàn luồng trong `docs/` | ✔ | `docs/sprint2/ket-qua-toan-luong.png` và 8 ảnh khác, danh sách ở `docs/sprint2/README.md`. 4 ảnh dòng lệnh chụp trên MacBook của em (25/10/2026); 5 ảnh dashboard còn là của môi trường thử |
| 5 | ≥ 5 unit test pass, lệnh test hiện số test | ✔ | `python -m pytest -q` → `94 passed` (bản clone mới chưa sinh mẫu: `93 passed, 1 skipped`); 43 test mới cho `match.py`, `load_dwh.py`, `doc_kho.py` và luồng UC1 → UC3 |
| 6 | Có test cho trường hợp biên hoặc luồng ngoại lệ | ✔ | `test_diem_bang_dung_nguong_van_tao_cap_fuzzy`, `test_khoang_diem_k3_bien_thuoc_khoang_tren`, `test_cap_da_co_hoac_da_giu_rieng_khong_de_xuat_lai`, `test_scd2_cau_hinh_doi_ma_thoi_diem_khong_tien_len_bi_tu_choi`, `test_uc3_loi_thi_dot_nap_van_con_va_chi_lenh_chay_lai`, `test_duong_nguong_k3_dung_cho_khi_doi_nguong`, `test_ly_do_rong_dung_nguyen_nhan`, `test_sua_tay_quy_tac_khong_ghi_updated_at_van_nap_duoc` |
| 7 | Ba trạng thái đang tải · rỗng · lỗi | ✔ | `dashboard/report.py`; ảnh `dashboard-rong.png`, `dashboard-loi.png` |
| 8 | README mục 3 đủ các bước, mỗi bước một lệnh | ✔ | mục 3 |
| 9 | Đã thử clone vào thư mục mới và chạy đúng README | ✔ | Môi trường thử, 24/10/2026: CSDL mới, làm đúng 12 bước; nhật ký `docs/sprint2/thu-clone-moi.txt`; phát hiện bước 12 ghi sai kết quả mong đợi (thực tế có 1 test `skipped`) → đã sửa. **MacBook của em, 25/10/2026:** clone từ GitHub vào thư mục mới, làm theo 12 bước; phát hiện thêm 3 chỗ README chưa rõ → đã sửa: bước 10 lệnh `streamlit` trần chạy nhầm Python 3.10 của pyenv (dashboard báo `ModuleNotFoundError`) nên đổi thành `python -m streamlit`; bước 7 phải xóa CSDL cũ để kết quả bước 9 đúng như README; bước 8 thay chỗ giữ chỗ `<thư mục Dataset>` bằng đường dẫn ví dụ |
| 10 | Commit theo quy ước, tổng số commit ≥ 8 | ✔ | `git log --oneline` |

**Yêu cầu riêng của track DA:**

| Yêu cầu | Cách làm | Kiểm chứng |
|---|---|---|
| Nạp dimension bằng khóa nghiệp vụ, rồi nạp fact theo lô ngày | `dim_batch` theo `batch_id`, `dim_rule` theo `rule_code` (SCD loại 2), `dim_date` theo `date_key`; fact nạp sau, mỗi ngày đo / ngày phát hiện một lô (`_nap_theo_lo_ngay`), khóa `result_id`, `pair_id` | `src/etl/load_dwh.py` |
| Đếm dòng staging và fact, giải thích chênh lệch | bảng đối soát ở mục 6.1 | in ra mỗi lần chạy |
| ≥ 2 biểu đồ, mỗi biểu đồ một câu hỏi phân tích | K1 – Q2; K2 (tỉ lệ đạt, điểm bị mất) – Q3; K3 – Q5, thẻ K3 – Q4 (`docs/data-requirements.md` mục 8) | ảnh `dashboard-k1.png` … `k3.png` |
| Mốc tham chiếu, dòng ghi nguồn và thời điểm dữ liệu | K1: đường 90 (Tốt) và 75 (Kém); K2: vạch ngưỡng đạt từng quy tắc và đường 10 điểm (tổng điểm được mất tối đa để còn Tốt); K3: ngưỡng tạo cặp FUZZY 85. Dưới mỗi biểu đồ: bảng/view nguồn, thời điểm lần đo mới nhất, bộ đệm 60 giây | ảnh dashboard |
| Nạp lần hai không nhân đôi dòng | mọi INSERT có `ON CONFLICT` / `NOT EXISTS` theo khóa nghiệp vụ | `python -m src.etl.load_dwh` in `+0`; `test_nap_kho_lan_hai_khong_nhan_doi_dong` |
| Bộ lọc rỗng hiện câu giải thích | câu nêu đơn vị, khoảng ngày, QT-14 và việc nên làm | `test_bo_loc_rong_noi_ro_vi_sao_va_nen_lam_gi`; ảnh `dashboard-rong.png` |

**NFR-01 phần 2** – phát hiện cặp nghi trùng trên 8.000 hồ sơ ≤ 120 giây. Đo 3 lần trên mẫu `mau_cum_8000.csv` (7.506 hồ sơ có số hợp lệ, 6.911 cặp ứng viên), mỗi lần một CSDL mới:

| Môi trường đo | UC3 (match + nạp kho) | UC1 (phần 1) | Cả lệnh | Kết luận |
|---|---|---|---|---|
| Linux, Python 3.11, PostgreSQL 16 (môi trường thử, 24/10/2026) – bản clone mới | 0,7 s | 1,3 s | 2,9 s | Đạt |
| MacBook của em (macOS, Python 3.11.16, PostgreSQL 14), 25/10/2026 – bản clone mới từ GitHub | 0,4 s | 0,9 s | 2,6 s | Đạt |

Trên cả tệp 67.037 dòng: UC3 7,4 s (môi trường thử), 4,4 s (MacBook của em). Ảnh: `docs/sprint2/ket-qua-nfr01.png` (MacBook).

**NFR-06** – mỗi khung dashboard tải ≤ 5 giây với ≤ 24 đợt nạp. Đo trên môi trường thử, từ lúc mở trang tới khi đủ 4 biểu đồ K1 – K3, 3 lần, lấy giá trị lớn nhất: 4,1 s với 1 đợt; 4,1 s với 24 đợt mẫu 8.000 dòng (nạp vào một CSDL riêng để đo). Đạt, nhưng sát ngưỡng ở lần mở đầu tiên (bộ đệm rỗng) – đo lại trên MacBook.

### 6.3 Còn lại

- [x] Em chạy lại trên MacBook (25/10/2026): đẩy repo lên GitHub, clone vào thư mục mới, làm theo 12 bước mục 3, đo NFR-01 phần 2 ba lần, chạy kiểm thử – ảnh dòng lệnh trong `docs/sprint2/` là ảnh chụp trên MacBook.
- [ ] Chụp 5 ảnh dashboard trên MacBook thay ảnh của môi trường thử, đo NFR-06 trên MacBook, đánh dấu các ô kiểm chứng ở `docs/ai-disclosure.md`.
- [ ] Peer review (buổi 10): bạn cùng lớp clone repo, chạy theo README và mở issue 3 dòng (mẫu `.github/ISSUE_TEMPLATE/peer-review.md`); em sửa README theo issue.
- [ ] **NFR-03:** em tự gán nhãn 300 cặp, tính precision/recall ở ngưỡng 85 (chuyển sang Sprint 3 – TD-14).
- [ ] NFR-02: tập 200 dòng gán nhãn tay đủ 5 dạng số.
- [ ] **Sprint 3 (buổi 11 – 12):**
  - `merge_service.py` (UC5): Gộp / Giữ riêng. Sau đó K3 có thêm tỉ lệ gộp theo khoảng điểm và số cặp quyết định theo ngày (TD-20).
  - `dashboard/app.py` (K4, UC6, UC9). UC6 chỉ cho thêm quy tắc đã có cách đo trong `dq_evaluate.py`.
  - Tài khoản chỉ đọc `dash_reader`; tài khoản ứng dụng không có quyền DELETE (NFR-04).

### 6.4 Sprint 1 – buổi 8 (giữ nguyên nội dung đã nộp buổi 8)

**Sprint 1 – đã hiện thực.** Đã chạy trên MacBook của em (macOS, Python 3.11, PostgreSQL 14) ngày 21/10/2026; trước đó đã chạy thử trên Linux.

- [x] Repo: bỏ `.venv` và `.env` khỏi git; có `.gitignore`, `.env.example`; có đủ hồ sơ BT1 (`srs.md`, 5 tệp `.drawio`); nhánh `main` và `dev`.
- [x] Phản hồi BT1 đã xử lý: `docs/thay-doi-thiet-ke.md` TD-01 – TD-05; PDF đúng tên, rút từ 27 còn 13 trang.
- [x] `src/` dựng theo sơ đồ kiến trúc (TD-06).
- [x] `sql/001_ops_schema.sql`: 6 bảng schema `ops`, 8 khóa ngoại, CHECK số điện thoại, `UNIQUE(phone) WHERE is_active`.
- [x] UC1 chạy bằng một lệnh; kết quả trên `customers_raw.csv` khớp mục 4 BT1:

  | Bước | Kết quả |
  |---|---|
  | extract (FR-01) | 67.037 dòng × 6 cột, đếm ô trống từng cột |
  | transform (FR-02, FR-03) | 19.041 số sai dạng đã chuẩn hóa, 0 số không quy đổi được; 5.930 họ tên được sửa cách viết |
  | phân loại | CLEAN 51.279 → `customer_clean`; PENDING_DUP 11.625; ERROR 4.133 (MISSING_PHONE) |
  | hồ sơ lỗi (FR-10) | CSV kèm lý do |
  | dq_evaluate (FR-08) | 12 dòng `dq_result`; chỉ số **87,20 → 94,76** |

  Ảnh chụp màn hình trên MacBook của em trong `docs/sprint1/`: `moi-truong.png`, `ket-qua-pipeline.png`, `ket-qua-csdl.png`, `ket-qua-tu-choi.png`, `ket-qua-pytest.png`, `ket-qua-nfr01-a.png`, `ket-qua-nfr01-b.png`. Báo cáo của lần chạy này: `docs/sprint1/bao-cao-uc1-dot-1.md`.
- [x] Các trường hợp bị từ chối và lỗi đều có test:

  | Trường hợp | Kết quả | Test |
  |---|---|---|
  | Thiếu cột (AC1.3) | mã thoát 2 | `test_ac13_*`, `test_ma_thoat` |
  | Nạp lại cùng tệp (AC1.4) | từ chối, bảng tạm không đổi; có `--nap-lai` thì thành đợt mới, hồ sơ hợp lệ thành PENDING_DUP | `test_ac14_nap_lai_bi_tu_choi_roi_xac_nhan` |
  | Người nạp sai vai trò | từ chối | `test_chi_nhan_vien_marketing_duoc_nap_tep` |
  | Giá trị dài hơn cột của `customer_clean` | từ chối, báo số dòng (TD-11) | `test_gia_tri_qua_dai_bi_tu_choi_ca_dot` |
  | Lỗi giữa giao dịch | ROLLBACK, không còn đợt nạp dở (TD-09) | `test_loi_giua_chung_thi_rollback_ca_dot` |

- [x] 51 test pass trên môi trường thử và trên MacBook của em. Trên bản clone chưa có dữ liệu và CSDL test, 2 test hồi quy và 5 test tích hợp tự bỏ qua.

**NFR-01, phần 1** – nạp và chuẩn hóa 8.000 dòng ≤ 60 giây. Đo 3 lần trên mẫu `mau_cum_8000.csv`, mỗi lần một CSDL mới, lấy giá trị lớn nhất:

| Môi trường đo | Pipeline (extract + transform + đo) | Cả lệnh (kể cả khởi động Python) | Kết luận |
|---|---|---|---|
| Linux, Python 3.11, PostgreSQL 16 (môi trường thử, 19/10) | 1,4 s | 2,1 s | Đạt |
| MacBook của em (máy phát triển), 21/10/2026 – lớn nhất của 2 lượt × 3 lần | 1,3 s | 3,0 s | Đạt |

**Còn lại (theo thứ tự ưu tiên – TD-04, gợi ý của giảng viên cho BT2)**

- [ ] **Sprint 2 (buổi 9 – 10):**
  - `match.py` (FR-04); đo NFR-01 phần 2: phát hiện cặp trên 8.000 hồ sơ ≤ 120 giây.
  - **NFR-03:** em tự gán nhãn 300 cặp, tính precision/recall ở ngưỡng 85.
  - `load_dwh.py` + `sql/002_dwh_schema.sql` (5 bảng kho, SCD loại 2, 2 view).
- [ ] NFR-02: tập 200 dòng gán nhãn tay đủ 5 dạng số.
- [ ] **Sprint 3 (buổi 11 – 12):**
  - `merge_service.py` (UC5).
  - `dashboard/app.py` (K4, UC6, UC9) và `report.py` (K1 – K3). UC6 chỉ cho thêm quy tắc đã có cách đo trong `dq_evaluate.py`.
  - Tài khoản chỉ đọc `dash_reader`; tài khoản ứng dụng không có quyền DELETE (NFR-04).
- [x] Em chạy lại trên MacBook: đo NFR-01 phần 1, thay ảnh trong `docs/sprint1/` bằng ảnh chụp màn hình của em, đánh dấu các ô kiểm chứng trong `docs/ai-disclosure.md`.

**Ghi chú:** không dùng phương án dự phòng; CSDL vẫn là PostgreSQL. `--khong-ghi-csdl` chỉ để chạy thử khi máy chưa có PostgreSQL (TD-10).

## 7. Khai báo sử dụng công cụ AI

| Công cụ | Dùng vào việc gì | Cách tự kiểm chứng |
|---|---|---|
| Claude (Anthropic) – BT1 | Rà soát hồ sơ Buổi 4; script profiling; bản nháp mục 3, 4, 5; tệp `.drawio`, Markdown | Chạy lại script profiling với seed 42 và đối chiếu từng con số ở mục 4.1, 4.5; mở từng tệp `.drawio` để đối chiếu; tự giải thích được GRAIN, SCD loại 2 |
| Claude (Anthropic) – buổi 8 | Rút gọn PDF BT1, nhật ký TD-01 – TD-12; bản nháp DDL, `extract.py`, `transform.py`, `dq_evaluate.py`, `pipeline.py`, test, README | Theo từng phần, có ô đánh dấu: `docs/ai-disclosure.md` |
| Claude (Anthropic) – buổi 10 | Bản nháp `sql/002_dwh_schema.sql`, `match.py`, `load_dwh.py`, `doc_kho.py`, `dashboard/report.py`, `sql/003`, 43 test mới, README mục 3 và 6, TD-14 – TD-21; ảnh dashboard trong `docs/sprint2/` chụp trên môi trường thử (4 ảnh dòng lệnh là ảnh em chụp trên MacBook) | Theo từng phần, có ô đánh dấu: `docs/ai-disclosure.md` mục Sprint 2 |

## Tài liệu

| Tệp | Nội dung |
|---|---|
| `docs/srs.md` | SRS 1.2: User Story, tiêu chí chấp nhận, đặc tả UC5, FR, NFR, quy tắc, truy vết, lịch sử thay đổi |
| `docs/data-requirements.md` | Nguồn dữ liệu, số đo profiling, từ điển dữ liệu 11 bảng, quy tắc DQ, thuật toán so khớp |
| `docs/thay-doi-thiet-ke.md` | Nhật ký thay đổi thiết kế TD-01 – TD-21 (đọc lại khi chấm BT2, BT3) |
| `docs/ra-soat-bt1.md` | Tự kiểm BT1, sáu phép kiểm nhất quán, năm lỗi ERD |
| `docs/ai-disclosure.md` | Khai báo AI theo từng phần |
| `docs/*.drawio`, `docs/export/` | Use Case, kiến trúc, data flow, ERD (ops + star schema), wireframe K1 – K4 |
| `docs/sprint1/`, `docs/sprint2/` | Ảnh kết quả chạy và báo cáo mẫu của từng sprint |
