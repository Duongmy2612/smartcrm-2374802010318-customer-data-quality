"""② danh_gia_match.py – pha TRANSFORM (hàm thuần), NFR-03: kiểm chứng chất lượng phát hiện trùng của match.py.

NFR-03 (docs/srs.md mục 4): "Trên tập 300 cặp gán nhãn tay, ở ngưỡng 85: precision ≥ 85% và recall ≥ 80%.
Cách kiểm chứng: tính precision/recall; chỉnh ngưỡng nếu chưa đạt." Làm ở BT2 theo nhận xét BT1 của giảng viên
(TD-32 trong docs/thay-doi-thiet-ke.md). Điều phối ở src/kiem_chung_nfr03.py.

Ba bước, đều là hàm THUẦN (không CSDL, không đọc/ghi tệp):
  1. khung_cap   – lập KHUNG CẶP: mọi cặp hệ thống ghép, cộng các cặp có thể là cùng một khách mà hệ thống không
                   ghép; chia 5 tầng T1 … T5 (bảng TANG).
  2. chon_mau    – chọn 300 cặp theo chỉ tiêu từng tầng (seed 42), để tập gán nhãn có cả cặp hệ thống ghép (đo
                   precision) lẫn cặp hệ thống bỏ qua (đo recall). Khung ≤ 300 cặp thì lấy hết.
  3. tinh_chi_so – so quyết định của hệ thống ở một ngưỡng với nhãn của người → ma trận nhầm lẫn, precision,
                   recall. quet_nguong lặp lại cho nhiều ngưỡng ("chỉnh ngưỡng nếu chưa đạt").

Quyết định của hệ thống cho MỘT cặp tính lại bằng chính các hàm của match.py (FR-04, QL7-02, QL7-03):
    cùng phone_norm                                   → ghép (EXACT_PHONE)
    khác số, cùng khối 5 số đầu/cuối, điểm ≥ ngưỡng   → ghép (FUZZY)
    còn lại, kể cả hồ sơ không có số hợp lệ (QL7-04)  → không ghép
Vì vậy đổi công thức điểm hay ngưỡng trong match.py thì phép kiểm chứng tự đo theo cách mới.
"""
import random

import pandas as pd

from src.etl.match import DO_DAI_KHOI, cap_ung_vien, diem_tuong_dong

YEU_CAU_PRECISION = 85          # NFR-03, đơn vị %
YEU_CAU_RECALL = 80
DIEM_SAT_NGUONG = 70            # T3: điểm từ 70 tới dưới ngưỡng – vùng hệ thống "suýt" ghép
CO_MAU = 300                    # NFR-03: 300 cặp

TANG = {
    'T1': 'Cùng số điện thoại (EXACT_PHONE) – hệ thống ghép',
    'T2': 'Khác số, cùng khối, điểm ≥ ngưỡng (FUZZY) – hệ thống ghép',
    'T3': 'Khác số, cùng khối, điểm 70 – dưới ngưỡng – hệ thống không ghép',
    'T4': 'Cùng họ tên, một bên không tham gia so khớp (thiếu/sai số – QL7-04) – hệ thống không ghép',
    'T5': 'Cùng họ tên, hai số khác khối hoặc điểm < 70 – hệ thống không ghép',
}
# Chỉ tiêu mỗi tầng (lấy theo thứ tự này). T2 thường rất ít nên lấy hết; T3 – T5 là nơi tìm cặp hệ thống BỎ SÓT
# (recall); T1 lấy phần còn lại cho đủ 300 (precision của cặp cùng số).
CHI_TIEU = {'T2': 50, 'T3': 60, 'T4': 60, 'T5': 40, 'T1': None}


class NhanKhongHopLe(ValueError):
    """Phiếu nhãn không dùng được (thiếu cột, ô nhãn trống/sai giá trị, cặp không thuộc khung) – mã thoát 2."""


# ------------------------------------------------------------------ 1. khung cặp
def _co_so(x) -> bool:
    return x is not None and not pd.isna(x)


