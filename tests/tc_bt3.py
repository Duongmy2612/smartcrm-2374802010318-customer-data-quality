"""12 test case hệ thống của Bài tập 3 – docs/test-plan.md (kế hoạch) và docs/test-report.md (kết quả).

Mỗi test case chạy HỆ THỐNG THẬT như người dùng: gọi lệnh `python -m src.pipeline` bằng tiến trình con trên
CSDL kiểm thử riêng (biến DB_NAME_TEST, mặc định smartcrm_test – không đụng CSDL smartcrm), rồi đếm bảng trước /
sau bằng SQL. Tiền điều kiện chung: xóa sạch schema ops, dwh của CSDL kiểm thử trước MỖI test case, nên kết quả
không phụ thuộc dữ liệu còn sót trên máy. Dữ liệu thử là dữ liệu GIẢ trong tests/du_lieu_tc/ và data/mau/.

Chạy một test case – in đủ tám cột của Test Report để chụp docs/screenshots/TC-xx.png:

    python -m tests.tc_bt3 TC-06                                       # máy có .venv
    docker compose run --rm pipeline python -m tests.tc_bt3 TC-06      # trong Docker (docs/deployment-guide.md)
    python -m tests.tc_bt3                                             # cả 12 test case

`python -m pytest -q` chạy cùng 12 test case này (tests/test_tc_bt3.py). Mã thoát của lệnh trên: 0 khi mọi test
case được chọn PASS, 1 khi có FAIL.
"""
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

GOC = Path(__file__).resolve().parent.parent
DU_LIEU = GOC / 'tests' / 'du_lieu_tc'
BANG_DICH = ['ops.load_batch', 'ops.stg_customer', 'ops.customer_clean', 'ops.dq_result', 'ops.dup_candidate',
             'dwh.dim_batch', 'dwh.fact_dq_check', 'dwh.fact_dup_pair']   # = load_ops.BANG_DICH

# Năm loại test của BT3 (đề mục 2.2) – trùng tên marker trong pytest.ini
LOAI = {'luong_dung': 'Luồng đúng', 'gia_tri_bien': 'Giá trị biên', 'du_lieu_sai': 'Dữ liệu sai',
        'chat_luong_bao_mat': 'Chất lượng dữ liệu / bảo mật', 'tai_lap': 'Tính tái lập'}


# ------------------------------------------------------------------ môi trường chạy
@dataclass
class KetQuaLenh:
    ma_thoat: int
    ra: str           # stdout
    loi: str          # stderr


class MoiTruong:
    """CSDL kiểm thử + cách gọi hệ thống. Không kết nối được → ném lỗi (pytest chuyển thành skip)."""

    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv(GOC / '.env')
        self.ten_csdl = os.getenv('DB_NAME_TEST') or 'smartcrm_test'
        self.env = {**os.environ, 'DB_NAME': self.ten_csdl, 'PYTHONIOENCODING': 'utf-8'}
        self.engine = self._engine()

    def _engine(self):
        from src import db
        cu = os.environ.get('DB_NAME')
        os.environ['DB_NAME'] = self.ten_csdl
        try:
            return db.tao_engine()
        finally:
            if cu is None:
                os.environ.pop('DB_NAME', None)
            else:
                os.environ['DB_NAME'] = cu

    def lam_sach(self) -> None:
        """Tiền điều kiện chung: CSDL kiểm thử không còn schema ops, dwh (như máy mới cài)."""
        with self.engine.begin() as conn:
            conn.exec_driver_sql('DROP SCHEMA IF EXISTS dwh CASCADE; DROP SCHEMA IF EXISTS ops CASCADE')

    def pipeline(self, *tham: str) -> KetQuaLenh:
        """Đúng lệnh người dùng gõ ở README bước 8, chạy trên CSDL kiểm thử."""
        p = subprocess.run([sys.executable, '-m', 'src.pipeline', *tham], cwd=GOC, env=self.env,
                           capture_output=True, text=True, encoding='utf-8', timeout=600)
        return KetQuaLenh(p.returncode, p.stdout, p.stderr)

    def sql(self, cau: str, **tham) -> list[tuple]:
        from sqlalchemy import text
        with self.engine.connect() as conn:
            return [tuple(r) for r in conn.execute(text(cau), tham)]

    def dem(self) -> dict[str, int]:
        """Số dòng 8 bảng đích; bảng chưa tồn tại (CSDL vừa làm sạch) tính là 0."""
        kq = {}
        for b in BANG_DICH:
            co = self.sql('SELECT to_regclass(:b) IS NOT NULL', b=b)[0][0]
            kq[b] = self.sql(f'SELECT count(*) FROM {b}')[0][0] if co else 0
        return kq


