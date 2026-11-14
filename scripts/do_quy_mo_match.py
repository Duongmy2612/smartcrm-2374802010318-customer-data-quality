"""Đo bước phát hiện cặp nghi trùng (UC3, src/etl/match.tim_cap) khi dữ liệu tăng k lần – trả lời câu hỏi
"dữ liệu tăng gấp mười thì chỗ nào hỏng trước?" (buổi 16). Kết quả: docs/pipeline-doc.md mục 6, dòng "Scale".

    python scripts/do_quy_mo_match.py 3                      # k = 3, môi trường phát triển (.venv)
    docker run --rm -m 2g --memory-swap 2g -v "$(pwd)/data/raw:/app/data/raw:ro" \\
        smartcrm-l7:local python scripts/do_quy_mo_match.py 10   # k = 10 trong container giới hạn 2 GB

Cần tệp thật data/raw/customers_raw.csv (LMS, không có trong repo). Không ghi CSDL, không in dữ liệu cá nhân.
k = 1 là các hồ sơ có số hợp lệ của tệp thật (qua đúng extract → transform của pipeline). k > 1 thêm k − 1 bản mô phỏng:
mỗi bản có cùng số hồ sơ, 5 số đầu lấy ngẫu nhiên từ tệp thật (giữ phân bố đầu số – khóa blocking), 5 số cuối và họ
tên ngẫu nhiên (seed 42, NFR-05). In: số hồ sơ, số khác nhau, số cặp ứng viên sau blocking, số cặp, giây, RAM đỉnh.
"""
import pathlib
import random
import resource
import sys
import time

GOC = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import pandas as pd                                     # noqa: E402

from src.etl import extract, match, transform          # noqa: E402

k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
bang = transform.chuan_hoa(extract.sang_bang_tam(extract.doc_tep(GOC / 'data' / 'raw' / 'customers_raw.csv')))
hs = bang[bang['error_code'].isna() & bang['phone_norm'].notna()]
hs = pd.DataFrame({'stg_id': hs['row_no'], 'phone_norm': hs['phone_norm'],
                   'name_key': hs['name_norm'].map(match.tao_name_key)})
ngau_nhien = random.Random(42)
n, dau_so, ho_ten = len(hs), hs['phone_norm'].str[:5].tolist(), hs['name_key'].tolist()
phan = [hs]
for c in range(1, k):
    phan.append(pd.DataFrame({
        'stg_id': range(c * 10**7, c * 10**7 + n),
        'phone_norm': [ngau_nhien.choice(dau_so) + f'{ngau_nhien.randrange(10**5):05d}' for _ in range(n)],
        'name_key': [ngau_nhien.choice(ho_ten) for _ in range(n)]}))
hs = pd.concat(phan, ignore_index=True)
print(f'k = {k}: {len(hs):,} hồ sơ có số hợp lệ – bắt đầu so khớp', flush=True)

thong_ke = {}
bat_dau = time.perf_counter()
cap = match.tim_cap(hs, thong_ke=thong_ke)
giay = time.perf_counter() - bat_dau
ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024 if sys.platform == 'darwin' else 1024)  # → MB
print(f"k = {k}: {thong_ke['so_khac_nhau']:,} số khác nhau · {thong_ke['cap_ung_vien']:,} cặp ứng viên · "
      f"{len(cap):,} cặp · {giay:.1f} giây · RAM đỉnh {ram:,.0f} MB")
