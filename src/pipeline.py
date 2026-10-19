"""Điều phối lớp ② theo thứ tự gọi ở Bảng 3.1 của BT1 – UC1 Nạp tệp khách hàng thô:

    extract → transform → dq_evaluate → load_dwh

Chạy bằng MỘT lệnh từ thư mục gốc repo (đã kích hoạt .venv):

    python -m src.pipeline --tep data/raw/customers_raw.csv
    python -m src.pipeline --tep data/raw/customers_raw.csv --khong-ghi-csdl   # chưa có PostgreSQL

Quyết định thiết kế:
  1. Cả UC1 nằm trong MỘT giao dịch (`with engine.begin()`): lỗi ở bất kỳ bước nào → ROLLBACK, không bao giờ
     còn lại một đợt nạp dở dang (TD-09).
  2. Tệp bị từ chối (thiếu cột, đã nạp mà chưa xác nhận, người nạp sai vai trò, giá trị dài hơn cột của
     customer_clean) được kiểm TRƯỚC khi ghi gì vào CSDL, nên load_batch và stg_customer không thay đổi (AC1.3, AC1.4).
  3. Mã thoát: 0 thành công · 1 lỗi kỹ thuật (không đọc được tệp, mất kết nối) · 2 dữ liệu bị từ chối.
"""
import argparse
import pathlib
import sys
import time
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from src import config
from src.etl import extract, transform

MA_THANH_CONG, MA_LOI_KY_THUAT, MA_TU_CHOI = 0, 1, 2


def so(n: int) -> str:
    """67037 → '67.037' (cách viết số trong hồ sơ BT1)."""
    return f'{n:,}'.replace(',', '.')


