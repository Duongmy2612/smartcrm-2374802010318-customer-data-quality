# Lịch sử trạng thái Sprint 1 – 2 (chép nguyên từ README trước BT2)

README được viết lại cho BT2 (buổi 12, 31/10/2026). Phần trạng thái của buổi 8 và buổi 10 giữ nguyên ở đây để đối chiếu với bản đã nộp. Lệnh `python -m src.etl.match --dot 1` nhắc ở dưới nay là `python -m src.pipeline --dot 1` (TD-22).

## 6. Trạng thái hiện tại (buổi 10 – 24/10/2026)

**Sprint 2 – đã hiện thực module mở rộng của track DA:** phát hiện cặp nghi trùng (`match.py`), nạp kho dữ liệu (`load_dwh.py`, `sql/002_dwh_schema.sql`) và dashboard K1 – K3 (`dashboard/report.py`). Luồng chính chạy bằng một lệnh (mục 3, bước 9). Phạm vi đã cắt và lý do: `docs/thay-doi-thiet-ke.md` TD-14.

### 6.1 Luồng chính – kết quả quan sát trên `customers_raw.csv`

Luồng lấy từ đặc tả UC1 «include» UC7 và UC3 của BT1 (Bảng 3.1). Bước 1 – 5 chạy trong lệnh của bước 9 mục 3, chia hai giao dịch (TD-17).

| # | Bước | Mô-đun | Đầu ra quan sát được |
|---|---|---|---|
| 1 | Nạp tệp, kiểm cột, ghi bảng tạm | `extract.py` | 67.037 dòng × 6 cột → `ops.stg_customer` +67.037 |
| 2 | Chuẩn hóa số điện thoại, họ tên; phân loại | `transform.py` | CLEAN 51.279 · PENDING_DUP 11.625 · ERROR 4.133 |
| 3 | Đo 6 quy tắc TRƯỚC/SAU làm sạch | `dq_evaluate.py` | chỉ số mức độ sạch 87,20 → 94,76 (Tốt) |
| 4 | Nạp kho – dimension trước, fact sau (hết giao dịch 1) | `load_dwh.py` | `dim_batch` +1 · `dim_rule` +6 · `fact_dq_check` +12 |
| 5 | Phát hiện cặp nghi trùng, nạp kho, đối soát (giao dịch 2) | `match.py`, `load_dwh.py` | 62.904 hồ sơ có số hợp lệ · 483.124 cặp ứng viên · EXACT_PHONE 11.625 · FUZZY 12 → `fact_dup_pair` +11.637; đối soát 6/6 ✔ |
| 6 | Xem dashboard K1 – K3 | `dashboard/report.py` | 4 biểu đồ (K2 có hai, như wireframe), mỗi biểu đồ gắn một câu hỏi phân tích (Q2, Q3, Q5); thẻ chỉ số K3 trả lời Q4 |

**Đối soát staging (`ops`) ↔ kho (`dwh`)** – in ở cuối bước 5 và khi chạy `python -m src.etl.load_dwh`:

| Mục | `ops` | `dwh` | Vì sao bằng / khác |
|---|---|---|---|
| Đợt nạp | 1 | 1 | cùng GRAIN: 1 dòng = 1 đợt |
| Kết quả đo | 12 | 12 | cùng GRAIN: 1 quy tắc × 1 đợt × 1 giai đoạn × 1 lần đo |
| Cặp nghi trùng | 11.637 | 11.637 | cùng GRAIN: 1 dòng = 1 cặp |
| Hồ sơ thô ↔ mẫu số DQ-01 | 67.037 | 67.037 | khác GRAIN: kho không lưu từng hồ sơ (67.037 dòng staging → 12 dòng fact); mẫu số DQ-01 là mọi hồ sơ của đợt nên phải bằng số hồ sơ thô |
| Hồ sơ lặp ↔ cặp EXACT_PHONE chờ xử lý | 11.625 | 11.625 | QL7-02: mỗi hồ sơ lặp sinh đúng một cặp với hồ sơ nạp sớm nhất cùng số |
| Lần đo trước phiên bản quy tắc đầu tiên | 0 | 0 | phải bằng 0 (TD-16) |

