# Ảnh kết quả chạy – Bài tập 2 (31/10/2026)

Cùng bộ ảnh với báo cáo PDF `BT2_2374802010318_DuongDiemMy.pdf`. Nơi chụp của từng ảnh ghi ở cột cuối.

- **MacBook của em, lần 1** (Python 3.11, PostgreSQL 14, 31/10/2026 chiều): bản clone mới `git clone --branch v0.2 …`
  khi tag trỏ commit `1c5a6a7`, làm đúng README mục 3, dữ liệu mẫu `data/mau/customers_mau.csv`. Từ `1c5a6a7` tới tag
  cuối, mã luồng chính, kho và dashboard không đổi dòng nào:
  `git diff 1c5a6a7 v0.2 -- src/pipeline.py src/etl/extract.py src/etl/transform.py src/etl/dq_evaluate.py src/etl/match.py src/etl/load_ops.py src/etl/load_dwh.py src/doc_kho.py dashboard sql`
  không ra dòng nào. Phần thêm sau đó là NFR-03 (TD-32) – vì vậy số test và test ranh giới tăng.
- **MacBook của em, lần 2** (31/10/2026 tối): bản clone mới nhất của nhánh `main` (`git clone --depth 1`, môi trường
  ảo Python 3.11), chép `customers_raw.csv` của LMS vào `data/raw/`, chạy lệnh NFR-03 ở README mục 6 và test ranh giới lớp.
- **Claude, môi trường thử Linux** (phiên chat riêng, 31/10/2026 tối): nạp lại dữ liệu thật `customers_raw.csv`
  (67.037 dòng, LMS) vào CSDL mới với mã giống tag `v0.2`, chụp dashboard bằng Chromium. Lý do: ảnh K1 – K3 em chụp
  trên MacBook chỉ rộng khoảng 600 điểm ảnh nên in ra bị mờ. Số trên ảnh khớp số em chạy trên MacBook (87,20 → 94,76;
  11.637 cặp = 11.625 EXACT_PHONE như BT1 + 12 FUZZY như buổi 10). Khai báo ở `docs/ai-disclosure.md`.

| Ảnh | Nội dung | Hình trong PDF | Mục BT2 | Nơi chụp |
|---|---|---|---|---|
| `01-dung-lai-tu-dau.png` | README bước 1 – 7: clone tag `v0.2`, venv, thư viện, `.env`, `createdb` | 6.1 | C1, TP4 | MacBook, lần 1 |
| `02-luong-chinh.png` | Bước 8: 5 bước, bảng 6 hàm kiểm có số dòng lỗi, đối soát 6/6, số dòng 8 bảng đích, mã thoát 0 | 3.1 | TP1, D1, D2 | MacBook, lần 1 |
| `03-chay-lai-lan-hai.png` | Bước 9: cảnh báo AC1.4, +0 ở cả 8 bảng đích, mã thoát 0 | 3.2 | C5 | MacBook, lần 1 |
| `04-du-lieu-sai.png` | Ba tệp lỗi trong `data/mau/` bị TỪ CHỐI, mã thoát 2 | 3.3 | C7 | MacBook, lần 1 |
| `05-bang-reject.png` | Bảng reject `ops.v_reject`: 31 dòng, lý do viết thành câu | 3.4 | D3 | MacBook, lần 1 |
| `06-ranh-gioi-lop.png` | `python -m pytest tests/test_ranh_gioi_lop.py -v`: 14 test ranh giới lớp PASS (E/T không chạm CSDL, T không gọi E/L, L không gọi E/T, chỉ pipeline gọi cả ba pha, lệnh NFR-03 không chạm CSDL, dashboard chỉ đọc) | 2.2 | C2, D1 | MacBook, lần 2 |
| `07-pytest.png` | Bước 11 – 12: bộ kiểm thử và bảng ba loại | 4.1 | TP2, C4 | MacBook, lần 1 (139 passed – trước NFR-03) |
| `08-mat-ket-noi.png` | PostgreSQL đã dừng → câu báo lỗi chỉ cách sửa, không lộ mật khẩu, mã thoát 1 | 3.5 | suy giảm có kiểm soát | MacBook, lần 1 |
| `09-dashboard-k1.png` … `11-dashboard-k3.png` | Dashboard có dữ liệu (dữ liệu thật): 4 biểu đồ, mốc tham chiếu, thẻ số có mốc, dòng ghi nguồn | 5.1 – 5.3 | TP3, D4 | Claude, môi trường thử |
| `12-dashboard-rong.png` | Trạng thái **rỗng**: người xem `ql.mm001`, đợt thuộc đơn vị khác (QT-14) | 5.5 | ba trạng thái | Claude, môi trường thử |
| `13-dashboard-dang-tai.png` | Trạng thái **đang tải**: khóa bảng `dwh.dim_batch` ở phiên khác rồi bấm Làm mới dữ liệu | 5.4 | ba trạng thái | Claude, môi trường thử |
| `14-dashboard-loi.png` | Trạng thái **lỗi**: dừng PostgreSQL rồi bấm Làm mới – chỉ in loại lỗi, có nút Thử lại | 5.6 | ba trạng thái | Claude, môi trường thử |
| `16-nfr03-du-lieu-that.png` | README mục 6: NFR-03 trên 300 cặp dữ liệu thật – TP 128 · FP 12 · FN 4 · TN 156, precision 91,43%, recall 96,97%, ĐẠT; dòng `md5` cho thấy đúng tệp `customers_raw.csv` của LMS | 3.6 | NFR-03 (nhận xét BT1) | MacBook, lần 2 |

Ảnh dashboard em chụp trên MacBook ở buổi 10 (cùng dữ liệu thật): `docs/sprint2/dashboard-*.png`. Bộ ảnh trước đó
xem được trong lịch sử commit `fd6bd8f2`. Nhật ký phép thử thư mục trống trên môi trường Linux: `thu-clone-moi.txt`.
