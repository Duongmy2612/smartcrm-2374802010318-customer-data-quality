# Ảnh chụp kết quả chạy – Bài tập 3

Tên ảnh theo mã test case (slide buổi 14): `TC-xx.png` là lần chạy cuối của test case; `TC-xx-lan1-FAIL.png` là lần
chạy đầu bị FAIL (trước khi sửa bug). `PT-xx` là các bước của phép thử máy trắng (`docs/test-report.md` mục 4).

| Ảnh | Nội dung | Nơi chụp |
|---|---|---|
| `TC-09-lan1-FAIL.png` | TC-09 lần 1 ở commit `574bfd0`: ngày `31/02/2026`, `2026-02-30` vẫn CLEAN, `v_reject` 0 dòng → BUG-15 | Claude, môi trường thử Linux (đầu ra dòng lệnh vẽ thành ảnh) |
| `TC-12-lan1-FAIL.png` | TC-12 lần 1 ở commit `574bfd0`: kết nối dashboard dùng tài khoản `postgres`, đọc được `ops.stg_customer` → BUG-16 | Claude, môi trường thử Linux (đầu ra dòng lệnh vẽ thành ảnh) |
