"""② load_dwh.py – FR-09: nạp kho dữ liệu schema dwh.  Trạng thái: Sprint 2 (buổi 9 – 10), xem TD-04.

Hợp đồng dữ liệu (đã chốt ở BT1, docs/data-requirements.md mục 5.2):
    Chạy sau mỗi lần phát hiện cặp (UC3), mỗi lần đo (UC7) và mỗi lần lưu cấu hình quy tắc (UC6).
    dim_rule      : SCD loại 2 – so ops.dq_rule với phiên bản hiện hành theo rule_code; khác thì đóng
                    phiên bản cũ (valid_to = updated_at) và thêm phiên bản mới.
    dim_batch     : thêm đợt chưa có (theo batch_id); không cập nhật (SCD loại 0). dim_date sinh sẵn.
    fact_dq_check : thêm dòng ops.dq_result chưa có (theo result_id – nạp lại không sinh trùng, NFR-05);
                    rule_key = phiên bản có valid_from ≤ measured_at < valid_to.
    fact_dup_pair : thêm cặp mới; cặp đã có chỉ cập nhật status, decided_date_key.
"""


def nap_kho(conn) -> dict:
    """Nạp dim/fact từ schema ops sang dwh; trả về số dòng thêm/cập nhật theo bảng."""
    raise NotImplementedError('load_dwh.py thuộc Sprint 2 – xem README mục 6 và TD-04')