# ------------------------------------------------------------------ định nghĩa test case
@dataclass
class CaKiemThu:
    ma: str
    ten: str
    loai: str                  # khóa của LOAI
    truy_vet: str              # quy tắc nghiệp vụ / yêu cầu
    uu_tien: str               # Cao · Trung bình · Thấp
    tien_dieu_kien: str
    cac_buoc: list[str]
    du_lieu: str
    mong_doi: str
    chay: Callable[[MoiTruong], tuple[list[str], bool]] = field(repr=False)


def _tep(ten: str) -> str:
    return f'tests/du_lieu_tc/{ten}'


def _so(x) -> str:
    return f'{float(x):.2f}'.replace('.', ',')


def _doi(truoc: dict, sau: dict, bang: str) -> str:
    return f'{bang} {truoc[bang]} → {sau[bang]}'


def _trang_thai(mt: MoiTruong) -> dict[str, int]:
    return dict(mt.sql('SELECT status, count(*) FROM ops.stg_customer GROUP BY status'))


def _cap(mt: MoiTruong) -> list[tuple]:
    return mt.sql('SELECT a.row_no, b.row_no, d.match_type, d.score FROM ops.dup_candidate d '
                  'JOIN ops.stg_customer a ON a.stg_id = d.stg_id_a JOIN ops.stg_customer b ON b.stg_id = d.stg_id_b '
                  'ORDER BY 1, 2')


def _mo_ta_cap(cap: list[tuple]) -> str:
    return ', '.join(f'dòng {a} ↔ dòng {b} {t} {_so(s)}' for a, b, t, s in cap) or 'không có cặp nào'


def tc01(mt):
    truoc = mt.dem()
    r = mt.pipeline('--tep', _tep('tc01_chuan_hoa_so.csv'))
    sau = mt.dem()
    so = mt.sql('SELECT phone_raw, phone_norm, status FROM ops.stg_customer ORDER BY row_no') if r.ma_thoat == 0 else []
    thuc_te = [f'mã thoát {r.ma_thoat}; ' + _doi(truoc, sau, 'ops.customer_clean')]
    thuc_te += [f'"{a}" → {b} ({c})' for a, b, c in so]
    dat = (r.ma_thoat == 0 and sau['ops.customer_clean'] - truoc['ops.customer_clean'] == 4
           and [b for _, b, _ in so] == ['0912345678', '0987654321', '0903111222', '0933444555']
           and {c for *_, c in so} == {'CLEAN'})
    return thuc_te, dat


def tc02(mt):
    truoc = mt.dem()
    r = mt.pipeline('--tep', _tep('tc02_ho_so_lap.csv'))
    sau = mt.dem()
    tt, cap = (_trang_thai(mt), _cap(mt)) if r.ma_thoat == 0 else ({}, [])
    thuc_te = [f'mã thoát {r.ma_thoat}; ' + _doi(truoc, sau, 'ops.customer_clean') + ' (tệp 3 dòng)',
               'trạng thái: ' + ' · '.join(f'{k} {v}' for k, v in sorted(tt.items())),
               'cặp: ' + _mo_ta_cap(cap)]
    dat = (r.ma_thoat == 0 and sau['ops.customer_clean'] == 2 and tt == {'CLEAN': 2, 'PENDING_DUP': 1}
           and [(a, b, t) for a, b, t, _ in cap] == [(1, 2, 'EXACT_PHONE')])
    return thuc_te, dat


