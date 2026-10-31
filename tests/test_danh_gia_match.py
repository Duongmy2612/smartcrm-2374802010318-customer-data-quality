"""Kiểm thử phép kiểm chứng NFR-03 – src/etl/danh_gia_match.py (hàm thuần) và src/kiem_chung_nfr03.py (TD-32).

Không cần CSDL. Mỗi test ghi loại ở cuối docstring: [luồng đúng] · [biên] · [dữ liệu sai].
"""
import pathlib

import pandas as pd
import pytest

from src import kiem_chung_nfr03 as kc
from src.etl import danh_gia_match as dg
from src.etl.match import tao_name_key

GOC = pathlib.Path(__file__).resolve().parent.parent
MAU = GOC / 'data' / 'mau' / 'customers_mau.csv'
NHAN_DUNG = GOC / 'data' / 'mau' / 'nhan_dung_mau.csv'
THAT = GOC / 'data' / 'raw' / 'customers_raw.csv'


def _ho_so(*dong):
    """dong = (ma, phone_norm, họ tên)."""
    return pd.DataFrame({'ma': [d[0] for d in dong], 'phone_norm': [d[1] for d in dong],
                         'name_key': [tao_name_key(d[2]) for d in dong]})


def _bang(*dong):
    """dong = (cung_so, cung_khoi, diem, nhan) – bảng đã có nhãn để tính chỉ số."""
    return pd.DataFrame([{'cung_so': a, 'cung_khoi': b, 'diem': c, 'nhan': d, 'trong_so': 1.0} for a, b, c, d in dong])


# ------------------------------------------------------------------ khung cặp và chọn mẫu
@pytest.mark.luong_dung
def test_khung_cap_chia_dung_nam_tang():
    """Cùng số → T1 (k − 1 cặp); số gõ nhầm 1 chữ số, cùng tên → T2; cùng tên nhưng một bên thiếu số → T4;
    cùng tên, hai số khác khối → T5; khác tên, khác khối → không thuộc khung. [luồng đúng]"""
    hs = _ho_so((1, '0901234567', 'Nguyễn Văn An'), (2, '0901234567', 'NGUYEN VAN AN'),
                (3, '0901234567', 'nguyễn văn an'), (4, '0901234568', 'Nguyễn Văn An'),
                (5, None, 'Lê Thị Mai'), (6, '0987000111', 'Lê Thị Mai'),
                (7, '0911222333', 'Phạm Minh Tú'), (8, '0388777666', 'Phạm Minh Tú'),
                (9, '0355444999', 'Võ Bảo Sơn'))
    tang = {(r.ma_a, r.ma_b): r.tang for r in dg.khung_cap(hs).itertuples()}
    assert tang == {(1, 2): 'T1', (1, 3): 'T1', (1, 4): 'T2', (5, 6): 'T4', (7, 8): 'T5'}


@pytest.mark.gia_tri_bien
def test_chon_mau_theo_chi_tieu_va_bu_bang_t1():
    """Tầng ít hơn chỉ tiêu thì lấy hết (T2: 5), các tầng khác lấy đúng chỉ tiêu, T1 bù cho đủ 300; trọng số
    = số cặp của tầng / số cặp lấy; cùng seed → cùng mẫu. [biên]"""
    khung = pd.DataFrame([(i, i + 1, t, t == 'T1', False, None) for t, n in
                          (('T1', 500), ('T2', 5), ('T3', 100), ('T4', 100), ('T5', 100)) for i in range(n)],
                         columns=['ma_a', 'ma_b', 'tang', 'cung_so', 'cung_khoi', 'diem'])
    khung['ma_a'] += khung.index * 10
    khung['ma_b'] = khung['ma_a'] + 1
    mau = dg.chon_mau(khung)
    assert len(mau) == 300 and mau['ma_cap'].is_unique
    assert mau['tang'].value_counts().to_dict() == {'T1': 135, 'T3': 60, 'T4': 60, 'T5': 40, 'T2': 5}
    assert mau.groupby('tang')['trong_so'].first().round(4).to_dict() == {
        'T1': round(500 / 135, 4), 'T2': 1.0, 'T3': round(100 / 60, 4), 'T4': round(100 / 60, 4), 'T5': 2.5}
    assert mau.equals(dg.chon_mau(khung))


