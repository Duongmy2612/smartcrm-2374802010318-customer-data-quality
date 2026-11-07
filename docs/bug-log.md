# Nhật ký lỗi đã gỡ – Giai đoạn 2 và 3 (buổi 7 – 16)

Sinh viên: Dương Diễm My – MSSV 2374802010318 · L7 – Chất lượng dữ liệu khách hàng · Track DA

Mỗi lỗi đủ **7 dòng**, theo quy trình gỡ bốn bước của buổi 11: tái lập → khoanh vùng → sửa nguyên nhân → xác nhận.
Link commit trỏ tới GitHub của repo. Thêm lỗi mới vào cuối, không sửa mục cũ.

**Bài tập 3 (buổi 13 – 16):** BUG-15 – BUG-18 ở mục cuối, theo mẫu bảy dòng của BT3 (mã và mức độ · phát hiện bởi
test case nào · triệu chứng · cách tái lập · nguyên nhân · cách sửa · link commit và xác nhận). Mỗi bug một commit
riêng `fix(…): … (BUG-xx)`.

Repo: https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality

| Mã | Lỗi | Loại | Commit sửa |
|---|---|---|---|
| BUG-01 | 21 cặp FUZZY cho 12 cặp số – Marketing phải quyết định lặp | Logic | `a5bc71ab` |
| BUG-02 | Sửa quy tắc bằng psql làm mọi lần nạp kho sau dừng | Hợp đồng dữ liệu | `28d1986c` |
| BUG-03 | Trạng thái rỗng của dashboard đổ lỗi sai nguyên nhân | Logic | `348f6e7a` |
| BUG-04 | Trục K2 không hiện mốc 100% | Trình bày | `33dc22e8` |
| BUG-05 | README bước 12 ghi sai kết quả mong đợi của bản clone mới | Tài liệu / tái lập | `5e00d0d6` |
| BUG-06 | Dashboard báo `ModuleNotFoundError` trên MacBook | Môi trường chạy | `52779738` |
| BUG-07 | Chạy lại luồng chính lần hai trả mã thoát 2 ("TỪ CHỐI") | Thiết kế luồng (C5) | `8d8e6038` |
| BUG-08 | `transform.py` vẫn có câu SQL – lớp load lẫn vào pha transform | Kiến trúc (C2) | `6a69241f` |
| BUG-09 | Tệp chỉ có dòng tiêu đề được nạp thành đợt rỗng, chấm 100 điểm "Tốt" | Dữ liệu sai (C7) | `b6b289c` |
| BUG-10 | Tệp rỗng / sai bảng mã / hỏng cấu trúc lộ lỗi thô của pandas, mã thoát 1 | Dữ liệu sai (C7) | `b6b289c` |
| BUG-11 | Câu đọc K3 luôn nói "sát ngưỡng"; thẻ số K1, K3 không có mốc so sánh | Trình bày (TP3) | `41492c3` |
| BUG-12 | Pha T import hàm từ pha E dù tài liệu ghi "các pha không gọi lẫn nhau" | Kiến trúc (C2) | `5db967b` |
| BUG-13 | Khung cặp NFR-03 đếm 16 cặp FUZZY trong khi pipeline ghi 12 | Logic (NFR-03) | `37eb1260` |
| BUG-14 | Báo cáo PDF xuất bằng Word for Mac hỏng chữ có dấu ("dfi liệu") | Tài liệu / trình bày | báo cáo PDF |

---

### BUG-01  FUZZY sinh nhiều cặp lặp cho cùng hai số điện thoại

1. **Ngày · nơi phát hiện:** 24/10/2026 · chạy `match.py` lần đầu trên cả `customers_raw.csv` (môi trường thử).
2. **Triệu chứng:** `FUZZY 21` nhưng chỉ có 12 cặp số khác nhau; cùng hai số xuất hiện ở 2 – 3 cặp.
3. **Tái lập:** bảng hồ sơ có số A (2 hồ sơ) và số B chỉ khác A một chữ số → so mọi hồ sơ cho 2 cặp FUZZY (A₁–B, A₂–B).
4. **Khoanh vùng:** `match.tim_cap`, vòng FUZZY lặp qua mọi hồ sơ trong khối blocking thay vì mỗi số một lần.
5. **Nguyên nhân gốc:** các hồ sơ cùng số đã nối với hồ sơ nạp sớm nhất bằng cặp EXACT_PHONE, nên so tiếp mọi hồ sơ là thừa (TD-18).
6. **Sửa:** FUZZY chỉ so hồ sơ đại diện (`drop_duplicates('phone_norm')`) – [a5bc71ab](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/a5bc71ab).
7. **Xác nhận:** `test_fuzzy_chi_so_ho_so_dai_dien_cua_moi_so` PASS; chạy lại tệp đầy đủ ra `FUZZY 12`.