def tc03(mt):
    r = mt.pipeline('--tep', _tep('tc03_diem_tuong_dong.csv'))
    cap = _cap(mt) if r.ma_thoat == 0 else []
    thuc_te = [f'mã thoát {r.ma_thoat}; cặp: ' + _mo_ta_cap(cap)]
    dat = r.ma_thoat == 0 and [(a, b, t, float(s)) for a, b, t, s in cap] == [(1, 2, 'FUZZY', 94.0)]
    return thuc_te, dat


def tc04(mt):
    truoc = mt.dem()
    r = mt.pipeline('--tep', _tep('tc04_ho_so_loi.csv'))
    sau = mt.dem()
    rej = mt.sql('SELECT row_no, error_code, ly_do FROM ops.v_reject ORDER BY row_no') if r.ma_thoat == 0 else []
    thuc_te = [f'mã thoát {r.ma_thoat}; ' + _doi(truoc, sau, 'ops.customer_clean') + f'; ops.v_reject {len(rej)} dòng:']
    thuc_te += [f'dòng {n} {m}: "{l}"' for n, m, l in rej]
    dat = (r.ma_thoat == 0 and sau['ops.customer_clean'] == 1
           and [(n, m) for n, m, _ in rej] == [(1, 'MISSING_PHONE'), (2, 'INVALID_PHONE'), (3, 'MISSING_NAME')]
           and all(l for *_, l in rej))
    return thuc_te, dat


def tc05(mt):
    r = mt.pipeline('--tep', _tep('tc05_tep_nho_10_dong.csv'))
    if r.ma_thoat != 0:
        return [f'mã thoát {r.ma_thoat}: {r.loi.strip()[:200]}'], False
    tt = _trang_thai(mt)
    chi_so = dict(mt.sql('SELECT measure_stage, clean_index FROM dwh.v_batch_score WHERE is_latest'))
    cap = _cap(mt)
    thuc_te = ['mã thoát 0; trạng thái: ' + ' · '.join(f'{k} {v}' for k, v in sorted(tt.items())),
               f"ops.customer_clean {mt.dem()['ops.customer_clean']}; cặp: " + _mo_ta_cap(cap),
               f"chỉ số trong kho (dwh.v_batch_score): TRƯỚC {_so(chi_so.get('TRUOC', 0))} → SAU {_so(chi_so.get('SAU', 0))}"]
    dat = (tt == {'CLEAN': 7, 'PENDING_DUP': 1, 'ERROR': 2} and mt.dem()['ops.customer_clean'] == 7
           and [(a, b, t) for a, b, t, _ in cap] == [(1, 6, 'EXACT_PHONE')]
           and float(chi_so.get('TRUOC', 0)) == 85.00 and float(chi_so.get('SAU', 0)) == 90.56)
    return thuc_te, dat


def _bien(mt, tep, can_cap: bool):
    r = mt.pipeline('--tep', _tep(tep))
    cap = _cap(mt) if r.ma_thoat == 0 else []
    ung_vien = re.findall(r'(\d+) cặp ứng viên', r.ra)
    thuc_te = [f"mã thoát {r.ma_thoat}; blocking 5 số đầu/cuối: {ung_vien[0] if ung_vien else '?'} cặp ứng viên được so",
               f'ops.dup_candidate {len(cap)} cặp: ' + _mo_ta_cap(cap)]
    if can_cap:
        dat = r.ma_thoat == 0 and [(a, b, t, float(s)) for a, b, t, s in cap] == [(1, 2, 'FUZZY', 85.43)]
    else:
        dat = r.ma_thoat == 0 and cap == [] and ung_vien == ['1']
    return thuc_te, dat


