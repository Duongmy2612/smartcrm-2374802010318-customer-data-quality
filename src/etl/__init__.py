"""Lớp ② Xử lý – nghiệp vụ (Hình 3.1). Ba pha E / T / L tách ở ba nơi (TD-22, BT2):

    pha E  extract.py        FR-01               UC1   đọc tệp, kiểm cột, băm SHA-256, đổi tên cột        (không CSDL)
    pha T  transform.py      FR-02, FR-03, FR-10 UC2   chuẩn hóa số điện thoại, họ tên; mã lỗi; phân loại  (không CSDL)
           dq_evaluate.py    FR-07, FR-08        UC7   6 hàm kiểm chất lượng DQ-01…06, chỉ số QL7-06        (không CSDL)
           match.py          FR-04               UC3   name_key, blocking, điểm tương đồng, tìm cặp         (không CSDL)
    pha L  load_ops.py       FR-01, 02, 08, 10   –     mọi lệnh đọc/ghi schema ops, CSV hồ sơ lỗi, bảng reject
           load_dwh.py       FR-09               –     nạp kho dwh, SCD loại 2 cho dim_rule, đối soát
           merge_service.py  FR-05, FR-06, FR-11 UC4/5 Gộp / Giữ riêng trong một giao dịch                (Giai đoạn 3)
    chung  tien_ich.py       –                   –     hàm thuần dùng chung (la_trong), không thuộc pha nào (TD-29)

Quy ước: pha E/T chỉ có hàm THUẦN (nhận/trả DataFrame hoặc giá trị) để kiểm thử được không cần CSDL; pha L chỉ chạy
lệnh SQL trên `conn` do src/pipeline.py mở, không tự tính nghiệp vụ. tests/test_ranh_gioi_lop.py giữ quy ước này.
"""
