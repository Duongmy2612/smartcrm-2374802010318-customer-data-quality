# Minh chứng Sprint 2 (buổi 10)

**Nguồn ảnh:** 4 ảnh dòng lệnh (`ket-qua-*.png`) chụp trên **MacBook của em** ngày 25/10/2026 (macOS, Python 3.11.16, PostgreSQL 14), trong bản clone mới lấy từ GitHub. 5 ảnh dashboard (`dashboard-*.png`) chụp trên **môi trường thử** (Linux, Python 3.11, PostgreSQL 16, 24/10/2026); em chụp lại trên MacBook rồi thay, giữ nguyên tên tệp. Ảnh dòng lệnh trước đó của môi trường thử vẫn còn trong lịch sử git; nhật ký `thu-clone-moi.txt` và báo cáo `bao-cao-uc1-uc3-dot-1.md` là của môi trường thử.

| Tệp | Nội dung | Mục kiểm chứng buổi 10 |
|---|---|---|
| `ket-qua-toan-luong.png` | Bước 9 trên MacBook: lần đầu báo `ThieuCauHinhCSDL` (chưa điền `DB_USER` ở bước 6), điền `.env` rồi chạy lại – 5 bước, đối soát staging ↔ kho 6/6 ✔ | Luồng chính end-to-end trên dữ liệu thật; đếm dòng staging và fact |
| `ket-qua-nap-lai.png` | `python -m src.etl.load_dwh` sau luồng chính: mọi bảng `+0`, `lô ngày 0`, đối soát vẫn khớp | Nạp lần hai không nhân đôi dòng |
| `ket-qua-pytest.png` | `python -m pytest -q` → `94 passed`; danh sách 48 test của Sprint 2 và test tích hợp | ≥ 5 unit test pass, có test biên và luồng ngoại lệ |
| `ket-qua-nfr01.png` | 3 lần chạy mẫu 8.000 dòng trên MacBook, mỗi lần một CSDL mới, lọc các dòng có số đo; `time` đo cả lệnh | NFR-01 phần 2 |
| `dashboard-k1.png` | K1 – đường chỉ số mức độ sạch TRƯỚC/SAU, mốc 90 · Tốt và 75 · Kém, dòng ghi nguồn | Biểu đồ gắn câu hỏi Q2, có mốc tham chiếu |
| `dashboard-k2.png` | K2 – hai biểu đồ: tỉ lệ đạt theo quy tắc (vạch ngưỡng đạt) và điểm bị mất từng quy tắc (đường 10 điểm) | Biểu đồ gắn câu hỏi Q3 |
| `dashboard-k3.png` | K3 – thẻ theo trạng thái (Q4); số cặp theo khoảng điểm, tách EXACT_PHONE / FUZZY, mốc ngưỡng 85 (Q5) | Biểu đồ gắn câu hỏi Q5 |
| `dashboard-rong.png` | Người xem `ql.mm001` (Quản lý cửa hàng MM001): có đợt nạp trong khoảng ngày nhưng thuộc đơn vị khác – câu giải thích nói đúng nguyên nhân và việc nên làm | Trạng thái rỗng (QT-14) |
| `dashboard-loi.png` | CSDL không kết nối được: thông báo không lộ chuỗi kết nối, nút Thử lại | Trạng thái lỗi |
| `bao-cao-uc1-uc3-dot-1.md` | Báo cáo số đếm của lần chạy luồng chính trên môi trường thử – cùng số với `ket-qua-toan-luong.png` trên MacBook | Đầu vào – đầu ra quan sát được |
| `thu-clone-moi.txt` | Nhật ký thử clone mới trên môi trường thử, làm đúng 12 bước README mục 3 | Đã thử clone vào thư mục mới |

Trạng thái đang tải là spinner "Đang tải dữ liệu từ kho dữ liệu…", chỉ hiện trong khoảng 1 – 3 giây nên không chụp.

**NFR-06 (môi trường thử):** trang dashboard hiện đủ 4 biểu đồ trong 4,1 giây với 1 đợt nạp và 4,1 giây với 24 đợt nạp mẫu 8.000 dòng (nạp vào một CSDL riêng để đo); lấy giá trị lớn nhất của 3 lần, lần đầu là lúc bộ đệm còn rỗng. Ngưỡng ≤ 5 giây.