### BUG-02  Sửa ngưỡng quy tắc bằng tay làm lần nạp kho sau dừng

1. **Ngày · nơi phát hiện:** 24/10/2026 · rà soát độc lập trước khi nộp buổi 10.
2. **Triệu chứng:** `LỖI: ValueError: DQ-06: updated_at … không sau valid_from …`, mọi lần chạy luồng chính sau đó ROLLBACK cả UC1.
3. **Tái lập:** `psql -c "UPDATE ops.dq_rule SET pass_threshold = 90 WHERE rule_code = 'DQ-06'"` rồi `python -m src.etl.load_dwh`.
4. **Khoanh vùng:** `load_dwh.quyet_dinh_scd2` – cấu hình đổi nhưng `updated_at` (= `valid_from` của phiên bản mới) đứng yên.
5. **Nguyên nhân gốc:** hợp đồng dữ liệu giữa người sửa cấu hình và SCD loại 2: câu UPDATE tay không ghi `updated_at` (TD-21).
6. **Sửa:** trigger `trg_dq_rule_updated_at` ở `sql/003_dq_rule_updated_at.sql` – [28d1986c](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/28d1986c).
7. **Xác nhận:** `test_sua_tay_quy_tac_khong_ghi_updated_at_van_nap_duoc` PASS (bỏ trigger thì test này lỗi).

### BUG-03  Trạng thái rỗng của dashboard nói sai nguyên nhân

1. **Ngày · nơi phát hiện:** 24/10/2026 · thử dashboard với người xem `ql.mm001` và bỏ chọn hết đơn vị.
2. **Triệu chứng:** màn hình báo "Kho chưa có đợt nạp nào" trong khi kho có 1 đợt (thuộc đơn vị khác / chưa chọn đơn vị).
3. **Tái lập:** `python -m streamlit run dashboard/report.py`, mở `?nguoi_xem=ql.mm001`.
4. **Khoanh vùng:** `dashboard/report.py` dùng một câu chung cho mọi trường hợp kết quả rỗng.
5. **Nguyên nhân gốc:** không phân biệt 6 nguyên nhân rỗng (kho trống, không có quyền, QT-14, khoảng ngày, chưa chọn đơn vị, chưa chọn đợt).
6. **Sửa:** hàm `doc_kho.ly_do_rong` + `cau_giai_thich_rong` – [348f6e7a](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/348f6e7a).
7. **Xác nhận:** `test_ly_do_rong_dung_nguyen_nhan` (7 trường hợp) PASS; ảnh `docs/sprint2/dashboard-rong.png`.

### BUG-04  Trục K2 không hiện mốc 100%

1. **Ngày · nơi phát hiện:** 24/10/2026 · xem K2 sau khi DQ-02 đạt 100%.
2. **Triệu chứng:** thanh DQ-02 chạm mép phải, trục chỉ có nhãn tới 80%, không đọc được giá trị tối đa.
3. **Tái lập:** mở tab K2 với đợt có quy tắc đạt 100%.
4. **Khoanh vùng:** cấu hình trục x của biểu đồ Plotly trong `dashboard/report.py`.
5. **Nguyên nhân gốc:** khoảng trục `[0, 101]` không có bước nhãn cố định nên Plotly tự chọn nhãn và bỏ mốc 100.
6. **Sửa:** `range=[0, 102]`, `dtick=20` – nhãn 0, 20, …, 100 luôn hiện – [33dc22e8](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/33dc22e8).
7. **Xác nhận:** ảnh `docs/sprint2/dashboard-k2.png` có mốc 100%.

### BUG-05  README bước 12 ghi sai kết quả mong đợi

1. **Ngày · nơi phát hiện:** 24/10/2026 · phép thử clone vào thư mục mới (`docs/sprint2/thu-clone-moi.txt`).
2. **Triệu chứng:** README ghi "79 passed" nhưng bản clone mới in `78 passed, 1 skipped`.
3. **Tái lập:** clone mới, làm đúng 12 bước README, chạy `python -m pytest -q`.
4. **Khoanh vùng:** test hồi quy trên mẫu 8.000 dòng cần tệp `data/processed/mau_cum_8000.csv` không có trong repo.
5. **Nguyên nhân gốc:** README được viết trên máy đã có sẵn tệp sinh ra từ trước – đúng loại lỗi "chạy trên máy em mới được".
6. **Sửa:** README ghi rõ cả hai kết quả và lệnh sinh mẫu – [5e00d0d6](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/5e00d0d6).
7. **Xác nhận:** chạy lại phép thử clone mới, kết quả khớp README.

