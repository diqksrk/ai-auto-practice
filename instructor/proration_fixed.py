"""구독 요금 일할 계산 모듈 (강사용 수정본 — 명세 R1~R6 반영).

실습③ 이 끝난 뒤 참가자 결과와 비교합니다.
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional


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
    """R1: 청구월 안에서 서비스를 이용한 일수 (시작일·종료일 모두 포함)."""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    period_start = start
    if period_start < first_day:
        period_start = first_day

    period_end = last_day
    if end is not None and end < last_day:
        period_end = end

    if period_start > period_end:
        return 0
    return (period_end - period_start).days + 1


def prorate(monthly_price: int, days: int, year: int, month: int) -> int:
    """R2·R3: 월 요금 × 이용일수 ÷ 청구월 실제 일수, 원 미만 버림 (정수 연산)."""
    days_in_month = calendar.monthrange(year, month)[1]
    return monthly_price * days // days_in_month


def apply_coupon(amount: int, coupon: Optional[Coupon]) -> int:
    """R4·R5: 일할 금액에 쿠폰 적용, 결과는 0원 미만이 되지 않는다."""
    if coupon is None:
        return amount

    if coupon.kind == "fixed":
        discount = coupon.value
    else:
        if coupon.value < 0 or coupon.value > 100:
            raise ValueError("정률 쿠폰은 0~100% 사이여야 합니다")
        discount = amount * coupon.value // 100
        if coupon.max_discount is not None:
            discount = min(discount, coupon.max_discount)

    charged = amount - discount
    if charged < 0:
        charged = 0
    return charged


def calculate_charge(
    monthly_price: int,
    start: date,
    end: Optional[date],
    year: int,
    month: int,
    coupon: Optional[Coupon] = None,
) -> int:
    """청구월(year, month)에 청구할 금액을 계산합니다."""
    if monthly_price < 0:
        raise ValueError("월 요금은 0 이상이어야 합니다")
    if end is not None and end < start:
        raise ValueError("종료일이 시작일보다 앞설 수 없습니다")
    days = usage_days(start, end, year, month)
    amount = prorate(monthly_price, days, year, month)
    return apply_coupon(amount, coupon)