@pytest.mark.gia_tri_bien
def test_khung_nho_hon_300_cap_thi_lay_het():
    """Khung chỉ có 3 cặp → lấy đủ 3 cặp, không lỗi, trọng số 1. [biên]"""
    hs = _ho_so((1, '0901234567', 'An'), (2, '0901234567', 'An'), (3, None, 'An'))
    mau = dg.chon_mau(dg.khung_cap(hs))
    assert len(mau) == 3 and set(mau['trong_so']) == {1.0}


# ------------------------------------------------------------------ chỉ số
@pytest.mark.luong_dung
def test_precision_recall_dung_cong_thuc():
    """3 cặp ghép đúng, 1 cặp ghép sai, 1 cặp bỏ sót, 2 cặp loại đúng → precision 3/4, recall 3/4. [luồng đúng]"""
    bang = _bang((True, True, 100, 1), (True, True, 100, 1), (False, True, 90, 1), (False, True, 88, 0),
                 (False, False, None, 1), (False, True, 72, 0), (False, False, None, 0))
    kq = dg.tinh_chi_so(bang, 85)
    assert (kq['tp'], kq['fp'], kq['fn'], kq['tn']) == (3, 1, 1, 2)
    assert kq['precision'] == kq['recall'] == 0.75 and not kq['dat']


@pytest.mark.gia_tri_bien
def test_precision_dung_85_va_recall_dung_80_la_dat():
    """Đúng bằng yêu cầu thì ĐẠT (≥): 17/20 = 85%; 16/20 = 80%. Thấp hơn một cặp thì chưa đạt. [biên]"""
    def kq(tp, fp, fn):
        return dg.tinh_chi_so(_bang(*([(True, True, 100, 1)] * tp + [(True, True, 100, 0)] * fp +
                                      [(False, False, None, 1)] * fn)), 85)
    assert kq(17, 3, 0)['dat_precision'] and not kq(16, 3, 0)['dat_precision']
    assert kq(16, 0, 4)['dat_recall'] and not kq(15, 0, 4)['dat_recall']


@pytest.mark.gia_tri_bien
def test_diem_bang_nguong_la_he_thong_ghep():
    """Cặp FUZZY có điểm đúng bằng ngưỡng được tính là hệ thống ghép, giống match.la_cap_fuzzy (QL7-02). [biên]"""
    bang = _bang((False, True, 85.0, 1))
    assert dg.he_thong_ghep(bang, 85).all() and not dg.he_thong_ghep(bang, 85.01).any()


# ------------------------------------------------------------------ chạy trọn trên dữ liệu mẫu
@pytest.mark.luong_dung
def test_kiem_chung_nfr03_tren_du_lieu_mau(tmp_path):
    """Một lệnh trên data/mau với nhãn đúng của script sinh: khung 63 cặp, T1 = 40 và T2 = 3 khớp đúng số cặp
    EXACT_PHONE và FUZZY của pipeline (README mục 5); precision 100%, recall 100% → ĐẠT. [luồng đúng]"""
    kq = kc.chay(MAU, 85, 42, nhan_dung=NHAN_DUNG, in_ra=lambda *_: None, thu_muc_bao_cao=tmp_path)
    dem = dg.dem_theo_tang(kq['khung'], kq['mau']).set_index('tang')['trong_khung'].to_dict()
    assert len(kq['khung']) == 63 and (dem['T1'], dem['T2']) == (40, 3)
    r = kq['ket_qua']
    assert (r['tp'], r['fp'], r['fn'], r['tn']) == (43, 0, 0, 20) and r['dat']
    assert len(list(tmp_path.glob('nfr03-*.md'))) == 1


