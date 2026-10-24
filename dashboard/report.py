"""① dashboard/report.py – Dashboard mức độ sạch dữ liệu khách hàng, khung K1 – K3 (UC8). Sprint 2 (buổi 10).

Chạy (sau khi luồng chính đã nạp kho):   streamlit run dashboard/report.py

- Chỉ hiển thị: truy vấn và quy tắc nằm ở src/doc_kho.py; kết nối CHỈ ĐỌC (src/db.tao_engine_chi_doc, TD-19).
- Lọc theo đơn vị nguồn của người xem (QT-14) + khoảng ngày nạp + đợt nạp.
- Ba trạng thái: đang tải (spinner) · rỗng (câu giải thích vì sao và nên làm gì) · lỗi (thông báo không lộ
  chuỗi kết nối, có nút Thử lại).
- Mỗi biểu đồ: một câu hỏi phân tích, một mốc tham chiếu, một dòng ghi nguồn và thời điểm dữ liệu.
"""
import pathlib
import sys
from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))   # để import src khi chạy streamlit
from src import config, db, doc_kho                                         # noqa: E402

BO_DEM_GIAY = 60
st.set_page_config(page_title='Smart CRM · Mức độ sạch dữ liệu khách hàng', layout='wide')


@st.cache_resource
def engine():
    return db.tao_engine_chi_doc()


@st.cache_data(ttl=BO_DEM_GIAY, show_spinner=False)
def tai(ten: str, *tham):
    """Mọi truy vấn đi qua đây để dùng chung bộ đệm (ttl 60 giây – ghi trên từng biểu đồ)."""
    with engine().connect() as conn:
        return getattr(doc_kho, ten)(conn, *tham)


def so(n) -> str:
    return f'{int(n):,}'.replace(',', '.')


def diem(x) -> str:
    return f'{float(x):.2f}'.replace('.', ',')


def pt(x) -> str:
    return f'{float(x) * 100:.2f}%'.replace('.', ',')


def ghi_nguon(nguon: str, td: dict) -> None:
    lan_do = td['lan_do'].strftime('%d/%m/%Y %H:%M') if td.get('lan_do') else 'chưa có lần đo'
    st.caption(f'Nguồn: {nguon} · dữ liệu đến lần đo {lan_do} · trang tải lúc {datetime.now():%H:%M:%S} · '
               f'bộ đệm {BO_DEM_GIAY} giây (bấm "Làm mới dữ liệu" để đọc lại ngay).')


# ------------------------------------------------------------------ thanh bên: người xem và bộ lọc
cau_hinh = config.doc_cau_hinh()
st.title('Mức độ sạch dữ liệu khách hàng')
st.caption('Smart CRM – Mekong Mobile · L7 · UC8 Xem dashboard mức độ sạch theo thời gian')

with st.sidebar:
    ds_nd = [nd['ten_dang_nhap'] for nd in cau_hinh['nguoi_dung']]
    mac_dinh = st.query_params.get('nguoi_xem')          # ví dụ ?nguoi_xem=ql.mm001 để mở sẵn góc nhìn Quản lý
    nguoi_xem = st.selectbox('Người xem', ds_nd, index=ds_nd.index(mac_dinh) if mac_dinh in ds_nd else 0,
                             format_func=lambda t: f"{t} ({config.tim_nguoi_dung(cau_hinh, t)['vai_tro']})")
    pham_vi = doc_kho.don_vi_duoc_xem(cau_hinh, nguoi_xem)
    st.caption('Phạm vi xem (QT-14): ' + ('toàn công ty' if pham_vi is None else ', '.join(pham_vi) or 'không có'))
    khoang = st.date_input('Khoảng ngày nạp', (date(2026, 1, 1), date.today()), format='DD/MM/YYYY')
    tu, den = (khoang if isinstance(khoang, tuple) and len(khoang) == 2 else (None, None))
    if st.button('Làm mới dữ liệu'):
        st.cache_data.clear()

