# 실습 가이드 (Hands-on) — 명세와 검증

강의 「AI 시대, 개발자가 알아야 할 명세와 검증」의 실습을 처음부터 끝까지 따라 하는 문서입니다. **강의 전에 0절을 꼭 해 오세요.** 1절부터는 강의 중에 함께 합니다.

오늘 다루는 것은 작은 구독 요금 계산 화면 하나입니다. AI가 짰고, 테스트도 전부 통과합니다. 그런데 월 요금 3,000원짜리에 5,000원 쿠폰을 쓰면 **청구 금액이 -4,000원**으로 나옵니다. 이 버그를 명세와 E2E 테스트로 잡아 봅니다.

![오늘의 버그 — 청구 금액 -4,000원](docs/images/demo_buggy.png)

| 실습 | 시간 | 하는 일 | 카드 |
|---|---|---|---|
| ① 명세 쓰기 | 7분 | 기획 메모 → AI 인터뷰 → 규칙과 AC(인수 기준) | `prompts/01` |
| ② 눈으로 버그 찾기 | 3분 | AI 없이 코드를 읽고 버그를 찾는다 | — |
| ③ 명세로 E2E 만들기 | 12분 | AC → Playwright 테스트 → 빨간불 → 리포트 → 코드만 고친다 | `prompts/02`, `03` |
| ③-2 같은 명세를 API 로 | 3분 | 브라우저 없이 API 를 끝까지 부르는 테스트 | `prompts/06` |
| ④ E2E 실패 분류 | 12분 | 동료 PR 이 E2E 를 깨뜨렸다 → AI 에게 "분류부터" | `prompts/04` |
| ⑤ 우리 팀 핵심 흐름 | 8분 | 내 서비스의 흐름 하나를 AC 5개로 (앱 팀은 Maestro 흐름 초안까지) | `specs/TEMPLATE.md`, `prompts/07` |

모든 명령은 **받은 폴더(`sdd-qa-lab`)에서** 실행합니다. 파이썬이 `python` 이 아니라 `py` 나 `python3` 로 실행되는 PC 는 아래 `python` 을 그 이름으로 바꾸세요.

---

## 0. 강의 전에 (Python · Node 가 있으면 10분)

**설치**: Python 3.10 이상 · **Node.js 20 이상**(LTS) · git · AI 코딩 도구 하나(Claude Code, Cursor, GitHub Copilot, 웹 채팅 무엇이든 — 로그인까지 해 두세요)

git 을 처음 쓰면 이름과 메일을 한 번 정해 둡니다. 실습에서 커밋합니다.
```bash
git config --global user.name "내 이름"
git config --global user.email "내 메일"
```

**받기와 확인**
```bash
git clone https://github.com/diqksrk/ai-auto-practice.git sdd-qa-lab
cd sdd-qa-lab
python -m pip install -r requirements.txt
python -m pytest                    # → 7 passed

cd e2e-ts
npm install
npx playwright install chromium     # 브라우저 약 300MB — 강의장 와이파이 말고 미리!
npx playwright test                 # → 1 passed
cd ..
```

`7 passed` 와 `1 passed` 가 나오면 준비 끝입니다. 막히면 `python tools/check_setup.py` 를 실행하세요. 무엇이 빠졌고 무엇을 하면 되는지 한 번에 알려 줍니다.

| 이런 메시지가 나오면 | 이렇게 |
|---|---|
| `node: v16...` · `npm ERR! engine` | Node 20 이상으로 (nvm 이면 `nvm install 20` → `nvm use 20`) |
| `Executable doesn't exist ... chromium` | `npx playwright install chromium` 을 다시 |
| `fatal: unable to auto-detect email address` | 위의 `git config --global user.email` |
| `'python' 은(는) ... 아닙니다` · `command not found` | `py` 나 `python3` 로. E2E 는 `PYTHON=py npx playwright test` (PowerShell: `$env:PYTHON="py"; npx playwright test`) |
| `http://127.0.0.1:8000 is already used` | 따로 띄워 둔 `python web/app.py` 를 Ctrl+C 로 끄고 다시 |

