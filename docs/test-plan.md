# Test Plan rút gọn – Bài tập 3

Dương Diễm My – 2374802010318 · L7 – Chất lượng dữ liệu khách hàng · Track DA · tag `v1.0`
Kết quả chạy: `docs/test-report.md` · lỗi đã sửa: `docs/bug-log.md` · mã test case: `tests/tc_bt3.py`

## 1. Phạm vi kiểm thử và phần chủ ý KHÔNG kiểm

**Kiểm** – mọi thứ hệ thống đang làm khi chạy lệnh `python -m src.pipeline` (README mục 3, Docker: dịch vụ `pipeline`):

- năm quy tắc nghiệp vụ đã hiện thực: **QT-02** chuẩn hóa số điện thoại · **QT-01** hồ sơ lặp số không tạo khách hàng
  mới · **QL7-03** điểm tương đồng (cùng ngưỡng **QL7-02** = 85) · **QL7-04** hồ sơ lỗi ở lại bảng tạm kèm lý do ·
  **QL7-06** chỉ số mức độ sạch;
- kiểm tra tệp đầu vào: thiếu cột (AC1.3), nạp lại cùng tệp (AC1.4), ngày tạo phải hợp lệ (data-requirements mục 3);
- chất lượng dữ liệu theo từng cột có ngưỡng riêng (D3) và bảo mật của kết nối dashboard (NFR-07);
- đóng gói: phép thử máy trắng **PT-01** theo `docs/deployment-guide.md` (dựng bằng hai lệnh, mục 5 có tám bước kiểm
  tra) cộng ba bước kiểm checklist bảo mật: quét secret, quét lỗ hổng phụ thuộc (`pip-audit`), gây lỗi mất CSDL.

**Chủ ý KHÔNG kiểm**, kèm lý do:

| Phần | Lý do |
|---|---|
| UC5 Gộp / Giữ riêng, K4, sửa quy tắc trên giao diện (UC6) | Chưa hiện thực (TD-27, TD-41) – không kiểm thứ hệ thống chưa làm |
| Bố cục, màu sắc của dashboard | Chỉ hiển thị, không có quy tắc nghiệp vụ. Số liệu dashboard đọc được kiểm ở kho (TC-05, TC-10) và 31 test của `src/doc_kho.py`; ba trạng thái đã chụp ở BT2 |
| Hiệu năng NFR-01, NFR-02 | Đề BT3 không yêu cầu; NFR-01 đã đo ở BT1 – BT2, pipeline vẫn in thời gian mỗi lần chạy |
| Kiểm thử xâm nhập, độ phủ cao, CI/CD đầy đủ | Đề BT3 mục 1 ghi "KHÔNG yêu cầu" |
| `notebooks/profiling_customers.py` | Công cụ phân tích dùng một lần ở BT1, không thuộc luồng chạy |

## 2. Loại test và số lượng mỗi tầng

| Tầng | Số lượng | Kiểm gì | Chạy bằng |
|---:|---:|---|---|
| Đơn vị (hàm thuần, không cần CSDL) | 171 | extract, transform, dq_evaluate, match, danh_gia_match, doc_kho, ranh giới lớp, khóa / mật khẩu | `python -m pytest -q` |
| Tích hợp (PostgreSQL thật, CSDL `smartcrm_test`) | 14 | ghi `ops` → `dwh`, chạy lại DDL, cấp quyền `dash_reader`, từ điển dữ liệu khớp CSDL | `python -m pytest -q` |
| Hệ thống – **12 test case BT3** | 12 | gọi lệnh thật như người dùng, đếm bảng trước / sau | `python -m tests.tc_bt3 TC-xx` (cũng nằm trong pytest) |
| Đầu-cuối đóng gói – PT-01 | 1 | máy trắng → hai lệnh → tám bước kiểm tra của Guide | Deployment Guide mục 5; GitHub Actions mỗi lần push |

Tổng 197 test trong một lệnh `python -m pytest -q`. Phân bổ 12 test case theo năm loại của đề BT3 mục 2.2:

| Loại | Số | Test case | Yêu cầu tối thiểu |
|---|---:|---|---|
| Luồng đúng | 5 | TC-01 (QT-02) · TC-02 (QT-01) · TC-03 (QL7-03) · TC-04 (QL7-04) · TC-05 (QL7-06) | 1 test cho mỗi quy tắc |
| Giá trị biên | 2 | TC-06 điểm 85,43 · TC-07 điểm 84,97 – hai bên ngưỡng 85 | 2, hai bên một ranh giới |
| Dữ liệu sai | 2 | TC-08 tệp thiếu cột · TC-09 ngày tạo sai | 2 |
| Chất lượng dữ liệu / bảo mật | 2 | TC-10 cố ý vi phạm ngưỡng · TC-12 tài khoản dashboard không đọc được dữ liệu cá nhân | 1 |
| Tái lập | 1 | TC-11 chạy lại cùng tệp | 1 |

## 3. Tiêu chí thành công ĐO ĐƯỢC

