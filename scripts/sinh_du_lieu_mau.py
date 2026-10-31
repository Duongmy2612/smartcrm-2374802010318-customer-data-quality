"""Sinh dữ liệu MẪU cho repo (BT2 – TP4: "có dữ liệu mẫu để hệ thống không lên trống trơn").

    python scripts/sinh_du_lieu_mau.py          # ghi data/mau/customers_mau.csv, ba tệp lỗi và nhan_dung_mau.csv

Dữ liệu GIẢ hoàn toàn (họ tên ghép ngẫu nhiên từ danh sách họ/đệm/tên, số điện thoại sinh ngẫu nhiên), không
lấy dòng nào từ customers_raw.csv của LMS, nên được commit. Cùng cấu trúc 6 cột và cùng các "bệnh" đã đo ở
mục 4 BT1, để mọi nhánh của luồng chính đều có dữ liệu đi qua:

    5 dạng ghi số điện thoại (0…, 84…, +84…, có dấu cách, có dấu chấm)   → transform chuẩn hóa (QT-02)
    hồ sơ lặp cùng số, họ tên viết khác (hoa, thường, mất dấu, thừa cách) → PENDING_DUP, cặp EXACT_PHONE
    hai số chỉ khác 1 chữ số, cùng họ tên                                  → cặp FUZZY (điểm ≥ 85)
    thiếu số / số không quy đổi được / thiếu họ tên                        → ERROR, bảng reject ops.v_reject
    email sai mẫu                                                           → DQ-06

Chỉ dùng thư viện chuẩn với random.Random(42) (NFR-05): chạy lại cho đúng từng byte như tệp đã commit.

Vì script tự sinh ra từng hồ sơ nên biết chắc hồ sơ nào là của cùng một khách: data/mau/nhan_dung_mau.csv ghi
record_id → ma_khach. Đây là NHÃN ĐÚNG để kiểm chứng NFR-03 trên dữ liệu mẫu (src/kiem_chung_nfr03.py, TD-32).
Gán ma_khach không gọi thêm số ngẫu nhiên nào, nên customers_mau.csv giữ đúng từng byte như trước.
"""
import csv
import datetime as dt
import pathlib
import random
import unicodedata

GOC =pathlib.Path(__file__).resolve().parent.parent
THU_MUC = GOC / 'data' / 'mau'
SEED = 42

HO = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Huỳnh', 'Hoàng', 'Võ', 'Phan', 'Trương', 'Bùi', 'Đặng', 'Đỗ', 'Ngô',
      'Dương', 'Lý']
DEM = ['Văn', 'Thị', 'Minh', 'Ngọc', 'Hoàng', 'Thanh', 'Quốc', 'Gia', 'Bảo', 'Thu', 'Diễm', 'Anh', 'Hữu', 'Kim']
TEN = ['An', 'Bình', 'Châu', 'Dũng', 'Giang', 'Hà', 'Hải', 'Hạnh', 'Hiếu', 'Hùng', 'Khoa', 'Lan', 'Linh', 'Long',
       'Mai', 'My', 'Nam', 'Ngân', 'Nhi', 'Phát', 'Phúc', 'Quân', 'Sơn', 'Tâm', 'Thảo', 'Trang', 'Trí', 'Tuấn',
       'Vy', 'Yến']
DAU_SO = ['090', '091', '093', '094', '096', '097', '098', '070', '076', '077', '078', '079', '081', '083', '086']
QUAN = ['Q.1', 'Q.3', 'Q.5', 'Q.7', 'Q.10', 'Bình Thạnh', 'Gò Vấp', 'Thủ Đức', 'Tân Bình', 'Ninh Kiều',
        'Cái Răng', 'TP. Long Xuyên', 'TP. Mỹ Tho']
DUONG = ['Lê Lợi', 'Nguyễn Huệ', 'Hai Bà Trưng', 'Trần Hưng Đạo', '3 Tháng 2', 'Cách Mạng Tháng 8',
         'Nguyễn Văn Cừ', 'Mậu Thân', 'Võ Văn Kiệt']
MIEN = ['gmail.com', 'yahoo.com', 'outlook.com', 'mekongmobile.vn']

SO_KHACH = 340          # khách khác nhau (mỗi khách một số)
SO_LAP = 40             # hồ sơ lặp cùng số với một khách có sẵn
SO_FUZZY = 3            # cặp hai số chỉ khác 1 chữ số, cùng họ tên
SO_THIEU_SO = 24        # ô số điện thoại trống          → MISSING_PHONE
SO_SAI_SO = ['090123456', '0901 234 56789', '1900 6789', 'không có', '+1 202 555 0147']   # → INVALID_PHONE
SO_THIEU_TEN = 2        # họ tên trống, số hợp lệ         → MISSING_NAME


