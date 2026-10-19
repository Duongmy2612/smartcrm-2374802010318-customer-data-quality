"""Đọc configs/config.yaml – người dùng, vai trò, ngưỡng của prototype (SRS mục 2.4).

Bí mật (mật khẩu CSDL) KHÔNG nằm ở đây mà ở .env (NFR-07), xem src/db.py.
"""
import pathlib

import yaml

GOC = pathlib.Path(__file__).resolve().parent.parent      # thư mục gốc của repo
TEP_CAU_HINH = GOC / 'configs' / 'config.yaml'


def doc_cau_hinh(duong_dan: pathlib.Path = TEP_CAU_HINH) -> dict:
    with open(duong_dan, encoding='utf-8') as f:
        return yaml.safe_load(f)


def tim_nguoi_dung(cau_hinh: dict, ten_dang_nhap: str) -> dict | None:
    """Trả về {ten_dang_nhap, vai_tro, don_vi} hoặc None nếu tên đăng nhập không có trong cấu hình."""
    for nd in cau_hinh.get('nguoi_dung', []):
        if nd['ten_dang_nhap'] == ten_dang_nhap:
            return nd
    return None


def nguoi_dung_mac_dinh(cau_hinh: dict, vai_tro: str) -> str | None:
    """Tên đăng nhập đầu tiên có vai trò cho trước (dùng khi chạy dòng lệnh không truyền --nguoi-nap)."""
    for nd in cau_hinh.get('nguoi_dung', []):
        if nd['vai_tro'] == vai_tro:
            return nd['ten_dang_nhap']
    return None


def duong_dan(cau_hinh: dict, khoa: str) -> pathlib.Path:
    """Đường dẫn trong cấu hình là tương đối so với gốc repo."""
    p = GOC / cau_hinh[khoa]
    p.mkdir(parents=True, exist_ok=True)
    return p
