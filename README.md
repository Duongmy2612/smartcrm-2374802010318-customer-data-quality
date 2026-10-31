# Smart CRM – Chất lượng dữ liệu khách hàng (L7)

**Sinh viên:** Dương Diễm My – MSSV 2374802010318 · **Track:** DA (Data Analytics)
**Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang · HK1 2026 – 2027
**Bài tập 2 (buổi 12):** tag `v0.2` · báo cáo `BT2_2374802010318_DuongDiemMy.pdf` (nộp trên VLU E-learning)
**Bài tập 1:** `BT1_2374802010318_DuongDiemMy.pdf` (bản nộp lại 21/10/2026)

## 1. Hệ thống làm gì

Mekong Mobile chưa có CRM nên một khách hàng có thể nằm ở nhiều tệp, với số điện thoại ghi theo nhiều kiểu.
Hệ thống nạp một tệp khách hàng thô và chuẩn hóa số điện thoại, họ tên. Hồ sơ không dùng được bị loại vào bảng
reject kèm lý do viết thành câu. Hệ thống đo 6 quy tắc chất lượng TRƯỚC/SAU làm sạch, rồi phát hiện cặp hồ sơ
nghi trùng. Mọi bước chạy bằng **một lệnh** (pipeline E → T → L) và nạp vào kho dữ liệu hình sao trên PostgreSQL.
Dashboard Streamlit đọc kho (chỉ đọc) và vẽ 4 biểu đồ, mỗi biểu đồ trả lời một câu hỏi phân tích.

Phạm vi và lý do: `docs/srs.md` (đặc tả), `docs/thay-doi-thiet-ke.md` (TD-01 – TD-31, mọi sai lệch so với BT1).

## 2. Yêu cầu môi trường

