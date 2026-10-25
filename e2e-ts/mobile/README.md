# 폰 화면 테스트 (실습③-3)

실습③-3 에서 `instructor/e2e/mobile-examples.spec.ts` 를 여기에 복사합니다. 처음에는 이 안내 파일만 있습니다.

```bash
cp instructor/e2e/mobile-examples.spec.ts e2e-ts/mobile/     # 키트 맨 위 폴더에서
```

실행 (`e2e-ts` 에서)
```bash
npx playwright test -c playwright.mobile.config.ts     # Pixel 7 · iPhone 15 흉내, 테스트 하나가 기기마다 한 번씩
```

기본 실행 `npx playwright test` 에는 섞이지 않습니다. `-c playwright.mobile.config.ts` 를 줄 때만 이 폴더를 돕니다.