def _cung_khoi(a: str, b: str) -> bool:
    """Blocking của FR-04: cùng 5 số đầu HOẶC cùng 5 số cuối."""
    return a[:DO_DAI_KHOI] == b[:DO_DAI_KHOI] or a[-DO_DAI_KHOI:] == b[-DO_DAI_KHOI:]


def xep_tang(cung_so: bool, cung_khoi: bool, diem: float | None, thieu_so: bool, cung_ten: bool,
             nguong: float = 85) -> str | None:
    """Tầng của một cặp (bảng TANG). None = cặp không thuộc khung (khác tên, khác số, điểm thấp)."""
    if cung_so:
        return 'T1'
    if cung_khoi and diem is not None and diem >= nguong:
        return 'T2'
    if cung_khoi and diem is not None and diem >= DIEM_SAT_NGUONG:
        return 'T3'
    if cung_ten and thieu_so:
        return 'T4'
    if cung_ten:
        return 'T5'
    return None


def khung_cap(ho_so: pd.DataFrame, nguong: float = 85) -> pd.DataFrame:
    """ho_so[ma, phone_norm, name_key] (ma = số dòng trong tệp) → khung cặp
    [ma_a, ma_b, tang, cung_so, cung_khoi, diem], ma_a < ma_b.
    phone_norm để TRỐNG ở hồ sơ không tham gia so khớp (có mã lỗi – QL7-04), đúng tập hồ sơ match.tim_cap nhận.

    Ba nguồn cặp:
      • cùng số: hồ sơ sớm nhất của mỗi số ghép với từng hồ sơ còn lại – đúng k − 1 cặp như QL7-02;
      • cùng khối: giữa hồ sơ đại diện của hai số khác nhau – đúng tập cặp match.tim_cap chấm điểm (TD-18);
      • cùng name_key mà KHÔNG thuộc hai nguồn trên (một bên không có số hợp lệ, hoặc hai số khác khối): nơi hệ
        thống không bao giờ so, nên có thể BỎ SÓT một khách.
    """
    so = dict(zip(ho_so['ma'], ho_so['phone_norm']))
    khoa = dict(zip(ho_so['ma'], ho_so['name_key']))
    cap = set()

    co_so = ho_so[ho_so['phone_norm'].map(_co_so)]
    for _, nhom in co_so.groupby('phone_norm')['ma']:
        ids = sorted(nhom.tolist())
        cap.update((ids[0], b) for b in ids[1:])
    dai_dien = co_so.sort_values('ma').drop_duplicates('phone_norm').rename(columns={'ma': 'stg_id'})
    cap.update(cap_ung_vien(dai_dien))
    co_ten = ho_so[ho_so['name_key'].map(_co_so)]
    for _, nhom in co_ten.groupby('name_key')['ma']:
        ids = sorted(nhom.tolist())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                if _co_so(so[a]) and _co_so(so[b]) and (so[a] == so[b] or _cung_khoi(so[a], so[b])):
                    continue                   # hệ thống đã xét cặp này ở nguồn cùng số / cùng khối
                cap.add((a, b))

    dong = []
    for a, b in sorted(cap):
        sa, sb = so[a], so[b]
        thieu_so = not (_co_so(sa) and _co_so(sb))
        cung_so = not thieu_so and sa == sb
        cung_khoi = not thieu_so and _cung_khoi(sa, sb)
        diem = diem_tuong_dong(sa, sb, khoa[a], khoa[b]) if (cung_so or cung_khoi) else None
        cung_ten = _co_so(khoa[a]) and khoa[a] == khoa[b]
        tang = xep_tang(cung_so, cung_khoi, diem, thieu_so, cung_ten, nguong)
        if tang:
            dong.append((a, b, tang, cung_so, cung_khoi, diem))
    return pd.DataFrame(dong, columns=['ma_a', 'ma_b', 'tang', 'cung_so', 'cung_khoi', 'diem'])