# ------------------------------------------------------------------ TRẠNG THÁI 1: đang tải
try:
    with st.spinner('Đang tải dữ liệu từ kho dữ liệu…'):
        td = tai('doc_thoi_diem_du_lieu')
        tat_ca = tai('doc_dot', pham_vi, [], tu, den)
        don_vi_co = sorted(tat_ca['source_unit'].unique()) if len(tat_ca) else []
        don_vi_chon = st.sidebar.multiselect('Đơn vị nguồn', don_vi_co, default=don_vi_co)
        dot = tat_ca[tat_ca['source_unit'].isin(don_vi_chon)] if len(tat_ca) else tat_ca
        if len(dot):
            nhan = {r.batch_key: f'Đợt #{r.batch_id} · {r.loaded_at:%d/%m/%Y} · {r.file_name}' for r in dot.itertuples()}
            chon = st.sidebar.multiselect('Đợt nạp', list(nhan), default=list(nhan), format_func=nhan.get)
            dot = dot[dot['batch_key'].isin(chon)]
        quy_tac = tai('doc_ty_le_quy_tac', list(dot['batch_key'])) if len(dot) else pd.DataFrame()
        cap = tai('doc_cap', list(dot['batch_key'])) if len(dot) else pd.DataFrame()
# ------------------------------------------------------------------ TRẠNG THÁI 3: lỗi
except Exception as e:                                  # noqa: BLE001
    st.error('Không đọc được dữ liệu từ kho dữ liệu. Kiểm tra PostgreSQL đang chạy, tệp .env đúng và luồng chính '
             'đã chạy ít nhất một lần, rồi bấm Thử lại.')
    st.caption(f'Loại lỗi: {type(e).__name__}')         # chỉ in loại lỗi – không in chuỗi kết nối, tên bảng, vết lỗi
    if st.button('Thử lại', type='primary'):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    st.stop()

# ------------------------------------------------------------------ TRẠNG THÁI 2: rỗng
if dot.empty:
    st.info(doc_kho.cau_giai_thich_rong(pham_vi, [] if len(tat_ca) == 0 else don_vi_chon, tu, den,
                                        co_du_lieu_trong_kho=bool(td['so_dot'])))
    st.stop()

k1, k2, k3 = st.tabs(['K1 · Tổng quan', 'K2 · Theo quy tắc', 'K3 · Cặp nghi trùng'])

# ------------------------------------------------------------------ K1 – Q2
with k1:
    st.subheader('Chỉ số mức độ sạch của từng đợt TRƯỚC và SAU làm sạch – đã đạt mức Tốt chưa?')
    moi = dot.iloc[-1]
    sau_moi = quy_tac[(quy_tac['batch_key'] == moi['batch_key']) & (quy_tac['measure_stage'] == 'SAU')]
    the = sau_moi.set_index('rule_code')
    c = st.columns(5)
    c[0].metric('Chỉ số SAU (đợt mới nhất)', diem(moi['sau']), moi['xep_loai'], delta_color='off',
                delta_arrow='off', border=True)
    c[1].metric('Chỉ số TRƯỚC làm sạch', diem(moi['truoc']),
                f"chênh lệch {float(moi['sau']) - float(moi['truoc']):+.2f} điểm".replace('.', ','),
                delta_color='off', delta_arrow='off', border=True)
    c[2].metric('Số hồ sơ được đánh giá', so(the.loc['DQ-01', 'total_records']), 'của đợt nạp mới nhất',
                delta_color='off', delta_arrow='off', border=True)
    c[3].metric('Thiếu số điện thoại', pt(1 - float(the.loc['DQ-01', 'pass_rate'])),
                f"{so(the.loc['DQ-01', 'fail_count'])} hồ sơ (DQ-01)", delta_color='off', delta_arrow='off', border=True)
    c[4].metric('Hồ sơ lặp có cặp Chờ xử lý', pt(1 - float(the.loc['DQ-05', 'pass_rate'])),
                f"{so(the.loc['DQ-05', 'fail_count'])} hồ sơ (DQ-05)", delta_color='off', delta_arrow='off', border=True)

    # Đường theo đợt nạp như wireframe K1 (BT1 Hình 5.1): SAU nét liền, TRƯỚC nét đứt; mốc 90 (Tốt) và 75 (Kém)
    nhan_dot = [f'Đợt #{r.batch_id}<br>{r.loaded_at:%d/%m/%Y}' for r in dot.itertuples()]
    fig = go.Figure([go.Scatter(name=doc_kho.GIAI_DOAN[gd], x=nhan_dot, y=dot[cot].astype(float),
                                mode='lines+markers+text', text=[diem(v) for v in dot[cot]], textposition=vi_tri,
                                line=dict(dash=net, width=3), marker=dict(size=10))
                     for gd, cot, net, vi_tri in (('SAU', 'sau', 'solid', 'top center'),
                                                  ('TRUOC', 'truoc', 'dash', 'bottom center'))])
    fig.add_hline(y=90, line_dash='dash', line_color='gray', annotation_text='90 · Tốt', annotation_position='top right')
    fig.add_hline(y=75, line_dash='dot', line_color='gray', annotation_text='75 · Kém',
                  annotation_position='bottom right')
    fig.update_layout(yaxis=dict(title='Chỉ số mức độ sạch (0–100)', range=[70, 101]), xaxis=dict(type='category'),
                      height=380, margin=dict(t=20, b=20), legend=dict(orientation='h', y=1.08))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Đọc biểu đồ:** đợt mới nhất (#{moi['batch_id']}) tăng từ {diem(moi['truoc'])} lên "
                f"{diem(moi['sau'])} điểm nhờ chuẩn hóa; xếp loại **{moi['xep_loai']}**. Phần còn thiếu để lên gần "
                f"100 nằm ở hồ sơ lặp chờ Gộp/Giữ riêng (DQ-05) và số điện thoại thiếu thật (DQ-01) – xem K2.")
    ghi_nguon('dwh.v_batch_score (fact_dq_check ⨝ dim_rule ⨝ dim_batch ⨝ dim_date), lần đo mới nhất mỗi đợt', td)
    st.dataframe(pd.DataFrame({
        'Đợt': dot['batch_id'], 'Ngày nạp': dot['loaded_at'].dt.strftime('%d/%m/%Y %H:%M'), 'Tệp': dot['file_name'],
        'Đơn vị nguồn': dot['source_unit'], 'TRƯỚC': dot['truoc'].map(diem), 'SAU': dot['sau'].map(diem),
        'Xếp loại': dot['xep_loai']}), hide_index=True, use_container_width=True)

