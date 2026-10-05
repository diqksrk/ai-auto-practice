import { test, expect } from '@playwright/test';

// 실습③-2 정답 예시: 같은 명세 예시를 화면이 아니라 API 로 끝까지 확인한다.
// 브라우저를 띄우지 않고 배포된 서버(여기서는 web/app.py)의 POST /api/charge 를 직접 부른다.
// 화면에서는 뺐던 '오류가 나야 하는 예시'(예시 10)도 API 로는 확인할 수 있다.
// 사용법: 이 파일을 e2e-ts/tests/ 로 복사 → cd e2e-ts → npx playwright test api-examples

type ChargeRequest = {
  price: number;
  start: string;
  end: string | null;
  month: string;
  coupon_kind: 'fixed' | 'percent' | null;
  coupon_value: number;
};

const charge = (overrides: Partial<ChargeRequest>): ChargeRequest => ({
  price: 10000,
  start: '2026-09-01',
  end: null,
  month: '2026-09',
  coupon_kind: null,
  coupon_value: 0,
  ...overrides,
});

test('API 명세 예시 8: 쿠폰이 요금보다 커도 0원', async ({ request }) => {
  const res = await request.post('/api/charge', {
    data: charge({ price: 3000, start: '2026-09-21', coupon_kind: 'fixed', coupon_value: 5000 }),
  });
  expect(res.status()).toBe(200);
  expect(await res.json()).toEqual({ amount: 0 });
});

test('API 명세 예시 10: 종료일이 시작일보다 앞서면 400 과 이유', async ({ request }) => {
  const res = await request.post('/api/charge', {
    data: charge({ start: '2026-09-10', end: '2026-09-09' }),
  });
  expect(res.status()).toBe(400);
  const body = await res.json();
  // 문장은 바뀔 수 있으니 통째로 비교하지 않는다 — '오류가 있다'와 '이유가 글자로 온다'만 약속으로 본다
  expect(typeof body.error).toBe('string');
  expect(body.error.length).toBeGreaterThan(0);
});
