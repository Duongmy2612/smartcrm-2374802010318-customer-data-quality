# -*- coding: utf-8 -*-
"""
Profiling dữ liệu nguồn cho luồng L7 – Chất lượng dữ liệu khách hàng (track DA).

Mọi con số ở docs/data-requirements.md và mục 4 của BT1 được sinh ra từ script này.

Cách chạy (từ thư mục gốc của repo, đã kích hoạt .venv):
    pip install pandas rapidfuzz
    python notebooks/profiling_customers.py data/raw/customers_raw.csv

Đầu ra:
    - In báo cáo ra màn hình.
    - data/processed/mau_cum_8000.csv      : mẫu phát triển 8.000 dòng trích theo cụm số điện thoại.
    - data/processed/profiling_result.json : toàn bộ số đo dạng JSON.

Tái lập (NFR-05): mọi bước ngẫu nhiên dùng SEED = 42.
"""
import json
import os
import random
import re
import sys
import unicodedata

import pandas as pd
from rapidfuzz import fuzz

SEED = 42
SAMPLE_ROWS = 8000            # cỡ mẫu phát triển (mục 2.4 SRS)
RANDOM_SAMPLE_ROWS = 6000     # cỡ mẫu ngẫu nhiên theo dòng của script Buổi 4 (để so sánh)
FUZZY_THRESHOLD = 85          # ngưỡng mặc định của QL7-02
EMAIL_RE = r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"
WEIGHTS = {"DQ-01": 0.25, "DQ-02": 0.25, "DQ-03": 0.15, "DQ-04": 0.10, "DQ-05": 0.20, "DQ-06": 0.05}


# --------------------------------------------------------------------------- chuẩn hóa
def norm_phone(p: str):
    """QT-02: bỏ dấu cách, dấu chấm, dấu gạch; +84/84 → 0; hợp lệ khi khớp ^0\\d{9}$."""
    s = re.sub(r"[\s.\-]", "", p.strip())
    if s.startswith("+84"):
        s = "0" + s[3:]
    elif s.startswith("84") and len(s) == 11:
        s = "0" + s[2:]
    return s if re.fullmatch(r"0\d{9}", s) else None