# ------------------------------------------------------------------ K2 – Q3
with k2:
    st.subheader('Quy tắc nào kéo chỉ số mức độ sạch xuống nhiều nhất?')
    a, b = st.columns(2)
    nhan = {r.batch_key: f'Đợt #{r.batch_id} · {r.loaded_at:%d/%m/%Y}' for r in dot.itertuples()}
    bk = a.selectbox('Đợt nạp', list(nhan)[::-1], format_func=nhan.get)
    gd = b.radio('Giai đoạn đo', ['SAU', 'TRUOC'], format_func=doc_kho.GIAI_DOAN.get, horizontal=True)
    q = quy_tac[(quy_tac['batch_key'] == bk) & (quy_tac['measure_stage'] == gd)].sort_values('lost_points')
    if q.empty:
        st.info('Đợt này chưa có lần đo ở giai đoạn đã chọn. Chạy lại luồng chính cho đợt này hoặc chọn giai đoạn khác.')
    else:
        nhan_qt = [f'{r.rule_code} · {r.rule_name}' for r in q.itertuples()]
        fig = go.Figure()
        fig.add_bar(y=nhan_qt, x=(q['pass_rate'].astype(float) * 100), orientation='h', name='Tỉ lệ đạt',
                    marker_color=['#2e7d32' if ok else '#c62828' for ok in q['is_pass']],
                    text=[f'{pt(r.pass_rate)} · mất {diem(r.lost_points)} điểm' for r in q.itertuples()],
                    textposition='inside', insidetextanchor='start')
        fig.add_scatter(y=nhan_qt, x=q['pass_threshold'].astype(float), mode='markers', name='Ngưỡng đạt của quy tắc',
                        marker=dict(symbol='line-ns', size=26, line=dict(width=3, color='black')))
        fig.update_layout(xaxis=dict(title='Tỉ lệ đạt (%) – vạch đen là ngưỡng đạt', range=[0, 101]), height=380,
                          margin=dict(t=20, b=20), legend=dict(orientation='h', y=1.08))
        st.plotly_chart(fig, use_container_width=True)
        top = q.iloc[-1]
        tong = float(q['lost_points'].sum())
        st.markdown(f"**Đọc biểu đồ:** {top['rule_code']} ({top['rule_name'].lower()}) làm mất nhiều điểm nhất "
                    f"(**{diem(top['lost_points'])}** trên tổng {diem(tong)} điểm bị mất → chỉ số "
                    f"{diem(100 - tong)}). Thanh đỏ là quy tắc chưa đạt ngưỡng.")
        ghi_nguon('dwh.v_rule_rate (fact_dq_check ⨝ dim_rule – trọng số, ngưỡng của phiên bản đang hiệu lực lúc đo)', td)
        st.dataframe(pd.DataFrame({
            'Quy tắc': q['rule_code'], 'Loại': q['rule_type'], 'Số kiểm': q['total_records'].map(so),
            'Số đạt': q['pass_count'].map(so), 'Tỉ lệ đạt': q['pass_rate'].map(pt),
            'Ngưỡng': q['pass_threshold'].map(lambda x: f'≥ {float(x):g}%'), 'Trọng số': q['weight'].map(lambda x: diem(x)),
            'Điểm bị mất': q['lost_points'].map(diem), 'Đạt': q['is_pass'].map({True: '✓', False: '✗'})}
        ).iloc[::-1], hide_index=True, use_container_width=True)

