"""Tài liệu kỹ thuật mô tả đúng hệ thống THẬT (BT3, tiêu chí C9): từ điển dữ liệu có đủ mọi cột mà pipeline tạo ra,
Deployment Guide và docker-compose.yml không nhắc biến nào mà .env.example không có (và ngược lại)."""
import re

import pytest
from sqlalchemy import text

from src import db

GOC = db.GOC
TU_DIEN = GOC / 'docs' / 'data-dictionary.md'
GUIDE = GOC / 'docs' / 'deployment-guide.md'


def _bien_env_example() -> set[str]:
    return set(re.findall(r'^([A-Z][A-Z0-9_]*)=', (GOC / '.env.example').read_text(encoding='utf-8'), re.M))


def _cot_trong_tu_dien() -> set[tuple[str, str]]:
    cot, bang = set(), None
    for dong in TU_DIEN.read_text(encoding='utf-8').splitlines():
        m = re.match(r'### `([a-z_]+\.[a-z_]+)`', dong)
        if m:
            bang = m.group(1)
        m = re.match(r'\| `([a-z_]+)` \|', dong)
        if m and bang:
            cot.add((bang, m.group(1)))
    return cot


def test_tu_dien_du_lieu_co_du_moi_cot_cua_moi_bang_dich(csdl_test):
    """Mọi cột của mọi bảng và view trong schema ops, dwh có một dòng trong docs/data-dictionary.md – và không có dòng
    nào mô tả cột không tồn tại."""
    engine, _, _ = csdl_test
    with engine.begin() as conn:
        db.khoi_tao_csdl(conn)
        that = {(f'{s}.{t}', c) for s, t, c in conn.execute(text(
            "SELECT table_schema, table_name, column_name FROM information_schema.columns "
            "WHERE table_schema IN ('ops', 'dwh')"))}
    tu_dien = _cot_trong_tu_dien()
    assert that - tu_dien == set(), 'cột có trong CSDL nhưng thiếu trong từ điển dữ liệu'
    assert tu_dien - that == set(), 'từ điển dữ liệu mô tả cột không có trong CSDL'


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
