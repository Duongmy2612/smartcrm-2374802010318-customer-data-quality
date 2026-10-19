"""② merge_service.py – FR-05, FR-06, FR-11 (UC4, UC5).  Trạng thái: Sprint 3 (buổi 11 – 12).

Hợp đồng (đặc tả UC5, docs/srs.md mục 3.3):
    danh_sach_cap : cặp sắp theo score giảm dần, lọc theo trạng thái và khoảng điểm; số điện thoại che
                    dạng 090****567 với vai trò không phải Quản lý (QT-15).
    gop / giu_rieng: khóa cặp, kiểm tra còn PENDING (8a), trong MỘT giao dịch cập nhật customer_clean
                    (is_active, merged_into – không xóa vật lý, QT-13), dup_candidate (decided_by,
                    decided_at, note – NFR-08); lỗi CSDL → ROLLBACK (9a); sau đó gọi dq_evaluate đo lại.
"""


def gop(conn, pair_id: int, survivor_stg_id: int, nguoi: str, ly_do: str | None = None) -> None:
    """UC5 luồng chính (bước 8 – 9): Gộp cặp, giữ hồ sơ gốc survivor_stg_id."""
    raise NotImplementedError('merge_service.py thuộc Sprint 3')


def giu_rieng(conn, pair_id: int, nguoi: str, ly_do: str | None = None) -> None:
    """UC5 luồng 3a: Giữ riêng; cặp không được đề xuất lại (QL7-05)."""
    raise NotImplementedError('merge_service.py thuộc Sprint 3')