---

## 1. 실습① 명세 쓰기 (7분)

**목표**: 기획자 메모 한 단락을 **번호 붙은 규칙 + 숫자로 된 예시(AC)** 로 바꾼다. 빈칸은 추측하지 않고 `[확인 필요]` 로 남긴다.

1. `specs/proration.md` 맨 위의 기획 메모를 읽습니다 (1분). 민원 1위가 "해지했는데 요금이 더 나왔다" 입니다.
2. `prompts/01_명세_인터뷰.md` 를 AI 에게 붙여 넣습니다. AI 가 질문을 10개쯤 합니다 — **위에서 5개만 직접 답하고**, 나머지는 카드 아래 "강사 기본값" 으로 답하세요 (3분).
3. AI 가 채운 규칙(R1~R6)과 예시 표(8행 이상)를 확인합니다 (3분).

**완료 기준**: [ ] 규칙에 번호 · [ ] 예시의 기대값이 숫자 · [ ] 31일 달 · 윤년 2월 · 지난달부터 이용 · 쿠폰 > 요금이 들어 있다 · [ ] 모르는 건 `[확인 필요]`

AI 가 코드를 쓰기 시작하면 카드 첫 줄 "아직 코드는 쓰지 마" 를 다시 보여 주세요. 다 못 채워도 괜찮습니다 — 강의에서 정답 표로 함께 확인합니다.

---

## 2. 실습② 눈으로 버그 찾기 (3분)

`src/billing/proration.py` 를 열어 **AI 없이** 버그를 찾아 보세요. 몇 개일까요? 정답은 강의에서.

(이 코드는 단위 테스트 7개를 전부 통과하고, 라인 커버리지가 93% 입니다)

---

## 3. 실습③ 명세로 E2E 만들기 (12분)

**목표**: 명세의 AC 를 Playwright 테스트로 옮기고, 빨간불을 보고, **테스트는 그대로 두고 코드만** 고친다.

### 3-1. 명세 → E2E 테스트 3개 (4분)
**새 대화**에서 `prompts/02_E2E_테스트_만들기.md` 를 붙여 넣습니다. AI 에게는 명세와 화면 객체(`e2e-ts/pages/charge-page.ts`)만 줍니다. 앱 코드를 보면 테스트가 코드의 가정을 베낍니다. **예시 8(쿠폰 > 요금)은 꼭** 넣게 합니다.

### 3-2. 만든 직후 커밋 → 실행 (1분)
```bash
git add e2e-ts/tests/spec-examples.spec.ts
git commit -m "명세 기반 E2E 테스트"
cd e2e-ts
npx playwright test          # 빨간불이 나오면 성공
```
커밋을 먼저 하는 이유: 나중에 `git diff` 로 "AI 가 테스트를 몰래 바꿨는지" 를 볼 수 있어야 하기 때문입니다.

### 3-3. 원인 보기 (2분)
```bash
npx playwright show-report   # 다 봤으면 터미널에서 Ctrl+C
```
실패한 테스트를 누르면 **Expected(명세) / Received(실제)** 가 나옵니다.

![HTML 리포트 — 3개 실패](docs/images/pw_report_list.png)

![실패 상세 — 기대 0원, 실제 -4,000원](docs/images/pw_report_detail.png)

**View Trace** 를 누르면 테스트를 한 단계씩 되감아 그 순간의 화면을 볼 수 있습니다.

![트레이스 — 그 순간의 화면](docs/images/pw_trace_top.png)

(`npx playwright test --ui` 로 열면 목록 · 단계 · 화면 · 코드를 한 창에서 봅니다)

![UI 모드](docs/images/pw_ui_after.png)

### 3-4. 코드만 고치기 (4분)
`prompts/03_코드만_고치기.md` 를 붙여 넣습니다. 핵심은 **"테스트는 절대 수정하지 마"** 입니다.

