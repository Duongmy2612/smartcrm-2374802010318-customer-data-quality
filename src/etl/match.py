"""② match.py – FR-04 (UC3): phát hiện cặp nghi trùng.  Trạng thái: Sprint 2 (buổi 9 – 10), xem TD-04.

Hợp đồng dữ liệu (đã chốt ở BT1, docs/data-requirements.md mục 7):
    Đầu vào : ops.stg_customer của một đợt, cột phone_norm (do transform.py ghi); hồ sơ không có số hợp lệ
              không tham gia (QL7-04).
    Xử lý   : name_key = họ tên bỏ dấu, chữ thường, bỏ khoảng trắng thừa; blocking cùng 5 số đầu hoặc
              5 số cuối của phone_norm; điểm = 0,6 × fuzz.ratio(số) + 0,4 × fuzz.token_sort_ratio(name_key)
              (QL7-03); cùng số → EXACT_PHONE (k hồ sơ → k − 1 cặp ghép với hồ sơ nạp sớm nhất); khác số
              và điểm ≥ nguong_fuzzy (configs/config.yaml) → FUZZY; bỏ cặp đã KEEP_SEPARATE (QL7-05).
    Đầu ra  : ops.dup_candidate (status PENDING); stg_customer.name_key.
    Đo      : NFR-01 phần 2 (≤ 120 giây trên mẫu 8.000 dòng), NFR-03 (precision ≥ 85%, recall ≥ 80%
              trên 300 cặp gán nhãn tay).
"""


def phat_hien_cap(conn, batch_id: int, nguong: float = 85) -> int:
    """Ghi các cặp nghi trùng của một đợt vào ops.dup_candidate; trả về số cặp mới."""
    raise NotImplementedError('match.py thuộc Sprint 2 – xem README mục 6 và TD-04')