# ------------------------------------------------------------------ K3 – Q4, Q5
with k3:
    st.subheader('Bao nhiêu cặp nghi trùng còn chờ xử lý, và điểm tương đồng phân bố thế nào quanh ngưỡng?')
    if cap.empty:
        st.info('Các đợt đã chọn chưa có cặp nghi trùng nào. Nếu vừa nạp tệp, kiểm tra bước [5/5] match của luồng '
                'chính đã chạy (không dùng --khong-phat-hien-cap).')
    else:
        tong = int(cap['so_cap'].sum())
        theo_tt = cap.groupby('status')['so_cap'].sum()
        da_xu_ly = int(theo_tt.get('MERGED', 0) + theo_tt.get('KEEP_SEPARATE', 0))
        c = st.columns(5)
        for o, (nhan_the, gia_tri) in zip(c, [('Tổng cặp nghi trùng', so(tong)),
                                              ('Chờ xử lý', so(theo_tt.get('PENDING', 0))),
                                              ('Gộp', so(theo_tt.get('MERGED', 0))),
                                              ('Giữ riêng', so(theo_tt.get('KEEP_SEPARATE', 0))),
                                              ('Tỉ lệ đã xử lý', pt(da_xu_ly / tong))]):
            o.metric(nhan_the, gia_tri, border=True)
        bang = (cap.groupby(['khoang_diem', 'trang_thai'])['so_cap'].sum().unstack(fill_value=0)
                .reindex(doc_kho.KHOANG_DIEM, fill_value=0))
        fig = go.Figure([go.Bar(name=tt, x=bang.index, y=bang[tt], text=bang[tt].map(so), textposition='outside')
                         for tt in bang.columns])
        nguong = float(cau_hinh['nguong_fuzzy'])
        fig.add_vline(x=0.5, line_dash='dash', annotation_text=f'ngưỡng tạo cặp FUZZY = {nguong:g} (QL7-02)',
                      annotation_position='top right')
        fig.update_layout(barmode='stack', xaxis_title='Khoảng điểm tương đồng',
                          yaxis_title='Số cặp', height=360, margin=dict(t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
        theo_loai = cap.groupby('match_type')['so_cap'].sum()
        st.markdown(f"**Đọc biểu đồ:** {so(theo_tt.get('PENDING', 0))}/{so(tong)} cặp còn chờ Nhân viên Marketing "
                    f"quyết định (UC5 – Sprint 3). EXACT_PHONE {so(theo_loai.get('EXACT_PHONE', 0))} cặp (cùng số), "
                    f"FUZZY {so(theo_loai.get('FUZZY', 0))} cặp (khác số, điểm ≥ {nguong:g}). Cặp EXACT_PHONE có điểm "
                    f"< 85 là cùng số nhưng họ tên khác xa – nên xem kỹ trước khi Gộp (QL7-01).")
        ghi_nguon('dwh.fact_dup_pair ⨝ dim_batch (điểm chia khoảng khi truy vấn, không lưu)', td)
