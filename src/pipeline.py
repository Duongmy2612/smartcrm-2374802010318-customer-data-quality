"""Điều phối lớp ② theo thứ tự gọi ở Bảng 3.1 của BT1 – luồng chính của L7 chạy end-to-end bằng MỘT lệnh:

    UC1 Nạp tệp khách hàng thô : extract → transform → dq_evaluate → load_dwh     (giao dịch 1)
    UC3 Phát hiện cặp nghi trùng: match → load_dwh                                (giao dịch 2)

Chạy từ thư mục gốc repo (đã kích hoạt .venv):

    python -m src.pipeline --tep data/raw/customers_raw.csv
    python -m src.pipeline --tep data/raw/customers_raw.csv --khong-ghi-csdl   # chưa có PostgreSQL

Dashboard đọc kho sau khi lệnh trên chạy xong: streamlit run dashboard/report.py

Quyết định thiết kế:
  1. Cả UC1 nằm trong MỘT giao dịch (`with engine.begin()`): lỗi ở bất kỳ bước nào → ROLLBACK, không bao giờ
     còn lại một đợt nạp dở dang (TD-09). UC3 là giao dịch thứ hai: so khớp lỗi thì đợt nạp vẫn còn, chỉ cần
     chạy lại UC3 (TD-17).
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

from sqlalchemy import text

from src import config
from src.etl import dq_evaluate, extract, load_dwh, match, transform

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


class LoiUC3(RuntimeError):
    """UC3 lỗi sau khi UC1 đã lưu: đợt nạp vẫn còn, thông báo chỉ lệnh chạy lại riêng UC3 (mã thoát 1, TD-17)."""


def kiem_nguoi_nap(cau_hinh: dict, ten: str) -> dict:
    """Bảng 1.2 của BT1: chỉ Nhân viên Marketing được nạp tệp (UC1)."""
    nd = config.tim_nguoi_dung(cau_hinh, ten)
    if nd is None:
        raise TuChoi(f'Người dùng "{ten}" không có trong configs/config.yaml')
    if nd['vai_tro'] != 'MARKETING':
        raise TuChoi(f'"{ten}" có vai trò {nd["vai_tro"]} – chỉ Nhân viên Marketing được nạp tệp (UC1)')
    return nd


def chay_uc1(tep, don_vi: str, nguoi_nap: str, nap_lai: bool = False, ghi_csdl: bool = True,
             in_ra=print, thu_muc_ra: pathlib.Path | None = None, phat_hien_cap: bool = True) -> dict:
    """Luồng chính: UC1 rồi UC3 (phat_hien_cap=False để chỉ chạy UC1).
    thu_muc_ra (dùng khi kiểm thử): ghi CSV hồ sơ lỗi và báo cáo vào đây thay vì thư mục trong cấu hình."""
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
    in_ra(f"[1/5] extract    {tep}: {so(hs['so_dong'])} dòng × {hs['so_cot']} cột · SHA-256 {file_hash[:12]}…")
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
        in_ra(f"[2/5] transform  số điện thoại: {so(tk['so_dung_dang_san'])} đúng dạng sẵn · "
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

        # ---------------- [3] dq_evaluate (FR-08) – UC1 «include» UC7: đo TRƯỚC/SAU ngay trong giao dịch nạp
        t0 = time.perf_counter()
        if conn is not None:
            dq_evaluate.khoi_tao_quy_tac(conn, 'he_thong')
            quy_tac = dq_evaluate.doc_quy_tac_dang_bat(conn)
        else:
            quy_tac = dq_evaluate.QUY_TAC_MAC_DINH
        ket_qua = dq_evaluate.do_mot_lan(df, quy_tac)
        # Thời điểm đo lấy từ ĐỒNG HỒ CSDL – cùng đồng hồ với dq_rule.updated_at (= valid_from của dim_rule),
        # để load_dwh tìm đúng phiên bản quy tắc kể cả khi máy chạy Python và máy CSDL lệch giờ (TD-16).
        do_luc = (conn.execute(text('SELECT clock_timestamp()::timestamp')).scalar_one()
                  if conn is not None else datetime.now())
        if conn is not None:
            n_kq = dq_evaluate.ghi_ket_qua(conn, batch_id, ket_qua, quy_tac, do_luc)
            ghi = f'→ ops.dq_result +{n_kq} dòng'
        else:
            ghi = '(không ghi CSDL)'
        bc['chat_luong'] = _bang_chat_luong(ket_qua, quy_tac)
        truoc = dq_evaluate.chi_so_muc_do_sach(ket_qua, quy_tac, 'TRUOC')
        sau = dq_evaluate.chi_so_muc_do_sach(ket_qua, quy_tac, 'SAU')
        bc['chi_so'] = {'TRUOC': round(truoc, 2), 'SAU': round(sau, 2)}
        in_ra(f'[3/5] dq_evaluate {len(quy_tac)} quy tắc × 2 giai đoạn {ghi}')
        in_ra(f"      {'Quy tắc':<8}{'Trọng số':>9}{'Ngưỡng':>9}   {'TRƯỚC':<18}{'SAU':<18}")
        for d in bc['chat_luong']:
            in_ra(f"      {d['ma']:<8}{d['trong_so']:>9}{d['nguong']:>9}   {d['truoc']:<18}{d['sau']:<18}")
        t, s_ = bc['chi_so']['TRUOC'], bc['chi_so']['SAU']      # chênh lệch tính trên số đã làm tròn, như BT1
        in_ra(f'      Chỉ số mức độ sạch (QL7-06): TRƯỚC {diem(t)} ({dq_evaluate.xep_loai(t)}) → '
              f'SAU {diem(s_)} ({dq_evaluate.xep_loai(s_)}), {diem(s_ - t, dau=True)} điểm')
        bc['thoi_gian']['dq_evaluate'] = time.perf_counter() - t0

        # ---------------- [4] load_dwh (FR-09) – UC1: dimension rồi fact, theo khóa nghiệp vụ
        t0 = time.perf_counter()
        if conn is not None:
            bc['nap_kho_uc1'] = load_dwh.nap_kho(conn)
            in_ra('[4/5] load_dwh    ' + _dong_nap_kho(bc['nap_kho_uc1']))
        else:
            in_ra('[4/5] load_dwh    (không ghi CSDL)')
        bc['thoi_gian']['load_dwh'] = time.perf_counter() - t0

    # ---------------- [5] UC3 phát hiện cặp nghi trùng (FR-04) → load_dwh – giao dịch thứ hai (TD-17)
    if phat_hien_cap:
        _chay_uc3(bc, df, engine, cau_hinh, in_ra)
    else:
        in_ra('[5/5] match       bỏ qua (--khong-phat-hien-cap)')

    tg = bc['thoi_gian']
    in_ra(f"Số dòng: tệp {so(hs['so_dong'])} → bảng tạm {so(len(df))} = sạch {so(tt['CLEAN'])} "
          f"+ chờ quyết định {so(tt['PENDING_DUP'])} + lỗi {so(tt['ERROR'])}")
    uc1 = tg['extract'] + tg['transform'] + tg['dq_evaluate']
    in_ra(f"Thời gian: extract {giay(tg['extract'])} · transform {giay(tg['transform'])} · "
          f"dq_evaluate {giay(tg['dq_evaluate'])} → {giay(uc1)} (NFR-01 phần 1: nạp và chuẩn hóa 8.000 dòng ≤ 60 s)")
    if 'match' in tg:
        in_ra(f"           UC3 phát hiện cặp + nạp kho {giay(tg['match'])} (NFR-01 phần 2: ≤ 120 s trên 8.000 hồ sơ) · "
              f"toàn luồng {giay(sum(tg.values()))}")
    tep_bc = ghi_bao_cao(bc, hs, thu_muc_ra or config.duong_dan(cau_hinh, 'thu_muc_bao_cao'))
    bc['tep_bao_cao'] = _tuong_doi(tep_bc)
    in_ra(f"Báo cáo: {bc['tep_bao_cao']}")
    return bc


def _dong_nap_kho(ra: dict) -> str:
    return ' · '.join(f'{k} +{so(v)}' for k, v in ra.items())


def _chay_uc3(bc: dict, df, engine, cau_hinh: dict, in_ra) -> None:
    """UC3 (match → load_dwh) trong giao dịch riêng; in đối soát staging ↔ kho sau khi nạp."""
    nguong = float(cau_hinh['nguong_fuzzy'])
    t0 = time.perf_counter()
    if engine is None:                              # chạy thử: so khớp trong bộ nhớ trên chính đợt này
        hs = df[df['error_code'].isna()].rename(columns={'row_no': 'stg_id'})
        hs = hs.assign(name_key=hs['name_norm'].map(match.tao_name_key))[['stg_id', 'phone_norm', 'name_key']]
        tk = {'cap_ung_vien': 0, 'so_khac_nhau': 0}
        cap = match.tim_cap(hs, None, nguong, thong_ke=tk)
        kq = {'ho_so_so_khop': len(hs), 'so_khac_nhau': tk['so_khac_nhau'], 'cap_ung_vien': tk['cap_ung_vien'],
              'nguong': nguong,
              'exact': int((cap['match_type'] == 'EXACT_PHONE').sum()), 'fuzzy': int((cap['match_type'] == 'FUZZY').sum())}
        ghi = '(không ghi CSDL)'
    else:
        try:
            with engine.begin() as conn:
                kq = match.phat_hien_cap(conn, bc['batch_id'], nguong)
                bc['nap_kho_uc3'] = load_dwh.nap_kho(conn)
                bc['doi_soat'] = load_dwh.doi_soat(conn)
        except Exception as e:                      # giao dịch 2 đã ROLLBACK; giao dịch 1 (UC1) đã lưu
            raise LoiUC3(f"UC3 lỗi ({type(e).__name__}: {e}). Đợt {bc['batch_id']} đã nạp và đo xong (UC1 đã lưu); "
                         f"sửa lỗi rồi chạy lại riêng UC3: python -m src.etl.match --dot {bc['batch_id']}") from e
        ghi = f"→ ops.dup_candidate +{so(kq['exact'] + kq['fuzzy'])} cặp PENDING"
    bc['thoi_gian']['match'] = time.perf_counter() - t0
    bc['so_khop'] = kq
    in_ra(f"[5/5] match       {so(kq['ho_so_so_khop'])} hồ sơ có số hợp lệ ({so(kq['so_khac_nhau'])} số khác nhau) · "
          f"blocking 5 số đầu/cuối: {so(kq['cap_ung_vien'])} cặp ứng viên · ngưỡng {kq['nguong']:g}")
    in_ra(f"      EXACT_PHONE {so(kq['exact'])} · FUZZY {so(kq['fuzzy'])} {ghi}")
    if engine is not None:
        in_ra('      load_dwh    ' + _dong_nap_kho(bc['nap_kho_uc3']))
        in_ra('      Đối soát staging (ops) ↔ kho (dwh):')
        load_dwh.in_doi_soat(bc['doi_soat'], in_ra)


def _tuong_doi(p: pathlib.Path) -> str:
    """Đường dẫn tương đối so với gốc repo nếu nằm trong repo (để in gọn)."""
    try:
        return str(p.relative_to(config.GOC))
    except ValueError:
        return str(p)


def diem(x: float, dau: bool = False) -> str:
    return (f'{x:+.2f}' if dau else f'{x:.2f}').replace('.', ',')


def _bang_chat_luong(ket_qua, quy_tac) -> list[dict]:
    """Một dòng / quy tắc: tỉ lệ đạt TRƯỚC, SAU và đạt/chưa đạt so với ngưỡng (để in và ghi báo cáo)."""
    theo = {(k.rule_code, k.measure_stage): k for k in ket_qua}
    dong = []
    for q in quy_tac:
        o = {'ma': q['rule_code'], 'ten': q['rule_name'], 'trong_so': f"{float(q['weight']):.2f}".replace('.', ','),
             'nguong': f"≥ {float(q['pass_threshold']):g}%"}
        for gd, khoa in (('TRUOC', 'truoc'), ('SAU', 'sau')):
            k = theo[(q['rule_code'], gd)]
            dat = k.ti_le * 100 >= float(q['pass_threshold'])
            o[khoa] = f"{pt(k.ti_le)} {'đạt' if dat else 'chưa đạt'}"
            o[khoa + '_so'] = f'{so(k.pass_count)}/{so(k.total_records)}'
        dong.append(o)
    return dong


def ghi_bao_cao(bc: dict, hs: dict, thu_muc: pathlib.Path) -> pathlib.Path:
    """Báo cáo Markdown chỉ có SỐ ĐẾM (không có họ tên, số điện thoại) nên an toàn để đính kèm minh chứng."""
    tt, tk = bc['chuan_hoa']['trang_thai'], bc['chuan_hoa']
    d = [f"# Báo cáo UC1 – đợt nạp {bc['batch_id']}", '',
         f"- Tệp: `{bc['tep']}` · SHA-256 `{bc['file_hash']}`",
         f"- Đơn vị nguồn: {bc['don_vi']} · Người nạp: {bc['nguoi_nap']} · Bắt đầu: {bc['bat_dau']}",
         f"- Ghi CSDL: {'có' if bc['ghi_csdl'] else 'không (--khong-ghi-csdl)'}", '',
         f"## 1. Extract – {so(hs['so_dong'])} dòng × {hs['so_cot']} cột", '',
         '| Cột | Ô trống | Tỉ lệ |', '|---|---:|---:|']
    d += [f'| {c} | {so(k)} | {pt(r)} |' for c, (k, r) in hs['o_trong'].items()]
    d += ['', '## 2. Transform – số dòng trước → sau', '',
          '| Hạng mục | Số hồ sơ |', '|---|---:|',
          f"| Số điện thoại đúng dạng sẵn | {so(tk['so_dung_dang_san'])} |",
          f"| Số điện thoại sai dạng đã chuẩn hóa | {so(tk['so_da_chuan_hoa'])} |",
          f"| Số điện thoại không quy đổi được (INVALID_PHONE) | {so(tk['so_khong_quy_doi_duoc'])} |",
          f"| Họ tên được sửa cách viết | {so(tk['ten_duoc_sua_cach_viet'])} |",
          f"| **CLEAN** – vào customer_clean | {so(tt['CLEAN'])} |",
          f"| **PENDING_DUP** – hồ sơ lặp chờ quyết định | {so(tt['PENDING_DUP'])} |",
          f"| **ERROR** – ở lại bảng tạm | {so(tt['ERROR'])} |"]
    d += [f'| &nbsp;&nbsp;{k} | {so(v)} |' for k, v in tk['ma_loi'].items()]
    d += ['', f"Tệp hồ sơ lỗi kèm lý do: `{bc['tep_ho_so_loi']}` (có dữ liệu cá nhân, không commit).", '',
          '## 3. Chất lượng TRƯỚC / SAU (FR-08, QL7-06)', '',
          '| Quy tắc | Tên | Trọng số | Ngưỡng | TRƯỚC (đạt/kiểm) | SAU (đạt/kiểm) |', '|---|---|---:|---:|---|---|']
    d += [f"| {o['ma']} | {o['ten']} | {o['trong_so']} | {o['nguong']} | {o['truoc']} ({o['truoc_so']}) | "
          f"{o['sau']} ({o['sau_so']}) |" for o in bc['chat_luong']]
    t, s = bc['chi_so']['TRUOC'], bc['chi_so']['SAU']
    d += ['', f"**Chỉ số mức độ sạch:** TRƯỚC {diem(t)} ({dq_evaluate.xep_loai(t)}) → SAU {diem(s)} "
              f"({dq_evaluate.xep_loai(s)}), {diem(s - t, dau=True)} điểm.", '']
    if 'so_khop' in bc:
        k = bc['so_khop']
        d += ['## 4. UC3 – phát hiện cặp nghi trùng (FR-04)', '',
              f"- Hồ sơ có số hợp lệ tham gia so khớp: {so(k['ho_so_so_khop'])} ({so(k['so_khac_nhau'])} số khác nhau); "
              f"cặp ứng viên sau blocking (giữa hồ sơ đại diện của hai số khác nhau): "
              f"{so(k['cap_ung_vien'])}; ngưỡng FUZZY {k['nguong']:g}.",
              f"- Cặp mới: EXACT_PHONE {so(k['exact'])} · FUZZY {so(k['fuzzy'])}.", '']
    if 'doi_soat' in bc:
        d += ['## 5. Nạp kho và đối soát staging (ops) ↔ kho (dwh)', '',
              '| Mục | ops | dwh | Khớp | Giải thích |', '|---|---:|---:|---|---|']
        d += [f"| {r['muc']} | {so(r['nguon'])} | {so(r['kho'])} | {'có' if r['khop'] else 'KHÔNG'} | {r['giai_thich']} |"
              for r in bc['doi_soat']]
        d += ['']
    d += ['## 6. Thời gian (NFR-01)', '', '| Bước | Giây |', '|---|---:|']
    d += [f"| {k} | {v:.2f} |".replace('.', ',') for k, v in bc['thoi_gian'].items()]
    p = thu_muc / f"uc1-dot-{bc['batch_id']}-{datetime.now():%Y%m%d_%H%M%S}.md"
    p.write_text('\n'.join(d) + '\n', encoding='utf-8')
    return p


class _khong_csdl:
    """Thay cho engine.begin() khi chạy --khong-ghi-csdl: trả về conn = None."""
    def __enter__(self):
        return None

    def __exit__(self, *exc):
        return False


def main(argv=None) -> int:
    cau_hinh = config.doc_cau_hinh()
    ap = argparse.ArgumentParser(description='Luồng chính L7: UC1 Nạp tệp khách hàng thô → UC3 Phát hiện cặp → kho')
    ap.add_argument('--tep', required=True, help='Tệp .csv hoặc .xlsx, cột bắt buộc ho_ten, so_dien_thoai')
    ap.add_argument('--don-vi', default=cau_hinh['don_vi_nguon_mac_dinh'], help='Đơn vị nguồn (QT-14)')
    ap.add_argument('--nguoi-nap', default=config.nguoi_dung_mac_dinh(cau_hinh, 'MARKETING'),
                    help='Tên đăng nhập trong configs/config.yaml, vai trò MARKETING')
    ap.add_argument('--nap-lai', action='store_true', help='Xác nhận nạp tệp đã từng nạp (AC1.4)')
    ap.add_argument('--khong-ghi-csdl', action='store_true', help='Chạy thử extract/transform, không ghi CSDL')
    ap.add_argument('--khong-phat-hien-cap', action='store_true', help='Chỉ chạy UC1, không chạy UC3 (match)')
    a = ap.parse_args(argv)
    try:
        chay_uc1(a.tep, a.don_vi, a.nguoi_nap, a.nap_lai, ghi_csdl=not a.khong_ghi_csdl,
                 phat_hien_cap=not a.khong_phat_hien_cap)
        return MA_THANH_CONG
    except (TuChoi, extract.TepBiTuChoi) as e:
        print(f'TỪ CHỐI: {e}', file=sys.stderr)
        return MA_TU_CHOI
    except Exception as e:                           # noqa: BLE001 – báo lỗi gọn cho người dùng
        print(f'LỖI: {type(e).__name__}: {e}', file=sys.stderr)
        return MA_LOI_KY_THUAT


if __name__ == '__main__':
    sys.exit(main())
