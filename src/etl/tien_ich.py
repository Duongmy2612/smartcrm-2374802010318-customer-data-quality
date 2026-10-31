"""② tien_ich.py – hàm thuần dùng chung cho các pha của lớp ② (TD-29).

Trước BT2, `la_trong` nằm ở extract.py nên transform.py và dq_evaluate.py (pha T) phải import từ pha E – trái với
quy ước "các pha không gọi lẫn nhau". Hàm được chuyển ra đây: không thuộc pha nào, không đọc/ghi CSDL, không gọi
mô-đun nào của src/etl. tests/test_ranh_gioi_lop.py kiểm pha T không import pha E, pha L.
"""
import pandas as pd


def la_trong(s: pd.Series) -> pd.Series:
    """Ô trống = chuỗi rỗng hoặc chỉ có khoảng trắng."""
    return s.fillna('').str.strip() == ''