### BUG-06  Dashboard báo `ModuleNotFoundError` trên MacBook

1. **Ngày · nơi phát hiện:** 25/10/2026 · thử clone mới trên MacBook của em.
2. **Triệu chứng:** trang Streamlit báo `ModuleNotFoundError` (thiếu thư viện) dù `pip install -r requirements.txt` trong `.venv` đã chạy.
3. **Tái lập:** máy có pyenv (Python 3.10 đã cài streamlit), kích hoạt `.venv` rồi gõ `streamlit run dashboard/report.py`.
4. **Khoanh vùng:** `which streamlit` trỏ vào bản của pyenv, không phải `.venv/bin/streamlit`.
5. **Nguyên nhân gốc:** lệnh `streamlit` trần chạy Python ngoài môi trường ảo.
6. **Sửa:** README dùng `python -m streamlit run …`; trang báo rõ nguyên nhân và lệnh đúng – [52779738](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/52779738).
7. **Xác nhận:** làm lại trên MacBook theo README mới, dashboard mở được (ảnh `docs/sprint2/dashboard-k1.png`).

### BUG-07  Chạy lại luồng chính lần hai trả mã thoát 2

1. **Ngày · nơi phát hiện:** 31/10/2026 · tự chấm theo bảng tiêu chí BT2, mục C5 "chạy lại lần thứ hai không lỗi".
2. **Triệu chứng:** lần hai in `TỪ CHỐI: Tệp này đã được nạp ở đợt 1…`, mã thoát 2 – dữ liệu không nhân đôi nhưng lệnh trông như lỗi.
3. **Tái lập:** `python -m src.pipeline --tep data/mau/customers_mau.csv` hai lần liên tiếp; `echo $?` sau lần hai.
4. **Khoanh vùng:** `src/pipeline.chay_uc1`, nhánh kiểm `tim_dot_cung_tep` ném `TuChoi`.
5. **Nguyên nhân gốc:** hiểu AC1.4 là "từ chối", trong khi AC1.4 chỉ yêu cầu cảnh báo và không nạp khi chưa xác nhận (TD-25).
6. **Sửa:** cảnh báo, không tạo đợt mới, đồng bộ kho + UC3 theo khóa nghiệp vụ, in số dòng 8 bảng đích trước → sau, mã thoát 0 – [8d8e6038](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/8d8e6038).
7. **Xác nhận:** `test_chay_lai_bang_lenh_tra_ma_0_va_khong_nhan_doi` PASS; ảnh `docs/bt2/03-chay-lai-lan-hai.png` (mọi bảng +0).

### BUG-08  Lớp load lẫn vào pha transform

1. **Ngày · nơi phát hiện:** 31/10/2026 · tự chấm C2 theo cách giảng viên chấm (mở tệp transform, tìm dấu vết lớp khác).
2. **Triệu chứng:** `grep -n "sqlalchemy\|INSERT INTO" src/etl/transform.py` ra kết quả (câu `INSERT INTO ops.customer_clean`).
3. **Tái lập:** lệnh `grep` ở dòng 2 trên mã trước BT2.
4. **Khoanh vùng:** phần "đọc / ghi CSDL" ở cuối `extract.py`, `transform.py`, `dq_evaluate.py`, `match.py`.
5. **Nguyên nhân gốc:** quy ước Sprint 1 cho mỗi mô-đun giữ cả hàm thuần lẫn hàm ghi CSDL của nhóm FR mình (TD-22).
6. **Sửa:** chuyển mọi hàm có `conn` sang `src/etl/load_ops.py` – [6a69241f](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/6a69241f); chú thích đầu `transform.py` không còn nhắc tên thư viện CSDL để phép `grep` không bắt nhầm.
7. **Xác nhận:** `tests/test_ranh_gioi_lop.py` (11 test) PASS; lệnh `grep` ở dòng 2 không còn kết quả.

### BUG-09  Tệp chỉ có dòng tiêu đề thành một đợt rỗng được chấm 100 điểm

