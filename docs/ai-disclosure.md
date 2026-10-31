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
| Claude (Anthropic) | Theo phản hồi BT1: rút gọn bản PDF từ 27 xuống 13 trang (giữ nguyên thiết kế), soạn nhật ký thay đổi TD-01 – TD-05, chuyển Phụ lục A, B và khung K4 vào repo, dọn repo (`.venv`, `.env`), chuẩn bị các commit để em đẩy hồ sơ BT1 lên repo. | `BT1_2374802010318_DuongDiemMy.pdf`; `docs/thay-doi-thiet-ke.md`, `docs/ra-soat-bt1.md`, `docs/srs.md` mục 8; `.gitignore`, `.env.example` | Đối chiếu tự động mọi con số giữa bản 13 trang và bản 27 trang: không con số nào bị đổi. [x] Em đọc lại cả 13 trang và tự giải thích được TD-01 – TD-05. |


## Bản nộp lại BT1 (21/10/2026)

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Theo nhận xét chấm BT1: rút bản PDF từ 13 xuống 9 trang (đặt hình và chữ hai cột, viết gọn câu chữ, giữ nguyên thiết kế), soạn TD-13, chuẩn bị commit cập nhật repo. | `BT1_2374802010318_DuongDiemMy.pdf`; `docs/thay-doi-thiet-ke.md` (TD-13), `docs/srs.md` mục 8, `README.md` | Đối chiếu tự động mọi con số giữa bản 9 trang với bản 13 trang và bản 09/10: không con số nào bị đổi. [x] Em đọc lại cả 9 trang và tự giải thích được từng thay đổi ở TD-13. |

## Sprint 1 – buổi 8 (19/10/2026): khai báo theo từng phần (TD-05)

Mỗi dòng ghi đúng phần AI soạn nháp và việc em phải tự làm để kiểm chứng. Em chỉ đánh dấu [x] ô nào đã thật sự làm; ô chưa đánh dấu là việc còn nợ.

| Phần | AI (Claude) đã làm | Em kiểm chứng |
|---|---|---|
| `sql/001_ops_schema.sql` | Soạn DDL 6 bảng từ từ điển dữ liệu `docs/data-requirements.md` mục 5.1 | [x] Đối chiếu từng cột, kiểu, ràng buộc với mục 5.1 · [x] Chạy trên PostgreSQL của máy em, mở bảng bằng psql/pgAdmin |
| `src/etl/extract.py` | Soạn đọc tệp, kiểm cột, SHA-256, ghi `load_batch` và `stg_customer` | [x] Tự giải thích vì sao đọc `dtype=str` và `keep_default_na=False` · [x] Thử tệp thiếu cột và nạp lại cùng tệp, thấy đúng thông báo |
| `src/etl/transform.py` | Soạn chuẩn hóa số (QT-02), họ tên (FR-03), mã lỗi, phân loại CLEAN / PENDING_DUP / ERROR, CSV hồ sơ lỗi | [x] Tự viết thêm ít nhất 1 test cho một dạng số em tự nghĩ ra · [x] Giải thích được vì sao hồ sơ lặp không tạo hồ sơ mới (QT-01) |
| `src/etl/dq_evaluate.py` | Soạn 6 quy tắc với mẫu số theo phạm vi áp dụng, chỉ số QL7-06 | [x] Chạy pipeline trên máy em, ra 87,20 → 94,76 · [x] Giải thích được mẫu số của DQ-02 và vì sao DQ-05 so theo `phone_norm` |
| `src/pipeline.py`, `src/db.py`, `src/config.py` | Soạn điều phối UC1 trong một giao dịch, mã thoát, báo cáo | [x] Giải thích được `with engine.begin()` tự ROLLBACK khi lỗi |
| `tests/` | Soạn 51 test (46 chạy không cần CSDL; 5 test tích hợp cần CSDL `smartcrm_test`) | [x] Chạy `pytest -q` trên máy em; không có test nào failed |
| `README.md`, `docs/thay-doi-thiet-ke.md` (TD-06 – TD-12), `docs/sprint1/` | Soạn nội dung; ảnh kết quả là ảnh dựng lại từ log chạy trên môi trường thử (Linux, PostgreSQL 16), không phải ảnh chụp trên máy em | [x] Đọc và đồng ý từng TD · [x] Chạy lại trên MacBook, thay ảnh bằng ảnh chụp màn hình của em, điền dòng đo NFR-01 trên máy em ở README mục 6 |