| Thành phần | Phiên bản | Ghi chú |
|---|---|---|
| Python | **3.11 trở lên** (macOS: `python3.11 --version` · Windows: `py -3.11 --version`) | pandas 3 không chạy trên 3.10 trở xuống. Đã chạy trên 3.11 (MacBook, Linux) và 3.13 (Linux) |
| PostgreSQL | **14 trở lên**, đang chạy | macOS: `brew services start postgresql@14` · Windows: trình cài EDB, dịch vụ tự chạy cùng Windows, đăng nhập bằng tài khoản `postgres` + mật khẩu đặt khi cài. Đã chạy trên 14 (MacBook) và 16 (Linux) |
| Thư viện | `requirements.txt` (mọi gói ghi `==`) | pandas, rapidfuzz, SQLAlchemy, psycopg2-binary, python-dotenv, PyYAML, openpyxl, pytest, streamlit, plotly |
| Biến môi trường | `.env` chép từ `.env.example` | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_NAME_TEST`, `DASH_DB_USER`, `DASH_DB_PASSWORD`. `DB_USER` để trống = tài khoản hệ điều hành (đúng mặc định PostgreSQL Homebrew – TD-31); Windows điền `DB_USER=postgres` và `DB_PASSWORD`. `.env` không commit (NFR-07) |
| Dữ liệu | **có sẵn trong repo**: `data/mau/` | Dữ liệu giả 414 dòng (seed 42) và 3 tệp lỗi để thử C7, sinh bằng `scripts/sinh_du_lieu_mau.py`. Dữ liệu thật 67.037 dòng (LMS) là tùy chọn – mục 6 |
| Cổng | 8501 còn trống | dashboard (`.streamlit/config.toml`; đổi bằng `--server.port`) |

## 3. Cài đặt và chạy – mỗi bước một lệnh

macOS và Windows cùng 12 bước, cùng số thứ tự (mục 5 tra kết quả đúng theo số bước). Chạy từ một thư mục trống,
PostgreSQL phải đang chạy. Mẹo: thêm `--depth 1` vào lệnh ở bước 1 để tải nhanh hơn (lịch sử repo còn thư mục
`.venv` cũ, khoảng 150 MB).

### 3.1. macOS (MacBook) – Terminal

Chuẩn bị một lần: cài [Homebrew](https://brew.sh), rồi `brew install python@3.11 postgresql@14` và
`brew services start postgresql@14`. Terminal báo `command not found: createdb` thì chạy
`echo 'export PATH="$(brew --prefix postgresql@14)/bin:$PATH"' >> ~/.zshrc` rồi mở Terminal mới.

| # | Việc | Lệnh |
|---|---|---|
| 1 | Lấy mã nguồn đúng tag nộp bài | `git clone --branch v0.2 https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality.git` |
| 2 | Vào thư mục repo | `cd smartcrm-2374802010318-customer-data-quality` |
| 3 | Tạo môi trường ảo. Máy không có lệnh `python3.11` thì dùng `python3 -m venv .venv`, với điều kiện `python3 --version` từ 3.11 trở lên (macOS: `python3` có sẵn của Apple là 3.9 – không dùng được) | `python3.11 -m venv .venv` |
| 4 | Kích hoạt môi trường ảo | `source .venv/bin/activate` |
| 5 | Cài thư viện | `pip install -r requirements.txt` |
| 6 | Tạo tệp cấu hình. PostgreSQL cài bằng Homebrew: **không cần sửa gì** (`DB_USER` trống = tài khoản macOS). PostgreSQL có tài khoản/mật khẩu riêng thì điền `DB_USER`, `DB_PASSWORD` trong `.env` | `cp .env.example .env` |
| 7 | Tạo CSDL rỗng (báo "already exists" thì `dropdb smartcrm` rồi chạy lại bước này) | `createdb smartcrm` |
| 8 | **Chạy luồng chính end-to-end** trên dữ liệu mẫu: extract → transform → đo chất lượng → load ops → nạp kho → phát hiện cặp → đối soát | `python -m src.pipeline --tep data/mau/customers_mau.csv` |
| 9 | **Chạy lại lần hai** đúng lệnh trên – không lỗi, không nhân đôi | `python -m src.pipeline --tep data/mau/customers_mau.csv` |
| 10 | Mở dashboard rồi vào http://localhost:8501 (giữ cửa sổ này; bước 11 – 12 làm ở tab Terminal mới, `cd` vào repo và `source .venv/bin/activate`) | `python -m streamlit run dashboard/report.py` |
| 11 | Tạo CSDL riêng cho kiểm thử (một lần) | `createdb smartcrm_test` |
| 12 | **Chạy bộ kiểm thử** | `python -m pytest -q` |

Linux: làm như macOS. PostgreSQL trên Linux thường bắt đăng nhập bằng mật khẩu: ở bước 6 điền `DB_USER`,
`DB_PASSWORD`; bước 7 và 11 dùng `createdb -h localhost -U postgres smartcrm` (và `smartcrm_test`).

### 3.2. Windows 10/11 – PowerShell

Chuẩn bị một lần:

- Python 3.11 trở lên từ [python.org](https://www.python.org/downloads/windows/) – khi cài, đánh dấu **Add python.exe to PATH**.
- PostgreSQL 14 trở lên từ [trình cài EDB](https://www.postgresql.org/download/windows/) – nhớ mật khẩu đặt cho tài khoản `postgres`; dịch vụ tự chạy cùng Windows.
- [Git for Windows](https://git-scm.com/download/win).
- Mỗi cửa sổ PowerShell mới: cho dùng được lệnh `createdb`, `psql` (thay `16` bằng phiên bản PostgreSQL đã cài):
  `$env:Path += ";C:\Program Files\PostgreSQL\16\bin"`

| # | Việc | Lệnh |
|---|---|---|
| 1 | Lấy mã nguồn đúng tag nộp bài | `git clone --branch v0.2 https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality.git` |
| 2 | Vào thư mục repo | `cd smartcrm-2374802010318-customer-data-quality` |
| 3 | Tạo môi trường ảo (máy chỉ có Python 3.12/3.13 thì `py -3.12` / `py -3.13`) | `py -3.11 -m venv .venv` |
| 4 | Kích hoạt môi trường ảo. Lệnh đầu chỉ cho phép chạy script kích hoạt trong cửa sổ này; dùng cmd thì gõ `.venv\Scripts\activate.bat` | `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force; .venv\Scripts\Activate.ps1` |
| 5 | Cài thư viện | `pip install -r requirements.txt` |
| 6 | Tạo tệp cấu hình; Notepad mở ra thì điền `DB_USER=postgres` và `DB_PASSWORD=<mật khẩu đặt khi cài PostgreSQL>`, lưu lại | `copy .env.example .env; notepad .env` |
| 7 | Tạo CSDL rỗng, bảng mã UTF-8 (hỏi mật khẩu `postgres`; báo "already exists" thì `dropdb -U postgres smartcrm` rồi chạy lại) | `createdb -U postgres -E UTF8 -T template0 smartcrm` |
| 8 | **Chạy luồng chính end-to-end** trên dữ liệu mẫu (như bước 8 của macOS) | `python -m src.pipeline --tep data/mau/customers_mau.csv` |
| 9 | **Chạy lại lần hai** đúng lệnh trên – không lỗi, không nhân đôi | `python -m src.pipeline --tep data/mau/customers_mau.csv` |
| 10 | Mở dashboard rồi vào http://localhost:8501 (Windows hỏi tường lửa thì bấm Allow; giữ cửa sổ này, bước 11 – 12 làm ở cửa sổ PowerShell mới: `cd` vào repo, chạy lệnh `$env:Path` ở trên và lệnh bước 4) | `python -m streamlit run dashboard/report.py` |
| 11 | Tạo CSDL riêng cho kiểm thử (một lần) | `createdb -U postgres -E UTF8 -T template0 smartcrm_test` |
| 12 | **Chạy bộ kiểm thử** | `python -m pytest -q` |

Các lệnh Windows soạn theo cách cài chuẩn ở trên. Phần khác macOS ở mã nguồn – đăng nhập bằng tài khoản
`postgres` có mật khẩu (kể cả mật khẩu có ký tự đặc biệt) và CSDL tạo bằng UTF-8 – đã chạy thử trên Linux: luồng
chính, chạy lại +0, `139 passed, 2 skipped`. Chưa chạy trên máy Windows thật.

### 3.3. Không có PostgreSQL

`python -m src.pipeline --tep data/mau/customers_mau.csv --khong-ghi-csdl` vẫn chạy extract,
transform, đo chất lượng và so khớp trong bộ nhớ (TD-10); bước 9, 10 cần CSDL.

## 4. Chạy kiểm thử

```
python -m pytest -q          # cả bộ; thêm -rs để xem lý do test bị bỏ qua
```

Cuối kết quả có bảng số test PASS theo **ba loại của đề BT2** (đánh dấu bằng marker trong `pytest.ini`):

| Loại | Ví dụ | Kiểm gì |
|---|---|---|
| 1. Luồng đúng | `tests/test_du_lieu_mau.py::test_du_lieu_mau_ra_dung_so_lieu_readme` | tệp mẫu đúng định dạng → nạp đủ 414 dòng, ra đúng các số ở mục 5 |
| 2. Giá trị biên | `tests/test_match.py::test_diem_bang_dung_nguong_van_tao_cap_fuzzy` | điểm đúng bằng ngưỡng 85 vẫn tạo cặp, 84,99 thì không |
| 3. Dữ liệu sai | `tests/test_pipeline_csdl.py::test_bang_reject_co_dong_va_ly_do_cho_nguoi_doc` | hồ sơ thiếu số vào bảng reject kèm lý do, không sập |

Kết quả đúng trên bản clone mới: **`139 passed, 2 skipped`** (luồng đúng 14 · giá trị biên 24 · dữ liệu sai 20).
Hai test bỏ qua là test hồi quy trên dữ liệu thật của LMS (`data/raw/customers_raw.csv`, mẫu 8.000 dòng) – không
có trong repo; có hai tệp đó thì `141 passed`. Chưa làm bước 11 thì thêm 12 test tích hợp cần PostgreSQL tự bỏ
qua (`127 passed, 14 skipped`), không báo lỗi. Kiểm thử tự dựng dữ liệu nó cần
(tệp 4 dòng trong `tmp_path`, CSDL `smartcrm_test` xóa và tạo lại schema ở mỗi test), không phụ thuộc dữ liệu
có sẵn trên máy.

## 5. Kiểm tra hệ thống đã chạy đúng

| Sau bước | Kết quả đúng |
|---|---|
| 8 | 5 bước `[1/5]` … `[5/5]`, mã thoát 0. `[2/5] transform`: CLEAN 343 · PENDING_DUP 40 · ERROR 31 (MISSING_PHONE 24, INVALID_PHONE 5, MISSING_NAME 2). `[3/5]`: bảng 6 hàm kiểm có cột "Dòng lỗi SAU (tỉ lệ lỗi)"; chỉ số mức độ sạch TRƯỚC 88,41 → SAU 95,79 (Tốt). `[5/5]`: EXACT_PHONE 40 · FUZZY 3. Đối soát staging ↔ kho 6/6 ✔. Bảng số dòng bảng đích: `ops.stg_customer` +414, `dwh.fact_dq_check` +12, `dwh.fact_dup_pair` +43 |
| 9 | `CẢNH BÁO (AC1.4): tệp này đã nạp ở đợt 1 …`; bảng số dòng bảng đích **+0 ở cả 8 bảng**; `Kết quả lần chạy lại: mọi bảng +0 – không nhân đôi dữ liệu.`; mã thoát 0 (TD-25) |
| 10 | Tab K1 – K3, 4 biểu đồ, mỗi biểu đồ có mốc tham chiếu và dòng ghi nguồn. Người xem `ql.mm001` → trạng thái rỗng có câu giải thích; dừng PostgreSQL rồi bấm Làm mới → trạng thái lỗi có nút Thử lại, không in chuỗi kết nối |
| 12 | `139 passed, 2 skipped` và bảng ba loại kiểm thử: luồng đúng 14 · giá trị biên 24 · dữ liệu sai 20 |

Thử thêm (giảng viên chấm C7 – dữ liệu sai, và suy giảm có kiểm soát):

| Thử | Lệnh | Kết quả đúng |
|---|---|---|
| Tệp thiếu cột | `python -m src.pipeline --tep data/mau/customers_thieu_cot.csv` | `TỪ CHỐI: Thiếu cột bắt buộc: so_dien_thoai – từ chối cả đợt, bảng tạm không thay đổi`, mã thoát 2 |
| Tệp chỉ có dòng tiêu đề | `python -m src.pipeline --tep data/mau/customers_chi_tieu_de.csv` | `TỪ CHỐI: Tệp "customers_chi_tieu_de.csv" không có dòng dữ liệu nào …`, mã thoát 2, không tạo đợt nạp (TD-28) |
| Tệp lưu sai bảng mã (Excel Windows) | `python -m src.pipeline --tep data/mau/customers_sai_bang_ma.csv` | `TỪ CHỐI: Tệp "customers_sai_bang_ma.csv" không phải bảng mã UTF-8 … chọn "Lưu dưới dạng" CSV UTF-8 rồi nạp lại`, mã thoát 2 (TD-28) |
| Bảng reject | `psql -d smartcrm -c "SELECT row_no, phone_raw, error_code, ly_do FROM ops.v_reject ORDER BY row_no LIMIT 8"` (Windows: thêm `-U postgres`) | 31 dòng tất cả; cột `ly_do` viết thành câu |
| Tắt CSDL | macOS: `brew services stop postgresql@14` · Windows (PowerShell chạy quyền Administrator): `net stop postgresql-x64-16` – rồi chạy lại bước 8; xong bật lại bằng `brew services start postgresql@14` / `net start postgresql-x64-16` | `LỖI: LoiKetNoiCSDL: Không kết nối được PostgreSQL ở localhost:5432 …` kèm cách sửa, mã thoát 1, không in mật khẩu |
| Chạy lại riêng UC3 | `python -m src.pipeline --dot 1` | `EXACT_PHONE +0 · FUZZY +0` (cặp đã có không tạo lại) |

## 6. Chạy trên dữ liệu thật (tùy chọn)

Tệp `customers_raw.csv` (67.037 dòng) lấy trong bộ "Dataset Smart CRM" trên LMS, không commit vì `.gitignore`
chặn `data/raw/`. Dùng CSDL mới (`dropdb smartcrm && createdb smartcrm`) rồi:

```
cp ~/Downloads/Dataset/customers_raw.csv data/raw/
python -m src.pipeline --tep data/raw/customers_raw.csv
```

Kết quả đúng (giống buổi 8 – 10): CLEAN 51.279 · PENDING_DUP 11.625 · ERROR 4.133; chỉ số 87,20 → 94,76;
EXACT_PHONE 11.625 · FUZZY 12; đối soát 6/6 ✔. Khi có tệp này, hai test hồi quy ở mục 4 cũng chạy.

## 7. Cấu trúc thư mục – nơi từng lớp nằm

Sơ đồ đã hiện thực: `docs/export/architecture-thuc-te.png` (nguồn `docs/architecture-thuc-te.html`); sơ đồ dự
kiến của BT1: `docs/architecture.drawio`. Ranh giới lớp được kiểm tự động bằng `tests/test_ranh_gioi_lop.py`.

```
dashboard/report.py       ① TRÌNH BÀY  Streamlit K1 – K3, ba trạng thái; chỉ gọi src/doc_kho.py
src/doc_kho.py            ①            truy vấn CHỈ ĐỌC kho dwh, QT-14, câu giải thích khi rỗng
src/pipeline.py           ② điều phối  một lệnh: UC1 → UC3; nơi duy nhất gọi cả ba pha
src/etl/extract.py        ② pha E      đọc tệp, kiểm cột, SHA-256                          (không CSDL)
src/etl/transform.py      ② pha T      chuẩn hóa, mã lỗi, phân loại                        (hàm thuần)
src/etl/dq_evaluate.py    ② pha T      6 hàm kiểm chất lượng DQ-01…06                      (hàm thuần)
src/etl/match.py          ② pha T      name_key, blocking, điểm, tìm cặp                   (hàm thuần)
src/etl/load_ops.py       ② pha L      mọi lệnh đọc/ghi schema ops, CSV hồ sơ lỗi, bảng reject
src/etl/load_dwh.py       ② pha L      nạp kho dwh, SCD loại 2, đối soát
src/etl/tien_ich.py       ② dùng chung la_trong (ô trống) – không thuộc pha nào, để pha T không import pha E (TD-29)
src/db.py, src/config.py  ② ↔ ③        kết nối từ .env, chạy migration sql/0*.sql
sql/001 – 004             ③ LƯU TRỮ    schema ops (6 bảng + view v_reject), dwh (5 bảng + 2 view), trigger
data/mau/                 dữ liệu mẫu giả + 3 tệp lỗi để thử C7 (commit) · data/raw, data/processed, reports/: không commit
tests/                    141 test pytest (pytest.ini: ba loại kiểm thử)
docs/                     srs.md, data-requirements.md, thay-doi-thiet-ke.md, ai-disclosure.md, bug-log.md,
                          architecture-thuc-te.html, *.drawio + export/, bt2/ (ảnh kết quả chạy BT2), sprint1/, sprint2/
