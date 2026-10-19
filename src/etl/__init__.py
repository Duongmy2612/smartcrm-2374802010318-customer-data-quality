"""Lớp ② Xử lý – nghiệp vụ (Hình 3.1). Mỗi mô-đun ứng với một bước xử lý và một nhóm FR:

    extract.py        FR-01               UC1   đọc tệp, kiểm cột, băm SHA-256, ghi đợt nạp và hồ sơ thô
    transform.py      FR-02, FR-03, FR-10 UC2   chuẩn hóa số điện thoại, họ tên; mã lỗi; customer_clean; CSV hồ sơ lỗi
    dq_evaluate.py    FR-07, FR-08        UC6/7 quy tắc chất lượng, đo TRƯỚC/SAU, ghi dq_result
    match.py          FR-04               UC3   name_key, blocking, điểm tương đồng, dup_candidate        (Sprint 2)
    load_dwh.py       FR-09               –     nạp kho dwh, SCD loại 2 cho dim_rule                      (Sprint 2)
    merge_service.py  FR-05, FR-06, FR-11 UC4/5 danh sách cặp, Gộp / Giữ riêng trong một giao dịch        (Sprint 3)

Quy ước: hàm nghiệp vụ là hàm THUẦN (nhận/trả DataFrame hoặc giá trị, không đọc ghi CSDL) để kiểm thử được;
hàm đọc ghi CSDL nhận tham số `conn` và chỉ chạy lệnh SQL.
"""