1. **Ngày · nơi phát hiện:** 31/10/2026 · rà soát lại BT2, thử "gọi một chức năng với dữ liệu SAI" (đề mục 4.3, bước 4).
2. **Triệu chứng:** tệp CSV chỉ có `ho_ten,so_dien_thoai` được nạp thành đợt 2 với 0 hồ sơ; mọi quy tắc có mẫu số 0 nên tỉ lệ đạt = 1, chỉ số 100,00 "Tốt"; dashboard K1 lấy đợt rỗng này làm "đợt mới nhất".
3. **Tái lập:** `python -m src.pipeline --tep data/mau/customers_chi_tieu_de.csv` → mã thoát 0, `ops.load_batch` thêm 1 dòng `row_count = 0`.
4. **Khoanh vùng:** `extract.doc_tep` chỉ kiểm cột bắt buộc, không kiểm số dòng; QL7-06 "mẫu số 0 → tỉ lệ 1" vốn dành cho MỘT quy tắc không áp dụng (ví dụ tệp không có email), không phải cho cả tệp rỗng.
5. **Nguyên nhân gốc:** thiếu điều kiện "tệp phải có ít nhất một dòng dữ liệu" ở pha E (FR-01).
6. **Sửa:** `doc_tep` ném `TepBiTuChoi` khi tệp không có dòng dữ liệu – từ chối cả đợt, mã thoát 2, không tạo đợt (TD-28) – [b6b289c](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/b6b289c).
7. **Xác nhận:** `test_bien_so_dong_du_lieu` (0 dòng bị từ chối, 1 dòng được nhận), `test_tep_mau_hong_bi_tu_choi_ma_thoat_2[customers_chi_tieu_de.csv]` PASS.

### BUG-10  Tệp không đọc được làm lộ lỗi thô của pandas

1. **Ngày · nơi phát hiện:** 31/10/2026 · rà soát C7 "từ chối có thông báo rõ ràng, không trả lỗi thô của thư viện".
2. **Triệu chứng:** tệp 0 byte → `LỖI: EmptyDataError: No columns to parse from file`; CSV lưu bằng Excel Windows → `LỖI: UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe1…`; thiếu dấu ngoặc kép đóng → `LỖI: ParserError: Error tokenizing data…`; cả ba mã thoát 1 (lỗi kỹ thuật).
3. **Tái lập:** `python -m src.pipeline --tep data/mau/customers_sai_bang_ma.csv`.
4. **Khoanh vùng:** `extract.doc_tep` gọi `pd.read_csv` không bắt lỗi; `pipeline.main` in nguyên tên và thông điệp lỗi của thư viện.
5. **Nguyên nhân gốc:** lỗi do DỮ LIỆU (tệp hỏng) bị xử lý như lỗi KỸ THUẬT; người nạp không biết phải sửa tệp thế nào.
6. **Sửa:** bắt `EmptyDataError`, `UnicodeDecodeError`, `ParserError` (và tệp `.xlsx` hỏng) rồi ném `TepBiTuChoi` bằng câu tiếng Việt chỉ cách sửa, mã thoát 2 (TD-28) – [b6b289c](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/b6b289c).
7. **Xác nhận:** `test_tep_khong_doc_duoc_bi_tu_choi_bang_cau_tieng_viet` (3 trường hợp, thông báo không chứa chữ "Error"), `test_tep_xlsx_hong_bi_tu_choi` PASS.

### BUG-11  Câu đọc biểu đồ K3 mô tả sai dữ liệu; thẻ số không có mốc

1. **Ngày · nơi phát hiện:** 31/10/2026 · mở K3 trên dữ liệu mẫu khi rà soát TP3.
2. **Triệu chứng:** K3 ghi "FUZZY 3 cặp, thấp nhất 94,00 điểm – sát ngưỡng 85" dù 94 cách ngưỡng 9 điểm; các thẻ 414, 5,80%, 10,39% (K1) và 43, 43, 0, 0 (K3) không có mốc so sánh như đề mục 2.3 yêu cầu.
3. **Tái lập:** chạy bước 8 README, mở dashboard, tab K3.
4. **Khoanh vùng:** `dashboard/report.py` – câu "sát ngưỡng" viết cứng trong f-string; tham số thứ ba của `st.metric` chỉ ghi số hồ sơ.
5. **Nguyên nhân gốc:** câu được viết theo dữ liệu thật buổi 10 (cặp thấp nhất sát 85) rồi không đổi khi dữ liệu đổi; mốc chỉ được làm cho biểu đồ, quên thẻ số.
6. **Sửa:** `doc_kho.cau_fuzzy_thap_nhat` chỉ nói "sát ngưỡng" khi cách ngưỡng dưới 5 điểm; `doc_kho.moc_ti_le_loi` ghi mốc ≤ 100 − ngưỡng; mỗi thẻ K1, K3 có mốc (TD-30) – [41492c3](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/41492c3).
7. **Xác nhận:** `test_cau_k3_chi_noi_sat_nguong_khi_cach_duoi_5_diem` (85 / 89,99 / 90 / 94), `test_moc_cua_the_ti_le_loi_bang_100_tru_nguong` PASS; ảnh K1, K3 trong báo cáo BT2 mục 5.

