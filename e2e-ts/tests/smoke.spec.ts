import { test } from '@playwright/test';
import { ChargePage } from '../pages/charge-page';

// AI 가 코드와 함께 만든 화면 테스트 (9월 = 30일 달 하나만 확인한다)
test('9월 한 달을 다 쓰면 10,000원', async ({ page }) => {
  const charge = new ChargePage(page);
  await charge.open();
  await charge.fill({ price: 10000, start: '2026-09-01', month: '2026-09' });
  await charge.calculate();
  await charge.expectCharge('10,000원');
});
