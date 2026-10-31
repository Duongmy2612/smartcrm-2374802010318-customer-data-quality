# Ảnh kết quả chạy – Bài tập 2 (buổi 12, 31/10/2026)

**Nơi chụp:** môi trường thử của Claude (Linux, Python 3.11.18, PostgreSQL 16.15), trên bản clone mới làm đúng README
mục 3, dữ liệu mẫu `data/mau/customers_mau.csv`. Ảnh dòng lệnh là kết quả chạy thật được dựng thành khung Terminal;
thanh tiêu đề mỗi ảnh ghi môi trường và giờ chụp. Đây **không** phải ảnh chụp trên MacBook của em (khai báo ở
`docs/ai-disclosure.md`, mục BT2). Ảnh dashboard chụp trên MacBook với dữ liệu thật ở buổi 10 vẫn ở `docs/sprint2/`.

| Ảnh | Nội dung | Mục BT2 |
|---|---|---|
| `01-luong-chinh.png` | CSDL mới → `python -m src.pipeline --tep data/mau/customers_mau.csv`: 5 bước, bảng 6 hàm kiểm có số dòng lỗi, đối soát 6/6 ✔, số dòng 8 bảng đích, mã thoát 0 | TP1, C1, D1, D2 |
| `02-chay-lai-lan-hai.png` | Chạy lại đúng lệnh trên: cảnh báo AC1.4, +0 ở cả 8 bảng đích, mã thoát 0 | C5 |
| `03-pytest.png` | `python -m pytest -q`: 123 passed, 2 skipped; bảng ba loại kiểm thử | TP2, C4 |
| `04-du-lieu-sai-va-bang-reject.png` | Tệp thiếu cột bị từ chối (mã 2); bảng reject `ops.v_reject` 31 dòng, lý do viết thành câu | C7, D3 |
| `05-ranh-gioi-lop.png` | `grep` pha E/T không có SQL; 6 hàm `kiem_dq…`; `tests/test_ranh_gioi_lop.py` 11 passed | C2, D1, D2 |
| `06-mat-ket-noi.png` | PostgreSQL đã dừng → câu báo lỗi chỉ cách sửa, không lộ mật khẩu, mã thoát 1 | suy giảm có kiểm soát |
| `07-dashboard-k1.png` … `09-dashboard-k3.png` | Dashboard có dữ liệu: 4 biểu đồ, mốc tham chiếu, dòng ghi nguồn và thời điểm | TP3, D4 |
| `10-dashboard-dang-tai.png` | Trạng thái **đang tải** (giữ khóa bảng `dwh.fact_dq_check` 8 giây ở phiên khác rồi bấm Làm mới dữ liệu) | TP3 – ba trạng thái |
| `11-dashboard-rong.png` | Trạng thái **rỗng**: người xem `ql.mm001`, đợt thuộc đơn vị khác (QT-14) – câu giải thích, không phải "chưa có dữ liệu" | TP3 – ba trạng thái |
| `12-dashboard-loi.png` | Trạng thái **lỗi**: dừng PostgreSQL rồi bấm Làm mới – chỉ in loại lỗi, không in chuỗi kết nối, có nút Thử lại | TP3 – ba trạng thái |
| `thu-clone-moi.txt` | Nhật ký phép thử thư mục trống, 12 bước README và 4 phép thử thêm, mã thoát từng bước | C1 |
