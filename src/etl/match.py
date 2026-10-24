"""② match.py – FR-04 (UC3): phát hiện cặp nghi trùng.  Sprint 2 (buổi 10), TD-14.

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
    Đầu ra  : ops.dup_candidate (status PENDING), ops.stg_customer.name_key.
    Đo      : NFR-01 phần 2 (≤ 120 giây trên mẫu 8.000 dòng) – pipeline in thời gian của bước này.
"""
import time
import unicodedata

import pandas as pd
from rapidfuzz import fuzz
from sqlalchemy import text

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


# ------------------------------------------------------------------ đọc / ghi CSDL
def phat_hien_cap(conn, batch_id: int, nguong: float = 85) -> dict:
    """UC3 cho một đợt: ghi name_key, ghi cặp mới vào ops.dup_candidate (PENDING); trả về số đếm và thời gian."""
    t0 = time.perf_counter()
    # 1. name_key cho hồ sơ hợp lệ của đợt (UPDATE theo tập qua bảng tạm thời)
    dot = pd.DataFrame(conn.execute(text(
        'SELECT stg_id, name_norm FROM ops.stg_customer '
        'WHERE batch_id = :b AND error_code IS NULL AND phone_norm IS NOT NULL'), {'b': batch_id}).fetchall(),
        columns=['stg_id', 'name_norm'])
    dot['name_key'] = dot['name_norm'].map(tao_name_key)
    conn.exec_driver_sql('CREATE TEMP TABLE tmp_name_key (stg_id BIGINT PRIMARY KEY, name_key VARCHAR(120)) '
                         'ON COMMIT DROP')
    dot[['stg_id', 'name_key']].to_sql('tmp_name_key', conn, if_exists='append', index=False, chunksize=5000)
    conn.execute(text('UPDATE ops.stg_customer s SET name_key = t.name_key FROM tmp_name_key t '
                      'WHERE s.stg_id = t.stg_id'))
    conn.exec_driver_sql('DROP TABLE tmp_name_key')

    # 2. hồ sơ hợp lệ của đợt này và các đợt trước; cặp đã có
    ho_so = pd.DataFrame(conn.execute(text(
        'SELECT stg_id, phone_norm, name_norm FROM ops.stg_customer '
        'WHERE batch_id <= :b AND error_code IS NULL AND phone_norm IS NOT NULL'), {'b': batch_id}).fetchall(),
        columns=['stg_id', 'phone_norm', 'name_norm'])
    ho_so['name_key'] = ho_so['name_norm'].map(tao_name_key)      # cả đợt nạp trước Sprint 2 (chưa có name_key)
    cap_da_co = {tuple(r) for r in conn.execute(text('SELECT stg_id_a, stg_id_b FROM ops.dup_candidate'))}

    # 3. so khớp và ghi
    t1 = time.perf_counter()
    tk = {'cap_ung_vien': 0, 'so_khac_nhau': 0}
    cap = tim_cap(ho_so, set(dot['stg_id']), nguong, cap_da_co, tk)
    t_so_khop = time.perf_counter() - t1
    if len(cap):
        conn.execute(text(
            'INSERT INTO ops.dup_candidate (stg_id_a, stg_id_b, match_type, score) '
            'VALUES (:stg_id_a, :stg_id_b, :match_type, :score) ON CONFLICT (stg_id_a, stg_id_b) DO NOTHING'),
            [{k: (int(v) if k.startswith('stg') else v) for k, v in r.items()} for r in cap.to_dict('records')])
    return {
        'ho_so_dot': len(dot), 'ho_so_so_khop': len(ho_so), 'so_khac_nhau': tk['so_khac_nhau'],
        'cap_ung_vien': tk['cap_ung_vien'],
        'exact': int((cap['match_type'] == 'EXACT_PHONE').sum()),
        'fuzzy': int((cap['match_type'] == 'FUZZY').sum()),
        'bo_qua_da_co': len(cap_da_co), 'nguong': nguong,
        'thoi_gian_so_khop': t_so_khop, 'thoi_gian': time.perf_counter() - t0,
    }


def main(argv=None) -> int:
    """Chạy lại riêng UC3 cho một đợt đã nạp (ví dụ khi bước [5/5] của luồng chính lỗi – TD-17):

        python -m src.etl.match --dot 1

    Mã thoát: 0 thành công · 1 lỗi kỹ thuật · 2 đợt không tồn tại.
    """
    import argparse
    import sys

    from src import config, db
    from src.etl import load_dwh
    ap = argparse.ArgumentParser(description='UC3 – Phát hiện cặp nghi trùng cho một đợt nạp, rồi nạp kho')
    ap.add_argument('--dot', type=int, required=True, help='batch_id trong ops.load_batch')
    a = ap.parse_args(argv)
    try:
        engine = db.tao_engine()
        with engine.begin() as conn:
            if not conn.execute(text('SELECT 1 FROM ops.load_batch WHERE batch_id = :b'), {'b': a.dot}).first():
                print(f'TỪ CHỐI: không có đợt nạp {a.dot}', file=sys.stderr)
                return 2
            kq = phat_hien_cap(conn, a.dot, float(config.doc_cau_hinh()['nguong_fuzzy']))
            nap = load_dwh.nap_kho(conn)
        so = lambda n: f'{n:,}'.replace(',', '.')        # noqa: E731
        giay = f"{kq['thoi_gian']:.1f}".replace('.', ',')
        print(f"UC3 đợt {a.dot}: {so(kq['ho_so_so_khop'])} hồ sơ · {so(kq['cap_ung_vien'])} cặp ứng viên · "
              f"EXACT_PHONE +{so(kq['exact'])} · FUZZY +{so(kq['fuzzy'])} · {giay} s")
        print('load_dwh: ' + load_dwh.dong_nap_kho(nap, so))
        return 0
    except Exception as e:                            # noqa: BLE001
        print(f'LỖI: {type(e).__name__}: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
