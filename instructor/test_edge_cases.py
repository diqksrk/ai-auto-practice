"""(보너스) 정답 예시: AI 에게 명세만 주고 뽑게 한 경계 사례 (강사용).

뮤테이션 도구가 "살아남았다" 고 알려준 줄을 겨냥해 추가한 것들이다.
"""
from datetime import date

import pytest

from billing.proration import Coupon, calculate_charge

D = date


def test_same_day_start_and_end_is_one_day():
    # R1 양끝 포함: 하루만 써도 1일. 10,000 × 1 ÷ 30 = 333.3 → 333
    assert calculate_charge(10_000, D(2026, 9, 5), D(2026, 9, 5), 2026, 9) == 333


def test_free_plan_is_zero_not_error():
    # R6 은 "음수면 오류" — 0원 요금제는 정상 입력
    assert calculate_charge(0, D(2026, 9, 1), None, 2026, 9) == 0


def test_negative_price_is_error():
    with pytest.raises(ValueError):
        calculate_charge(-1, D(2026, 9, 1), None, 2026, 9)


def test_end_after_billing_month_counts_to_last_day():
    assert calculate_charge(10_000, D(2026, 9, 1), D(2026, 12, 31), 2026, 9) == 10_000


def test_fixed_coupon_equal_to_amount_is_zero():
    assert calculate_charge(10_000, D(2026, 9, 1), None, 2026, 9, Coupon("fixed", 10_000)) == 0


def test_percent_100_is_zero():
    assert calculate_charge(10_000, D(2026, 9, 1), None, 2026, 9, Coupon("percent", 100)) == 0


def test_percent_0_is_no_discount():
    assert calculate_charge(10_000, D(2026, 9, 1), None, 2026, 9, Coupon("percent", 0)) == 10_000


@pytest.mark.parametrize("bad_percent", [-1, 101])
def test_percent_out_of_range_is_error(bad_percent):
    with pytest.raises(ValueError):
        calculate_charge(10_000, D(2026, 9, 1), None, 2026, 9, Coupon("percent", bad_percent))


def test_percent_cap_exactly_equal():
    # 50% = 5,000 할인, 한도 5,000 → 그대로 5,000 할인
    coupon = Coupon("percent", 50, max_discount=5_000)
    assert calculate_charge(10_000, D(2026, 9, 1), None, 2026, 9, coupon) == 5_000
