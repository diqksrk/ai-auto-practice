import { defineConfig } from '@playwright/test';

// 파이썬이 `python` 이 아니라 `py` 로 잡히는 PC 는 PYTHON=py 로 실행하세요.
const python = process.env.PYTHON ?? 'python';

export default defineConfig({
  testDir: './tests',
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'on', // 실습용: 항상 기록. 실무에서는 'on-first-retry' 를 많이 씁니다.
    screenshot: 'only-on-failure',
    actionTimeout: 5_000, // 칸을 못 찾으면 5초 만에 실패 (실습 시간 절약)
  },
  // 테스트 전에 요금 계산 화면(web/app.py)을 자동으로 띄웁니다.
  webServer: {
    command: `${python} ../web/app.py`,
    url: 'http://127.0.0.1:8000',
    // 이미 떠 있는 앱을 재사용하지 않는다: 코드를 고친 뒤에도 옛 코드로 돌던 서버가 테스트되는 일을 막는다.
    // 'already used' 오류가 나면 따로 띄운 python web/app.py 를 Ctrl+C 로 끄고 다시 실행 (= 분류상 '환경').
    reuseExistingServer: false,
  },
});
