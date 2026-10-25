# 명세와 검증 실습 키트

강의 「AI 시대, 개발자가 알아야 할 명세와 검증」 실습용 저장소입니다. **처음부터 끝까지 따라 하는 실습 가이드는 [HANDS_ON.md](HANDS_ON.md)** 입니다.
구독 요금을 일할 계산하는 작은 웹 화면이 들어 있습니다. **AI 가 짠 코드이고, 테스트도 전부 통과합니다. 그런데 버그가 있습니다.**
오늘은 이 버그를 **명세**와 **화면 끝까지 확인하는 E2E 테스트(Playwright)** 로 잡습니다.

## 강의 전에 (Python · Node 가 있으면 10분) — 꼭 해 오세요

1. 설치: Python 3.10 이상, Node.js 20 이상 (LTS), git
   버전 확인(`python --version` · `node -v` · `git --version`)과 설치 방법(설치 파일 · winget · brew · nvm)은 [HANDS_ON.md 의 '강의 전에'](HANDS_ON.md#강의-전에-python--node-가-있으면-10분) 에 있습니다.
   git 을 처음 쓰면 이름과 메일도 한 번 정해 둡니다 (실습에서 커밋합니다).
   `git config --global user.name "내 이름"` · `git config --global user.email "내 메일"`
2. 저장소를 받고 두 가지를 실행합니다.
   ```bash
   git clone https://github.com/diqksrk/ai-auto-practice.git sdd-qa-lab
   cd sdd-qa-lab
   python -m pip install -r requirements.txt
   python -m pytest                    # → 7 passed

   cd e2e-ts
   npm install
   npx playwright install chromium     # 브라우저 내려받기 (약 300MB — 강의장 와이파이 말고 미리!)
   npx playwright test                 # → 1 passed
   ```
   `7 passed` 와 `1 passed` 가 나오면 준비 끝입니다.
   막히면 키트 루트에서 `python tools/check_setup.py` — 무엇이 빠졌고 무엇을 하면 되는지 한 번에 알려 줍니다.
   (파이썬이 `python` 이 아니라 `py`·`python3` 로 실행되는 PC 는 이 문서의 `python` 을 그 이름으로 바꿔 쓰세요.
   E2E 는 `PYTHON=py npx playwright test`, PowerShell 은 `$env:PYTHON="py"; npx playwright test`)
3. AI 도구 하나 — Claude Code, Cursor, GitHub Copilot, 웹 채팅 무엇이든 됩니다.

## 폴더

| 폴더 | 내용 |
|---|---|
| `src/billing/proration.py` | AI 가 짠 요금 계산 코드 (실습 대상) |
| `web/app.py` | 요금 계산 화면 (`python web/app.py` → http://127.0.0.1:8000) |
| `tests/` | AI 가 코드와 함께 짠 단위 테스트 7개 |
| `e2e-ts/` | **Playwright E2E** — `pages/` 화면 객체, `tests/` 화면 테스트, `mobile/` 폰 화면 테스트(보너스 — 3시간 강의에서는 안 함, `playwright.mobile.config.ts` 로만 돈다), `playwright.config.ts`, `package.json`(`npm run codegen` · `ui` · `report`) |
| `specs/` | 명세 템플릿(`TEMPLATE.md` 8칸 — 큰 기능이면 2절에 우선순위 P1 · P2, 4절 AC 줄 앞에 `[P1]`), 실습① 에서 채울 빈 명세(`proration.md`), 출시 점검 리스트 예시(`RELEASE_CHECKLIST.md`) |
| `prompts/` | 실습별 프롬프트 카드 (복사해서 쓰세요) |
| `tools/lab4_change.py` | 실습④: "동료의 PR" 을 적용/되돌리기 |
| `tools/mutate.py` | (보너스) 테스트가 버그를 잡는지 채점하는 뮤테이션 도구 |
| `AGENTS.md`, `CLAUDE.md` | AI 에게 주는 프로젝트 규칙 |
| `.claude/settings.json` | Claude Code 가 파일을 고칠 때마다 단위 테스트를 돌리는 설정 (pytest 가 깔린 파이썬을 `python` → `python3` → `py` 순서로 찾아 한 번 실행. 윈도우는 Git Bash 필요) |
| `.github/` | PR 에서 단위 테스트 + E2E 를 돌리는 CI, PR 템플릿(AC 이행 현황), 테스트 변경을 따로 승인받는 CODEOWNERS 예시 |
| `instructor/` | 막혔을 때 쓰는 정답. 먼저 보지 말고 막혔을 때만. [instructor/README.md](instructor/README.md) 는 강사 · 혼자 다시 해 보는 사람용 상세 따라 하기 (실제 출력 · AI 의 실제 답 · 정답) |
| `e2e/` | (선택) 같은 E2E 를 파이썬 Playwright 로 쓴 버전 |
| `maestro/` | (보너스) 같은 명세 예시 8 을 앱 테스트 도구 Maestro 로 — Java 17+ 와 Maestro 설치 필요, 파일 맨 위 설명 참고 |

## 실습 순서

| 실습 | 시간 | 하는 일 | 프롬프트 |
|---|---|---|---|
| ① 명세 쓰기 | 10분 | `specs/proration.md` 의 빈칸을 AI 인터뷰로 채운다 | `01_명세_인터뷰.md` |
| ② 눈으로 버그 찾기 | 3분 | `src/billing/proration.py` 를 읽고 버그를 찾는다 (AI 없이) | — |
| codegen 녹화 따라 하기 | 7분 | 앱을 켜고 클릭을 녹화 → 녹화한 기대값으로는 초록 → 명세 값(0원)으로 바꾸면 빨강 → 연습 파일 지우기 | — (HANDS_ON) |
| ③ 명세로 E2E 만들기 | 15분 | 명세 예시(8번 포함) → Playwright 테스트 → **커밋** → 빨간불 → 리포트·트레이스로 원인 보기 → AI 가 코드만 고친다 → **커밋** | `02_E2E_테스트_만들기.md`, `03_코드만_고치기.md` |
| ③-2 같은 명세를 API 로 | 3분 | 정답 API 테스트를 복사해 돌리고 읽는다 — 브라우저 없이 `POST /api/charge` 로 예시 8 + 오류 예시 10. 시간이 남으면 AI 로 직접 | `06_API_E2E_만들기.md` |
| ④ 동료 PR 이 E2E 를 깨뜨렸다 | 15분 | 동료 PR 적용 → 단위 테스트는 초록, E2E 는 빨강 → AI 에게 "분류부터" (고칠 때마다 다시 분류). API 테스트를 만들었다면 제품 버그가 API 쪽에서 먼저 보인다 | `04_E2E_실패분류.md` |
| ⑤ 우리 팀 핵심 흐름 | 15분 | 팀 서비스의 핵심 흐름 하나를 AC 5개로 + 어디서 볼지(화면 · API · 단위)를 명세 6절 '테스트 계획' 에 + 나눠 보기 5분. **앱 팀은 Maestro 흐름 초안 + 화면 id 계약 표** | `specs/TEMPLATE.md`, 앱: `07_앱_흐름_초안.md` |

모든 실습의 순서 · 명령 · 실제 출력은 [HANDS_ON.md](HANDS_ON.md) 에 있습니다. 강의에서 결과만 화면으로 보여 주는 Playwright 테스트 에이전트(planner · generator · healer) 따라 하기와 폰 화면 실습(`08_폰_화면_고치기.md`)은 보너스입니다.

PR 을 올릴 때는 `.github/pull_request_template.md` 의 **AC 이행 현황** 표를 채웁니다 — 명세의 AC 를 그대로 옮기고, 무엇으로 확인했는지 적습니다.

## Playwright 명령 모음 (`e2e-ts` 폴더에서)

| 명령 | 하는 일 |
|---|---|
| `npx playwright test` | 전부 실행 |
| `npx playwright test -c playwright.mobile.config.ts` | 폰 화면 테스트만 (`mobile/` 폴더, Pixel 7 · iPhone 15 흉내 — 보너스). 위의 기본 실행에는 섞이지 않는다 |
| `npx playwright show-report` (= `npm run report`) | HTML 리포트 — 실패 원인, 스크린샷, 트레이스. 다 봤으면 Ctrl+C |
| `npx playwright test --ui` (= `npm run ui`) | UI 모드 — 한 화면에서 실행·되감기 |
| `npm run codegen` (= `npx playwright codegen http://127.0.0.1:8000`) | 화면을 클릭하면 테스트 코드가 생긴다. 앱은 다른 터미널에서 먼저 띄우고(키트 루트에서 `python web/app.py`), 녹화가 끝나면 Ctrl+C 로 끈다 — 켜 두면 테스트가 'already used' 로 시작을 못 한다 |
| `npx playwright init-agents --loop=claude` | AI 테스트 에이전트(planner · generator · healer) 파일 만들기. `tests/seed.spec.ts` · `.claude/` · `.mcp.json` 이 생기므로 **실습 키트가 아니라 다른 폴더에 받은 연습용 복사본의 `e2e-ts`** 에서 (HANDS_ON 보너스) |

## 규칙 세 가지

1. 테스트가 실패하면 **테스트를 고치지 말고 코드를 고칩니다.** 화면이 바뀐 경우에만 `pages/` 의 위치 정보를 고칩니다.
2. 테스트의 기대값은 **코드가 아니라 명세에서** 옵니다.
3. AI 가 "다 됐습니다" 라고 해도, 테스트 결과와 `git diff` 를 직접 봅니다.

## 오늘의 체크리스트

**명세** — [ ] 규칙에 번호 · [ ] 예시(AC)에 숫자 기대값 · [ ] 테스트로 못 옮기는 예시는 고친다 · [ ] 테스트 계획: 어떤 예시를 E2E 로 · [ ] 모르면 [확인 필요]

**E2E** — [ ] 핵심 화면 흐름만 · [ ] 화면 조작은 pages/ 에 · [ ] 역할(role)·글자로 요소 찾기 · [ ] 실패하면 리포트·트레이스부터

**관문** — [ ] AI 편집마다 테스트(훅) · [ ] PR 에서 CI 필수 + 브랜치 보호 · [ ] 테스트 파일 변경은 따로 승인 · [ ] 출시 전 QA 점검 리스트(Go / No-Go)

**AI 검증** — [ ] 실패는 분류부터 (화면 변경 / 제품 버그 / 불안정 / 환경) · [ ] 제품 버그면 테스트 수정 금지 · [ ] healer 처럼 '고쳐 주는' AI 를 썼으면 git diff 에서 fixme · skip · 기대값 변경 · [ ] 쓴 AI ≠ 검증 AI · [ ] 최종 판단은 사람
