"""② match.py – pha TRANSFORM của UC3, FR-04: phát hiện cặp nghi trùng.  Sprint 2 (buổi 10), TD-14.
Chỉ có hàm THUẦN; đọc hồ sơ và ghi cặp là việc của load_ops.py, thứ tự gọi ở src/pipeline.chay_uc3 (TD-22).

Hợp đồng dữ liệu (chốt ở BT1, docs/data-requirements.md mục 7):
    Đầu vào : hồ sơ thô có số hợp lệ (phone_norm, không có mã lỗi – QL7-04) của đợt vừa nạp, so với chính nó
              và với hồ sơ hợp lệ của các đợt trước.
    Xử lý   : name_key = họ tên bỏ dấu, chữ thường, bỏ khoảng trắng thừa.
              EXACT_PHONE – cùng phone_norm: nhóm k hồ sơ tạo k − 1 cặp, ghép hồ sơ nạp sớm nhất với từng hồ sơ
                            còn lại (QL7-02).
              FUZZY       – khác số, cùng 5 số đầu HOẶC cùng 5 số cuối (blocking, NFR-01), điểm ≥ ngưỡng.
                            Chỉ so HỒ SƠ ĐẠI DIỆN (nạp sớm nhất) của mỗi số: các hồ sơ khác cùng số đã nối với
                            đại diện bằng cặp EXACT_PHONE, so tiếp sẽ sinh nhiều cặp lặp cho cùng hai số (TD-18).
              Điểm (QL7-03) = 0,6 × độ giống số (100 nếu bằng nhau, ngược lại fuzz.ratio) +
                              0,4 × fuzz.token_sort_ratio(name_key).
              Cặp đã có trong dup_candidate (kể cả đã Giữ riêng – QL7-05) không tạo lại.
    Đầu ra  : bảng cặp [stg_id_a, stg_id_b, match_type, score] – load_ops.ghi_cap ghi vào ops.dup_candidate
              (status PENDING); name_key – load_ops.ghi_name_key ghi vào ops.stg_customer.
    Đo      : NFR-01 phần 2 (≤ 120 giây trên mẫu 8.000 dòng) – pipeline in thời gian của bước này.
"""
import unicodedata

import pandas as pd
from rapidfuzz import fuzz

DO_DAI_KHOI = 5                                  # blocking: 5 số đầu / 5 số cuối


# ------------------------------------------------------------------ hàm thuần (kiểm thử ở tests/test_match.py)
def tao_name_key(ten) -> str | None:
    """Khóa họ tên: bỏ dấu (kể cả đ/Đ), chữ thường, bỏ khoảng trắng thừa. Giống name_key của script profiling."""
    if ten is None or pd.isna(ten):
        return None
    s = unicodedata.normalize('NFD', str(ten))
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn').replace('đ', 'd').replace('Đ', 'D')
    s = ' '.join(s.lower().split())
    return s or None


def do_giong_so(a: str, b: str) -> float:
    return 100.0 if a == b else float(fuzz.ratio(a, b))


def diem_tuong_dong(so_a: str, so_b: str, khoa_a: str | None, khoa_b: str | None) -> float:
    """QL7-03, làm tròn 2 chữ số như cột score NUMERIC(5,2)."""
    giong_ten = float(fuzz.token_sort_ratio(khoa_a or '', khoa_b or ''))
    return round(0.6 * do_giong_so(so_a, so_b) + 0.4 * giong_ten, 2)


def la_cap_fuzzy(diem: float, nguong: float) -> bool:
    """QL7-02: điểm BẰNG ngưỡng vẫn tạo cặp (≥)."""
    return diem >= nguong


def cap_ung_vien(ho_so: pd.DataFrame) -> set[tuple[int, int]]:
    """Blocking: mọi cặp (a, b), a < b, cùng 5 số đầu hoặc cùng 5 số cuối của phone_norm.
    Truyền vào bảng hồ sơ đại diện (mỗi số một hồ sơ) thì mọi cặp trả về đều khác số."""
    cap = set()
    for khoa in (ho_so['phone_norm'].str[:DO_DAI_KHOI], ho_so['phone_norm'].str[-DO_DAI_KHOI:]):
        for _, nhom in ho_so.groupby(khoa)['stg_id']:
            ids = sorted(nhom.tolist())
            cap.update((ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids)))
    return cap


def tim_cap(ho_so: pd.DataFrame, ho_so_moi: set[int] | None = None, nguong: float = 85,
            cap_da_co: set[tuple[int, int]] = frozenset(), thong_ke: dict | None = None) -> pd.DataFrame:
    """Phát hiện cặp nghi trùng (FR-04) trên bảng ho_so[stg_id, phone_norm, name_key].

    ho_so_moi: stg_id của đợt vừa nạp – chỉ trả về cặp có ít nhất một hồ sơ mới (None = mọi hồ sơ là mới).
    cap_da_co: cặp (a, b) đã có trong dup_candidate, kể cả đã Giữ riêng (QL7-05) – không tạo lại.
    thong_ke : nếu truyền dict vào thì ghi thêm số cặp ứng viên sau blocking (để báo cáo NFR-01).
    Trả về DataFrame[stg_id_a, stg_id_b, match_type, score], stg_id_a < stg_id_b (a là hồ sơ nạp sớm hơn).
    """
    cot = ['stg_id_a', 'stg_id_b', 'match_type', 'score']
    hs = ho_so[ho_so['phone_norm'].notna()]                     # QL7-04: không có số hợp lệ → không tham gia
    if hs.empty:
        return pd.DataFrame(columns=cot)
    moi = set(hs['stg_id']) if ho_so_moi is None else set(ho_so_moi)
    so = dict(zip(hs['stg_id'], hs['phone_norm']))
    khoa = dict(zip(hs['stg_id'], hs['name_key']))
    dong = []

    # EXACT_PHONE: hồ sơ nạp sớm nhất (stg_id nhỏ nhất) của mỗi số ghép với từng hồ sơ còn lại
    for _, nhom in hs.groupby('phone_norm')['stg_id']:
        ids = sorted(nhom.tolist())
        for b in ids[1:]:
            a = ids[0]
            if (a in moi or b in moi) and (a, b) not in cap_da_co:
                dong.append((a, b, 'EXACT_PHONE', diem_tuong_dong(so[a], so[b], khoa[a], khoa[b])))

    # FUZZY: chỉ giữa hồ sơ đại diện của hai số KHÁC nhau, trong cùng khối, điểm ≥ ngưỡng (TD-18)
    dai_dien = hs.sort_values('stg_id').drop_duplicates('phone_norm')
    ung_vien = cap_ung_vien(dai_dien)
    if thong_ke is not None:
        thong_ke.update(cap_ung_vien=len(ung_vien), so_khac_nhau=len(dai_dien))
    for a, b in ung_vien:
        if (a not in moi and b not in moi) or (a, b) in cap_da_co:
            continue
        d = diem_tuong_dong(so[a], so[b], khoa[a], khoa[b])
        if la_cap_fuzzy(d, nguong):
            dong.append((a, b, 'FUZZY', d))
    return pd.DataFrame(dong, columns=cot).sort_values(['stg_id_a', 'stg_id_b'], ignore_index=True)