Fact không mất dòng nào khi nối dimension: `fact_dq_check` tìm phiên bản quy tắc bằng LEFT JOIN và có phương án dự phòng (TD-16), `dim_batch` được nạp trước trong cùng giao dịch.

### 6.2 Checklist buổi 10

| # | Mục kiểm chứng | | Minh chứng |
|---|---|---|---|
| 1 | Module mở rộng theo track đã hiện thực và chạy được | ✔ | `match.py`, `load_dwh.py`, `sql/002_dwh_schema.sql`, `dashboard/report.py` |
| 2 | Luồng chính chạy end-to-end, không lỗi treo | ✔ | mục 3 bước 9, mã thoát 0; `docs/sprint2/ket-qua-toan-luong.png` |
| 3 | Chạy trên dữ liệu mẫu thật | ✔ | `customers_raw.csv` (67.037 dòng) và mẫu `mau_cum_8000.csv` |
| 4 | Ảnh kết quả toàn luồng trong `docs/` | ✔ | `docs/sprint2/ket-qua-toan-luong.png` và 8 ảnh khác, danh sách ở `docs/sprint2/README.md`. cả 9 ảnh (4 ảnh dòng lệnh, 5 ảnh dashboard) chụp trên MacBook của em ngày 25/10/2026 |
| 5 | ≥ 5 unit test pass, lệnh test hiện số test | ✔ | `python -m pytest -q` → `95 passed` (bản clone mới chưa sinh mẫu: `94 passed, 1 skipped`); 43 test mới cho `match.py`, `load_dwh.py`, `doc_kho.py` và luồng UC1 → UC3; 1 test em tự viết: `tests/test_cua_em.py` |
| 6 | Có test cho trường hợp biên hoặc luồng ngoại lệ | ✔ | `test_diem_bang_dung_nguong_van_tao_cap_fuzzy`, `test_khoang_diem_k3_bien_thuoc_khoang_tren`, `test_cap_da_co_hoac_da_giu_rieng_khong_de_xuat_lai`, `test_scd2_cau_hinh_doi_ma_thoi_diem_khong_tien_len_bi_tu_choi`, `test_uc3_loi_thi_dot_nap_van_con_va_chi_lenh_chay_lai`, `test_duong_nguong_k3_dung_cho_khi_doi_nguong`, `test_ly_do_rong_dung_nguyen_nhan`, `test_sua_tay_quy_tac_khong_ghi_updated_at_van_nap_duoc` |
| 7 | Ba trạng thái đang tải · rỗng · lỗi | ✔ | `dashboard/report.py`; ảnh `dashboard-rong.png`, `dashboard-loi.png` |
| 8 | README mục 3 đủ các bước, mỗi bước một lệnh | ✔ | mục 3 |
| 9 | Đã thử clone vào thư mục mới và chạy đúng README | ✔ | Môi trường thử, 24/10/2026: CSDL mới, làm đúng 12 bước; nhật ký `docs/sprint2/thu-clone-moi.txt`; phát hiện bước 12 ghi sai kết quả mong đợi (thực tế có 1 test `skipped`) → đã sửa. **MacBook của em, 25/10/2026:** clone từ GitHub vào thư mục mới, làm theo 12 bước; phát hiện thêm 3 chỗ README chưa rõ → đã sửa: bước 10 lệnh `streamlit` trần chạy nhầm Python 3.10 của pyenv (dashboard báo `ModuleNotFoundError`) nên đổi thành `python -m streamlit`; bước 7 phải xóa CSDL cũ để kết quả bước 9 đúng như README; bước 8 thay chỗ giữ chỗ `<thư mục Dataset>` bằng đường dẫn ví dụ |
| 10 | Commit theo quy ước, tổng số commit ≥ 8 | ✔ | `git log --oneline` |

