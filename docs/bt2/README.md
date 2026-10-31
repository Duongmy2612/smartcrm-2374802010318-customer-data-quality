# Ảnh kết quả chạy – Bài tập 2 (buổi 12, 31/10/2026)

**Nơi chụp:** ảnh 01 – 13 em chụp trên MacBook ngày 31/10/2026. Ảnh dòng lệnh 01 – 08: bản clone mới
`git clone --branch v0.2 …` làm đúng README mục 3, dữ liệu mẫu `data/mau/customers_mau.csv`. Ảnh dashboard 09 – 13:
kho đã nạp đợt dữ liệu thật `customers_raw.csv` (67.037 dòng, nạp ngày 25/10/2026) nên số là 87,20 → 94,76 và
11.637 cặp, khớp BT1. **Ảnh 14** (trạng thái lỗi) do Claude chụp trên môi trường thử Linux vì em chưa chụp được trên
MacBook – có nhãn ngay trên ảnh, ghi trong chú thích Hình 5.6 và Phụ lục báo cáo. Cùng bộ ảnh với báo cáo PDF
`BT2_2374802010318_DuongDiemMy.pdf` (Hình 2.2 – 6.1).

Ảnh 01 chụp lúc tag `v0.2` trỏ commit `1c5a6a7`. Sau đó tag được gắn lại lên commit chỉ thêm ảnh và tài liệu; mã
nguồn không đổi: `git diff 1c5a6a7 v0.2 -- src tests sql dashboard scripts data` không ra dòng nào.

Bộ ảnh cũ chụp trên môi trường thử của Claude (Linux) đã bỏ khỏi thư mục này: đề BT2 mục 4.4 yêu cầu ảnh chụp từ
máy của sinh viên, và ảnh cũ còn kết quả trước TD-28 – TD-31 (123 test). Ảnh cũ vẫn xem được trong lịch sử commit
`77619fb0`. Nhật ký phép thử thư mục trống trên môi trường thử: `thu-clone-moi.txt`.

| Ảnh | Nội dung | Hình trong PDF | Mục BT2 |
|---|---|---|---|
| `01-dung-lai-tu-dau.png` | Bước 1 – 7 README: clone tag `v0.2`, venv, thư viện, `.env`, `createdb` | 6.1 | C1, TP4 |
| `02-luong-chinh.png` | Bước 8: 5 bước, bảng 6 hàm kiểm có số dòng lỗi, đối soát 6/6, số dòng 8 bảng đích, mã thoát 0 | 3.1 | TP1, D1, D2 |
| `03-chay-lai-lan-hai.png` | Bước 9: cảnh báo AC1.4, +0 ở cả 8 bảng đích, mã thoát 0 | 3.2 | C5 |
| `04-du-lieu-sai.png` | Ba tệp lỗi trong `data/mau/` bị TỪ CHỐI, mã thoát 2 | 3.3 | C7 |
| `05-bang-reject.png` | Bảng reject `ops.v_reject`: 31 dòng, lý do viết thành câu | 3.4 | D3 |
| `06-ranh-gioi-lop.png` | `grep` pha E/T không có SQL, pha T chỉ import `tien_ich`; 6 hàm `kiem_dq…`; 11 test ranh giới lớp | 2.2 | C2, D1, D2 |
| `07-pytest.png` | Bước 11 – 12: `139 passed, 2 skipped`, bảng ba loại kiểm thử 14 · 24 · 20 | 4.1 | TP2, C4 |
| `08-mat-ket-noi.png` | PostgreSQL đã dừng → câu báo lỗi chỉ cách sửa, không lộ mật khẩu, mã thoát 1 | 3.5 | suy giảm có kiểm soát |
| `09-dashboard-k1.png` … `11-dashboard-k3.png` | Dashboard có dữ liệu (kho dữ liệu thật 67.037 dòng): 4 biểu đồ, mốc tham chiếu, thẻ số có mốc, dòng ghi nguồn | 5.1 – 5.3 | TP3, D4 |
| `12-dashboard-rong.png` | Trạng thái **rỗng**: người xem `ql.mm001`, đợt thuộc đơn vị khác (QT-14) | 5.5 | ba trạng thái |
| `13-dashboard-dang-tai.png` | Trạng thái **đang tải** (giữ khóa bảng `dwh.dim_batch` ở tab Terminal khác rồi bấm Làm mới dữ liệu) | 5.4 | ba trạng thái |
| `14-dashboard-loi.png` | Trạng thái **lỗi**: dừng PostgreSQL rồi bấm Làm mới – chỉ in loại lỗi, có nút Thử lại. Chụp trên môi trường thử của Claude (nhãn trên ảnh) | 5.6 | ba trạng thái |
