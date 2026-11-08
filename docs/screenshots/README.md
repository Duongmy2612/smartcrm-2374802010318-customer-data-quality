# Ảnh kết quả chạy – Bài tập 3

Tên ảnh theo mã test case (slide buổi 14): `TC-xx.png` là lần chạy cuối của test case; `TC-xx-lan1-FAIL.png` là lần
chạy 1 bị FAIL (mã nguồn trước khi sửa bug). `PT-xx-…` là các bước của phép thử máy trắng (`docs/test-report.md`
mục 4, Deployment Guide mục 5) và của checklist bảo mật.

**Nơi chụp.** Toàn bộ 22 ảnh là **ảnh chụp màn hình trên MacBook của em** (Docker Desktop, ngày 08/11/2026), làm theo
đúng thứ tự của đề BT3 mục 2.4: thư mục trống `~/bt3`, clone nhánh `main` ở commit `c58cd79`, `cp .env.example .env`,
`docker compose up -d --build`, các bước kiểm tra của Guide mục 5, lần chạy 1 trên mã nguồn `574bfd0`, 12 test case,
chạy lại, mất CSDL, quét lỗ hổng. Ảnh giữ nguyên độ phân giải gốc (Retina, rộng 1 196 – 2 684 px); chỉ cắt bỏ dòng
nhắc chụp, con trỏ và dòng bị cắt dở ở mép ảnh; ảnh lần chạy 1 chụp chung hai test case nên được tách làm hai tệp.

| Ảnh | Lệnh chạy | Kết quả |
|---|---|---|
| `PT-01-hai-lenh.png` | `docker builder prune -af` · `git clone --branch main …` · `cp .env.example .env` · `docker compose up -d --build` | ảnh `smartcrm-l7:local` Built; db Healthy; pipeline Exited; dashboard Started |
| `PT-02-healthy.png` | `docker compose ps -a` · `curl -s http://localhost:8501/_stcore/health` | dashboard, db `Up (healthy)`; pipeline `Exited (0)`; `ok` |
| `PT-03-du-lieu-mau.png` | `docker compose logs pipeline` · đếm `ops.stg_customer` theo trạng thái | 414 = 343 + 40 + 31; 88,41 → 95,79; CLEAN 343 · ERROR 31 · PENDING_DUP 40 |
| `PT-04-pytest.png` | `docker compose run --rm pipeline python -m pytest -q` | 194 passed, 3 skipped; bảng năm loại |
| `TC-09-lan1-FAIL.png`, `TC-12-lan1-FAIL.png` | `git archive 574bfd0` + test case bản đang kiểm, gắn vào ảnh Docker: `docker compose run --rm -e DASH_DB_USER= -e DASH_DB_PASSWORD= -v ~/bt3-cu:/app pipeline python -m tests.tc_bt3 TC-09` (và TC-12) | TC-09 FAIL (ngày sai vẫn CLEAN → BUG-15); TC-12 FAIL (tài khoản `smartcrm` của pipeline đọc được `ops` → BUG-16) |
| `TC-01.png` … `TC-12.png` | `docker compose run --rm pipeline python -m tests.tc_bt3 TC-xx` – lần chạy cuối | 12/12 PASS |
| `PT-05-chay-lai.png` | `docker compose up -d` lần hai · `docker compose logs pipeline` | tám bảng đích +0 |
| `PT-06-dashboard.png` | mở http://localhost:8501 (tài khoản `dash_reader`) | K1: SAU 95,79 · TRƯỚC 88,41 · 414 hồ sơ |
| `PT-07-mat-csdl.png` | `docker compose stop db` · chạy pipeline · `docker compose start db` (checklist mục 5; BUG-18 đã sửa) | câu báo chỉ lệnh `docker compose`, không lộ mật khẩu |
| `PT-08-pip-audit.png` | `pip-audit -r requirements.txt` trong container `python:3.11-slim` (checklist mục 7; BUG-17 đã sửa) | No known vulnerabilities found |

Trước đó, cùng các bước đã chạy trên môi trường thử Linux của Claude (lần 1 – 2 của Test Report) và chạy lại ở mỗi lần
push trên GitHub Actions, cho cùng kết quả.
