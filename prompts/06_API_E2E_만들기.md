# 실습③-2 같은 명세를 API 로 끝까지 확인하기 (Playwright request) — 3분

**기본 (3분): 복사 → 실행 → 읽기.** 키트 루트에서
```bash
cp instructor/e2e/api-examples.spec.ts e2e-ts/tests/
cd e2e-ts
npx playwright test api-examples      # 브라우저 없이 1~2초
cd ..
git add e2e-ts/tests/api-examples.spec.ts
git commit -m "API 테스트"
```
실습③ 에서 코드를 고쳤다면 `2 passed` 가 정상입니다. 파일을 열어 화면 테스트와 무엇이 다른지 보세요 — `page` 대신 `request.post`, 화면 글자 대신 상태 코드와 JSON. 고치기 전 코드라면 예시 8 이 `amount: -4000` 으로 빨간불입니다.

**시간이 남으면: AI 에게 직접 만들게 해 보기.** 아래가 그 카드입니다.

화면이 없는 서버, 또는 앱 뒤의 서버는 **API 로 E2E** 를 합니다. 브라우저를 띄우지 않고, 앱이 부르는 API 를 똑같이 불러서 결과를 봅니다.
이 키트의 화면도 계산할 때 `POST /api/charge` 를 부릅니다(`web/app.py`).

**새 대화**에서 시작하세요. 명세와 아래 API 약속만 줍니다.
붙여 넣기 전에, 내 명세 표에 '종료일 < 시작일' 행이 없으면 **직접** 추가하세요(기대값은 사람이 정합니다): `10,000 · 2026-09-10 ~ 2026-09-09 · 2026-09 · 쿠폰 없음 → 오류 · R6` (강사 정답 표의 예시 10).

```
아래 명세의 "4. 예시" 중 두 개를 Playwright 의 request 로 API 테스트로 만들어 줘. 브라우저(page)는 쓰지 마.

- 예시 8 (쿠폰이 요금보다 큰 경우) — 화면 E2E 에서 본 그 예시를 API 로
- 종료일이 시작일보다 앞서는 경우 → 오류. 화면 E2E 에서는 뺀 '오류가 나야 하는' 예시
- 파일: e2e-ts/tests/api-examples.spec.ts
- API 약속:
    POST /api/charge   (baseURL 은 설정에 있음)
    요청 JSON: { "price": 숫자, "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" 또는 null,
                 "month": "YYYY-MM", "coupon_kind": "fixed" | "percent" | null, "coupon_value": 숫자 }
    성공: 200, { "amount": 숫자(원) }
    입력 오류: 400, { "error": "이유" }
- 기대값은 명세 표에서만 가져와. 오류 메시지 문장은 바뀔 수 있으니 통째로 비교하지 말고,
  상태 코드와 'error 가 비어 있지 않은 글자'만 확인해.
- src/, web/, instructor/ 는 읽지 마. 테스트 파일만 만들고 멈춰.

(여기에 specs/proration.md 붙여 넣기)
```

번호는 강사 정답 표 기준입니다. 내 명세의 번호와 달라도 '쿠폰 > 요금' · '종료일 < 시작일' 두 행이면 됩니다.

## 실행 (키트 루트에서)
```bash
git add e2e-ts/tests/api-examples.spec.ts
git commit -m "API 테스트"
cd e2e-ts
npx playwright test api-examples      # 브라우저 없이 1초 안팎
cd ..
```
실습③ 에서 코드를 고쳤다면 둘 다 초록이어야 정상입니다. 고치기 전 코드라면 예시 8 이 `amount: -4000` 으로 빨간불.


**실습④ 에서 다시 보세요.** 동료 PR 이 화면 문구를 바꾸면 화면 E2E 는 전부 '칸을 못 찾음'으로 막히지만, API 테스트는 문구와 상관없이 돌아서 예시 8 의 제품 버그를 처음부터 보여 줍니다. 층마다 테스트를 나누는 이유입니다.