def tc06(mt):
    return _bien(mt, 'tc06_bien_tren_85.csv', can_cap=True)


def tc07(mt):
    return _bien(mt, 'tc07_bien_duoi_85.csv', can_cap=False)


def tc08(mt):
    nap = mt.pipeline('--tep', 'data/mau/customers_mau.csv')          # dữ liệu có sẵn – tệp hỏng không được đụng tới
    if nap.ma_thoat != 0:
        return [f'bước 1 (nạp sẵn dữ liệu mẫu) lỗi, mã thoát {nap.ma_thoat}'], False
    truoc = mt.dem()
    r = mt.pipeline('--tep', 'data/mau/customers_thieu_cot.csv')
    sau = mt.dem()
    khac = [b for b in truoc if truoc[b] != sau[b]]
    thuc_te = [f'mã thoát {r.ma_thoat}; ' + _doi(truoc, sau, 'ops.load_batch') + '; ' + _doi(truoc, sau, 'ops.stg_customer')
               + '; ' + _doi(truoc, sau, 'ops.customer_clean'),
               '8 bảng đích: ' + ('không bảng nào đổi' if not khac else 'ĐỔI ' + ', '.join(khac)),
               f'thông báo: {r.loi.strip()}']
    dat = (r.ma_thoat == 2 and r.loi.startswith('TỪ CHỐI') and 'so_dien_thoai' in r.loi
           and 'Traceback' not in r.loi + r.ra and sau == truoc and truoc['ops.stg_customer'] == 414)
    return thuc_te, dat


def tc09(mt):
    truoc = mt.dem()
    r = mt.pipeline('--tep', _tep('tc09_ngay_sai.csv'))
    sau = mt.dem()
    if r.ma_thoat != 0:
        return [f'mã thoát {r.ma_thoat}: {r.loi.strip()[:200]}'], False
    rej = mt.sql('SELECT v.row_no, s.created_raw, v.error_code, v.ly_do FROM ops.v_reject v '
                 'JOIN ops.stg_customer s USING (batch_id, row_no) ORDER BY v.row_no')
    tt = mt.sql('SELECT row_no, created_raw, status FROM ops.stg_customer ORDER BY row_no')
    thuc_te = ['mã thoát 0; ' + _doi(truoc, sau, 'ops.customer_clean') + f'; ops.v_reject {len(rej)} dòng'
               + (':' if rej else '')]
    thuc_te += [f'dòng {n} "{c}" {m}: "{l}"' for n, c, m, l in rej]
    thuc_te += [] if rej else ['trạng thái: ' + ' · '.join(f'dòng {n} "{c}" {s}' for n, c, s in tt)]
    dat = (sau['ops.customer_clean'] == 1 and [(n, m) for n, _, m, _ in rej] == [(2, 'INVALID_DATE'), (3, 'INVALID_DATE')]
           and all(l for *_, l in rej))
    return thuc_te, dat


def tc10(mt):
    r = mt.pipeline('--tep', _tep('tc10_vi_pham_nguong.csv'))
    if r.ma_thoat != 0:
        return [f'mã thoát {r.ma_thoat}: {r.loi.strip()[:200]}'], False
    dong = {d.split()[0]: ' '.join(d.split()) for d in r.ra.splitlines()
            if d.strip().split(' ')[0] in ('so_dien_thoai', 'dia_chi', 'DQ-01')}
    kho = mt.sql("SELECT measure_stage, round(pass_rate * 100, 2), is_pass FROM dwh.v_rule_rate "
                 "WHERE rule_code = 'DQ-01' ORDER BY measure_stage DESC")
    thuc_te = ['mã thoát 0 (lỗi chất lượng được BÁO, không làm dừng luồng)']
    thuc_te += [f'màn hình: {dong[k]}' for k in ('so_dien_thoai', 'dia_chi', 'DQ-01') if k in dong]
    thuc_te += ['kho dwh.v_rule_rate DQ-01: ' + ' · '.join(f'{g} {_so(t)}% is_pass={p}' for g, t, p in kho)]
    dat = ('80,00%  <  98%  CHƯA ĐẠT' in r.ra and '70,00%  <  90%  CHƯA ĐẠT' in r.ra
           and 'chưa đạt' in dong.get('DQ-01', '') and len(kho) == 2 and not any(p for *_, p in kho))
    return thuc_te, dat


