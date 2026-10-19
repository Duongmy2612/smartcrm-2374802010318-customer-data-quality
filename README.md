# Smart CRM – Chất lượng dữ liệu khách hàng (L7)

**Sinh viên:** Dương Diễm My – MSSV: 2374802010318
**Track:** DA (Data Analytics)
**Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang

## 1. Mô tả bài toán
Mekong Mobile chưa có CRM; dữ liệu khách hàng rải rác ở Excel từng cửa hàng, Zalo và sổ tay bảo hành nên một khách có thể tồn tại nhiều lần (vấn đề V1 của case study). Đo trên `customers_raw.csv` (67.037 dòng): 18,48% hồ sơ có số điện thoại là hồ sơ lặp, 6,17% hồ sơ thiếu số, 28,40% hồ sơ ghi số sai dạng.

**Luồng nghiệp vụ L7 (bắt đầu → kết thúc):** Nhân viên Marketing nạp tệp khách hàng thô → hệ thống chuẩn hóa số điện thoại và họ tên → phát hiện cặp hồ sơ nghi trùng bằng so khớp mờ → Nhân viên Marketing xác nhận Gộp hoặc Giữ riêng từng cặp → hệ thống đo chỉ số mức độ sạch TRƯỚC/SAU làm sạch và nạp kho dữ liệu → Quản lý cửa hàng xem dashboard mức độ sạch theo thời gian và xuất danh sách hồ sơ lỗi để cửa hàng sửa tại nguồn.

## 2. Phạm vi
**Làm**
- Nạp tệp khách hàng thô (CSV/Excel) theo đợt nạp; chuẩn hóa số điện thoại và họ tên (UC1, UC2).
- Phát hiện cặp nghi trùng bằng so khớp mờ; Nhân viên Marketing xem và xác nhận Gộp hoặc Giữ riêng từng cặp (UC3, UC4, UC5).
- Cấu hình bộ quy tắc chất lượng dữ liệu; đo chỉ số mức độ sạch của từng đợt trước và sau làm sạch (UC6, UC7).
- Dashboard mức độ sạch theo thời gian và xuất danh sách hồ sơ lỗi để cửa hàng sửa tại nguồn (UC8, UC9).

**Không làm**
- Tự động gộp cặp nghi trùng có điểm tương đồng cao mà không cần xác nhận (US10 của bản Buổi 4).
- Xử lý dữ liệu đơn hàng, bảo hành, kho linh kiện; phân khúc khách hàng (L1); dự báo khách rời bỏ (L9).
- Gửi tin khuyến mãi/chiến dịch thực tế; tích hợp trực tiếp hệ thống bán hàng; đăng nhập một lần (SSO); triển khai máy chủ.

## 3. Công nghệ sử dụng
| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11 |
| Làm sạch, so khớp mờ | pandas, rapidfuzz |
| Lưu trữ | PostgreSQL – schema `ops` (tác nghiệp), schema `dwh` (kho dữ liệu hình sao) |
| Kết nối CSDL | SQLAlchemy, psycopg2 |
| Ứng dụng và dashboard | Streamlit |
| Sơ đồ | draw.io (file gốc `.drawio` trong `docs/`) |

## 4. Cấu trúc thư mục
```
docs/
  srs.md                 # SRS 1.1 (nguồn của file BT1)
  data-requirements.md   # yêu cầu dữ liệu track DA, số đo profiling
  ai-disclosure.md       # khai báo sử dụng công cụ AI
  usecase.drawio  architecture.drawio  dataflow.drawio  erd.drawio  wireframe.drawio
  wireframe.png          # 4 khung wireframe K1–K4
  export/                # ảnh PNG của từng sơ đồ
data/
  raw/                   # customers_raw.csv (tải từ LMS, KHÔNG commit)
  processed/             # sinh lại bằng script với seed 42 (KHÔNG commit)
notebooks/
  profiling_customers.py # profiling + trích mẫu theo cụm (seed 42)
src/etl/                 # (giai đoạn hiện thực) extract.py, transform.py, match.py, merge_service.py, dq_evaluate.py, load_dwh.py
dashboard/               # (giai đoạn hiện thực) app.py – ứng dụng làm sạch, report.py – dashboard K1–K3
tests/
```

## 5. Hướng dẫn cài đặt & chạy (đang hoàn thiện)
```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt      # cần có pandas, rapidfuzz
cp .env.example .env                 # điền thông tin kết nối PostgreSQL
# đặt customers_raw.csv (thư mục dataset/ trên LMS) vào data/raw/
python notebooks/profiling_customers.py data/raw/customers_raw.csv
```
**Nộp bài tập (TD-01):** một tệp PDF duy nhất, đúng tên `BT<số>_2374802010318_DuongDiemMy.pdf`; mở lại tệp sau khi nộp; link repo ở trang bìa bấm được; repo để public (hoặc đã mời giảng viên làm collaborator) và đã `git push` đủ tệp gốc.

**Tái lập (NFR-05):** mọi bước ngẫu nhiên dùng `seed = 42`; mẫu phát triển `data/processed/mau_cum_8000.csv` sinh lại giống hệt mỗi lần chạy.

## 6. Khai báo sử dụng công cụ AI
| Công cụ | Dùng vào việc gì | Cách tự kiểm chứng |
|---|---|---|
| Claude (Anthropic) | Rà soát hồ sơ Buổi 4 theo checklist BT1; viết và chạy script profiling; soạn bản nháp kiến trúc, mô hình dữ liệu, wireframe và các tệp `.drawio` | Chạy lại script profiling với seed 42 và đối chiếu từng con số ở mục 4.1, 4.5; mở từng tệp `.drawio` bằng draw.io để đối chiếu với hình; đọc lại, sửa câu chữ 4 câu lập luận và tự giải thích được GRAIN, SCD loại 2 |

Chi tiết: `docs/ai-disclosure.md`.
