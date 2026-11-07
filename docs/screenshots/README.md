# Ảnh kết quả chạy – Bài tập 3

Tên ảnh theo mã test case (slide buổi 14): `TC-xx.png` là lần chạy cuối của test case; `TC-xx-lan1-FAIL.png` là lần
chạy đầu bị FAIL (trước khi sửa bug). `PT-xx-…` là các bước của phép thử máy trắng (`docs/test-report.md` mục 4,
Deployment Guide mục 5).

**Cách tạo ảnh hiện có.** Lệnh chạy thật; đầu ra dòng lệnh được lưu thành tệp văn bản rồi **vẽ thành ảnh PNG** (không
phải ảnh chụp màn hình), riêng `PT-06-dashboard.png` là ảnh chụp trình duyệt Chromium. Mỗi ảnh có nhãn vàng ghi nơi
chạy, commit và ngày, để không lẫn với ảnh chụp trên MacBook.

| Ảnh | Nội dung | Nơi chạy · cách tạo ảnh |
|---|---|---|
| `TC-09-lan1-FAIL.png` | TC-09 lần 1 ở commit `574bfd0`: ngày `31/02/2026`, `2026-02-30` vẫn CLEAN, `v_reject` 0 dòng → BUG-15 | Claude, môi trường thử Linux (`.venv`) · đầu ra dòng lệnh vẽ thành ảnh |
| `TC-12-lan1-FAIL.png` | TC-12 lần 1 ở commit `574bfd0`: kết nối dashboard dùng tài khoản `postgres`, đọc được `ops.stg_customer` → BUG-16 | như trên |
| `PT-01-hai-lenh.png` … `PT-05-chay-lai.png`, `PT-07-mat-csdl.png` | Phép thử máy trắng: hai lệnh; healthy; dữ liệu mẫu; pytest; chạy lại +0; mất CSDL | Claude, môi trường thử Linux, Docker (ảnh gốc dựng lại cục bộ vì registry bị chặn), commit ghi trên nhãn · đầu ra dòng lệnh vẽ thành ảnh |
| `TC-01.png` … `TC-12.png` | 12 test case chạy bằng `docker compose run --rm pipeline python -m tests.tc_bt3 TC-xx`, tất cả PASS | như trên |
| `PT-06-dashboard.png` | Dashboard K1 đọc kho qua tài khoản `dash_reader` | Claude, Docker như trên · ảnh chụp trình duyệt Chromium |

Em chạy lại toàn bộ trên MacBook bằng Docker Desktop rồi thay các ảnh cùng tên tệp bằng ảnh em chụp màn hình; khi
đó cột "Nơi chạy · cách tạo ảnh" ghi "MacBook của em · ảnh chụp màn hình" và nhãn vàng không còn.
