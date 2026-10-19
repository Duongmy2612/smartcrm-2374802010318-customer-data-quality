# Khai báo sử dụng công cụ AI

Sinh viên: Dương Diễm My – MSSV 2374802010318 · Luồng L7 – Chất lượng dữ liệu khách hàng · Track DA

## Bài tập 1 (nộp 09/10/2026) – giống Phụ lục C của bản PDF

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Tham khảo cách trình bày, rà soát nội dung và đề xuất hướng triển khai bài tập. Cụ thể, AI hỗ trợ rà soát hồ sơ Buổi 4 theo checklist, đề xuất chỉnh sửa tại Phụ lục B, xây dựng và chạy script profiling dữ liệu `customers_raw.csv`, soạn bản nháp mục 3, 4, 5, chỉnh sửa sơ đồ Use Case, tạo các tệp `.drawio`, Markdown cho repo và hỗ trợ dàn trang tài liệu. | Mục 1, 2 (cập nhật theo Phụ lục B), mục 3, 4, 5, Phụ lục A, B; `docs/*.drawio`, `docs/*.md`, `README.md`; `notebooks/profiling_customers.py` | Chạy lại script profiling với seed 42 và đối chiếu từng con số ở mục 4.1, 4.5; mở từng tệp `.drawio` bằng draw.io để đối chiếu với hình; đọc lại, sửa câu chữ 4 câu lập luận và tự giải thích được GRAIN, SCD loại 2. |

**Tôi xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.**

Họ tên: Dương Diễm My · MSSV: 2374802010318 · Ngày: 09/10/2026

## Bản chỉnh sửa BT1 sau phản hồi (19/10/2026, buổi 8)

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Theo phản hồi BT1: rút gọn bản PDF từ 27 xuống 13 trang (giữ nguyên thiết kế), soạn nhật ký thay đổi TD-01 – TD-05, chuyển Phụ lục A, B và khung K4 vào repo, dọn repo (`.venv`, `.env`), chuẩn bị các commit để em đẩy hồ sơ BT1 lên repo. | `BT1_2374802010318_DuongDiemMy.pdf`; `docs/thay-doi-thiet-ke.md`, `docs/ra-soat-bt1.md`, `docs/srs.md` mục 8; `.gitignore`, `.env.example` | Đối chiếu tự động mọi con số giữa bản 13 trang và bản 27 trang: không con số nào bị đổi. [ ] Em đọc lại cả 13 trang và tự giải thích được TD-01 – TD-05. |


## Sprint 1 – buổi 8 (19/10/2026): khai báo theo từng phần (TD-05)

Mỗi dòng ghi đúng phần AI soạn nháp và việc em phải tự làm để kiểm chứng. Em chỉ đánh dấu [x] ô nào đã thật sự làm; ô chưa đánh dấu là việc còn nợ.

| Phần | AI (Claude) đã làm | Em kiểm chứng |
|---|---|---|
| `sql/001_ops_schema.sql` | Soạn DDL 6 bảng từ từ điển dữ liệu `docs/data-requirements.md` mục 5.1 | [ ] Đối chiếu từng cột, kiểu, ràng buộc với mục 5.1 · [ ] Chạy trên PostgreSQL của máy em, mở bảng bằng psql/pgAdmin |
| `src/etl/extract.py` | Soạn đọc tệp, kiểm cột, SHA-256, ghi `load_batch` và `stg_customer` | [ ] Tự giải thích vì sao đọc `dtype=str` và `keep_default_na=False` · [ ] Thử tệp thiếu cột và nạp lại cùng tệp, thấy đúng thông báo |
| `src/etl/transform.py` | Soạn chuẩn hóa số (QT-02), họ tên (FR-03), mã lỗi, phân loại CLEAN / PENDING_DUP / ERROR, CSV hồ sơ lỗi | [ ] Tự viết thêm ít nhất 1 test cho một dạng số em tự nghĩ ra · [ ] Giải thích được vì sao hồ sơ lặp không tạo hồ sơ mới (QT-01) |
| `src/etl/dq_evaluate.py` | Soạn 6 quy tắc với mẫu số theo phạm vi áp dụng, chỉ số QL7-06 | [ ] Chạy pipeline trên máy em, ra 87,20 → 94,76 · [ ] Giải thích được mẫu số của DQ-02 và vì sao DQ-05 so theo `phone_norm` |
| `src/pipeline.py`, `src/db.py`, `src/config.py` | Soạn điều phối UC1 trong một giao dịch, mã thoát, báo cáo | [ ] Giải thích được `with engine.begin()` tự ROLLBACK khi lỗi |
| `tests/` | Soạn 51 test (46 chạy không cần CSDL; 5 test tích hợp cần CSDL `smartcrm_test`) | [ ] Chạy `pytest -q` trên máy em; không có test nào failed |
| `README.md`, `docs/thay-doi-thiet-ke.md` (TD-06 – TD-11), `docs/sprint1/` | Soạn nội dung; ảnh kết quả là ảnh dựng lại từ log chạy trên môi trường thử (Linux, PostgreSQL 16), không phải ảnh chụp trên máy em | [ ] Đọc và đồng ý từng TD · [ ] Chạy lại trên MacBook, thay ảnh bằng ảnh chụp màn hình của em, điền dòng đo NFR-01 trên máy em ở README mục 6 |
