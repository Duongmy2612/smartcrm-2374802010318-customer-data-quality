# Smart CRM – Chất lượng dữ liệu khách hàng (L7)

**Sinh viên:** Dương Diễm My – MSSV: 2374802010318
**Track:** DA (Data Analytics)
**Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang · HK1 2026 – 2027
**Bài tập 1:** `BT1_2374802010318_DuongDiemMy.pdf` – bản chỉnh sửa theo phản hồi (19/10/2026); nhật ký `docs/thay-doi-thiet-ke.md`

> Đánh số mục theo checklist buổi 8: mục 2 là yêu cầu môi trường, mục 6 là trạng thái hiện tại.

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

Đặc tả đầy đủ: `docs/srs.md`.

## 2. Yêu cầu môi trường

| Thành phần | Yêu cầu | Ghi chú |
|---|---|---|
| Python | **3.11 trở lên** | pandas 3 không chạy trên 3.10 trở xuống; máy phát triển dùng 3.11 (Homebrew) |
| Thư viện | `requirements.txt` | pandas, openpyxl, rapidfuzz, SQLAlchemy, psycopg2-binary, python-dotenv, PyYAML, pytest |
| CSDL | **PostgreSQL 14 trở lên** (đã chạy trên 16) | Cần một CSDL `smartcrm` và một tài khoản có quyền tạo schema trong CSDL đó. Pipeline tự tạo schema `ops` (DDL chạy lại an toàn). |
| Biến môi trường | `.env` (chép từ `.env.example`) | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. `.env` **không commit** (NFR-07). |
| Dữ liệu | `data/raw/customers_raw.csv` | Lấy trong bộ "Dataset Smart CRM" trên LMS. **Không commit** vì có dữ liệu cá nhân. |
| Không có PostgreSQL? | `--khong-ghi-csdl` | Vẫn chạy được extract, chuẩn hóa, đo chất lượng, xuất CSV và báo cáo (phương án dự phòng – TD-10). |

## 3. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11 |
| Làm sạch, đo chất lượng | pandas |
| So khớp mờ (Sprint 2) | rapidfuzz |
| Lưu trữ | PostgreSQL – schema `ops` (tác nghiệp), `dwh` (kho dữ liệu hình sao, Sprint 2) |
| Kết nối CSDL | SQLAlchemy + psycopg2 |
| Ứng dụng và dashboard (Sprint 3) | Streamlit |
| Sơ đồ | draw.io (tệp gốc `.drawio` trong `docs/`) |

## 4. Cấu trúc thư mục

Thư mục ánh xạ một–một với các lớp của sơ đồ kiến trúc `docs/architecture.drawio` (Hình 3.1 BT1); xem thêm TD-06.

```
dashboard/            ① TRÌNH BÀY  app.py (UC1,3–6,9) · report.py (K1–K3)                       – Sprint 3
src/etl/              ② XỬ LÝ – NGHIỆP VỤ, mỗi mô-đun một nhóm FR:
  extract.py              FR-01  đọc tệp, kiểm cột, SHA-256, ghi load_batch + stg_customer        ✔ Sprint 1
  transform.py            FR-02, FR-03, FR-10  chuẩn hóa, mã lỗi, customer_clean, CSV hồ sơ lỗi   ✔ Sprint 1
  dq_evaluate.py          FR-07, FR-08  quy tắc DQ-01…06, đo TRƯỚC/SAU, dq_result                 ✔ Sprint 1
  match.py                FR-04  name_key, blocking, điểm tương đồng, dup_candidate               – Sprint 2
  load_dwh.py             FR-09  nạp kho dwh, SCD loại 2                                          – Sprint 2
  merge_service.py        FR-05, FR-06, FR-11  Gộp / Giữ riêng trong một giao dịch                – Sprint 3
src/pipeline.py       thứ tự gọi lớp ② theo Bảng 3.1 – UC1: extract → transform → dq_evaluate → load_dwh
src/db.py             mũi tên ② ↔ ③: SQLAlchemy + psycopg2, kết nối đọc từ .env, giao dịch
src/config.py         đọc configs/config.yaml (người dùng, vai trò, ngưỡng – không có bí mật)
sql/                  ③ LƯU TRỮ  001_ops_schema.sql (6 bảng) ✔ · 002_dwh_schema.sql – Sprint 2
tests/                51 test (pytest): 44 unit test, 2 test hồi quy cần dữ liệu, 5 test tích hợp cần PostgreSQL
docs/                 srs.md, data-requirements.md, thay-doi-thiet-ke.md, ra-soat-bt1.md, ai-disclosure.md,
                      5 tệp .drawio + export/*.png, sprint1/ (ảnh kết quả chạy, báo cáo mẫu)
notebooks/            profiling_customers.py – sinh mọi con số ở mục 4 BT1 và mẫu 8.000 dòng (seed 42)
scripts/check_env.py  kiểm tra môi trường (Buổi 2)
data/raw, processed/  dữ liệu – KHÔNG commit · reports/ – báo cáo số đếm sinh mỗi lần chạy, KHÔNG commit
```

