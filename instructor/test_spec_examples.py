"""명세 4절 예시 표를 그대로 옮긴 테스트 (강사용 정답).

코드를 보지 않고 명세만 보고 만든다. 기대값은 명세에서 온다.
"""
from datetime import date

import pytest

from billing.proration import Coupon, calculate_charge

D = date
FIXED_5000 = Coupon(kind="fixed", value=5_000)
PERCENT_10 = Coupon(kind="percent", value=10)

SPEC_EXAMPLES = [
    # (번호, 월 요금, 시작일, 종료일, 청구 연, 청구 월, 쿠폰, 기대값)
    (1, 10_000, D(2026, 9, 1), None, 2026, 9, None, 10_000),
    (2, 10_000, D(2026, 10, 1), None, 2026, 10, None, 10_000),
    (3, 10_000, D(2028, 2, 1), None, 2028, 2, None, 10_000),
    (4, 10_000, D(2026, 8, 20), None, 2026, 9, None, 10_000),
    (5, 10_000, D(2026, 7, 1), D(2026, 8, 10), 2026, 9, None, 0),
    (6, 10_000, D(2026, 10, 31), None, 2026, 10, None, 322),
    (7, 10_000, D(2026, 9, 16), D(2026, 9, 20), 2026, 9, None, 1_666),
    (8, 3_000, D(2026, 9, 21), None, 2026, 9, FIXED_5000, 0),
    (9, 10_000, D(2026, 9, 1), D(2026, 9, 10), 2026, 9, PERCENT_10, 3_000),
]


@pytest.mark.parametrize(
    "no, price, start, end, year, month, coupon, expected",
    SPEC_EXAMPLES,
    ids=[f"spec-{row[0]}" for row in SPEC_EXAMPLES],
)
def test_spec_example(no, price, start, end, year, month, coupon, expected):
    assert calculate_charge(price, start, end, year, month, coupon) == expected


def test_spec_10_end_before_start_is_error():
    with pytest.raises(ValueError):
        calculate_charge(10_000, D(2026, 9, 10), D(2026, 9, 9), 2026, 9)
