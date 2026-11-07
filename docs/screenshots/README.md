# Ảnh kết quả chạy – Bài tập 3

Tên ảnh theo mã test case (slide buổi 14): `TC-xx.png` là lần chạy cuối của test case; `TC-xx-lan1-FAIL.png` là lần
chạy 1 bị FAIL (mã nguồn trước khi sửa bug). `PT-xx-…` là các bước của phép thử máy trắng (`docs/test-report.md`
mục 4, Deployment Guide mục 5) và của checklist bảo mật.

**Cách tạo ảnh hiện có.** Toàn bộ 22 ảnh là **một lần chạy liền** của script phép thử máy trắng trên môi trường thử
Linux của Claude, bằng Docker (hai ảnh gốc dựng lại cục bộ vì môi trường chặn registry): clone mới nhánh `main` ở
commit `7242ae4`, ngày 07/11/2026 (giờ UTC). Lệnh chạy thật; đầu ra dòng lệnh được lưu thành tệp văn bản rồi **vẽ
thành ảnh PNG** (không phải ảnh chụp màn hình), riêng `PT-06-dashboard.png` là ảnh chụp trình duyệt Chromium. Mỗi ảnh
có nhãn vàng ghi nơi chạy, commit và ngày, để không lẫn với ảnh chụp trên MacBook.

| Ảnh | Nội dung | Kết quả |
|---|---|---|
| `PT-01-hai-lenh.png` | Xóa dấu vết, clone vào thư mục trống, `cp .env.example .env`, `docker compose up -d --build` | mã thoát 0; db Healthy, pipeline Exited, dashboard Started |
| `PT-02-healthy.png` | `docker compose ps -a`, `curl …/_stcore/health` | db, dashboard `Up (healthy)`; pipeline `Exited (0)`; `ok` |
| `PT-03-du-lieu-mau.png` | Log pipeline, đếm `ops.stg_customer` theo trạng thái | 414 = 343 + 40 + 31; 88,41 → 95,79 |
| `PT-04-pytest.png` | `docker compose run --rm pipeline python -m pytest -q` | 194 passed, 3 skipped; bảng năm loại |
| `TC-09-lan1-FAIL.png`, `TC-12-lan1-FAIL.png` | Lần chạy 1: mã nguồn commit `574bfd0` (trước khi sửa) gắn vào ảnh Docker, test case của bản đang kiểm | TC-09 FAIL (ngày sai vẫn CLEAN → BUG-15); TC-12 FAIL (tài khoản của pipeline đọc được `ops` → BUG-16) |
| `TC-01.png` … `TC-12.png` | `docker compose run --rm pipeline python -m tests.tc_bt3 TC-xx` – lần chạy cuối | 12/12 PASS |
| `PT-05-chay-lai.png` | `docker compose up -d` lần hai | mọi bảng +0 |
| `PT-06-dashboard.png` | Dashboard K1 đọc kho qua tài khoản `dash_reader` | 95,79 / 88,41 / 414 |
| `PT-07-mat-csdl.png` | Dừng `db` rồi chạy pipeline (checklist mục 5; BUG-18 đã sửa) | câu báo chỉ lệnh `docker compose`, không lộ mật khẩu |
| `PT-08-pip-audit.png` | `pip-audit -r requirements.txt` trong container `python:3.11-slim` (checklist mục 7; BUG-17 đã sửa) | No known vulnerabilities found |

Lần chạy 1 gốc (07/11/2026, `.venv` trên môi trường thử, test case khi đó) cho cùng kết quả: TC-09, TC-12 FAIL; khi
đó kết nối dashboard dùng tài khoản `postgres`, trong Docker là `smartcrm` – đều là tài khoản của pipeline.

Em chạy lại toàn bộ trên MacBook bằng Docker Desktop (script `chup-anh-bt3.sh`) rồi thay các ảnh cùng tên tệp bằng
ảnh em chụp màn hình; khi đó đoạn "Cách tạo ảnh" ghi "MacBook của em · ảnh chụp màn hình" và nhãn vàng không còn.