def tc11(mt):
    r1 = mt.pipeline('--tep', 'data/mau/customers_mau.csv')
    lan1 = mt.dem()
    r2 = mt.pipeline('--tep', 'data/mau/customers_mau.csv')
    lan2 = mt.dem()
    canh_bao = [d.strip() for d in r2.ra.splitlines() if 'CẢNH BÁO' in d]
    thuc_te = [f'lần 1: mã thoát {r1.ma_thoat}; lần 2: mã thoát {r2.ma_thoat}',
               (canh_bao[0][:110] + '…') if canh_bao else 'lần 2 không có cảnh báo AC1.4',
               '8 bảng đích sau lần 1 → sau lần 2: ' + ' · '.join(
                   f"{b.split('.')[1]} {lan1[b]}→{lan2[b]}" for b in BANG_DICH)]
    dat = (r1.ma_thoat == 0 and r2.ma_thoat == 0 and canh_bao and lan1 == lan2
           and lan1['ops.stg_customer'] == 414 and lan1['ops.dup_candidate'] == 43)
    return thuc_te, dat


def tc12(mt):
    from sqlalchemy import text
    r = mt.pipeline('--tep', _tep('tc01_chuan_hoa_so.csv'))
    if r.ma_thoat != 0:
        return [f'mã thoát {r.ma_thoat}: {r.loi.strip()[:200]}'], False
    from src import db
    cu = os.environ.get('DB_NAME')
    os.environ['DB_NAME'] = mt.ten_csdl
    try:
        try:
            e = db.tao_engine_chi_doc()
        except Exception as loi:                       # noqa: BLE001
            return [f'không mở được kết nối của dashboard: {type(loi).__name__}: {loi}'], False
        tai_khoan = e.url.username or '(tài khoản hệ điều hành)'
        ket_qua = {}
        for nhan, cau in (('kho dwh.v_batch_score', 'SELECT count(*) FROM dwh.v_batch_score'),
                          ('ops.stg_customer (họ tên, số điện thoại)',
                           'SELECT full_name_raw, phone_raw FROM ops.stg_customer LIMIT 1')):
            try:
                with e.connect() as conn:
                    dong = conn.execute(text(cau)).fetchall()
                ket_qua[nhan] = (True, f'ĐỌC ĐƯỢC {len(dong)} dòng')
            except Exception as loi:                   # noqa: BLE001
                ket_qua[nhan] = (False, 'bị từ chối: ' + str(getattr(loi, 'orig', loi)).splitlines()[0])
        e.dispose()
    finally:
        if cu is None:
            os.environ.pop('DB_NAME', None)
        else:
            os.environ['DB_NAME'] = cu
    thuc_te = [f'kết nối của dashboard dùng tài khoản: {tai_khoan}']
    thuc_te += [f'{k}: {v}' for k, (_, v) in ket_qua.items()]
    dat = ket_qua['kho dwh.v_batch_score'][0] and not ket_qua['ops.stg_customer (họ tên, số điện thoại)'][0]
    return thuc_te, dat