## 5. Hướng dẫn cài đặt và chạy

```bash
# 1. Môi trường ảo và thư viện (macOS; Windows: .venv\Scripts\activate)
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Kết nối CSDL: tạo CSDL rỗng một lần, rồi điền .env
createdb smartcrm                      # hoặc trong psql: CREATE DATABASE smartcrm;
cp .env.example .env                   # điền DB_USER, DB_PASSWORD

# 3. Dữ liệu: chép customers_raw.csv (Dataset Smart CRM trên LMS) vào data/raw/
python notebooks/profiling_customers.py data/raw/customers_raw.csv   # sinh data/processed/mau_cum_8000.csv

# 4. Chạy UC1 bằng MỘT lệnh (tự tạo schema ops nếu chưa có)
python -m src.pipeline --tep data/raw/customers_raw.csv
python -m src.pipeline --tep data/processed/mau_cum_8000.csv --khong-ghi-csdl   # không cần PostgreSQL

# 5. Kiểm thử (test tích hợp dùng CSDL RIÊNG smartcrm_test, tạo một lần; thiếu thì 5 test đó tự bỏ qua)
createdb smartcrm_test
python -m pytest -q
```

Tùy chọn của `src.pipeline`:

| Tùy chọn | Ý nghĩa |
|---|---|
| `--tep` | Tệp `.csv` hoặc `.xlsx`; bắt buộc có cột `ho_ten`, `so_dien_thoai` |
| `--don-vi` | Đơn vị nguồn (QT-14); mặc định `TONG_HOP` |
| `--nguoi-nap` | Tên đăng nhập vai trò `MARKETING` trong `configs/config.yaml` |
| `--nap-lai` | Xác nhận nạp tệp đã từng nạp; không có cờ này thì bị từ chối (AC1.4) |
| `--khong-ghi-csdl` | Chạy thử, không ghi CSDL |

Mã thoát của lệnh:

| Mã | Ý nghĩa |
|---|---|
| 0 | Thành công |
| 1 | Lỗi kỹ thuật (không đọc được tệp, không kết nối được CSDL). Mọi ghi chép của lần chạy được ROLLBACK. |
| 2 | Bị từ chối theo quy tắc nghiệp vụ (thiếu cột, tệp đã nạp, người nạp sai vai trò). Bảng tạm không đổi. |

Mỗi lần chạy ghi:
- `reports/uc1-dot-<n>-<thời điểm>.md`: chỉ có số đếm;
- `data/processed/ho_so_loi_dot_<n>.csv`: hồ sơ lỗi kèm lý do (FR-10).

**Tái lập (NFR-05):** mọi bước ngẫu nhiên dùng `seed = 42`. Ba lần nạp mẫu 8.000 dòng vào ba CSDL mới cho cùng một kết quả. Trên `customers_raw.csv`, kết quả là CLEAN 51.279 · PENDING_DUP 11.625 · ERROR 4.133, chỉ số 87,20 → 94,76.
- `test_hoi_quy_khop_so_lieu_bt1` kiểm các con số này bằng phần tính toán (không cần CSDL).
- `tests/test_pipeline_csdl.py` kiểm phần ghi CSDL.

**Trước khi nộp bài tập (TD-01):**
- Một tệp PDF duy nhất, đúng tên `BT<số>_2374802010318_DuongDiemMy.pdf`.
- Mở lại tệp sau khi nộp; link repo ở trang bìa bấm được.
- Repo public (hoặc đã mời giảng viên làm collaborator) và đã `git push` đủ tệp gốc.

## 6. Trạng thái hiện tại (buổi 8 – 19/10/2026)