## Sprint 2 – buổi 10 (24/10/2026): khai báo theo từng phần (TD-05)

Như Sprint 1: AI soạn bản nháp và chạy thử trên môi trường thử (Linux, PostgreSQL 16); em chỉ đánh dấu [x] ô nào đã thật sự làm.

| Phần | AI (Claude) đã làm | Em kiểm chứng |
|---|---|---|
| `sql/002_dwh_schema.sql` | Soạn DDL 5 bảng kho, 2 view từ từ điển dữ liệu `docs/data-requirements.md` mục 5.2 | [x] Đối chiếu từng cột, GRAIN, công thức `v_rule_rate`, `v_batch_score` với mục 5.2 · [x] Mở hai view bằng psql/pgAdmin trên máy em |
| `src/etl/match.py` | Soạn name_key, blocking 5 số đầu/cuối, điểm tương đồng QL7-03, cặp EXACT_PHONE k − 1, FUZZY giữa hồ sơ đại diện (TD-18) | [x] Tính tay điểm của một cặp FUZZY thật trong `ops.dup_candidate` và so với cột `score` · [x] Giải thích được vì sao blocking bỏ sót cặp ở `test_blocking_khong_so_hai_so_khac_ca_nua_dau_lan_nua_cuoi` |
| `src/etl/load_dwh.py` | Soạn nạp dimension theo khóa nghiệp vụ, SCD loại 2 của `dim_rule`, nạp fact không nhân đôi, bảng đối soát | [x] Chạy `python -m src.etl.load_dwh` hai lần trên máy em, thấy `+0` · [x] Giải thích được dòng đối soát "Hồ sơ thô ↔ mẫu số DQ-01" |
| `src/pipeline.py` (UC3, hai giao dịch), `src/db.py` (kết nối chỉ đọc), `sql/003` (trigger) | Soạn ghép UC1 → UC3, thông báo khi UC3 lỗi (TD-17), `measured_at` theo đồng hồ CSDL (TD-16), trigger `updated_at` (TD-21) | [x] Giải thích được vì sao UC3 là giao dịch thứ hai |
| `src/doc_kho.py`, `dashboard/report.py` | Soạn truy vấn chỉ đọc, QT-14, ba trạng thái, K1 – K3 có mốc tham chiếu và dòng ghi nguồn | [x] Mở dashboard trên máy em, thử người xem `ql.mm001` để thấy trạng thái rỗng · [x] Tắt PostgreSQL để thấy trạng thái lỗi, bật lại rồi bấm Thử lại |
| `tests/` (43 test mới) | Soạn test cho `match.py`, `load_dwh.py`, `doc_kho.py` và luồng UC1 → UC3 | [x] Chạy `python -m pytest -q` trên máy em, ra `95 passed` (hoặc `94 passed, 1 skipped` nếu chưa sinh mẫu 8.000 dòng) · [x] Tự viết thêm ít nhất 1 test cho một cặp họ tên em tự nghĩ ra |
| `README.md` mục 3, 6; `docs/thay-doi-thiet-ke.md` TD-14 – TD-21; `docs/sprint2/` | Soạn nội dung; ảnh trong `docs/sprint2/` là ảnh em chụp trên MacBook ngày 25/10/2026 (AI chỉ lấy ảnh từ báo cáo em gửi để đưa vào repo); nhật ký `thu-clone-moi.txt` là của môi trường thử | [x] Đọc và đồng ý từng TD · [x] Clone repo vào thư mục mới trên MacBook, làm đúng 12 bước mục 3 · [x] Thay ảnh `docs/sprint2/` bằng ảnh chụp màn hình của em, điền dòng đo NFR-01 phần 2 trên máy em ở README mục 6.2 |


## Bài tập 2 – buổi 12 (31/10/2026): khai báo theo đề BT2 mục 2.6