1. 12/12 test case PASS ở tag `v1.0`, trên Docker và trên MacBook (cột "Kết quả thực tế" có số đếm trước / sau).
2. Mỗi quy tắc nghiệp vụ đã hiện thực có ít nhất 1 test luồng đúng; ngưỡng 85 có 2 test ở hai phía.
3. `python -m pytest -q`: **0 failed** (Docker: 194 passed, 3 skipped – 3 test hồi quy cần dữ liệu thật không có trong repo).
4. **0 bug Critical đang mở**; bug Major phải sửa, hoặc ghi lý do và hướng xử lý.
5. PT-01: mọi bước đúng kết quả mong đợi ở Guide mục 5; chạy lại lần hai +0 ở cả 8 bảng đích.
6. `pip-audit -r requirements.txt`: 0 lỗ hổng đã biết; quét repo và lịch sử commit: 0 secret.

**"Làm sao biết đã kiểm thử ĐỦ?"** – L7 có năm quy tắc nghiệp vụ đã hiện thực; mỗi quy tắc có một test luồng đúng
(TC-01 – TC-05), ngưỡng 85 – ranh giới quan trọng nhất của phát hiện trùng – có hai test ở hai phía (TC-06, TC-07).
Thêm hai test dữ liệu sai (TC-08, TC-09), một test chất lượng (TC-10), một test bảo mật (TC-12) và một test tái lập
(TC-11). Em cố ý không kiểm UC5, K4 vì chưa hiện thực, và không kiểm bố cục dashboard vì nó không có quy tắc nghiệp
vụ – đã ghi ở mục 1.

## 4. Môi trường và dữ liệu thử

- **Nơi chạy:** container của `docker compose` (Python 3.11, PostgreSQL 16) – lệnh ở Guide mục 5; hoặc MacBook với
  `.venv` Python 3.11 và PostgreSQL 14 (README mục 3). GitHub Actions chạy lại PT-01 và pytest ở mỗi lần push.
- **CSDL:** test case dùng CSDL riêng `smartcrm_test` (`DB_NAME_TEST`), không đụng CSDL `smartcrm`. Docker tạo CSDL
  này ở lần dựng đầu (`docker/initdb/`). **Trước MỖI test case**, `MoiTruong.lam_sach()` xóa schema `ops`, `dwh` nên kết
  quả không phụ thuộc dữ liệu còn sót trên máy; hệ thống tự tạo lại bảng khi chạy.
- **Dữ liệu thử – toàn bộ là dữ liệu GIẢ, có trong repo:** `tests/du_lieu_tc/` (9 tệp, 2 – 10 dòng, thiết kế để tính
  tay) và `data/mau/` (414 dòng sinh bằng script, seed 42, cùng 3 tệp lỗi). Ba test hồi quy dùng tệp LMS thật chỉ chạy
  khi máy có tệp đó; không test nào cần dữ liệu riêng trên máy em.
- **Kỹ thuật chọn dữ liệu:** *phân vùng tương đương* – TC-01 lấy bốn cách viết số (`+84 …`, dấu chấm, `84…`, gạch nối);
  TC-04 lấy ba loại hồ sơ lỗi và một hồ sơ đúng. *Giá trị biên* – điểm = 0,6 × độ giống số + 0,4 × độ giống tên. Hai số
  10 chữ số khác nhau chỉ có độ giống 90, 80, …, nên điểm đúng 85,00 đòi độ giống tên đúng 77,5 – em không tìm được cặp
  tên tiếng Việt thông thường nào cho giá trị đó. Vì vậy em lấy hai cặp sát ngưỡng nhất ở hai phía, cùng một hồ sơ gốc:
  85,43 (TC-06) và 84,97 (TC-07). Trường hợp "điểm BẰNG ngưỡng vẫn tạo cặp" được kiểm ở test đơn vị `la_cap_fuzzy`.
- **Tính tay cho TC-05** (10 hồ sơ; trọng số và phạm vi theo data-requirements mục 6):

| Quy tắc | Trọng số | Phạm vi (mẫu số) | Đạt TRƯỚC | Đạt SAU |
|---|---:|---|---:|---:|
| DQ-01 số không trống | 0,25 | 10 hồ sơ | 9/10 | 9/10 |
| DQ-02 số đúng mẫu | 0,25 | 9 hồ sơ có số | 6/9 (thô) | 8/9 (sau chuẩn hóa) |
| DQ-03 họ tên không trống | 0,15 | 10 | 10/10 | 10/10 |
| DQ-04 họ tên hợp lệ | 0,10 | 10 | 10/10 | 10/10 |
| DQ-05 số không trùng | 0,20 | 8 hồ sơ có số hợp lệ | 7/8 | 7/8 |
| DQ-06 email đúng mẫu | 0,05 | 3 hồ sơ có email | 2/3 | 2/3 |

TRƯỚC = 100 × (0,25 × 0,9 + 0,25 × 6/9 + 0,15 + 0,10 + 0,20 × 0,875 + 0,05 × 2/3) = **85,00**;
SAU = TRƯỚC + 100 × 0,25 × (8/9 − 6/9) = **90,56**. Số dòng: 7 CLEAN (dòng 1, 2, 3, 4, 8, 9, 10) · 1 PENDING_DUP
(dòng 6 trùng số dòng 1) · 2 ERROR (dòng 5 thiếu số, dòng 7 số `12345`).