# ------------------------------------------------------------------ 2. chọn mẫu
def chon_mau(khung: pd.DataFrame, co_mau: int = CO_MAU, seed: int = 42) -> pd.DataFrame:
    """Chọn co_mau cặp theo CHI_TIEU (thứ tự T2 → T3 → T4 → T5 → T1); tầng ít hơn chỉ tiêu thì lấy hết, T1 bù cho
    đủ. Thêm cột trong_so = số cặp của tầng trong khung / số cặp lấy (để ước lượng cho toàn khung).
    Trả về theo thứ tự xáo trộn (seed) để người gán nhãn không đoán được tầng qua vị trí dòng."""
    r = random.Random(seed)
    phan = []
    con_lai = co_mau
    for tang, chi_tieu in CHI_TIEU.items():
        nhom = khung[khung['tang'] == tang].sort_values(['ma_a', 'ma_b'])
        lay = min(len(nhom), con_lai if chi_tieu is None else min(chi_tieu, con_lai))
        chon = sorted(r.sample(range(len(nhom)), lay))
        p = nhom.iloc[chon].copy()
        p['trong_so'] = len(nhom) / lay if lay else 0.0
        phan.append(p)
        con_lai -= lay
    mau = pd.concat(phan, ignore_index=True)
    thu_tu = list(range(len(mau)))
    r.shuffle(thu_tu)
    mau = mau.iloc[thu_tu].reset_index(drop=True)
    mau.insert(0, 'ma_cap', [f'C{i:03d}' for i in range(1, len(mau) + 1)])
    return mau


def dem_theo_tang(khung: pd.DataFrame, mau: pd.DataFrame) -> pd.DataFrame:
    """Bảng số cặp trong khung và số cặp lấy mẫu của từng tầng (in ra khi chạy, đưa vào báo cáo)."""
    return pd.DataFrame([{'tang': t, 'mo_ta': TANG[t], 'trong_khung': int((khung['tang'] == t).sum()),
                          'lay_mau': int((mau['tang'] == t).sum())} for t in TANG])


# ------------------------------------------------------------------ 3. nhãn và chỉ số
def kiem_phieu_nhan(phieu: pd.DataFrame) -> pd.DataFrame:
    """Kiểm phiếu do người gán: đủ cột ma_cap, dong_a, dong_b, nhan; mỗi ô nhan là 1 (cùng một khách) hoặc
    0 (hai khách khác nhau); không trùng cặp. Trả về [ma_cap, ma_a, ma_b, nhan] với nhan kiểu int."""
    thieu = [c for c in ('ma_cap', 'dong_a', 'dong_b', 'nhan') if c not in phieu.columns]
    if thieu:
        raise NhanKhongHopLe(f"Phiếu nhãn thiếu cột: {', '.join(thieu)} – dùng đúng phiếu do lệnh --tao-phieu tạo")
    if phieu.empty:
        raise NhanKhongHopLe('Phiếu nhãn không có cặp nào')
    nhan = phieu['nhan'].map(lambda x: '' if pd.isna(x) else str(x).strip().removesuffix('.0'))
    trong = phieu.loc[nhan == '', 'ma_cap'].astype(str).tolist()
    if trong:
        raise NhanKhongHopLe(f'Còn {len(trong)} cặp chưa gán nhãn (ví dụ {", ".join(trong[:5])}) – điền 1 hoặc 0 '
                             'vào cột nhan rồi chạy lại')
    sai = phieu.loc[~nhan.isin(['0', '1']), 'ma_cap'].astype(str).tolist()
    if sai:
        raise NhanKhongHopLe(f'Cột nhan chỉ nhận 1 (cùng một khách) hoặc 0 (hai khách khác nhau); {len(sai)} ô sai '
                             f'(ví dụ {", ".join(sai[:5])})')
    try:
        ma_a = phieu['dong_a'].astype(int)
        ma_b = phieu['dong_b'].astype(int)
    except (TypeError, ValueError):
        raise NhanKhongHopLe('Cột dong_a, dong_b phải là số dòng – không sửa hai cột này trong phiếu') from None
    ra = pd.DataFrame({'ma_cap': phieu['ma_cap'].astype(str), 'ma_a': ma_a.where(ma_a < ma_b, ma_b),
                       'ma_b': ma_b.where(ma_a < ma_b, ma_a), 'nhan': nhan.astype(int)})
    lap = ra.duplicated(['ma_a', 'ma_b'])
    if lap.any():
        raise NhanKhongHopLe(f"Phiếu có cặp lặp lại: {', '.join(ra.loc[lap, 'ma_cap'].head(5))}")
    return ra