def pt(x: float) -> str:
    """0.0617 → '6,17%'. Làm tròn nửa lên như cách viết tay (494/8.000 = 6,175% → 6,18%, khớp BT1)."""
    q = Decimal(str(round(x * 100, 9))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f'{q}%'.replace('.', ',')


def giay(x: float) -> str:
    return f'{x:.1f} s'.replace('.', ',')


class TuChoi(Exception):
    """Dữ liệu hoặc thao tác bị từ chối theo quy tắc nghiệp vụ (mã thoát 2)."""


def kiem_nguoi_nap(cau_hinh: dict, ten: str) -> dict:
    """Bảng 1.2 của BT1: chỉ Nhân viên Marketing được nạp tệp (UC1)."""
    nd = config.tim_nguoi_dung(cau_hinh, ten)
    if nd is None:
        raise TuChoi(f'Người dùng "{ten}" không có trong configs/config.yaml')
    if nd['vai_tro'] != 'MARKETING':
        raise TuChoi(f'"{ten}" có vai trò {nd["vai_tro"]} – chỉ Nhân viên Marketing được nạp tệp (UC1)')
    return nd


def chay_uc1(tep, don_vi: str, nguoi_nap: str, nap_lai: bool = False, ghi_csdl: bool = True,
             in_ra=print, thu_muc_ra: pathlib.Path | None = None) -> dict:
    """UC1. thu_muc_ra (dùng khi kiểm thử): ghi CSV hồ sơ lỗi và báo cáo vào đây thay vì thư mục trong cấu hình."""
    cau_hinh = config.doc_cau_hinh()
    kiem_nguoi_nap(cau_hinh, nguoi_nap)
    bc = {'tep': str(tep), 'don_vi': don_vi, 'nguoi_nap': nguoi_nap, 'ghi_csdl': ghi_csdl,
          'bat_dau': datetime.now().isoformat(timespec='seconds'), 'thoi_gian': {}}

    # ---------------- [1] extract (FR-01) – đọc và kiểm TRƯỚC khi chạm vào CSDL
    t0 = time.perf_counter()
    df_nguon = extract.doc_tep(tep)
    hs = extract.ho_so_tep(df_nguon)
    file_hash = extract.bam_sha256(tep)
    bang_tam = extract.sang_bang_tam(df_nguon)
    bc.update(so_dong_tep=hs['so_dong'], so_cot_tep=hs['so_cot'], file_hash=file_hash)
    in_ra(f"[1/4] extract    {tep}: {so(hs['so_dong'])} dòng × {hs['so_cot']} cột · SHA-256 {file_hash[:12]}…")
    in_ra('      Ô trống: ' + ' · '.join(f'{c} {so(k)} ({pt(r)})' for c, (k, r) in hs['o_trong'].items()))
    t_ex = time.perf_counter() - t0

    # Phần THUẦN của transform chạy trước khi mở giao dịch: tệp có giá trị không vừa customer_clean bị từ chối
    # ngay, kèm số dòng, thay vì làm lệnh INSERT lỗi giữa chừng.
    t0 = time.perf_counter()
    df = transform.chuan_hoa(bang_tam)
    vi_pham = transform.kiem_do_dai_ho_so_sach(df)
    if vi_pham:
        chi_tiet = '; '.join(f'{c} > {transform.DO_DAI_HO_SO_SACH[c]} ký tự ở dòng {", ".join(map(str, r[:10]))}'
                             + (' …' if len(r) > 10 else '') for c, r in vi_pham.items())
        raise TuChoi(f'Giá trị dài hơn cột của customer_clean: {chi_tiet} – sửa tệp nguồn rồi nạp lại')
    t_tf = time.perf_counter() - t0

    engine = None
    if ghi_csdl:
        from src import db                        # chỉ cần thư viện CSDL khi thật sự ghi
        engine = db.tao_engine()
    with (engine.begin() if engine else _khong_csdl()) as conn:
        t0 = time.perf_counter()
        if conn is not None:
            db.khoi_tao_csdl(conn)
            trung = extract.tim_dot_cung_tep(conn, file_hash)
            if trung and not nap_lai:
                ds = ', '.join(f'đợt {b} ({f}, {t:%d/%m/%Y %H:%M})' for b, f, t in trung)
                raise TuChoi(f'Tệp này đã được nạp ở {ds}. Nạp lại sẽ tạo hồ sơ lặp giữa hai đợt; '
                             'chỉ nạp khi chắc chắn bằng cách thêm --nap-lai (AC1.4)')
            batch_id = extract.ghi_dot_nap(conn, pathlib.Path(tep).name, file_hash, don_vi, hs['so_dong'], nguoi_nap)
            n_ghi = extract.ghi_ho_so_tho(conn, batch_id, bang_tam)
            if n_ghi != hs['so_dong']:            # tổng kiểm soát row_count (docs/data-requirements.md mục 5.1)
                raise RuntimeError(f'Ghi {n_ghi} hồ sơ thô nhưng tệp có {hs["so_dong"]} dòng')
            so_dang_hieu_luc = transform.lay_so_dang_hieu_luc(conn)
            in_ra(f'      → ops.load_batch: đợt {batch_id} ({don_vi}, {nguoi_nap}); '
                  f'ops.stg_customer +{so(n_ghi)} hồ sơ thô (LOADED)')
        else:
            batch_id, so_dang_hieu_luc = 'thu', set()
            in_ra('      (không ghi CSDL – chạy thử với --khong-ghi-csdl)')
        bc['batch_id'] = batch_id
        bc['thoi_gian']['extract'] = t_ex + time.perf_counter() - t0

        # ---------------- [2] transform (FR-02, FR-03, FR-10) – df đã chuẩn hóa ở trên, giờ phân loại và ghi
        t0 = time.perf_counter()
        df['status'] = transform.phan_loai(df, so_dang_hieu_luc)
        tk = transform.thong_ke_chuan_hoa(df)
        bc['chuan_hoa'] = tk
        in_ra(f"[2/4] transform  số điện thoại: {so(tk['so_dung_dang_san'])} đúng dạng sẵn · "
              f"{so(tk['so_da_chuan_hoa'])} sai dạng đã chuẩn hóa · {so(tk['so_khong_quy_doi_duoc'])} không quy đổi được · "
              f"{so(len(df) - tk['so_co_gia_tri'])} trống")
        in_ra(f"      họ tên: {so(tk['ten_duoc_sua_cach_viet'])} hồ sơ được sửa cách viết (FR-03)")
        tt, ml = tk['trang_thai'], tk['ma_loi']
        in_ra(f"      phân loại: CLEAN {so(tt['CLEAN'])} · PENDING_DUP {so(tt['PENDING_DUP'])} · ERROR {so(tt['ERROR'])} "
              f"(MISSING_PHONE {so(ml['MISSING_PHONE'])}, INVALID_PHONE {so(ml['INVALID_PHONE'])}, "
              f"MISSING_NAME {so(ml['MISSING_NAME'])})")
        if conn is not None:
            transform.ghi_ket_qua_chuan_hoa(conn, batch_id, df)
            truoc = len(so_dang_hieu_luc)
            them = transform.ghi_customer_clean(conn, batch_id)
            bc['customer_clean'] = (truoc, truoc + them)
            in_ra(f'      → ops.customer_clean: {so(truoc)} → {so(truoc + them)} hồ sơ đang hiệu lực (+{so(them)})')
        thu_muc_xuat = thu_muc_ra or config.duong_dan(cau_hinh, 'thu_muc_xuat')
        tep_loi = thu_muc_xuat / f'ho_so_loi_dot_{batch_id}.csv'
        n_loi = transform.xuat_ho_so_loi(df, tep_loi)
        bc['tep_ho_so_loi'] = _tuong_doi(tep_loi)
        in_ra(f"      → hồ sơ lỗi kèm lý do: {bc['tep_ho_so_loi']} ({so(n_loi)} dòng, FR-10)")
        bc['thoi_gian']['transform'] = t_tf + time.perf_counter() - t0

        # ---------------- [3] dq_evaluate (FR-08) – commit sau
        in_ra('[3/4] dq_evaluate chưa hiện thực')

        # ---------------- [4] load_dwh (FR-09)
        in_ra('[4/4] load_dwh    chưa hiện thực – Sprint 2 (TD-04)')

    tg = bc['thoi_gian']
    in_ra(f"Số dòng: tệp {so(hs['so_dong'])} → bảng tạm {so(len(df))} = sạch {so(tt['CLEAN'])} "
          f"+ chờ quyết định {so(tt['PENDING_DUP'])} + lỗi {so(tt['ERROR'])}")
    in_ra(f"Thời gian: extract {giay(tg['extract'])} · transform {giay(tg['transform'])} · "
          f"tổng {giay(sum(tg.values()))} (NFR-01: nạp và chuẩn hóa 8.000 dòng ≤ 60 s)")
    return bc


def _tuong_doi(p: pathlib.Path) -> str:
    """Đường dẫn tương đối so với gốc repo nếu nằm trong repo (để in gọn)."""
    try:
        return str(p.relative_to(config.GOC))
    except ValueError:
        return str(p)


class _khong_csdl:
    """Thay cho engine.begin() khi chạy --khong-ghi-csdl: trả về conn = None."""
    def __enter__(self):
        return None

    def __exit__(self, *exc):
        return False


def main(argv=None) -> int:
    cau_hinh = config.doc_cau_hinh()
    ap = argparse.ArgumentParser(description='UC1 – Nạp tệp khách hàng thô (L7)')
    ap.add_argument('--tep', required=True, help='Tệp .csv hoặc .xlsx, cột bắt buộc ho_ten, so_dien_thoai')
    ap.add_argument('--don-vi', default=cau_hinh['don_vi_nguon_mac_dinh'], help='Đơn vị nguồn (QT-14)')
    ap.add_argument('--nguoi-nap', default=config.nguoi_dung_mac_dinh(cau_hinh, 'MARKETING'),
                    help='Tên đăng nhập trong configs/config.yaml, vai trò MARKETING')
    ap.add_argument('--nap-lai', action='store_true', help='Xác nhận nạp tệp đã từng nạp (AC1.4)')
    ap.add_argument('--khong-ghi-csdl', action='store_true', help='Chạy thử extract/transform, không ghi CSDL')
    a = ap.parse_args(argv)
    try:
        chay_uc1(a.tep, a.don_vi, a.nguoi_nap, a.nap_lai, ghi_csdl=not a.khong_ghi_csdl)
        return MA_THANH_CONG
    except (TuChoi, extract.TepBiTuChoi) as e:
        print(f'TỪ CHỐI: {e}', file=sys.stderr)
        return MA_TU_CHOI
    except Exception as e:                           # noqa: BLE001 – báo lỗi gọn cho người dùng
        print(f'LỖI: {type(e).__name__}: {e}', file=sys.stderr)
        return MA_LOI_KY_THUAT


if __name__ == '__main__':
    sys.exit(main())