**Yêu cầu riêng của track DA:**

| Yêu cầu | Cách làm | Kiểm chứng |
|---|---|---|
| Nạp dimension bằng khóa nghiệp vụ, rồi nạp fact theo lô ngày | `dim_batch` theo `batch_id`, `dim_rule` theo `rule_code` (SCD loại 2), `dim_date` theo `date_key`; fact nạp sau, mỗi ngày đo / ngày phát hiện một lô (`_nap_theo_lo_ngay`), khóa `result_id`, `pair_id` | `src/etl/load_dwh.py` |
| Đếm dòng staging và fact, giải thích chênh lệch | bảng đối soát ở mục 6.1 | in ra mỗi lần chạy |
| ≥ 2 biểu đồ, mỗi biểu đồ một câu hỏi phân tích | K1 – Q2; K2 (tỉ lệ đạt, điểm bị mất) – Q3; K3 – Q5, thẻ K3 – Q4 (`docs/data-requirements.md` mục 8) | ảnh `dashboard-k1.png` … `k3.png` |
| Mốc tham chiếu, dòng ghi nguồn và thời điểm dữ liệu | K1: đường 90 (Tốt) và 75 (Kém); K2: vạch ngưỡng đạt từng quy tắc và đường 10 điểm (tổng điểm được mất tối đa để còn Tốt); K3: ngưỡng tạo cặp FUZZY 85. Dưới mỗi biểu đồ: bảng/view nguồn, thời điểm lần đo mới nhất, bộ đệm 60 giây | ảnh dashboard |
| Nạp lần hai không nhân đôi dòng | mọi INSERT có `ON CONFLICT` / `NOT EXISTS` theo khóa nghiệp vụ | `python -m src.etl.load_dwh` in `+0`; `test_nap_kho_lan_hai_khong_nhan_doi_dong` |
| Bộ lọc rỗng hiện câu giải thích | câu nêu đơn vị, khoảng ngày, QT-14 và việc nên làm | `test_bo_loc_rong_noi_ro_vi_sao_va_nen_lam_gi`; ảnh `dashboard-rong.png` |

**NFR-01 phần 2** – phát hiện cặp nghi trùng trên 8.000 hồ sơ ≤ 120 giây. Đo 3 lần trên mẫu `mau_cum_8000.csv` (7.506 hồ sơ có số hợp lệ, 6.911 cặp ứng viên), mỗi lần một CSDL mới:

| Môi trường đo | UC3 (match + nạp kho) | UC1 (phần 1) | Cả lệnh | Kết luận |
|---|---|---|---|---|
| Linux, Python 3.11, PostgreSQL 16 (môi trường thử, 24/10/2026) – bản clone mới | 0,7 s | 1,3 s | 2,9 s | Đạt |
| MacBook của em (macOS, Python 3.11.16, PostgreSQL 14), 25/10/2026 – bản clone mới từ GitHub | 0,4 s | 0,9 s | 2,6 s | Đạt |

Trên cả tệp 67.037 dòng: UC3 7,4 s (môi trường thử), 4,4 s (MacBook của em). Ảnh: `docs/sprint2/ket-qua-nfr01.png` (MacBook).

**NFR-06** – mỗi khung dashboard tải ≤ 5 giây với ≤ 24 đợt nạp. Đo trên môi trường thử, từ lúc mở trang tới khi đủ 4 biểu đồ K1 – K3, 3 lần, lấy giá trị lớn nhất: 4,1 s với 1 đợt; 4,1 s với 24 đợt mẫu 8.000 dòng (nạp vào một CSDL riêng để đo). Đạt, nhưng sát ngưỡng ở lần mở đầu tiên (bộ đệm rỗng) – đo lại trên MacBook.

### 6.3 Còn lại

