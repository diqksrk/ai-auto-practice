"""구독 요금 일할 계산 모듈.

월 구독 요금을 이용 기간에 맞춰 일할 계산하고, 쿠폰 할인을 적용합니다.

사용 예:
    >>> from datetime import date
    >>> calculate_charge(10_000, date(2026, 9, 16), None, 2026, 9)
    5000
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional

DAYS_IN_MONTH = 30  # 월 기준 일수


@dataclass(frozen=True)
class Coupon:
    """할인 쿠폰.

    kind 가 "fixed" 이면 value 원을 할인하고,
    "percent" 이면 value % 를 할인합니다 (max_discount 가 있으면 그 금액까지만).
    """

    kind: Literal["fixed", "percent"]
    value: int
    max_discount: Optional[int] = None


def usage_days(start: date, end: Optional[date], year: int, month: int) -> int:
    """청구월 안에서 서비스를 이용한 일수를 반환합니다."""
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    period_end = end if end is not None else last_day
    if period_end > last_day:
        period_end = last_day
    if start > period_end:
        return 0
    return (period_end - start).days + 1


def prorate(monthly_price: int, days: int, year: int, month: int) -> int:
    """월 요금을 이용 일수만큼 일할 계산합니다."""
    amount = monthly_price * days / DAYS_IN_MONTH
    return round(amount)


def apply_coupon(amount: int, coupon: Optional[Coupon]) -> int:
    """일할 계산된 금액에 쿠폰 할인을 적용합니다."""
    if coupon is None:
        return amount
    if coupon.kind == "fixed":
        return amount - coupon.value
    if coupon.value < 0 or coupon.value > 100:
        raise ValueError("정률 쿠폰은 0~100% 사이여야 합니다")
    discount = amount * coupon.value // 100
    if coupon.max_discount is not None:
        discount = min(discount, coupon.max_discount)
    return amount - discount


def calculate_charge(
    monthly_price: int,
    start: date,
    end: Optional[date],
    year: int,
    month: int,
    coupon: Optional[Coupon] = None,
) -> int:
    """청구월(year, month)에 청구할 금액을 계산합니다.

    Args:
        monthly_price: 월 구독 요금 (원)
        start: 이용 시작일
        end: 이용 종료일 (해지하지 않았으면 None)
        year, month: 청구월
        coupon: 적용할 쿠폰 (없으면 None)
    """
    if monthly_price < 0:
        raise ValueError("월 요금은 0 이상이어야 합니다")
    if end is not None and end < start:
        raise ValueError("종료일이 시작일보다 앞설 수 없습니다")
    days = usage_days(start, end, year, month)
    amount = prorate(monthly_price, days, year, month)
    return apply_coupon(amount, coupon)