### BUG-12  Pha T import hàm từ pha E

1. **Ngày · nơi phát hiện:** 31/10/2026 · rà soát C2 "không gọi chéo sai chiều".
2. **Triệu chứng:** `transform.py` và `dq_evaluate.py` có dòng `from src.etl.extract import la_trong`, trong khi `pipeline.py` và báo cáo ghi "các pha không gọi lẫn nhau".
3. **Tái lập:** `grep -n "from src.etl.extract" src/etl/*.py`.
4. **Khoanh vùng:** hàm `la_trong` (ô trống) nằm ở `extract.py` nhưng được cả pha E và pha T dùng.
5. **Nguyên nhân gốc:** `tests/test_ranh_gioi_lop.py` chỉ kiểm pha T không gọi pha L, chưa kiểm chiều T → E nên không phát hiện.
6. **Sửa:** chuyển `la_trong` sang `src/etl/tien_ich.py` (không thuộc pha nào); test ranh giới kiểm thêm chiều T → E (TD-29) – [5db967b](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/5db967b).
7. **Xác nhận:** `test_pha_t_khong_goi_pha_e_va_l` (3 tệp pha T) PASS; lệnh grep ở bước 3 không còn kết quả.

### BUG-13  Khung cặp NFR-03 đếm thừa cặp FUZZY

1. **Ngày · nơi phát hiện:** 31/10/2026 · lần chạy đầu `python -m src.kiem_chung_nfr03 --tep data/raw/customers_raw.csv --tao-phieu …` (TD-32).
2. **Triệu chứng:** tầng T2 (khác số, cùng khối, điểm ≥ 85) có 16 cặp, trong khi pipeline ghi FUZZY 12 – phép kiểm chứng đo một tập cặp khác với tập hệ thống thật sự tạo.
3. **Tái lập:** dựng khung với nguồn "cặp cùng họ tên" lấy MỌI cặp hai số khác nhau, kể cả hai số cùng khối → T2 = 16.
4. **Khoanh vùng:** so 16 cặp với tập cặp tính theo hồ sơ đại diện: 4 cặp thừa, cả 4 đều có một hồ sơ KHÔNG phải hồ sơ đại diện (nạp sớm nhất) của số điện thoại của nó.
5. **Nguyên nhân gốc:** `match.tim_cap` chỉ so hồ sơ đại diện của hai số (TD-18); nguồn cặp cùng họ tên trong khung lại so cả hồ sơ thứ hai, thứ ba của cùng một số – cùng một mối nối giữa hai số bị đếm nhiều lần.
6. **Sửa:** nguồn cặp cùng họ tên bỏ cặp hai số cùng số hoặc cùng khối (đã xét ở nguồn hồ sơ đại diện); hồ sơ có mã lỗi để trống `phone_norm` trong khung như QL7-04 – sửa trước khi commit, trong [37eb1260](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/37eb1260).
7. **Xác nhận:** `test_khung_du_lieu_that_khop_so_cap_cua_pipeline`: T1 = 11.625, T2 = 12 – khớp đúng EXACT_PHONE, FUZZY của pipeline; trên dữ liệu mẫu T1 = 40, T2 = 3 (`test_kiem_chung_nfr03_tren_du_lieu_mau`).

### BUG-14  Báo cáo PDF hỏng chữ có dấu khi xuất bằng Word for Mac

1. **Ngày · nơi phát hiện:** 31/10/2026 · rà soát bản PDF BT2 trước khi nộp.
2. **Triệu chứng:** trong PDF, "dữ liệu" hiện thành "dfi liệu", "từ chối" thành "tfi chối", "Dương" thành "Dffơng", "được" thành "đffợc".
3. **Tái lập:** `pdftotext BT2_….pdf - | grep -c "dfi liệu"` → 24 chỗ, chỉ 3 chỗ "dữ liệu" đúng.
4. **Khoanh vùng:** chỉ bản xuất bằng Microsoft Word for Mac bị; bản BT1, buổi 8, buổi 10 xuất bằng LibreOffice đọc ra đúng chữ.
5. **Nguyên nhân gốc:** phông Times New Roman do Word for Mac nhúng vào PDF ánh xạ chữ "ư", "ữ" sang ký tự ghép "ff", "fi" – cả lớp chữ (pdftotext) lẫn hình hiển thị (trình xem dùng phông nhúng) đều ra chữ sai; trình xem trên máy em có thể vẫn hiện đúng nên khó thấy.
6. **Sửa:** xuất PDF bằng LibreOffice (TD-33); trước khi nộp chạy lệnh ở bước 3.
7. **Xác nhận:** bản PDF mới: `grep -c "dfi"` = 0.