@pytest.mark.luong_dung
def test_tao_phieu_mu_va_tinh_lai_tu_phieu(tmp_path):
    """--tao-phieu ghi phiếu MÙ (không có tầng, điểm, quyết định của hệ thống); điền nhãn rồi --nhan tính được và
    cho cùng kết quả với nhãn đúng. [luồng đúng]"""
    p = tmp_path / 'phieu.xlsx'
    assert kc.main(['--tep', str(MAU), '--tao-phieu', str(p)]) == kc.MA_THANH_CONG
    phieu = pd.read_excel(p, dtype=str, keep_default_na=False)
    assert not {'tang', 'diem', 'cung_so', 'cung_khoi', 'trong_so'} & set(phieu.columns)
    assert len(phieu) == 63 and (phieu['nhan'] == '').all()
    goc = pd.read_csv(MAU, dtype=str, keep_default_na=False)
    assert set(phieu['so_dien_thoai_a']) <= set(goc['so_dien_thoai'])      # .xlsx giữ nguyên số 0 đầu, dấu cách
    dung = pd.read_csv(NHAN_DUNG, dtype=str).set_index('record_id')['ma_khach']
    phieu['nhan'] = (dung.loc[phieu['dong_a']].to_numpy() == dung.loc[phieu['dong_b']].to_numpy()).astype(int)
    phieu.to_csv(tmp_path / 'da_gan.csv', index=False)
    kq = kc.chay(MAU, 85, 42, nhan=tmp_path / 'da_gan.csv', in_ra=lambda *_: None, thu_muc_bao_cao=tmp_path)
    assert (kq['ket_qua']['tp'], kq['ket_qua']['fp'], kq['ket_qua']['fn']) == (43, 0, 0)


# ------------------------------------------------------------------ phiếu nhãn sai
@pytest.mark.du_lieu_sai
@pytest.mark.parametrize('sua, cau', [
    ({'nhan': ''}, 'chưa gán nhãn'),
    ({'nhan': 'có'}, 'chỉ nhận 1'),
    ({'dong_b': 'abc'}, 'phải là số dòng'),
])
def test_phieu_nhan_sai_bi_tu_choi_ro_rang(sua, cau):
    """Ô nhãn trống, nhãn không phải 1/0, cột số dòng bị sửa → TỪ CHỐI bằng câu tiếng Việt. [dữ liệu sai]"""
    phieu = pd.DataFrame({'ma_cap': ['C001', 'C002'], 'dong_a': ['1', '3'], 'dong_b': ['2', '4'], 'nhan': ['1', '0']})
    for cot, gia_tri in sua.items():
        phieu.loc[1, cot] = gia_tri
    with pytest.raises(dg.NhanKhongHopLe, match=cau):
        dg.kiem_phieu_nhan(phieu)


@pytest.mark.du_lieu_sai
def test_phieu_cua_tep_khac_bi_tu_choi_ma_thoat_2(tmp_path, capsys):
    """Phiếu có cặp không thuộc khung của tệp nguồn (phiếu tạo từ tệp khác) → mã thoát 2, không lỗi thô. [dữ liệu sai]"""
    p = tmp_path / 'phieu.csv'
    pd.DataFrame({'ma_cap': ['C001'], 'dong_a': ['1'], 'dong_b': ['414'], 'nhan': ['1']}).to_csv(p, index=False)
    assert kc.main(['--tep', str(MAU), '--nhan', str(p)]) == kc.MA_TU_CHOI
    loi = capsys.readouterr().err
    assert loi.startswith('TỪ CHỐI:') and 'không thuộc khung' in loi and 'Error' not in loi


@pytest.mark.du_lieu_sai
def test_tao_phieu_khong_ghi_de_phieu_da_co(tmp_path):
    """Phiếu đã có (có thể đã chứa nhãn em gán) → không ghi đè, mã thoát 2. [dữ liệu sai]"""
    p = tmp_path / 'phieu.xlsx'
    p.write_text('nhãn đã gán', encoding='utf-8')
    assert kc.main(['--tep', str(MAU), '--tao-phieu', str(p)]) == kc.MA_TU_CHOI
    assert p.read_text(encoding='utf-8') == 'nhãn đã gán'


# ------------------------------------------------------------------ dữ liệu thật (LMS, không có trong repo)
@pytest.mark.skipif(not THAT.is_file(), reason='cần data/raw/customers_raw.csv (LMS, không commit)')
def test_khung_du_lieu_that_khop_so_cap_cua_pipeline():
    """Trên tệp thật 67.037 dòng: T1 = 11.625 và T2 = 12 – đúng số cặp EXACT_PHONE, FUZZY pipeline ghi
    (docs/data-requirements.md mục 7), nên phép kiểm chứng đo đúng những gì hệ thống làm. [hồi quy]"""
    khung, _ = kc.lap_mau(kc.doc_ho_so(THAT), 85, 42)
    dem = khung['tang'].value_counts().to_dict()
    assert (dem['T1'], dem['T2']) == (11625, 12)