scripts/                  sinh_du_lieu_mau.py (seed 42), check_env.py
```

**Tùy chọn của `python -m src.pipeline`:** `--tep` tệp .csv/.xlsx (bắt buộc cột `ho_ten`, `so_dien_thoai`) ·
`--dot n` chỉ chạy lại UC3 cho đợt n · `--don-vi` (QT-14, mặc định `TONG_HOP`) · `--nguoi-nap` (vai trò
MARKETING) · `--nap-lai` xác nhận nạp tệp đã nạp thành đợt mới (AC1.4) · `--khong-ghi-csdl` · `--khong-phat-hien-cap`.

**Mã thoát:** 0 thành công (kể cả chạy lại cùng tệp) · 1 lỗi kỹ thuật (không đọc được tệp, mất kết nối; mọi ghi
chép của lần chạy được ROLLBACK) · 2 dữ liệu bị từ chối (thiếu cột, người nạp sai vai trò, giá trị quá dài, đợt
không tồn tại).

**Tái lập (NFR-05):** mọi bước ngẫu nhiên dùng `seed = 42`; nạp cùng tệp vào CSDL mới cho cùng kết quả.

## 8. Trạng thái Bài tập 2 – tự kiểm theo bảng tiêu chí (đề BT2 mục 4.2)

| Mục | Đạt | Minh chứng |
|---|---|---|
| C1 · CỐT LÕI – chạy từ trạng thái ban đầu theo README | ✔ | Phép thử clone `--branch v0.2` vào thư mục trống, làm đúng 12 bước: `docs/bt2/thu-clone-moi.txt` |
| C2 · CỐT LÕI – tách lớp đúng | ✔ | Bảng mục 7; `tests/test_ranh_gioi_lop.py` (11 test: E/T không chạm CSDL, T không gọi E và L, L không gọi E/T); TD-22, TD-29 |
| C3 – ≥ 2 quy tắc nghiệp vụ thật | ✔ | QT-02 chuẩn hóa số, QT-01 hồ sơ lặp không tạo mới, QL7-03 điểm tương đồng, QL7-04 hồ sơ lỗi ở lại bảng tạm, QL7-06 chỉ số |
| C4 · CỐT LÕI – ≥ 3 test ba loại, PASS bằng một lệnh | ✔ | `python -m pytest -q` → 139 passed, 2 skipped (14 · 24 · 20); bảng ba loại in cuối kết quả |
| C5 · CỐT LÕI – chạy lại không lỗi, không nhân đôi | ✔ | Bước 9: +0 ở 8 bảng đích, mã thoát 0 (TD-25) |
| C6 – tệp khóa, `.env.example`, không có `.env` | ✔ | `requirements.txt` (==), `.env.example` đủ 8 biến, `.gitignore` chặn `.env` |
| C7 – dữ liệu sai bị từ chối rõ ràng | ✔ | Mục 5 bảng "Thử thêm": thiếu cột, chỉ có tiêu đề, sai bảng mã → TỪ CHỐI mã 2 bằng câu tiếng Việt, không lộ lỗi thô của thư viện (TD-28); 20 test loại "dữ liệu sai" |
| D1 – pipeline một lệnh, ba pha ở ba nơi | ✔ | Bước 8; E/T/L ở mục 7 |
| D2 – ≥ 5 hàm kiểm chất lượng trả về số đo | ✔ | 6 hàm `kiem_dq01_…` – `kiem_dq06_…` trả về số dòng lỗi, tỉ lệ lỗi (TD-24) |
| D3 – bảng reject có dòng, lý do cho người đọc | ✔ | `ops.v_reject`, 31 dòng trên dữ liệu mẫu (TD-23) |
| D4 – ≥ 2 biểu đồ có mốc tham chiếu, ghi nguồn | ✔ | 4 biểu đồ K1 – K3 (mốc 90/75, ngưỡng đạt, 10 điểm, ngưỡng 85); mỗi thẻ số ở K1, K3 cũng có mốc (TD-30) |

Ảnh kết quả chạy BT2: `docs/bt2/` (danh sách ở `docs/bt2/README.md`). Nhật ký lỗi đã gỡ: `docs/bug-log.md`.
Phần chuyển sang Giai đoạn 3 (UC5 Gộp/Giữ riêng, K4, `dash_reader`, NFR-02, NFR-03, Docker): TD-27.
Trạng thái Sprint 1 – 2 đã nộp ở buổi 8, 10: `docs/lich-su-sprint.md`.

## 9. Khai báo sử dụng công cụ AI

Theo từng phần, có cột "đã kiểm chứng thế nào": `docs/ai-disclosure.md` (BT1, buổi 8, buổi 10, BT2).

## Tài liệu

| Tệp | Nội dung |
|---|---|
| `docs/srs.md` | SRS 1.2: User Story, tiêu chí chấp nhận, đặc tả UC5, FR, NFR, quy tắc, truy vết |
| `docs/data-requirements.md` | Nguồn dữ liệu, profiling, từ điển dữ liệu, quy tắc DQ, thuật toán so khớp |
| `docs/thay-doi-thiet-ke.md` | TD-01 – TD-31: mọi thay đổi so với BT1 (BT2: TD-22 – TD-31) |
| `docs/bug-log.md` | 12 lỗi đã gỡ, mỗi lỗi 7 dòng, kèm commit |
| `docs/ai-disclosure.md` | Khai báo AI theo từng phần |
| `docs/architecture-thuc-te.html`, `docs/export/` | Sơ đồ kiến trúc đã hiện thực và sơ đồ BT1 |
| `docs/bt2/`, `docs/sprint1/`, `docs/sprint2/` | Ảnh kết quả chạy từng giai đoạn |
