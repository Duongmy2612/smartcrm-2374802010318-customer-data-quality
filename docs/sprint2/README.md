# Minh chứng Sprint 2 (buổi 10)

Ảnh trong thư mục này chụp ngày 24/10/2026 trên **môi trường thử** (Linux, Python 3.11, PostgreSQL 16), từ một bản clone mới làm đúng README mục 3 – chưa phải ảnh chụp trên MacBook của em. Ảnh dòng lệnh được dựng lại từ nhật ký chạy và có ghi rõ ở thanh tiêu đề. Em chạy lại trên MacBook rồi thay từng ảnh, giữ nguyên tên tệp (`docs/ai-disclosure.md`, mục Sprint 2).

| Tệp | Nội dung | Mục kiểm chứng buổi 10 |
|---|---|---|
| `ket-qua-toan-luong.png` | Bước 9: `python -m src.pipeline --tep data/raw/customers_raw.csv` – 5 bước, đối soát staging ↔ kho 6/6 ✔, mã thoát 0 | Luồng chính end-to-end trên dữ liệu thật; đếm dòng staging và fact |
| `ket-qua-nap-lai.png` | `python -m src.etl.load_dwh` sau luồng chính: mọi bảng `+0`, đối soát vẫn khớp | Nạp lần hai không nhân đôi dòng |
| `ket-qua-pytest.png` | `python -m pytest -q` → `79 passed`; danh sách 33 test của Sprint 2 và test tích hợp | ≥ 5 unit test pass, có test biên và luồng ngoại lệ |
| `ket-qua-nfr01.png` | 3 lần chạy mẫu 8.000 dòng, mỗi lần một CSDL mới (trích các dòng có số đo) | NFR-01 phần 2 |
| `dashboard-k1.png` | K1 – đường chỉ số mức độ sạch TRƯỚC/SAU, mốc 90 · Tốt và 75 · Kém, dòng ghi nguồn | Biểu đồ gắn câu hỏi Q2, có mốc tham chiếu |
| `dashboard-k2.png` | K2 – tỉ lệ đạt theo quy tắc, vạch ngưỡng đạt, điểm bị mất | Biểu đồ gắn câu hỏi Q3 |
| `dashboard-k3.png` | K3 – cặp nghi trùng theo khoảng điểm và trạng thái, mốc ngưỡng 85 | Biểu đồ gắn câu hỏi Q4, Q5 |
| `dashboard-rong.png` | Người xem `ql.mm001` (Quản lý cửa hàng MM001): bộ lọc rỗng, có câu giải thích vì sao và nên làm gì | Trạng thái rỗng (QT-14) |
| `dashboard-loi.png` | CSDL không kết nối được: thông báo không lộ chuỗi kết nối, nút Thử lại | Trạng thái lỗi |
| `bao-cao-uc1-uc3-dot-1.md` | Báo cáo số đếm của lần chạy trong `ket-qua-toan-luong.png` | Đầu vào – đầu ra quan sát được |
| `thu-clone-moi.txt` | Nhật ký thử clone mới, làm đúng 12 bước README mục 3 | Đã thử clone vào thư mục mới |

Trạng thái đang tải là spinner "Đang tải dữ liệu từ kho dữ liệu…", chỉ hiện trong khoảng 1 – 3 giây nên không chụp.

**NFR-06:** trang dashboard hiện đủ 3 biểu đồ trong 3,8 giây (lớn nhất của 3 lần, 1 đợt nạp) và 3,7 giây (24 đợt nạp mẫu 8.000 dòng, nạp vào một CSDL riêng để đo). Ngưỡng là ≤ 5 giây. Mỗi lần đo tính từ lúc mở trang tới khi đủ 3 biểu đồ, lần đầu tiên là lúc bộ đệm còn rỗng.