Bảng theo đúng bốn cột của đề BT2. Em nhờ Claude đối chiếu repo với bảng tiêu chí BT2, sửa mã, viết test và tài
liệu, chạy thử trên môi trường thử của Claude (Linux), commit và đẩy lên GitHub (các commit từ `6a69241f`; commit
chiều 31/10 có thêm dòng `Co-Authored-By: Claude`), nên khai báo từng phần dưới đây. Phần em tự làm: gắn tag
`v0.2`; rà lại nhãn 300 cặp NFR-03; chạy lại trên MacBook theo README và chụp các ảnh dòng lệnh của báo cáo PDF. Sáu
ảnh dashboard (Hình 5.1 – 5.6) do Claude chụp trên môi trường thử Linux – ghi rõ ở dòng riêng dưới đây và trong báo cáo. Cột cuối có hai phần: việc đã kiểm
chứng bằng máy (test, lệnh chạy) và ô [ ] em tự làm – em chỉ đánh [x] ô nào đã thật sự làm, trước khi gắn tag lần
cuối.

| Công cụ | Dùng vào việc gì | Áp dụng ở tệp / hàm nào | Em đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Tách mọi lệnh đọc/ghi CSDL ra pha load (TD-22) | `src/etl/load_ops.py` (toàn bộ); `src/pipeline.py`: `chay_uc3`, `chay_lai_uc3`, `mo_ket_noi`; bỏ phần CSDL ở `extract.py`, `transform.py`, `dq_evaluate.py`, `match.py` | Máy: 95 test cũ vẫn PASS; `tests/test_ranh_gioi_lop.py` PASS; `grep -n "sqlalchemy\|INSERT INTO" src/etl/transform.py` không còn kết quả. [x] Em mở `transform.py` và `load_ops.py`, chỉ được hàm nào thuộc pha nào |
| Claude (Anthropic) | Sáu hàm kiểm chất lượng trả về số dòng lỗi, tỉ lệ lỗi (TD-24) | `src/etl/dq_evaluate.py`: `kiem_dq01_…` – `kiem_dq06_…`, `HAM_KIEM`, `KetQua.so_loi`, `KetQua.ti_le_loi` | Máy: số đo trên dữ liệu mẫu không đổi trước/sau khi tách (88,41 → 95,79); `test_sau_ham_kiem_tra_ve_so_dong_loi_va_ti_le_loi` PASS. [x] Em giải thích được mẫu số của DQ-02 và vì sao DQ-05 so theo `phone_norm` |
| Claude (Anthropic) | Chạy lại cùng tệp: cảnh báo, mọi bảng +0, mã thoát 0 (TD-25) | `src/pipeline.py`: `_tep_da_nap`, `_in_bang_dich`; `load_ops.dem_dong_bang_dich` | Máy: chạy lệnh luồng chính hai lần, lần hai in +0 ở 8 bảng đích, mã thoát 0 (ảnh trong báo cáo PDF, Hình 3.2); `test_chay_lai_bang_lenh_tra_ma_0_va_khong_nhan_doi` PASS. [x] Em tự chạy lại hai lần trên MacBook |
| Claude (Anthropic) | Bảng reject `ops.v_reject` (TD-23) | `sql/004_v_reject.sql`; `load_ops.doc_reject` | Máy: `test_bang_reject_co_dong_va_ly_do_cho_nguoi_doc`, `test_ly_do_trong_view_reject_khop_transform` PASS; truy vấn view bằng psql (báo cáo PDF, Hình 3.4). [x] Em chạy câu `SELECT … FROM ops.v_reject` trên MacBook và giải thích vì sao reject là view, không phải bảng thứ hai |
| Claude (Anthropic) | Dữ liệu mẫu giả và script sinh (TD-26) | `scripts/sinh_du_lieu_mau.py`; `data/mau/*.csv` | Máy: `test_tep_mau_sinh_lai_dung_tung_byte`, `test_du_lieu_mau_ra_dung_so_lieu_readme` PASS. [x] Em mở `customers_mau.csv`, tìm được một hồ sơ lặp và một cặp FUZZY |
| Claude (Anthropic) | Bộ kiểm thử thêm cho BT2 và cách in số test theo ba loại | `tests/test_ranh_gioi_lop.py`, `tests/test_du_lieu_mau.py`; test mới trong `test_transform.py`, `test_dq_evaluate.py`, `test_pipeline.py`, `test_pipeline_csdl.py`; `pytest.ini`; `tests/conftest.py` (`pytest_terminal_summary`) | Máy: `python -m pytest -q` → 139 passed, 2 skipped (2 test cần dữ liệu thật của LMS), in số test PASS theo ba loại. [x] Em đọc một test mỗi loại và nói được nó kiểm gì |
| Claude (Anthropic) | Tài liệu BT2 | `README.md`; `docs/thay-doi-thiet-ke.md` TD-22 – TD-31; `docs/bug-log.md` BUG-07 – BUG-12; `docs/architecture-thuc-te.html` và ảnh; `docs/bt2/` | Đối chiếu từng lệnh README bằng phép thử clone vào thư mục mới (`docs/bt2/thu-clone-moi.txt`). [x] Em đọc và đồng ý TD-22 – TD-31 |
| Claude (Anthropic) | Chạy thử trên môi trường thử, commit, đẩy lên GitHub | lịch sử commit; `docs/bt2/thu-clone-moi.txt` | Nhật ký phép thử thư mục trống trên môi trường thử của Claude (Linux, Python 3.11, PostgreSQL 16) – không phải MacBook của em. [x] Em clone tag `v0.2` trên MacBook và chạy lại đủ 12 bước theo README |
| Claude (Anthropic) | Rà soát lần cuối, sửa BUG-09 – BUG-12: tệp lỗi bị TỪ CHỐI rõ ràng (TD-28), `la_trong` sang `tien_ich.py` (TD-29), mốc cho thẻ số và câu đọc K3 (TD-30), `DB_USER` trống và README bước 3, 6 (TD-31) | `src/etl/extract.py` `doc_tep`; `src/etl/tien_ich.py`; `src/doc_kho.py` `cau_fuzzy_thap_nhat`, `moc_ti_le_loi`; `dashboard/report.py`; `src/db.py`; `scripts/sinh_du_lieu_mau.py`; test mới trong `test_extract.py`, `test_du_lieu_mau.py`, `test_doc_kho.py` | Máy: 139 passed, 2 skipped; ba tệp lỗi trong `data/mau/` bị TỪ CHỐI mã 2; Python 3.13 cũng PASS. [x] Em chạy ba tệp lỗi trên MacBook và giải thích vì sao trước đây tệp chỉ có tiêu đề được 100 điểm |
| Claude (Anthropic) | Hướng dẫn chạy trên macOS và Windows trong README (mục 2, 3.1 – 3.3, 5) | `README.md` | Máy: phần khác macOS ở mã nguồn – đăng nhập bằng tài khoản `postgres` có mật khẩu, CSDL tạo bằng UTF-8 – chạy trên môi trường thử Linux: luồng chính, chạy lại +0, 139 passed. Các lệnh Windows chưa chạy trên máy Windows thật |
| Claude (Anthropic) | Soạn bản PDF BT2 đầu tiên (khung chữ, bảng) | bản PDF đầu (không nộp – thay bằng bản dựng lại ở TD-33) | Không áp dụng |
| Claude (Anthropic) – phiên chat riêng | Nạp lại dữ liệu thật `customers_raw.csv` vào CSDL mới trên môi trường thử Linux (mã giống tag `v0.2`) và chụp 6 ảnh dashboard bằng trình duyệt Chromium: K1 – K3 đủ nét (ảnh K1 – K3 em chụp trước đó chỉ rộng khoảng 600 điểm ảnh, in ra bị mờ) và ba trạng thái đang tải · rỗng · lỗi | `docs/bt2/09` – `14-dashboard-*.png`; báo cáo Hình 5.1 – 5.6 | Số trên ảnh khớp số em chạy trên MacBook: 87,20 → 94,76, 11.637 cặp (ảnh dashboard em chụp ở buổi 10: `docs/sprint2/dashboard-*.png`). Không phải ảnh chụp trên máy em – ghi ở chú thích và Phụ lục báo cáo. [ ] Em mở dashboard trên MacBook và thấy đủ ba trạng thái như ảnh |
| Claude (Anthropic) | Kiểm chứng NFR-03 theo nhận xét BT1 (TD-32): thiết kế khung cặp 5 tầng và cách chọn 300 cặp, viết mã, test, tài liệu | `src/etl/danh_gia_match.py` (`khung_cap`, `chon_mau`, `kiem_phieu_nhan`, `tinh_chi_so`, `quet_nguong`); `src/kiem_chung_nfr03.py`; `scripts/sinh_du_lieu_mau.py` (ghi `nhan_dung_mau.csv`); `tests/test_danh_gia_match.py`; README bước 13, mục 5, 6; TD-32, TD-33; BUG-13, BUG-14 | Máy: bản clone mới `155 passed, 3 skipped`; trên tệp thật T1 = 11.625, T2 = 12 khớp đúng số cặp pipeline ghi (test hồi quy); `customers_mau.csv` sinh lại đúng từng byte. [ ] Em chạy bước 13 trên MacBook ra TP 43 · FP 0 · FN 0 · TN 20 [ ] Em giải thích được vì sao khung phải có T3 – T5 (thiếu thì recall luôn 100%) và vì sao 17/20 = 85% được tính là đạt |
| Claude (Anthropic) | Tạo phiếu gán nhãn 300 cặp từ `customers_raw.csv` bằng lệnh `--tao-phieu` của chính repo | `data/nhan/nfr03_phieu_gan_nhan.xlsx` (lúc tạo cột `nhan` để trống) | Máy: lệnh `--nhan` kiểm mọi cặp trong phiếu thuộc khung của tệp nguồn, phiếu sai tệp bị từ chối mã 2 |
| Claude (Anthropic) – phiên chat riêng | Gợi ý nhãn ban đầu cho 300 cặp (cột `nhan`, `ghi_chu`): Claude chuẩn hóa họ tên, số điện thoại rồi xét từng cặp theo họ tên, số, ngày tạo | `data/nhan/nfr03_phieu_gan_nhan.xlsx` (không commit – có dữ liệu cá nhân); `data/nhan/nfr03_nhan_300_cap.csv` (chỉ mã cặp, số dòng, nhãn) | Máy: lệnh `--nhan` kiểm phiếu đủ 300 nhãn 1/0 và mọi cặp thuộc khung. Hạn chế: nhãn do AI gợi ý không độc lập hoàn toàn như nhãn tay (TD-32); phép kiểm độc lập là bước 13 trên dữ liệu mẫu (nhãn đúng của script sinh). Phiếu em gửi lại giữ nguyên cả 300 nhãn Claude gợi ý (132 cặp = 1, 168 cặp = 0), không sửa cặp nào. [ ] Em đã rà từng cặp và đồng ý với nhãn cuối [ ] Em giải thích được nhãn của 12 cặp FUZZY và 4 cặp T4 bị bỏ sót (TD-32) |
| Claude (Anthropic) | Dựng lại báo cáo PDF BT2 theo nhận xét trình bày (TD-33): một cột, chữ 13, ảnh hết chiều ngang, xuất bằng LibreOffice (BUG-14); ghép ảnh vào báo cáo; viết phần nhận định NFR-03 theo đúng số của lần chạy | báo cáo PDF nộp E-learning | Máy: `pdftotext` bản mới không còn chữ "dfi"; mọi số trong báo cáo đối chiếu với nhật ký lệnh lưu cùng ảnh. [ ] Em đọc lại cả bài trên bản PDF mới trước khi nộp |
| Claude (Anthropic) | Script hỗ trợ chụp ảnh dòng lệnh (`chup-anh-bt2.sh`, `chup-4-anh.sh`): clone repo vào thư mục mới, chạy đúng các lệnh README, dừng chờ em chụp, kiểm độ phân giải ảnh | không nằm trong repo | Máy: chạy thử trọn vẹn trên môi trường Linux trước khi gửi em; nơi chụp của từng ảnh ghi ở `docs/bt2/README.md` |
| — không dùng — | Gắn tag `v0.2`; chạy README trên MacBook và chụp các ảnh dòng lệnh của báo cáo BT2; ảnh dashboard dữ liệu thật buổi 10 | tag `v0.2`; ảnh dòng lệnh trong `docs/bt2/` và báo cáo PDF; `docs/sprint2/dashboard-*.png` | Không áp dụng |

**Em xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp** (ký sau khi đã đánh dấu các ô ở trên).
Họ tên: Dương Diễm My · MSSV: 2374802010318 · Ngày: 31/10/2026
