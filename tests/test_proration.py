"""proration 모듈 테스트 (코드와 함께 AI 가 생성)."""
from datetime import date

import pytest

from billing.proration import Coupon, calculate_charge


def test_full_month():
    assert calculate_charge(10_000, date(2026, 9, 1), None, 2026, 9) == 10_000


def test_half_month():
    assert calculate_charge(10_000, date(2026, 9, 16), None, 2026, 9) == 5_000


def test_fixed_coupon():
    coupon = Coupon(kind="fixed", value=1_000)
    assert calculate_charge(10_000, date(2026, 9, 1), None, 2026, 9, coupon) == 9_000


def test_percent_coupon():
    coupon = Coupon(kind="percent", value=10)
    assert calculate_charge(10_000, date(2026, 9, 1), None, 2026, 9, coupon) == 9_000


def test_percent_coupon_with_cap():
    coupon = Coupon(kind="percent", value=50, max_discount=3_000)
    assert calculate_charge(10_000, date(2026, 9, 1), None, 2026, 9, coupon) == 7_000


def test_end_before_start_raises():
    with pytest.raises(ValueError):
        calculate_charge(10_000, date(2026, 9, 10), date(2026, 9, 9), 2026, 9)


def test_not_started_yet():
    assert calculate_charge(10_000, date(2026, 10, 5), None, 2026, 9) == 0