---

## Bài tập 3 – Giai đoạn 3 (buổi 13 – 16)

Phân loại theo bảng mức độ của đề BT3 mục 2.3, trả lời hai câu hỏi: người dùng còn làm được việc không (có cách làm
tạm không) · dữ liệu có bị sai hay bị lộ không.

| Mã | Mức độ | Phát hiện bởi | Lỗi | Commit sửa |
|---|---|---|---|---|
| BUG-15 | MAJOR | TC-09 | Ngày tạo sai định dạng vẫn thành hồ sơ sạch | [`a3566b0`](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/a3566b009a9a6673d6754bad0ce52e0189b41583) |
| BUG-16 | CRITICAL | TC-12 | Kết nối của dashboard đọc được họ tên, số điện thoại ở schema `ops` | [`aab583b`](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/aab583b96b6b289a722af6e0722611f6d983c391) |
| BUG-17 | MAJOR | PT-01 – checklist mục 7 | Ảnh Docker cài pillow 12.3.0 có 39 lỗ hổng đã công bố | [`43be2fa`](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/43be2fa849e139b0ca9e280607c72545fbdda6f7) |
| BUG-18 | MINOR | PT-01 – checklist mục 5 | Mất CSDL trong Docker nhưng câu báo khuyên lệnh Homebrew | [`e91fdc1`](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/e91fdc1788fac83a8e24154d1b3f1130f2aae0a0) |

### BUG-15  Ngày tạo sai định dạng vẫn thành hồ sơ sạch

1. **Mã và mức độ:** BUG-15 · **MAJOR** – dữ liệu sai lọt vào `customer_clean` mà không ai được báo; chưa làm sai chỉ
   số hay kho (ngày tạo chưa dùng ở bước sau) và có cách làm tạm (lọc tay tệp nguồn), nên không xếp Critical.
2. **Phát hiện bởi:** TC-09 (dữ liệu sai), lần chạy 1 ngày 07/11/2026 ở commit `574bfd0` – kết quả FAIL.
3. **Triệu chứng:** tệp 3 hồ sơ có ngày `31/02/2026` và `2026-02-30` → mã thoát 0, `customer_clean` 0 → 3,
   `ops.v_reject` 0 dòng; cả ba hồ sơ CLEAN.
4. **Cách tái lập:** `git checkout 574bfd0` → `python -m tests.tc_bt3 TC-09` (hoặc nạp
   `tests/du_lieu_tc/tc09_ngay_sai.csv` rồi `SELECT row_no, created_raw, status FROM ops.stg_customer`). Không cần
   Python – trong thư mục đã chạy Deployment Guide: `mkdir ../cu && git archive 574bfd0 | tar -x -C ../cu` →
   `docker compose run --rm -v "$(pwd)/../cu:/app" pipeline python -m tests.tc_bt3 TC-09` (mã nguồn cũ, ảnh mới).
5. **Nguyên nhân:** `transform.gan_ma_loi` chỉ xét số điện thoại và họ tên; cột `created_raw` được chép vào bảng tạm
   nhưng không hàm nào kiểm, dù `docs/data-requirements.md` mục 3 ghi `ngay_tao` phải là ngày hợp lệ dạng yyyy-mm-dd.
   Miền giá trị `error_code` (CHECK ở `sql/001`) cũng chỉ có ba mã, nên không có chỗ ghi lỗi này.
6. **Cách sửa:** thêm `transform.ngay_tao_hop_le` (trống là hợp lệ – cột tùy chọn; có giá trị phải đúng yyyy-mm-dd
   và là ngày có thật) và mã `INVALID_DATE`, xét sau cùng (MISSING_PHONE > INVALID_PHONE > MISSING_NAME > INVALID_DATE);
   migration `sql/005_invalid_date.sql` thêm mã vào CHECK của CSDL cũ; `ops.v_reject` có câu lý do và cột
   `created_raw` (TD-37). 13 test mới, gồm biên 29/02 năm nhuận / năm thường.