def no_accent(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def name_key(s: str) -> str:
    """Khóa so khớp họ tên: không dấu, chữ thường, bỏ khoảng trắng thừa (QL7-03)."""
    return " ".join(no_accent(s).lower().split())


def phone_form(p: str) -> str:
    p0 = p.strip()
    if p0 == "":
        return "trống"
    if re.fullmatch(r"0\d{9}", p0):
        return "chuẩn 0xxxxxxxxx"
    if re.fullmatch(r"\+84\d{9}", p0):
        return "+84…"
    if re.fullmatch(r"84\d{9}", p0):
        return "84…"
    if re.fullmatch(r"0\d{3} \d{3} \d{3}", p0):
        return "có dấu cách"
    if re.fullmatch(r"0\d{3}\.\d{3}\.\d{3}", p0):
        return "có dấu chấm"
    return "khác"


def blank(s: pd.Series) -> pd.Series:
    return s.str.strip() == ""


# --------------------------------------------------------------------------- đo chất lượng
def measure(frame: pd.DataFrame, stage: str, resolved_dups: bool = False):
    """Tỉ lệ đạt DQ-01 … DQ-06 với mẫu số = phạm vi áp dụng của từng quy tắc (mục 4.5 BT1).

    stage = "TRUOC": đo trên giá trị thô; "SAU": đo sau chuẩn hóa.
    resolved_dups = True: giả định mọi cặp nghi trùng đã được quyết định (DQ-05 đạt 100%).
    """
    ph_raw = frame["so_dien_thoai"].str.strip()
    r = {"DQ-01": (int((ph_raw != "").sum()), len(frame))}
    present = frame[ph_raw != ""]
    if stage == "TRUOC":
        ok = present["so_dien_thoai"].str.strip().str.fullmatch(r"0\d{9}")
    else:
        ok = present["phone_norm"].notna()
    r["DQ-02"] = (int(ok.sum()), len(present))
    nm_raw = frame["ho_ten"]
    r["DQ-03"] = (int((nm_raw.str.strip() != "").sum()), len(frame))
    nm = nm_raw[nm_raw.str.strip() != ""]
    nmv = nm.str.strip() if stage == "SAU" else nm
    ok_name = nmv.str.len().between(2, 120) & ~nmv.str.contains(r"\d")
    r["DQ-04"] = (int(ok_name.sum()), len(nm))
    v = frame[frame["phone_norm"].notna()]
    excess = 0 if resolved_dups else len(v) - v["phone_norm"].nunique()
    r["DQ-05"] = (len(v) - excess, len(v))
    em = frame["email"].str.strip()
    has_em = em != ""
    r["DQ-06"] = (int((has_em & em.str.fullmatch(EMAIL_RE)).sum()), int(has_em.sum()))
    rates = {k: {"dat": a, "mau_so": b, "ti_le_pct": round(a / b * 100, 2)} for k, (a, b) in r.items()}
    score = round(sum(WEIGHTS[k] * a / b for k, (a, b) in r.items()) * 100, 2)
    return rates, score


def label(score: float) -> str:
    return "Tốt" if score >= 90 else ("Chấp nhận được" if score >= 75 else "Kém")


# --------------------------------------------------------------------------- trích mẫu
def cluster_sample(df: pd.DataFrame, n_rows: int, seed: int) -> pd.DataFrame:
    """Trích theo cụm số điện thoại: chọn ngẫu nhiên các số (seed), lấy MỌI hồ sơ của số đó,
    rồi cộng thêm hồ sơ thiếu/sai số theo đúng tỉ lệ của dữ liệu gốc. Giữ nguyên các cặp trùng."""
    v = df[df["phone_norm"].notna()]
    size = v.groupby("phone_norm").size().to_dict()
    keys = sorted(size)
    random.Random(seed).shuffle(keys)
    target_valid = int(n_rows * (len(v) / len(df)))
    chosen, cnt = [], 0
    for k in keys:
        if cnt + size[k] > target_valid:
            continue
        chosen.append(k)
        cnt += size[k]
        if cnt >= target_valid - 2:
            break
    part_valid = v[v["phone_norm"].isin(set(chosen))]
    part_invalid = df[df["phone_norm"].isna()].sample(n=n_rows - len(part_valid), random_state=seed)
    return pd.concat([part_valid, part_invalid])


def dup_stats(frame: pd.DataFrame) -> dict:
    v = frame[frame["phone_norm"].notna()]
    g = v.groupby("phone_norm").size()
    gd = g[g > 1]
    return {
        "ho_so_co_so": len(v),
        "so_khac_nhau": int(g.size),
        "nhom_trung": int(gd.size),
        "phan_bo_co_nhom": {int(k): int(c) for k, c in gd.value_counts().sort_index().items()},
        "ho_so_thuoc_nhom_trung": int(gd.sum()),
        "ho_so_lap": int(len(v) - g.size),
        "ti_le_ho_so_lap_pct": round((len(v) - g.size) / len(v) * 100, 2) if len(v) else 0.0,
        "cap_neo_k_tru_1": int((gd - 1).sum()),
        "cap_C_k_2": int((gd * (gd - 1) // 2).sum()),
    }


# --------------------------------------------------------------------------- blocking
def block_pairs(s: pd.DataFrame, col: str) -> set:
    pairs = set()
    for _, g in s.groupby(col):
        ids = sorted(g.index.tolist())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pairs.add((ids[i], ids[j]))
    return pairs


def flag_pairs(pairs: set, ph: dict, nk: dict):
    """Đếm cặp được tạo theo QL7-02: cùng số (EXACT_PHONE) hoặc điểm QL7-03 ≥ ngưỡng (FUZZY)."""
    exact = fuzzy = 0
    for a, b in pairs:
        if ph[a] == ph[b]:
            exact += 1
            continue
        score = 0.6 * fuzz.ratio(ph[a], ph[b]) + 0.4 * fuzz.token_sort_ratio(nk[a], nk[b])
        if score >= FUZZY_THRESHOLD:
            fuzzy += 1
    return exact, fuzzy


# --------------------------------------------------------------------------- chương trình chính
def main(path: str):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["phone_norm"] = df["so_dien_thoai"].map(norm_phone)
    df["name_key"] = df["ho_ten"].map(name_key)
    N = len(df)
    R = {"tep": os.path.basename(path), "so_dong": N, "cot": df.columns[:6].tolist()}

    # 1. Tỉ lệ thiếu từng cột
    R["thieu_pct"] = {c: float(round(blank(df[c]).mean() * 100, 2)) for c in R["cot"]}
    R["thieu_so_dong"] = {c: int(blank(df[c]).sum()) for c in R["cot"]}

    # 2. Số điện thoại: dạng ghi và kết quả chuẩn hóa
    forms = df["so_dien_thoai"].map(phone_form)
    R["dang_so_dien_thoai"] = {k: {"so_dong": int(c), "pct": round(c / N * 100, 2)}
                               for k, c in forms.value_counts().items()}
    nonblank = ~blank(df["so_dien_thoai"])
    R["chuan_hoa"] = {
        "co_gia_tri": int(nonblank.sum()),
        "sai_dang_nhung_chuan_hoa_duoc": int((nonblank & (forms != "chuẩn 0xxxxxxxxx") & df["phone_norm"].notna()).sum()),
        "hop_le_sau_chuan_hoa": int(df["phone_norm"].notna().sum()),
        "khong_chuan_hoa_duoc": int((nonblank & df["phone_norm"].isna()).sum()),
    }

    # 3. Trùng theo số điện thoại chuẩn hóa
    R["trung_toan_bo"] = dup_stats(df)
    v = df[df["phone_norm"].notna()]
    gname = v.groupby("phone_norm")["name_key"].nunique()
    gdate = v.groupby("phone_norm")["ngay_tao"].nunique()
    R["nhom_cung_so_khac_ten_va_ngay"] = int(((gname > 1) & (gdate > 1)).sum())

    # 4. Họ tên
    name = df["ho_ten"]
    nk_phones = v.groupby("name_key")["phone_norm"].nunique()
    lens = name.str.strip().str.len()
    R["ho_ten"] = {
        "in_hoa": int(((name.str.strip() != "") & (name == name.str.upper())).sum()),
        "chu_thuong": int(((name.str.strip() != "") & (name == name.str.lower())).sum()),
        "thua_khoang_trang": int(((name != name.str.strip()) | name.str.contains("  ")).sum()),
        "co_chu_so": int(name.str.contains(r"\d").sum()),
        "do_dai_min_max": [int(lens.min()), int(lens.max())],
        "so_khoa_ten": int(nk_phones.size),
        "khoa_ten_dung_chung_boi_ge2_so": int((nk_phones > 1).sum()),
        "so_dien_thoai_toi_da_cho_1_ten": int(nk_phones.max()),
    }

    # 5. Email, ngày ghi nhận
    em = df["email"].str.strip()
    R["email"] = {"co_gia_tri": int((em != "").sum()),
                  "dung_mau": int(((em != "") & em.str.fullmatch(EMAIL_RE)).sum())}
    nt = df["ngay_tao"].str.strip()
    iso = nt.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    R["ngay_tao"] = {"dang_yyyy_mm_dd": int(iso.sum()), "min": nt[iso].min(), "max": nt[iso].max()}

    # 6. Chỉ số mức độ sạch (QL7-06) trên toàn bộ tệp
    R["chi_so_toan_bo"] = {
        "TRUOC": measure(df, "TRUOC"),
        "SAU_chua_quyet_dinh": measure(df, "SAU"),
        "SAU_xu_ly_het_cap_uoc_tinh": measure(df, "SAU", resolved_dups=True),
    }

    # 7. So sánh hai cách trích mẫu
    rnd = df.sample(n=RANDOM_SAMPLE_ROWS, random_state=SEED)
    R["mau_ngau_nhien_theo_dong"] = dup_stats(rnd)
    cs = cluster_sample(df, SAMPLE_ROWS, SEED)
    R["mau_theo_cum"] = dup_stats(cs)
    R["mau_theo_cum"]["thieu_so_pct"] = float(round(blank(cs["so_dien_thoai"]).mean() * 100, 2))
    R["chi_so_mau_theo_cum"] = {
        "TRUOC": measure(cs, "TRUOC"),
        "SAU_chua_quyet_dinh": measure(cs, "SAU"),
        "SAU_xu_ly_het_cap_uoc_tinh": measure(cs, "SAU", resolved_dups=True),
    }

    # 8. Blocking trên mẫu theo cụm (chỉ hồ sơ có số hợp lệ – QL7-04)
    s = cs[cs["phone_norm"].notna()].copy()
    s["b_dau"] = s["phone_norm"].str[:5]
    s["b_cuoi"] = s["phone_norm"].str[-5:]
    s["b_ten_goi"] = s["name_key"].str.split().str[-1]
    P1, P2, P3 = block_pairs(s, "b_dau"), block_pairs(s, "b_cuoi"), block_pairs(s, "b_ten_goi")
    ph, nk = s["phone_norm"].to_dict(), s["name_key"].to_dict()
    n = len(s)
    R["blocking"] = {
        "ho_so": n,
        "so_toan_bo": n * (n - 1) // 2,
        "cung_5_so_dau": len(P1),
        "cung_5_so_cuoi": len(P2),
        "dau_hoac_cuoi": len(P1 | P2),
        "ti_le_phai_so_pct": round(len(P1 | P2) / (n * (n - 1) // 2) * 100, 3),
        "cung_ten_goi": len(P3),
        "so_ten_goi": int(s["b_ten_goi"].nunique()),
        "ca_ba_khoa": len(P1 | P2 | P3),
        "cap_tao_ra_dau_hoac_cuoi_(exact,fuzzy)": flag_pairs(P1 | P2, ph, nk),
        "cap_tao_them_chi_nho_ten_goi_(exact,fuzzy)": flag_pairs(P3 - (P1 | P2), ph, nk),
    }

    # 9. Ghi kết quả
    os.makedirs("data/processed", exist_ok=True)
    cs.drop(columns=["phone_norm", "name_key"]).to_csv("data/processed/mau_cum_8000.csv", index=False)
    with open("data/processed/profiling_result.json", "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=1)

    # 10. Tóm tắt
    print(f"Tệp {R['tep']}: {N:,} dòng × {len(R['cot'])} cột {R['cot']}")
    print("Thiếu (%):", R["thieu_pct"])
    print("Dạng số điện thoại:", {k: x['pct'] for k, x in R['dang_so_dien_thoai'].items()})
    print("Chuẩn hóa:", R["chuan_hoa"])
    print("Trùng (toàn bộ):", R["trung_toan_bo"])
    print("Nhóm cùng số nhưng khác họ tên và ngày ghi nhận:", R["nhom_cung_so_khac_ten_va_ngay"])
    print("Họ tên:", R["ho_ten"])
    for k, (rates, score) in R["chi_so_toan_bo"].items():
        print(f"Chỉ số {k}: {score} ({label(score)}) –", {q: x["ti_le_pct"] for q, x in rates.items()})
    print("Mẫu ngẫu nhiên theo dòng:", R["mau_ngau_nhien_theo_dong"])
    print("Mẫu theo cụm:", R["mau_theo_cum"])
    for k, (rates, score) in R["chi_so_mau_theo_cum"].items():
        print(f"Chỉ số mẫu {k}: {score} ({label(score)})")
    print("Blocking:", R["blocking"])
    print("Đã ghi data/processed/mau_cum_8000.csv và data/processed/profiling_result.json")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/raw/customers_raw.csv")