DK_CHUNG = 'CSDL kiểm thử sạch (xóa schema ops, dwh)'
TCS = [
    CaKiemThu('TC-01', 'Chuẩn hóa số điện thoại về 0xxxxxxxxx', 'luong_dung', 'QT-02 (FR-02)', 'Cao', DK_CHUNG,
             ['python -m src.pipeline --tep tests/du_lieu_tc/tc01_chuan_hoa_so.csv',
              'SELECT phone_raw, phone_norm, status FROM ops.stg_customer'],
             '4 hồ sơ, 4 cách viết số: "+84 912 345 678" · "0987.654.321" · "84903111222" · "0933-444-555"',
             'mã thoát 0; phone_norm 0912345678 · 0987654321 · 0903111222 · 0933444555; 4 CLEAN; '
             'customer_clean 0 → 4', tc01),
    CaKiemThu('TC-02', 'Hồ sơ lặp số điện thoại không tạo khách hàng mới', 'luong_dung', 'QT-01, QL7-02', 'Cao',
             DK_CHUNG, ['python -m src.pipeline --tep tests/du_lieu_tc/tc02_ho_so_lap.csv',
                        'đếm customer_clean, trạng thái stg_customer, cặp dup_candidate'],
             '3 hồ sơ; dòng 1 "0912345678" và dòng 2 "0912 345 678" là cùng một số',
             'customer_clean 0 → 2 (không phải 3); CLEAN 2 · PENDING_DUP 1; 1 cặp EXACT_PHONE dòng 1 ↔ dòng 2', tc02),
    CaKiemThu('TC-03', 'Điểm tương đồng của cặp FUZZY', 'luong_dung', 'QL7-03', 'Trung bình', DK_CHUNG,
             ['python -m src.pipeline --tep tests/du_lieu_tc/tc03_diem_tuong_dong.csv',
              'SELECT match_type, score FROM ops.dup_candidate'],
             '"Nguyễn Thanh Tâm" 0912345678 và "Nguyễn Thanh Tâm" 0912345670 (khác 1 chữ số)',
             '1 cặp FUZZY, điểm = 0,6 × 90 + 0,4 × 100 = 94,00', tc03),
    CaKiemThu('TC-04', 'Hồ sơ lỗi ở lại bảng tạm, có lý do cho người đọc', 'luong_dung', 'QL7-04, FR-10', 'Cao',
             DK_CHUNG, ['python -m src.pipeline --tep tests/du_lieu_tc/tc04_ho_so_loi.csv',
                        'SELECT row_no, error_code, ly_do FROM ops.v_reject'],
             '4 hồ sơ: thiếu số · số "12345" · thiếu họ tên · 1 hồ sơ đúng',
             'mã thoát 0; v_reject 3 dòng: 1 MISSING_PHONE, 2 INVALID_PHONE, 3 MISSING_NAME, mỗi dòng một câu lý do; '
             'customer_clean 0 → 1', tc04),
    CaKiemThu('TC-05', 'Tệp nhỏ 10 dòng: số dòng và chỉ số mức độ sạch khớp tính tay', 'luong_dung',
             'QL7-06, QL7-04, QT-01', 'Cao', DK_CHUNG,
             ['python -m src.pipeline --tep tests/du_lieu_tc/tc05_tep_nho_10_dong.csv',
              'SELECT measure_stage, clean_index FROM dwh.v_batch_score'],
             '10 hồ sơ: 1 thiếu số, 2 số viết sai dạng (chuẩn hóa được), 1 số "12345", 1 hồ sơ lặp số, '
             '3 email (1 sai)',
             'CLEAN 7 · PENDING_DUP 1 · ERROR 2; customer_clean 7; 1 cặp EXACT_PHONE dòng 1 ↔ 6; '
             'chỉ số TRƯỚC 85,00 → SAU 90,56 (tính tay ở docs/test-plan.md)', tc05),
    CaKiemThu('TC-06', 'Biên ngưỡng 85 – phía trên: điểm 85,43 tạo cặp', 'gia_tri_bien', 'QL7-02, QL7-03', 'Cao',
             DK_CHUNG, ['python -m src.pipeline --tep tests/du_lieu_tc/tc06_bien_tren_85.csv',
                        'SELECT match_type, score FROM ops.dup_candidate'],
             '"Nguyễn Thanh Tâm" 0912345678 · "Lê Thanh Tâm" 0912345670',
             '1 cặp FUZZY điểm 85,43 (≥ 85)', tc06),
    CaKiemThu('TC-07', 'Biên ngưỡng 85 – phía dưới: điểm 84,97 không tạo cặp', 'gia_tri_bien', 'QL7-02, QL7-03',
             'Cao', DK_CHUNG, ['python -m src.pipeline --tep tests/du_lieu_tc/tc07_bien_duoi_85.csv',
                               'SELECT count(*) FROM ops.dup_candidate'],
             '"Nguyễn Thanh Tâm" 0912345678 · "Nguyễn Văn Tuấn" 0912345670',
             '1 cặp ứng viên được so (cùng 5 số đầu) nhưng 0 cặp được tạo vì 84,97 < 85', tc07),
    CaKiemThu('TC-08', 'Tệp thiếu cột bắt buộc bị từ chối cả tệp', 'du_lieu_sai', 'AC1.3, FR-01', 'Cao',
             DK_CHUNG + ', rồi nạp sẵn dữ liệu mẫu 414 dòng (bước 1)',
             ['python -m src.pipeline --tep data/mau/customers_mau.csv',
              'python -m src.pipeline --tep data/mau/customers_thieu_cot.csv',
              'đếm 8 bảng đích trước / sau bước 2'],
             'data/mau/customers_thieu_cot.csv – không có cột so_dien_thoai',
             'mã thoát 2; "TỪ CHỐI: …" nêu tên cột thiếu, không có Traceback; 8 bảng đích không đổi '
             '(load_batch 1 → 1, stg_customer 414 → 414)', tc08),
    CaKiemThu('TC-09', 'Ngày tạo sai định dạng vào bảng reject kèm lý do', 'du_lieu_sai',
             'data-requirements mục 3 (ngay_tao: ngày hợp lệ yyyy-mm-dd), QL7-04', 'Trung bình', DK_CHUNG,
             ['python -m src.pipeline --tep tests/du_lieu_tc/tc09_ngay_sai.csv',
              'SELECT row_no, created_raw, error_code, ly_do FROM ops.v_reject'],
             '3 hồ sơ: ngày "2026-01-05" (đúng) · "31/02/2026" · "2026-02-30"',
             'mã thoát 0 (luồng không dừng); v_reject 2 dòng INVALID_DATE (dòng 2, 3) có lý do; customer_clean 0 → 1',
             tc09),
    CaKiemThu('TC-10', 'Cố ý vi phạm ngưỡng chất lượng – hệ thống phát hiện và báo', 'chat_luong_bao_mat',
             'D3, QL7-06 (ngưỡng DQ-01), nguong_day_du', 'Cao', DK_CHUNG,
             ['python -m src.pipeline --tep tests/du_lieu_tc/tc10_vi_pham_nguong.csv',
              "SELECT measure_stage, pass_rate, is_pass FROM dwh.v_rule_rate WHERE rule_code = 'DQ-01'"],
             '10 hồ sơ: 2 thiếu số điện thoại (80%), 3 thiếu địa chỉ (70%)',
             'mã thoát 0; màn hình: so_dien_thoai 80,00% < 98% CHƯA ĐẠT, dia_chi 70,00% < 90% CHƯA ĐẠT, DQ-01 chưa đạt; '
             'kho: DQ-01 is_pass = false ở cả TRƯỚC và SAU', tc10),
    CaKiemThu('TC-11', 'Chạy lại cùng tệp lần hai không lỗi, không nhân đôi', 'tai_lap', 'AC1.4, NFR-05 (TD-25)',
             'Cao', DK_CHUNG, ['python -m src.pipeline --tep data/mau/customers_mau.csv',
                               'chạy lại đúng lệnh ở bước 1', 'đếm 8 bảng đích sau mỗi lần'],
             'data/mau/customers_mau.csv (414 dòng, dữ liệu mẫu giả)',
             'cả hai lần mã thoát 0; lần 2 có "CẢNH BÁO (AC1.4)"; 8 bảng đích giống hệt lần 1 '
             '(stg_customer 414, dup_candidate 43)', tc11),
    CaKiemThu('TC-12', 'Tài khoản dashboard không đọc được dữ liệu cá nhân', 'chat_luong_bao_mat',
             'NFR-07, TD-19, checklist bảo mật mục 3', 'Cao',
             DK_CHUNG + '; đã chạy luồng chính trên tc01_chuan_hoa_so.csv; .env theo .env.example',
             ['mở kết nối đúng như dashboard: db.tao_engine_chi_doc()',
              'SELECT count(*) FROM dwh.v_batch_score', 'SELECT full_name_raw, phone_raw FROM ops.stg_customer'],
             'kho sau khi nạp 4 hồ sơ của TC-01',
             'đọc được kho dwh; bị PostgreSQL từ chối khi đọc ops.stg_customer (permission denied)', tc12),
]
THEO_MA = {t.ma: t for t in TCS}