### 3-5. 확인 → 커밋 (1분)
```bash
# (e2e-ts 폴더에 있다면 먼저 cd ..)
python -m pytest                          # 단위 테스트 통과?
cd e2e-ts; npx playwright test; cd ..     # E2E 통과?
git diff --stat -- tests e2e-ts/tests     # 아무것도 없어야 정상 (테스트를 안 바꿨다)
git add src/billing/proration.py
git commit -m "명세대로 코드 수정"
```

![고친 뒤 — 0원](docs/images/demo_fixed.png)

**9분이 지났는데 아직 3-4 라면**: 정답 코드를 넣고 넘어가세요. 다음 실습이 이 상태에서 시작합니다.
```bash
cp instructor/proration_fixed.py src/billing/proration.py
git add src/billing/proration.py
git commit -m "정답 코드"
```

---

## 4. 실습③-2 같은 명세를 API 로 (3분)

**목표**: 화면이 없어도(또는 앱 뒤의 서버도) **API 를 끝까지 불러서** 명세를 확인할 수 있다는 것을 본다.

```bash
cp instructor/e2e/api-examples.spec.ts e2e-ts/tests/
cd e2e-ts
npx playwright test api-examples      # 브라우저 없이 1~2초 → 2 passed
cd ..
git add e2e-ts/tests/api-examples.spec.ts
git commit -m "API 테스트"
```
`e2e-ts/tests/api-examples.spec.ts` 를 열어 화면 테스트와 무엇이 다른지 보세요. `page` 대신 `request.post('/api/charge')`, 화면 글자 대신 **상태 코드와 JSON** 을 확인합니다. 오류 예시(종료일 < 시작일)는 400 과 `error` 가 있는지만 봅니다 — 오류 문장은 바뀔 수 있어서 통째로 비교하지 않습니다.

빨리 끝났다면 `prompts/06` 아래쪽 카드로 AI 에게 같은 테스트를 직접 만들게 해서 비교해 보세요.

---

## 5. 실습④ 동료 PR 이 E2E 를 깨뜨렸다 (12분)

**목표**: 테스트가 깨졌을 때 AI 에게 "고쳐 줘" 가 아니라 **"분류부터"** 시킨다.

### 5-1. 동료 PR 적용 → 바로 커밋 (1분)
```bash
python tools/lab4_change.py               # 동료의 PR: "화면 문구 정리 + 쿠폰 계산 리팩터링"
git add web/app.py
git commit -m "동료 PR"
python -m pytest                          # 단위 테스트는? → 전부 초록
cd e2e-ts; npx playwright test; cd ..     # E2E 는? → 빨강
```
단위 테스트는 초록인데 E2E 는 빨갛습니다. 계산 모듈은 안 바뀌었으니까요. "바깥에서 안쪽으로" 확인해야 하는 이유입니다.

### 5-2. 분류부터 (6분)
`prompts/04_E2E_실패분류.md` 를 붙여 넣습니다. 실패마다 넷 중 하나로 분류하고 근거를 보여 달라고 합니다.

| 분류 | 증상 | 고치는 곳 |
|---|---|---|
| 화면 변경 | 버튼 · 칸 이름이 바뀌어 요소를 못 찾음 | `e2e-ts/pages/` 의 위치 정보만 |
| 제품 버그 | 화면은 그대로인데 값이 명세와 다름 | **테스트 금지**, 코드를 고친다 |
| 불안정 | 다시 돌리면 통과 (타이밍) | 기다리는 방법 |
| 환경 | 서버가 안 떴거나 네트워크 | 환경 |

넷 중 어디에도 안 맞거나 명세가 틀려 보이면, 고치지 말고 멈춰서 사람에게 묻게 합니다. **하나를 고칠 때마다 다시 돌리고 다시 분류** 하세요 — 앞의 실패가 뒤의 실패를 가리고 있을 수 있습니다. (실습③-2 의 API 테스트가 무엇을 먼저 보여 주는지도 눈여겨보세요)

### 5-3. 확인 (2분)
```bash
git diff --stat                           # "동료 PR" 커밋 이후: e2e-ts/pages/ + web/app.py 만 바뀌었어야 정상
git diff -- e2e-ts/tests tests            # 아무것도 없어야 정상
cd e2e-ts; npx playwright test; cd ..     # 전부 통과
```

