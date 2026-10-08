import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000/');
    await page.getByRole('spinbutton', { name: '월 요금(원)' }).click();
    await page.getByRole('spinbutton', { name: '월 요금(원)' }).fill('3000');
    await page.locator('html').click();
    await page.getByRole('textbox', { name: '이용 시작일' }).fill('2026-09-21');
    await page.getByRole('textbox', { name: '청구월' }).click();
    await page.getByRole('textbox', { name: '청구월' }).click();
    await page.getByRole('textbox', { name: '청구월' }).click();
    await page.getByRole('textbox', { name: '청구월' }).click();
    await page.getByRole('textbox', { name: '청구월' }).click();
    await page.getByRole('textbox', { name: '청구월' }).click();
    await page.getByRole('textbox', { name: '청구월' }).click();
    await page.getByRole('textbox', { name: '청구월' }).press('Tab');
    await page.getByRole('textbox', { name: '청구월' }).fill('2026-09');
    await page.getByLabel('쿠폰 없음 정액(원) 정률(%)').selectOption('fixed');
    await page.getByRole('spinbutton', { name: '쿠폰 값' }).click();
    await page.getByRole('spinbutton', { name: '쿠폰 값' }).fill('5000');
    await page.getByRole('button', { name: '계산' }).click();
    await expect(page.locator('#result')).toContainText('청구 금액: 0원');
});