def bo_dau(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd').replace('Đ', 'D')


def dang_ghi(so: str, r: random.Random) -> str:
    """Một trong năm dạng ghi đo được ở BT1 mục 4.1 (tỉ lệ gần giống dữ liệu thật: ~70% đúng dạng sẵn)."""
    x = r.random()
    if x < 0.70:
        return so
    if x < 0.76:
        return '84' + so[1:]
    if x < 0.82:
        return '+84' + so[1:]
    if x < 0.91:
        return f'{so[:4]} {so[4:7]} {so[7:]}'
    return f'{so[:4]}.{so[4:7]}.{so[7:]}'


def viet_khac(ten: str, r: random.Random) -> str:
    """Cùng một người nhưng họ tên viết khác: hoa, thường, mất dấu, thừa khoảng trắng (FR-03, name_key)."""
    return r.choice([ten.upper(), ten.lower(), bo_dau(ten), '  ' + ten.replace(' ', '  ') + ' ', ten])


def sinh() -> tuple[list[dict], dict]:
    r = random.Random(SEED)
    so_da_dung, khach = set(), []
    while len(khach) < SO_KHACH:
        so = r.choice(DAU_SO) + f'{r.randrange(10**7):07d}'
        if so in so_da_dung:
            continue
        so_da_dung.add(so)
        khach.append({'ten': f'{r.choice(HO)} {r.choice(DEM)} {r.choice(TEN)}', 'so': so,
                      'ma': f'K{len(khach) + 1:03d}'})
    ma_moi = iter(range(SO_KHACH + 1, 10**6))                 # người khác hẳn (thiếu số, số sai, thiếu tên)

    def email(ten: str) -> str:
        if r.random() < 0.45:                                 # ~45% không có email (BT1: 44,99%)
            return ''
        cuc_bo = '.'.join(bo_dau(ten).lower().split()[-2:]) + str(r.randrange(100))
        e = f'{cuc_bo}@{r.choice(MIEN)}'
        return e.replace('@', '.') if r.random() < 0.06 else e     # vài email sai mẫu (DQ-06)

    def dia_chi() -> str:
        return '' if r.random() < 0.09 else f'{r.randrange(1, 400)} {r.choice(DUONG)}, {r.choice(QUAN)}'

    def ngay() -> str:
        d = dt.date(2024, 1, 1) + dt.timedelta(days=r.randrange((dt.date(2026, 8, 28) - dt.date(2024, 1, 1)).days))
        return d.isoformat()

    dong = [{'ho_ten': k['ten'], 'so_dien_thoai': dang_ghi(k['so'], r), 'email': email(k['ten']),
             'dia_chi': dia_chi(), 'ngay_tao': ngay(), 'ma_khach': k['ma']} for k in khach]
    for k in r.sample(khach, SO_LAP):                         # hồ sơ lặp cùng số
        dong.append({'ho_ten': viet_khac(k['ten'], r), 'so_dien_thoai': dang_ghi(k['so'], r), 'email': '',
                     'dia_chi': dia_chi(), 'ngay_tao': ngay(), 'ma_khach': k['ma']})
    for k in r.sample(khach, SO_FUZZY):                       # cùng 5 số đầu, khác chữ số cuối → FUZZY
        so = k['so'][:-1] + str((int(k['so'][-1]) + 1) % 10)
        while so in so_da_dung:
            so = so[:-1] + str((int(so[-1]) + 1) % 10)
        so_da_dung.add(so)
        dong.append({'ho_ten': viet_khac(k['ten'], r), 'so_dien_thoai': dang_ghi(so, r), 'email': email(k['ten']),
                     'dia_chi': dia_chi(), 'ngay_tao': ngay(), 'ma_khach': k['ma']})   # cùng khách, số gõ nhầm
    for _ in range(SO_THIEU_SO):
        dong.append({'ho_ten': f'{r.choice(HO)} {r.choice(DEM)} {r.choice(TEN)}', 'so_dien_thoai': '',
                     'email': '', 'dia_chi': dia_chi(), 'ngay_tao': ngay(), 'ma_khach': f'K{next(ma_moi):03d}'})
    for sai in SO_SAI_SO:
        dong.append({'ho_ten': f'{r.choice(HO)} {r.choice(DEM)} {r.choice(TEN)}', 'so_dien_thoai': sai,
                     'email': '', 'dia_chi': dia_chi(), 'ngay_tao': ngay(), 'ma_khach': f'K{next(ma_moi):03d}'})
    for _ in range(SO_THIEU_TEN):
        so = r.choice(DAU_SO) + f'{r.randrange(10**7):07d}'
        while so in so_da_dung:
            so = r.choice(DAU_SO) + f'{r.randrange(10**7):07d}'
        so_da_dung.add(so)
        dong.append({'ho_ten': '', 'so_dien_thoai': so, 'email': '', 'dia_chi': dia_chi(), 'ngay_tao': ngay(),
                     'ma_khach': f'K{next(ma_moi):03d}'})

    r.shuffle(dong)
    for i, d in enumerate(dong, start=1):
        d['record_id'] = str(i)
    return dong, {'khach': SO_KHACH, 'lap': SO_LAP, 'fuzzy': SO_FUZZY, 'thieu_so': SO_THIEU_SO,
                  'sai_so': len(SO_SAI_SO), 'thieu_ten': SO_THIEU_TEN}


COT = ['record_id', 'ho_ten', 'so_dien_thoai', 'email', 'dia_chi', 'ngay_tao']


def ghi(dong: list[dict], duong_dan: pathlib.Path, cot=COT) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    with open(duong_dan, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cot, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        w.writerows(dong)


DAU_THANH = '̣̀́̃̉'          # huyền, sắc, ngã, hỏi, nặng (dạng dấu rời)


def ma_hoa_windows_1258(chuoi: str) -> bytes:
    """Mã hóa như Excel trên Windows lưu "CSV" tiếng Việt (bảng mã Windows-1258): chữ có dấu thanh được tách thành
    chữ gốc + dấu thanh rời (ễ → ê + dấu ngã). Dùng để sinh tệp SAI bảng mã (C7, TD-28)."""
    ra = bytearray()
    for ch in chuoi:
        try:
            ra += ch.encode('cp1258')
        except UnicodeEncodeError:
            tach = unicodedata.normalize('NFD', ch)              # ặ → a + dấu nặng + dấu trăng
            thanh = ''.join(c for c in tach if c in DAU_THANH)    # dấu thanh: viết rời
            goc = unicodedata.normalize('NFC', ''.join(c for c in tach if c not in DAU_THANH))   # ă
            ra += goc.encode('cp1258') + thanh.encode('cp1258')
    return bytes(ra)


def ghi_sai_bang_ma(dong: list[dict], duong_dan: pathlib.Path, cot=COT) -> None:
    dong_csv = [','.join(cot)] + [','.join(f'"{d[c]}"' if ',' in d[c] else d[c] for c in cot) for d in dong]
    duong_dan.write_bytes(ma_hoa_windows_1258('\n'.join(dong_csv) + '\n'))


def main() -> None:
    dong, tk = sinh()
    ghi(dong, THU_MUC / 'customers_mau.csv')
    # Ba tệp SAI để thử luồng ngoại lệ (C7) – mỗi tệp bị TỪ CHỐI cả đợt, mã thoát 2, không tạo đợt nạp:
    #   thiếu cột so_dien_thoai (AC1.3) · chỉ có dòng tiêu đề · lưu bằng bảng mã Windows-1258 thay vì UTF-8 (TD-28)
    ghi(dong[:5], THU_MUC / 'customers_thieu_cot.csv', ['record_id', 'ho_ten', 'email', 'dia_chi', 'ngay_tao'])
    ghi([], THU_MUC / 'customers_chi_tieu_de.csv')
    ghi_sai_bang_ma(dong[:5], THU_MUC / 'customers_sai_bang_ma.csv')
    # Nhãn đúng cho NFR-03 (TD-32): hai hồ sơ cùng ma_khach là cùng một khách hàng
    ghi(dong, THU_MUC / 'nhan_dung_mau.csv', ['record_id', 'ma_khach'])
    print(f"data/mau/customers_mau.csv: {len(dong)} dòng – {tk['khach']} khách, {tk['lap']} hồ sơ lặp cùng số, "
          f"{tk['fuzzy']} cặp số gần giống, {tk['thieu_so']} thiếu số, {tk['sai_so']} số sai, {tk['thieu_ten']} thiếu tên")
    print('data/mau/customers_thieu_cot.csv: 5 dòng, thiếu cột so_dien_thoai (thử AC1.3)')
    print('data/mau/customers_chi_tieu_de.csv: chỉ có dòng tiêu đề, 0 dòng dữ liệu (thử C7)')
    print('data/mau/customers_sai_bang_ma.csv: 5 dòng lưu bằng bảng mã Windows-1258 (thử C7)')
    print(f"data/mau/nhan_dung_mau.csv: {len(dong)} dòng record_id → ma_khach (nhãn đúng để kiểm chứng NFR-03)")


if __name__ == '__main__':
    main()
