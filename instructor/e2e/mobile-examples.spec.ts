import { test, expect } from '@playwright/test';
import { ChargePage } from '../pages/charge-page';

// 실습③-3 정답: 같은 명세를 폰 화면으로 (e2e-ts/mobile/ 에 복사해서 돈다).
// 실행: cd e2e-ts → npx playwright test -c playwright.mobile.config.ts
// 기기는 설정 파일의 projects(Pixel 7 · iPhone 15) — 테스트 하나가 기기마다 한 번씩 돈다.

test('명세 예시 8 (폰): 쿠폰이 요금보다 커도 0원', async ({ page }) => {
  const charge = new ChargePage(page);
  await charge.open();
  await charge.fill({ price: 3000, start: '2026-09-21', month: '2026-09', coupon: { kind: 'fixed', value: 5000 } });
  await charge.calculate();
  await charge.expectCharge('0원');
});

test('폰 AC-1: 화면을 폰 폭에 맞춰 그린다 (통째로 줄여 보이지 않는다)', async ({ page }) => {
  await page.goto('/');
  const layoutWidth = await page.evaluate(() => document.documentElement.clientWidth);
  expect(layoutWidth).toBe(page.viewportSize()!.width); // 다르면 폰이 데스크톱 폭(980px)으로 그린 뒤 줄여 보여 준다
});

test('폰 AC-2: 계산 버튼은 엄지로 누를 크기 (높이 44px 이상)', async ({ page }) => {
  await page.goto('/');
  const box = await page.getByRole('button', { name: '계산' }).boundingBox();
  expect(box!.height).toBeGreaterThanOrEqual(44); // Apple 권장 최소 44pt · Android(Material) 48dp
});