- [x] Em chạy lại trên MacBook (25/10/2026): đẩy repo lên GitHub, clone vào thư mục mới, làm theo 12 bước mục 3, đo NFR-01 phần 2 ba lần, chạy kiểm thử – ảnh dòng lệnh trong `docs/sprint2/` là ảnh chụp trên MacBook.
- [x] Chụp 5 ảnh dashboard trên MacBook (25/10/2026), gồm trạng thái rỗng (QT-14) và lỗi (tắt PostgreSQL).
- [x] Em tự viết thêm 1 test (`tests/test_cua_em.py`, 25/10/2026): "Duong Diem My" và "DIEM MY DUONG" – đảo thứ tự, viết hoa – cùng số điện thoại thì điểm tương đồng là 100.
- [ ] Đo NFR-06 trên MacBook.
- [x] Đánh dấu các ô kiểm chứng ở `docs/ai-disclosure.md` (mục Sprint 2): 14/14 ô em đã tự làm.
- [ ] Peer review (buổi 10): bạn cùng lớp clone repo, chạy theo README và mở issue 3 dòng (mẫu `.github/ISSUE_TEMPLATE/peer-review.md`); em sửa README theo issue.
- [ ] **NFR-03:** em tự gán nhãn 300 cặp, tính precision/recall ở ngưỡng 85 (chuyển sang Sprint 3 – TD-14).
- [ ] NFR-02: tập 200 dòng gán nhãn tay đủ 5 dạng số.
- [ ] **Sprint 3 (buổi 11 – 12):**
  - `merge_service.py` (UC5): Gộp / Giữ riêng. Sau đó K3 có thêm tỉ lệ gộp theo khoảng điểm và số cặp quyết định theo ngày (TD-20).
  - `dashboard/app.py` (K4, UC6, UC9). UC6 chỉ cho thêm quy tắc đã có cách đo trong `dq_evaluate.py`.
  - Tài khoản chỉ đọc `dash_reader`; tài khoản ứng dụng không có quyền DELETE (NFR-04).

### 6.4 Sprint 1 – buổi 8 (giữ nguyên nội dung đã nộp buổi 8)

**Sprint 1 – đã hiện thực.** Đã chạy trên MacBook của em (macOS, Python 3.11, PostgreSQL 14) ngày 21/10/2026; trước đó đã chạy thử trên Linux.

- [x] Repo: bỏ `.venv` và `.env` khỏi git; có `.gitignore`, `.env.example`; có đủ hồ sơ BT1 (`srs.md`, 5 tệp `.drawio`); nhánh `main` và `dev`.
- [x] Phản hồi BT1 đã xử lý: `docs/thay-doi-thiet-ke.md` TD-01 – TD-05; PDF đúng tên, rút từ 27 còn 13 trang.
- [x] `src/` dựng theo sơ đồ kiến trúc (TD-06).
- [x] `sql/001_ops_schema.sql`: 6 bảng schema `ops`, 8 khóa ngoại, CHECK số điện thoại, `UNIQUE(phone) WHERE is_active`.
- [x] UC1 chạy bằng một lệnh; kết quả trên `customers_raw.csv` khớp mục 4 BT1:

  | Bước | Kết quả |
  |---|---|
  | extract (FR-01) | 67.037 dòng × 6 cột, đếm ô trống từng cột |
  | transform (FR-02, FR-03) | 19.041 số sai dạng đã chuẩn hóa, 0 số không quy đổi được; 5.930 họ tên được sửa cách viết |
  | phân loại | CLEAN 51.279 → `customer_clean`; PENDING_DUP 11.625; ERROR 4.133 (MISSING_PHONE) |
  | hồ sơ lỗi (FR-10) | CSV kèm lý do |
  | dq_evaluate (FR-08) | 12 dòng `dq_result`; chỉ số **87,20 → 94,76** |

  Ảnh chụp màn hình trên MacBook của em trong `docs/sprint1/`: `moi-truong.png`, `ket-qua-pipeline.png`, `ket-qua-csdl.png`, `ket-qua-tu-choi.png`, `ket-qua-pytest.png`, `ket-qua-nfr01-a.png`, `ket-qua-nfr01-b.png`. Báo cáo của lần chạy này: `docs/sprint1/bao-cao-uc1-dot-1.md`.