끝나면 `python tools/lab4_change.py --undo` 로 PR 적용 전으로 되돌릴 수 있습니다 (`e2e-ts/pages/` 를 고쳤다면 `git checkout -- e2e-ts/pages` 도).

---

## 6. 실습⑤ 우리 팀 핵심 흐름 하나 (8분)

**목표**: 오늘 한 것을 내 서비스에. 틀리면 제일 아픈 흐름 하나(가입 · 결제 · 권한 · 알림 …)를 고른다.

1. 흐름 고르기 (1분)
2. `specs/TEMPLATE.md` 의 4절에 AC 5개: `- [ ] AC-n: 입력 → 기대 결과` (2분)
3. 어디서 확인할지 나누기 (4분)
   - **웹 · 백엔드**: 화면(Playwright)으로 볼 것 1~2개, 나머지는 API · 단위 테스트로
   - **앱**: `prompts/07_앱_흐름_초안.md` — 화면 요소 **id 계약 표** 5개를 먼저 만들고, 그 id 로만 **Maestro 흐름 초안**을 쓰게 한다 (본보기: `maestro/spec-example-8.yaml`). 실행은 팀에 돌아가서.
4. `AGENTS.md` 5줄 — 명령 1 · 금지 2 · '왜' 2. 사람이 직접, 짧게 (1분)

**숙제**: 다음 스프린트 첫 PR 에 E2E 1개 + CI 관문(`.github/workflows/ci.yml` 을 복사해서 시작). 출시 전에는 `specs/RELEASE_CHECKLIST.md` 같은 점검 리스트를 QA 와 함께.

---

## 보너스

**같은 버그를 앱 테스트 도구 Maestro 로** — Java 17 이상과 [Maestro CLI](https://docs.maestro.dev) 가 필요합니다. `python web/app.py` 를 띄운 뒤 다른 터미널에서 `maestro test maestro/spec-example-8.yaml`. 고치기 전 코드면 마지막 줄이 FAILED, 고친 뒤면 COMPLETED.

| 고치기 전 | 고친 뒤 |
|---|---|
| ![Maestro — 고치기 전](docs/images/maestro_buggy.png) | ![Maestro — 고친 뒤](docs/images/maestro_fixed.png) |

**AI 로 엣지 케이스를 뽑고 뮤테이션으로 채점** — `prompts/보너스_엣지케이스_뮤테이션.md` 로 경계 사례를 뽑고, `python tools/mutate.py --min-score 80` 으로 "코드를 일부러 망가뜨렸을 때 테스트가 잡는 비율" 을 잽니다. 커버리지는 '실행됐다', 뮤테이션은 '잡는다' 입니다.

**AI 테스트 에이전트** — 빈 폴더에서 `npx playwright init-agents --loop=claude` → `.claude/agents/playwright-test-healer.md` 를 열어 "Fixing assertions and expected values" 를 찾아보세요. 왜 위험한지 강의에서 이야기합니다.

---

## 오늘의 체크리스트

- **명세** — [ ] 규칙에 번호 · [ ] AC 에 숫자 기대값 · [ ] 테스트로 못 옮기는 AC 는 고친다 · [ ] 모르면 `[확인 필요]`
- **E2E** — [ ] 핵심 흐름만 · [ ] 화면 조작은 `pages/` 에 · [ ] 사람이 보는 이름(앱은 id)으로 찾기 · [ ] 실패하면 리포트 · 트레이스부터
- **관문** — [ ] AI 편집마다 테스트 · [ ] PR 에서 CI 필수 + 브랜치 보호 · [ ] 테스트 변경은 따로 승인 · [ ] 출시 전 QA 점검 리스트 (Go / No-Go)
- **AI 검증** — [ ] 실패는 분류부터 · [ ] 제품 버그면 테스트 수정 금지 · [ ] 쓴 AI ≠ 검증 AI · [ ] 최종 판단은 사람

`instructor/` 는 막혔을 때 쓰는 정답입니다. 먼저 보지 말고 막혔을 때만 여세요.