def chay_mot(tc: CaKiemThu, mt: MoiTruong) -> tuple[list[str], bool]:
    mt.lam_sach()
    try:
        return tc.chay(mt)
    except Exception as e:                             # noqa: BLE001 – lỗi của chính test case cũng là FAIL
        return [f'test case dừng giữa chừng: {type(e).__name__}: {str(e).splitlines()[0]}'], False


# ------------------------------------------------------------------ in đủ tám cột để chụp màn hình
def _in(nhan: str, gia_tri, rong: int = 100) -> None:
    dong = gia_tri if isinstance(gia_tri, list) else [gia_tri]
    dau = f'{nhan:<15}: '
    for i, d in enumerate(dong):
        for j, phan in enumerate(textwrap.wrap(str(d), rong) or ['']):
            print((dau if i == 0 and j == 0 else ' ' * len(dau)) + phan)


def main(argv=None) -> int:
    ma = [a.upper() for a in (sys.argv[1:] if argv is None else argv)] or list(THEO_MA)
    sai = [m for m in ma if m not in THEO_MA]
    if sai:
        print(f"Không có test case {', '.join(sai)}. Có: {', '.join(THEO_MA)}", file=sys.stderr)
        return 2
    mt = MoiTruong()
    ket_qua = []
    for m in ma:
        tc = THEO_MA[m]
        print('═' * 112)
        print(f'{tc.ma} · {tc.ten}')
        _in('Loại · truy vết', f'{LOAI[tc.loai]} · {tc.truy_vet}')
        _in('Ưu tiên', tc.uu_tien)
        _in('Tiền điều kiện', tc.tien_dieu_kien + f' – CSDL {mt.ten_csdl}')
        _in('Các bước', [f'{i}. {b}' for i, b in enumerate(tc.cac_buoc, 1)])
        _in('Dữ liệu thử', tc.du_lieu)
        _in('Mong đợi', tc.mong_doi)
        thuc_te, dat = chay_mot(tc, mt)
        _in('Thực tế', thuc_te)
        print(f"{'Kết quả':<15}: {'PASS' if dat else 'FAIL'}")
        ket_qua.append((tc.ma, dat))
    if len(ma) > 1:
        print('═' * 112)
        print('Tổng: ' + ' · '.join(f"{m} {'PASS' if d else 'FAIL'}" for m, d in ket_qua)
              + f' → {sum(d for _, d in ket_qua)}/{len(ket_qua)} PASS')
    mt.engine.dispose()
    return 0 if all(d for _, d in ket_qua) else 1


if __name__ == '__main__':
    sys.exit(main())
