# Ảnh chụp kết quả chạy – Bài tập 3

Tên ảnh theo mã test case (slide buổi 14): `TC-xx.png` là lần chạy cuối của test case; `TC-xx-lan1-FAIL.png` là lần
chạy đầu bị FAIL (trước khi sửa bug). `PT-xx-…` là các bước của phép thử máy trắng (`docs/test-report.md` mục 4,
Deployment Guide mục 5). Mỗi ảnh có nhãn vàng ghi nơi chạy.

| Ảnh | Nội dung | Nơi chụp |
|---|---|---|
| `TC-09-lan1-FAIL.png` | TC-09 lần 1 ở commit `574bfd0`: ngày `31/02/2026`, `2026-02-30` vẫn CLEAN, `v_reject` 0 dòng → BUG-15 | Claude, môi trường thử Linux (`.venv`), đầu ra dòng lệnh vẽ thành ảnh |
| `TC-12-lan1-FAIL.png` | TC-12 lần 1 ở commit `574bfd0`: kết nối dashboard dùng tài khoản `postgres`, đọc được `ops.stg_customer` → BUG-16 | như trên |
| `PT-01-hai-lenh.png` … `PT-05-chay-lai.png`, `PT-07-mat-csdl.png` | Phép thử máy trắng: hai lệnh; healthy; dữ liệu mẫu; pytest 194 passed; chạy lại +0; mất CSDL | Claude, môi trường thử Linux, Docker (ảnh gốc dựng lại cục bộ), commit `e3c7a28`, đầu ra dòng lệnh vẽ thành ảnh |
| `TC-01.png` … `TC-12.png` | 12 test case chạy bằng `docker compose run --rm pipeline python -m tests.tc_bt3 TC-xx`, tất cả PASS | như trên |
| `PT-06-dashboard.png` | Dashboard K1 đọc kho qua tài khoản `dash_reader` | Claude, Chromium trên môi trường thử, Docker |

Em chạy lại toàn bộ trên MacBook bằng Docker Desktop rồi thay các ảnh `PT-…`, `TC-01` … `TC-12` bằng ảnh em chụp
(cùng tên tệp); khi đó cột "Nơi chụp" ghi MacBook.
