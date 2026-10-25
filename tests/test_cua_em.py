from src.etl.match import tao_name_key, diem_tuong_dong


def test_cap_ho_ten_em_tu_nghi():
    # Hai cách viết họ tên của CÙNG một người – em tự nghĩ
    ten_a = "Duong Diem My"
    ten_b = "DIEM MY DUONG"
    khoa_a = tao_name_key(ten_a)
    khoa_b = tao_name_key(ten_b)
    assert khoa_a == "duong diem my"          # name_key em tự tính ra cho ten_a
    # Cùng một số điện thoại, nên độ giống số = 100
    assert diem_tuong_dong("0901234567", "0901234567", khoa_a, khoa_b) == 100   # điểm em tự tính