7. **Link commit và xác nhận:** [a3566b0](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/a3566b009a9a6673d6754bad0ce52e0189b41583) · TC-09 PASS (`v_reject` 2 dòng
   INVALID_DATE, `customer_clean` 0 → 1); dữ liệu mẫu và dữ liệu thật không có ngày sai nên mọi con số cũ giữ nguyên
   (88,41 → 95,79; 87,20 → 94,76); `python -m pytest -q` 0 failed. Ảnh: `docs/screenshots/TC-09-lan1-FAIL.png` →
   `TC-09.png`.

### BUG-16  Kết nối của dashboard đọc được dữ liệu cá nhân ở schema ops

1. **Mã và mức độ:** BUG-16 · **CRITICAL** – lỗ hổng bảo mật: lớp hiển thị đọc được họ tên, số điện thoại của khách
   hàng, trái NFR-07 ("dashboard chỉ đọc kho số đếm").
2. **Phát hiện bởi:** TC-12 (bảo mật), lần chạy 1 ngày 07/11/2026 ở commit `574bfd0` – kết quả FAIL.
3. **Triệu chứng:** `db.tao_engine_chi_doc()` – đúng kết nối dashboard dùng – chạy được
   `SELECT full_name_raw, phone_raw FROM ops.stg_customer` và trả về dữ liệu; tài khoản kết nối là tài khoản của
   pipeline (`postgres` trên máy thử `.venv`; `smartcrm` khi làm lại trong Docker).
4. **Cách tái lập:** `git checkout 574bfd0`, `.env` theo `.env.example` (khi đó `DASH_DB_USER` trống) →
   `python -m tests.tc_bt3 TC-12`. Trong Docker như BUG-15:
   `docker compose run --rm -e DASH_DB_USER= -e DASH_DB_PASSWORD= -v "$(pwd)/../cu:/app" pipeline python -m tests.tc_bt3 TC-12`.
5. **Nguyên nhân:** khi `DASH_DB_USER` trống, `tao_engine_chi_doc` dùng lại `DB_USER` – tài khoản có mọi quyền trên
   `ops` – và chỉ đặt `default_transaction_read_only=on`. Tùy chọn này chặn GHI chứ không chặn ĐỌC, nên phần quyền
   đọc vẫn là của pipeline. Tài khoản riêng `dash_reader` được thiết kế ở TD-19 nhưng hoãn sang Giai đoạn 3 (TD-27).
6. **Cách sửa:** `DASH_DB_USER`, `DASH_DB_PASSWORD` bắt buộc (`.env.example` có giá trị mẫu `dash_reader`);
   `db.khoi_tao_csdl` gọi `cap_quyen_dashboard`: tạo hoặc đồng bộ mật khẩu tài khoản (NOSUPERUSER), `GRANT USAGE` +
   `SELECT` trên schema `dwh`, `REVOKE` mọi quyền trên `ops`; tên tài khoản kiểm bằng biểu thức chính quy, mật khẩu
   truyền dạng tham số. Thiếu cấu hình thì dashboard báo đúng tên biến cần điền (TD-36). 6 test mới.
7. **Link commit và xác nhận:** [aab583b](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/aab583b96b6b289a722af6e0722611f6d983c391) · TC-12 PASS: tài khoản
   `dash_reader` đọc được `dwh.v_batch_score`, đọc `ops.stg_customer` bị từ chối "permission denied for schema ops";
   dashboard K1 – K3 vẫn hiển thị đủ. Ảnh: `docs/screenshots/TC-12-lan1-FAIL.png` → `TC-12.png`, `PT-06-dashboard.png`.

### BUG-17  Ảnh Docker cài pillow 12.3.0 có 39 lỗ hổng đã công bố

1. **Mã và mức độ:** BUG-17 · **MAJOR** – thư viện có lỗ hổng đã công bố nằm trong ảnh chạy hệ thống. Không xếp
   Critical vì chưa có đường khai thác trong ứng dụng hiện tại: các lỗ hổng nằm ở bộ giải mã ảnh của pillow, còn
   dashboard không nhận tệp ảnh nào từ người dùng. Vẫn sửa ngay vì checklist bảo mật mục 7 yêu cầu.
2. **Phát hiện bởi:** PT-01 – phép thử máy trắng, bước kiểm checklist bảo mật mục 7, ngày 07/11/2026 ở commit `4ba61ab`.
3. **Triệu chứng:** `pip-audit -r requirements.txt` → `pillow 12.3.0` với 39 mã lỗ hổng (PYSEC-2026-4327, PYSEC-2026-4328,
   GHSA-78g4-xqwv-q3g8, …), bản sửa 13.0.0; pillow không có trong `requirements.txt`.