def gan_nhan_vao_khung(khung: pd.DataFrame, nhan: pd.DataFrame, mau: pd.DataFrame) -> pd.DataFrame:
    """Ghép nhãn với khung (tầng, điểm) và trọng số tầng của mẫu. Cặp có nhãn mà không thuộc khung → phiếu không
    khớp tệp nguồn (sai tệp, hoặc tệp đã đổi sau khi tạo phiếu) → từ chối."""
    bang = nhan.merge(khung, on=['ma_a', 'ma_b'], how='left', indicator=True)
    la = bang.loc[bang['_merge'] == 'left_only', 'ma_cap'].tolist()
    if la:
        raise NhanKhongHopLe(f'{len(la)} cặp trong phiếu không thuộc khung cặp của tệp nguồn (ví dụ '
                             f'{", ".join(la[:5])}) – phiếu tạo từ tệp khác hoặc tệp nguồn đã đổi')
    bang = bang.drop(columns='_merge')
    trong_so = mau.groupby('tang')['trong_so'].first()
    bang['trong_so'] = bang['tang'].map(trong_so).fillna(1.0)
    return bang


def he_thong_ghep(bang: pd.DataFrame, nguong: float) -> pd.Series:
    """Quyết định của hệ thống ở ngưỡng cho trước: cùng số, hoặc cùng khối và điểm ≥ ngưỡng (QL7-02, FR-04)."""
    return bang['cung_so'].astype(bool) | (bang['cung_khoi'].astype(bool) & (bang['diem'].fillna(-1) >= nguong))


def _ti_le(tu: float, mau: float) -> float | None:
    return tu / mau if mau else None


def _dat(tu: float, mau: float, yeu_cau_phan_tram: int) -> bool:
    """tu / mau ≥ yêu cầu, so bằng phép nhân để 17/20 = 85% được tính là ĐẠT (không lệch do số thực)."""
    return mau > 0 and tu * 100 >= yeu_cau_phan_tram * mau


def tinh_chi_so(bang: pd.DataFrame, nguong: float = 85, co_trong_so: bool = False) -> dict:
    """Ma trận nhầm lẫn và precision, recall ở một ngưỡng.

    TP: hệ thống ghép, người nói cùng một khách · FP: hệ thống ghép, người nói khác khách
    FN: hệ thống KHÔNG ghép, người nói cùng một khách (bỏ sót) · TN: không ghép, khác khách.
    precision = TP / (TP + FP) – trong các cặp hệ thống ghép, bao nhiêu phần đúng.
    recall    = TP / (TP + FN) – trong các cặp đúng là một khách, hệ thống tìm ra bao nhiêu phần.
    co_trong_so=True: mỗi cặp đếm bằng trọng số tầng → ước lượng cho toàn khung thay vì cho 300 cặp.
    """
    ghep = he_thong_ghep(bang, nguong)
    dung = bang['nhan'] == 1
    w = bang['trong_so'] if co_trong_so else pd.Series(1, index=bang.index)
    tp, fp = float(w[ghep & dung].sum()), float(w[ghep & ~dung].sum())
    fn, tn = float(w[~ghep & dung].sum()), float(w[~ghep & ~dung].sum())
    if not co_trong_so:
        tp, fp, fn, tn = int(tp), int(fp), int(fn), int(tn)
    dat_p, dat_r = _dat(tp, tp + fp, YEU_CAU_PRECISION), _dat(tp, tp + fn, YEU_CAU_RECALL)
    return {'nguong': nguong, 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': _ti_le(tp, tp + fp), 'recall': _ti_le(tp, tp + fn),
            'dat_precision': dat_p, 'dat_recall': dat_r, 'dat': dat_p and dat_r}


def quet_nguong(bang: pd.DataFrame, cac_nguong=(70, 75, 80, 85, 90, 95)) -> pd.DataFrame:
    """Precision/recall ở nhiều ngưỡng trên cùng tập nhãn – căn cứ để giữ hoặc chỉnh ngưỡng 85 (NFR-03)."""
    return pd.DataFrame([tinh_chi_so(bang, n) for n in cac_nguong])