**Sprint 1 – đã hiện thực.** Đã chạy trên môi trường thử Linux + PostgreSQL 16; em chạy lại trên MacBook trước buổi 9.

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

  Ảnh kết quả (dựng lại từ log chạy thử, sẽ thay bằng ảnh chụp trên máy em): `docs/sprint1/ket-qua-pipeline.png`, `ket-qua-csdl.png`, `ket-qua-pytest.png`. Báo cáo mẫu: `docs/sprint1/bao-cao-uc1-dot-1.md`.
- [x] Các trường hợp bị từ chối và lỗi đều có test:

  | Trường hợp | Kết quả | Test |
  |---|---|---|
  | Thiếu cột (AC1.3) | mã thoát 2 | `test_ac13_*`, `test_ma_thoat` |
  | Nạp lại cùng tệp (AC1.4) | từ chối, bảng tạm không đổi; có `--nap-lai` thì thành đợt mới, hồ sơ hợp lệ thành PENDING_DUP | `test_ac14_nap_lai_bi_tu_choi_roi_xac_nhan` |
  | Người nạp sai vai trò | từ chối | `test_chi_nhan_vien_marketing_duoc_nap_tep` |
  | Giá trị dài hơn cột của `customer_clean` | từ chối, báo số dòng (TD-11) | `test_gia_tri_qua_dai_bi_tu_choi_ca_dot` |
  | Lỗi giữa giao dịch | ROLLBACK, không còn đợt nạp dở (TD-09) | `test_loi_giua_chung_thi_rollback_ca_dot` |

- [x] 51 test pass trên môi trường thử. Trên bản clone chưa có dữ liệu và CSDL test, 2 test hồi quy và 5 test tích hợp tự bỏ qua.

**NFR-01, phần 1** – nạp và chuẩn hóa 8.000 dòng ≤ 60 giây. Đo 3 lần trên mẫu `mau_cum_8000.csv`, mỗi lần một CSDL mới, lấy giá trị lớn nhất:

| Môi trường đo | Pipeline (extract + transform + đo) | Cả lệnh (kể cả khởi động Python) | Kết luận |
|---|---|---|---|
| Linux, Python 3.11, PostgreSQL 16 (môi trường thử, 19/10) | 1,4 s | 2,1 s | Đạt |
| MacBook của em (máy phát triển) | *chưa đo – đo trước buổi 9* | | |

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
- [ ] Em chạy lại trên MacBook: đo NFR-01 phần 1, thay ảnh trong `docs/sprint1/` bằng ảnh chụp màn hình của em, đánh dấu các ô kiểm chứng trong `docs/ai-disclosure.md`.

**Ghi chú:** không dùng phương án dự phòng; CSDL vẫn là PostgreSQL. `--khong-ghi-csdl` chỉ để chạy thử khi máy chưa có PostgreSQL (TD-10).

## 7. Khai báo sử dụng công cụ AI

| Công cụ | Dùng vào việc gì | Cách tự kiểm chứng |
|---|---|---|
| Claude (Anthropic) – BT1 | Rà soát hồ sơ Buổi 4; script profiling; bản nháp mục 3, 4, 5; tệp `.drawio`, Markdown | Chạy lại script profiling với seed 42 và đối chiếu từng con số ở mục 4.1, 4.5; mở từng tệp `.drawio` để đối chiếu; tự giải thích được GRAIN, SCD loại 2 |
| Claude (Anthropic) – buổi 8 | Rút gọn PDF BT1, nhật ký TD-01 – TD-12; bản nháp DDL, `extract.py`, `transform.py`, `dq_evaluate.py`, `pipeline.py`, test, README | Theo từng phần, có ô đánh dấu: `docs/ai-disclosure.md` |

## Tài liệu

| Tệp | Nội dung |
|---|---|
| `docs/srs.md` | SRS 1.2: User Story, tiêu chí chấp nhận, đặc tả UC5, FR, NFR, quy tắc, truy vết, lịch sử thay đổi |
| `docs/data-requirements.md` | Nguồn dữ liệu, số đo profiling, từ điển dữ liệu 11 bảng, quy tắc DQ, thuật toán so khớp |
| `docs/thay-doi-thiet-ke.md` | Nhật ký thay đổi thiết kế TD-01 – TD-12 (đọc lại khi chấm BT2, BT3) |
| `docs/ra-soat-bt1.md` | Tự kiểm BT1, sáu phép kiểm nhất quán, năm lỗi ERD |
| `docs/ai-disclosure.md` | Khai báo AI theo từng phần |
| `docs/*.drawio`, `docs/export/` | Use Case, kiến trúc, data flow, ERD (ops + star schema), wireframe K1 – K4 |
