"""E2E 테스트: 사용자가 화면에서 입력하고, 화면에 보이는 금액을 확인한다.

실행 (선택 실습):
    pip install playwright
    python -m playwright install chromium
    python -m pytest e2e
"""
import threading

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

from web.app import make_server  # noqa: E402


@pytest.fixture(scope="module")
def base_url():
    server = make_server(port=0)  # 빈 포트 아무거나
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser, base_url):
    page = browser.new_page()
    page.goto(base_url)
    yield page
    page.close()


def test_full_month_in_31_day_month_is_monthly_price(page):
    """명세 예시 2: 31일 달을 다 써도 월 요금 그대로."""
    page.fill("#price", "10000")
    page.fill("#start", "2026-10-01")
    page.fill("#month", "2026-10")
    page.click("#calc")
    sync_api.expect(page.get_by_role("status")).to_have_text("청구 금액: 10,000원")


def test_big_coupon_never_negative(page):
    """명세 예시 8: 쿠폰이 금액보다 커도 0원."""
    page.fill("#price", "3000")
    page.fill("#start", "2026-09-21")
    page.fill("#month", "2026-09")
    page.select_option("#coupon-kind", "fixed")
    page.fill("#coupon-value", "5000")
    page.click("#calc")
    sync_api.expect(page.get_by_role("status")).to_have_text("청구 금액: 0원")