- [x] Các trường hợp bị từ chối và lỗi đều có test:

  | Trường hợp | Kết quả | Test |
  |---|---|---|
  | Thiếu cột (AC1.3) | mã thoát 2 | `test_ac13_*`, `test_ma_thoat` |
  | Nạp lại cùng tệp (AC1.4) | từ chối, bảng tạm không đổi; có `--nap-lai` thì thành đợt mới, hồ sơ hợp lệ thành PENDING_DUP | `test_ac14_nap_lai_bi_tu_choi_roi_xac_nhan` |
  | Người nạp sai vai trò | từ chối | `test_chi_nhan_vien_marketing_duoc_nap_tep` |
  | Giá trị dài hơn cột của `customer_clean` | từ chối, báo số dòng (TD-11) | `test_gia_tri_qua_dai_bi_tu_choi_ca_dot` |
  | Lỗi giữa giao dịch | ROLLBACK, không còn đợt nạp dở (TD-09) | `test_loi_giua_chung_thi_rollback_ca_dot` |

- [x] 51 test pass trên môi trường thử và trên MacBook của em. Trên bản clone chưa có dữ liệu và CSDL test, 2 test hồi quy và 5 test tích hợp tự bỏ qua.

**NFR-01, phần 1** – nạp và chuẩn hóa 8.000 dòng ≤ 60 giây. Đo 3 lần trên mẫu `mau_cum_8000.csv`, mỗi lần một CSDL mới, lấy giá trị lớn nhất:

| Môi trường đo | Pipeline (extract + transform + đo) | Cả lệnh (kể cả khởi động Python) | Kết luận |
|---|---|---|---|
| Linux, Python 3.11, PostgreSQL 16 (môi trường thử, 19/10) | 1,4 s | 2,1 s | Đạt |
| MacBook của em (máy phát triển), 21/10/2026 – lớn nhất của 2 lượt × 3 lần | 1,3 s | 3,0 s | Đạt |

**Còn lại (theo thứ tự ưu tiên – TD-04, gợi ý của giảng viên cho BT2)**

- [ ] **Sprint 2 (buổi 9 – 10):**
  - `match.py` (FR-04); đo NFR-01 phần 2: phát hiện cặp trên 8.000 hồ sơ ≤ 120 giây.
  - **NFR-03:** em tự gán nhãn 300 cặp, tính precision/recall ở ngưỡng 85.
  - `load_dwh.py` + `sql/002_dwh_schema.sql` (5 bảng kho, SCD loại 2, 2 view).
- [ ] NFR-02: tập 200 dòng gán nhãn tay đủ 5 dạng số.
- [ ] **Sprint 3 (buổi 11 – 12):**
  - `merge_service.py` (UC5).
  - `dashboard/app.py` (K4, UC6, UC9) và `report.py` (K1 – K3). UC6 chỉ cho thêm quy tắc đã có cách đo trong `dq_evaluate.py`.
  - Tài khoản chỉ đọc `dash_reader`; tài khoản ứng dụng không có quyền DELETE (NFR-04).
- [x] Em chạy lại trên MacBook: đo NFR-01 phần 1, thay ảnh trong `docs/sprint1/` bằng ảnh chụp màn hình của em, đánh dấu các ô kiểm chứng trong `docs/ai-disclosure.md`.

**Ghi chú:** không dùng phương án dự phòng; CSDL vẫn là PostgreSQL. `--khong-ghi-csdl` chỉ để chạy thử khi máy chưa có PostgreSQL (TD-10).

