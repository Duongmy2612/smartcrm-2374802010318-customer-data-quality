# Ảnh kết quả chạy – Bài tập 2 (31/10/2026)

Cùng bộ ảnh với báo cáo PDF `BT2_2374802010318_DuongDiemMy.pdf` (11 trang). Nơi chụp của từng ảnh ghi ở cột cuối.

- **MacBook của em, lần 3 – phép thử thư mục trống** (Python 3.11, PostgreSQL 14, 31/10/2026 tối): clone tag `v0.2`
  (lúc đó trỏ commit `300f973`) vào thư mục mới `thu-nghiem`, CSDL mới, làm đúng 13 bước README mục 3 trên dữ liệu
  mẫu `data/mau/customers_mau.csv` (414 dòng), không gõ thêm lệnh nào. Dashboard (bước 10) đọc kho của chính lần chạy
  này nên số trên ảnh khớp ảnh dòng lệnh: chỉ số 88,41 → 95,79; 43 cặp. Các commit sau `300f973` chỉ đổi ảnh và tài
  liệu: `git diff 300f973 v0.2 -- src tests sql dashboard scripts data` không ra dòng nào.
- **MacBook của em, lần 2** (31/10/2026 tối): bản clone mới nhất của nhánh `main` (`git clone --depth 1`, môi trường
  ảo Python 3.11), chép `customers_raw.csv` của LMS vào `data/raw/`, chạy test ranh giới lớp và lệnh NFR-03 ở README
  mục 6.
- **MacBook của em, lần 1** (31/10/2026 chiều): bản clone mới `git clone --branch v0.2 …` khi tag trỏ commit `1c5a6a7`,
  làm đúng README mục 3. Từ `1c5a6a7` tới tag cuối, mã luồng chính, kho và dashboard không đổi dòng nào:
  `git diff 1c5a6a7 v0.2 -- src/pipeline.py src/etl/extract.py src/etl/transform.py src/etl/dq_evaluate.py src/etl/match.py src/etl/load_ops.py src/etl/load_dwh.py src/doc_kho.py src/db.py dashboard sql`
  không ra dòng nào.
- **Claude, môi trường thử Linux** (phiên chat riêng, 31/10/2026): chỉ ảnh `14-dashboard-loi.png` – dừng PostgreSQL rồi
  bấm Làm mới trên dashboard, mã giống tag `v0.2`, chụp bằng Chromium. Khai báo ở `docs/ai-disclosure.md`.

| Ảnh | Nội dung | Hình trong PDF | Mục BT2 | Nơi chụp |
|---|---|---|---|---|
| `01-dung-lai-tu-dau.png` | README bước 1 – 7: clone tag `v0.2`, venv, thư viện, `.env`, `createdb` | 6.1 | C1, TP4 | MacBook, lần 1 |
| `02-luong-chinh.png` | Bước 8: 5 bước, bảng 6 hàm kiểm có số dòng lỗi, chỉ số 88,41 → 95,79, đối soát 6/6, số dòng 8 bảng đích | 3.1 | TP1, D1, D2 | MacBook, lần 3 |
| `03-chay-lai-lan-hai.png` | Bước 9: cảnh báo AC1.4, không tạo đợt mới, +0 ở cả 8 bảng đích | 3.2 | C5 | MacBook, lần 3 |
| `04-du-lieu-sai.png` | Ba tệp lỗi trong `data/mau/` bị TỪ CHỐI, mã thoát 2 | 3.3 | C7 | MacBook, lần 3 |
| `05-bang-reject.png` | Bảng reject `ops.v_reject`, 8 dòng đầu (cả bảng 31 dòng), lý do viết thành câu | 3.4 | D3 | MacBook, lần 3 |
| `06-ranh-gioi-lop.png` | `python -m pytest tests/test_ranh_gioi_lop.py -v`: 14 test ranh giới lớp PASS (E/T không chạm CSDL, T không gọi E/L, L không gọi E/T, chỉ pipeline gọi cả ba pha, lệnh NFR-03 không chạm CSDL, dashboard chỉ đọc) | 2.2 | C2, D1 | MacBook, lần 2 |
| `07-pytest.png` | Bước 12: `155 passed, 3 skipped`, bảng ba loại kiểm thử 18 · 28 · 25 | 4.1 | TP2, C4 | MacBook, lần 3 |
| `08-mat-ket-noi.png` | PostgreSQL đã dừng → câu báo lỗi chỉ cách sửa, không lộ mật khẩu, mã thoát 1 | 3.5 | suy giảm có kiểm soát | MacBook, lần 1 |
| `09-dashboard-k1.png` | K1: chỉ số 88,41 → 95,79 (Tốt), đường 90/75, thẻ số có mốc ("24 hồ sơ · mốc ≤ 2%", "SAU +7,38 · cần ≥ +10") | 5.1 | TP3, D4 | MacBook, lần 3 |
| `10-dashboard-k2.png` | K2: tỉ lệ đạt và điểm bị mất theo quy tắc | 5.2 | TP3, D4 | MacBook, lần 3 |
| `11-dashboard-k3.png` | K3: 43 cặp (40 EXACT_PHONE + 3 FUZZY), phân bố điểm quanh ngưỡng 85 | 5.3 | TP3, D4 | MacBook, lần 3 |
| `13-dashboard-dang-tai.png` | Trạng thái **đang tải**: đổi người xem từ `ql.mm001` sang `my.marketing`, dashboard đọc lại kho | 5.4 | ba trạng thái | MacBook, lần 3 |
| `12-dashboard-rong.png` | Trạng thái **rỗng**: người xem `ql.mm001`, đợt thuộc đơn vị khác (QT-14) | 5.5 | ba trạng thái | MacBook, lần 3 |
| `14-dashboard-loi.png` | Trạng thái **lỗi**: dừng PostgreSQL rồi bấm Làm mới – chỉ in loại lỗi, có nút Thử lại | 5.6 | ba trạng thái | Claude, môi trường thử |
| `15-nfr03-du-lieu-mau.png` | Bước 13: NFR-03 trên dữ liệu mẫu, nhãn đúng của script sinh – TP 43 · FP 0 · FN 0 · TN 20, ĐẠT | 3.6 | NFR-03 (nhận xét BT1) | MacBook, lần 3 |
| `16-nfr03-du-lieu-that.png` | README mục 6: NFR-03 trên 300 cặp dữ liệu thật – TP 128 · FP 12 · FN 4 · TN 156, precision 91,43%, recall 96,97%, ĐẠT; dòng `md5` cho thấy đúng tệp `customers_raw.csv` của LMS | 3.7 | NFR-03 (nhận xét BT1) | MacBook, lần 2 |

Dashboard trên dữ liệu thật (67.037 dòng, 87,20 → 94,76; 11.637 cặp): ảnh em chụp ở buổi 10 trong `docs/sprint2/`;
bộ ảnh dữ liệu thật Claude chụp trên môi trường thử xem được trong lịch sử ở commit `300f973`. Bộ ảnh dòng lệnh trước
đó: commit `fd6bd8f2`. Nhật ký phép thử thư mục trống trên môi trường Linux của Claude, ghi mã thoát từng bước:
`thu-clone-moi.txt`.
