import { test } from '@playwright/test';
import { ChargePage, type ChargeInput } from '../pages/charge-page';

// 실습③ 정답 예시: 명세 4절 예시 중 "사용자가 화면에서 겪는" 핵심 흐름만 E2E 로.
// (나머지 경계 사례는 단위 테스트가 맡는다 — E2E 는 적게)
// 사용법: 이 파일을 e2e-ts/tests/ 로 복사한 뒤 import 경로를 '../pages/charge-page' 그대로 둔다.
const cases: { no: number; title: string; input: ChargeInput; expected: string }[] = [
  { no: 2, title: '31일 달을 다 써도 월 요금 그대로', input: { price: 10000, start: '2026-10-01', month: '2026-10' }, expected: '10,000원' },
  { no: 4, title: '지난달부터 쓰던 고객도 한 달 요금', input: { price: 10000, start: '2026-08-20', month: '2026-09' }, expected: '10,000원' },
  {
    no: 8,
    title: '쿠폰이 요금보다 커도 0원',
    input: { price: 3000, start: '2026-09-21', month: '2026-09', coupon: { kind: 'fixed', value: 5000 } },
    expected: '0원',
  },
];

for (const c of cases) {
  test(`명세 예시 ${c.no}: ${c.title}`, async ({ page }) => {
    const charge = new ChargePage(page);
    await charge.open();
    await charge.fill(c.input);
    await charge.calculate();
    await charge.expectCharge(c.expected);
  });
}