4. **Cách tái lập:** `git checkout 4ba61ab` → `pip install pip-audit` → `pip-audit -r requirements.txt`.
5. **Nguyên nhân:** `requirements.txt` chỉ ghim 10 gói dùng trực tiếp; 38 gói gián tiếp (pillow do streamlit kéo theo;
   đếm bằng `pip freeze` sau khi cài vào môi trường ảo sạch trên Linux) để pip tự chọn lúc dựng, nên không ai biết
   ảnh Docker đang chứa phiên bản nào và không bước nào kiểm lỗ hổng. Thêm vào đó streamlit 1.64.0 khai báo `pillow < 13` nên không nâng riêng pillow được.
6. **Cách sửa:** streamlit 1.64.0 → 1.67.0 (khai báo `pillow < 14`), ghim `pillow==13.0.0`; `requirements.txt` thành
   tệp khóa đầy đủ 47 gói – 10 trực tiếp + 37 gián tiếp, lấy từ `pip freeze` của môi trường ảo sạch (streamlit 1.67 bỏ
   được `toml`, `httptools`; watchdog chỉ ngoài macOS, colorama chỉ trên Windows – đúng khai báo của gói); ghi cách
   cập nhật ở đầu tệp (TD-40). Thông điệp commit 43be2fa ghi nhầm "36 gián tiếp / 48 gói" – số đúng là 38 và 47,
   kiểm lại ngày 07/11/2026 bằng cài mới hai bản `requirements.txt`. Bước `pip-audit` trong CI thêm ở commit sau
   ([1a315f9](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/1a315f938c779df7ea7b5f1de8d4fc72ee1e9f03)), để lỗi này không quay lại.
7. **Link commit và xác nhận:** [43be2fa](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/43be2fa849e139b0ca9e280607c72545fbdda6f7) · `pip-audit`: "No known
   vulnerabilities found"; pytest 192 passed (.venv), 190 passed, 3 skipped (Docker); dashboard K1 – K3 hiển thị đúng
   với streamlit 1.67.0. Ảnh: `docs/screenshots/PT-08-pip-audit.png`.

### BUG-18  Mất CSDL trong Docker nhưng câu báo khuyên lệnh Homebrew

1. **Mã và mức độ:** BUG-18 · **MINOR** – nghiệp vụ vẫn đúng (mã thoát 1, không ghi gì, không lộ mật khẩu); chỉ lời
   khuyên sai môi trường làm người vận hành mất thời gian.
2. **Phát hiện bởi:** PT-01 – phép thử máy trắng, bước "gây một lỗi và đọc phản hồi" của checklist bảo mật mục 5, ngày
   07/11/2026 ở commit `43be2fa`.
3. **Triệu chứng:** `docker compose stop db` rồi `docker compose run --rm --no-deps pipeline` → "Không kết nối được
   PostgreSQL ở db:5432 … Kiểm tra PostgreSQL đang chạy (macOS: brew services start postgresql@14), CSDL đã tạo
   (createdb smartcrm) …" – hai lệnh không có và không cần trong container.
4. **Cách tái lập:** `git checkout 43be2fa` → hai lệnh của Deployment Guide → `docker compose stop db` →
   `docker compose run --rm --no-deps pipeline`.
5. **Nguyên nhân:** câu báo của `LoiKetNoiCSDL` viết cố định ở BT2 (TD-31), khi hệ thống chỉ có cách cài trên máy cá
   nhân; mã không biết mình đang chạy trong container nên không chọn được cách sửa đúng.
6. **Cách sửa:** `Dockerfile` đặt `SMARTCRM_TRONG_DOCKER=1`; `pipeline.cach_sua_ket_noi()` chọn câu theo nơi chạy –
   trong Docker: `docker compose ps -a`, `docker compose up -d db`, `down -v` khi đã đổi mật khẩu. 1 test mới; test cũ
   bỏ biến này để chạy được cả trong container.
7. **Link commit và xác nhận:** [e91fdc1](https://github.com/Duongmy2612/smartcrm-2374802010318-customer-data-quality/commit/e91fdc1788fac83a8e24154d1b3f1130f2aae0a0) · làm lại bước gây lỗi: câu báo
   chỉ lệnh `docker compose`, không còn `brew`, `createdb`, không có mật khẩu; pytest 193 passed (.venv), 191 passed,
   3 skipped (Docker). Ảnh: `docs/screenshots/PT-07-mat-csdl.png`.

