import { defineConfig, devices } from '@playwright/test';
import base from './playwright.config';

// 실습③-3: 같은 명세를 폰 화면으로.
// 크롬 개발자 도구의 '기기 모드'(F12 → Ctrl+Shift+M)와 같은 기기 흉내를 Playwright 가 자동으로 한다
// — 화면 크기 · 화면 배율 · 터치 · 폰 브라우저 정보. 설치할 것은 없다(이미 받은 크로미움을 그대로 쓴다).
// 기본 실행(npx playwright test)에는 섞이지 않는다: 이 설정을 -c 로 줄 때만 mobile/ 폴더를 돈다.
export default defineConfig({
  ...base,
  testDir: './mobile',
  projects: [
    { name: 'Pixel 7', use: { ...devices['Pixel 7'] } },
    // iPhone 은 원래 사파리 엔진(webkit)으로 흉내 낸다. 브라우저를 더 받지 않으려고 크로미움으로 — 크롬 기기 모드와 같다.
    { name: 'iPhone 15', use: { ...devices['iPhone 15'], defaultBrowserType: 'chromium' } },
  ],
});
