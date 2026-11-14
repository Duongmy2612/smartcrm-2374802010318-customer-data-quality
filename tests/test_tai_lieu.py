"""Tài liệu kỹ thuật mô tả đúng hệ thống THẬT (BT3, tiêu chí C9): từ điển dữ liệu có đủ mọi cột mà pipeline tạo ra
(đúng kiểu, đúng NULL như \\d trong psql); Deployment Guide và docker-compose.yml không nhắc biến nào mà
.env.example không có (và ngược lại)."""
import re

import pytest
from sqlalchemy import text

from src import db

GOC = db.GOC
TU_DIEN = GOC / 'docs' / 'data-dictionary.md'
GUIDE = GOC / 'docs' / 'deployment-guide.md'


def _bien_env_example() -> set[str]:
    return set(re.findall(r'^([A-Z][A-Z0-9_]*)=', (GOC / '.env.example').read_text(encoding='utf-8'), re.M))


def _dong_tu_dien() -> dict[tuple[str, str], tuple[str, str]]:
    """(bảng, cột) → (cột Type, cột Null) của mỗi dòng trong docs/data-dictionary.md."""
    dong_td, bang = {}, None
    for dong in TU_DIEN.read_text(encoding='utf-8').splitlines():
        m = re.match(r'### `([a-z_]+\.[a-z_]+)`', dong)
        if m:
            bang = m.group(1)
        m = re.match(r'\| `([a-z_]+)` \|', dong)
        if m and bang:
            o = [x.strip() for x in dong.split('|')[1:-1]]
            dong_td[(bang, m.group(1))] = (o[1], o[4])
    return dong_td


def _kieu_nhu_tu_dien(kieu_pg: str) -> str:
    """format_type() của PostgreSQL (đúng chữ \\d in ra) → cách viết trong từ điển: character varying(50) →
    VARCHAR(50)."""
    for goc, viet in (('character varying', 'VARCHAR'), ('character', 'CHAR'),
                      ('timestamp without time zone', 'TIMESTAMP')):
        if kieu_pg.startswith(goc + '(') or kieu_pg == goc:
            return viet + kieu_pg[len(goc):]
    return kieu_pg.upper()


def test_tu_dien_du_lieu_co_du_moi_cot_cua_moi_bang_dich(csdl_test):
    """Mọi cột của mọi bảng và view trong schema ops, dwh có một dòng trong docs/data-dictionary.md – và không có dòng
    nào mô tả cột không tồn tại. Kiểu của mọi cột và NULL của mọi cột BẢNG khớp \\d trong psql (buổi 16: đối chiếu
    từ điển với \\d tên_bảng); cột của view thì PostgreSQL luôn báo có thể NULL nên chỉ so kiểu."""
    engine, _, _ = csdl_test
    with engine.begin() as conn:
        db.khoi_tao_csdl(conn)
        that = {(f'{s}.{t}', c): (_kieu_nhu_tu_dien(k), 'no' if khong_null else 'yes', loai)
                for s, t, c, k, khong_null, loai in conn.execute(text(
                    "SELECT n.nspname, c.relname, a.attname, format_type(a.atttypid, a.atttypmod), a.attnotnull, "
                    "c.relkind FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname IN ('ops', 'dwh') AND c.relkind IN ('r', 'v') AND a.attnum > 0 "
                    "AND NOT a.attisdropped"))}
    tu_dien = _dong_tu_dien()
    assert set(that) - set(tu_dien) == set(), 'cột có trong CSDL nhưng thiếu trong từ điển dữ liệu'
    assert set(tu_dien) - set(that) == set(), 'từ điển dữ liệu mô tả cột không có trong CSDL'
    sai_kieu = {k: (tu_dien[k][0], v[0]) for k, v in that.items() if tu_dien[k][0] != v[0]}
    assert sai_kieu == {}, 'kiểu trong từ điển khác \\d (từ điển, CSDL)'
    sai_null = {k: (tu_dien[k][1], v[1]) for k, v in that.items() if v[2] == 'r' and tu_dien[k][1] != v[1]}
    assert sai_null == {}, 'cột Null của bảng trong từ điển khác \\d (từ điển, CSDL)'


def test_guide_liet_ke_du_moi_bien_cua_env_example():
    """Deployment Guide mục 3: mỗi biến trong .env.example có một dòng trong bảng biến môi trường."""
    guide = GUIDE.read_text(encoding='utf-8')
    thieu = {b for b in _bien_env_example() if f'| `{b}` |' not in guide}
    assert thieu == set()


def test_docker_compose_chi_dung_bien_co_trong_env_example():
    """Mọi ${BIEN} trong docker-compose.yml đều có mẫu trong .env.example (người dựng chỉ cần cp .env.example .env)."""
    compose = (GOC / 'docker-compose.yml').read_text(encoding='utf-8')
    dung = set(re.findall(r'(?<!\$)\$\{([A-Z][A-Z0-9_]*)', compose))      # $${…} là biến của container, bỏ qua
    assert dung and dung - _bien_env_example() == set()
