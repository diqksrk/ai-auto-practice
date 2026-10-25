# 실습 가이드 (Hands-on) — 명세와 검증

오늘 다루는 것은 작은 구독 요금 계산 화면 하나입니다. AI가 짰고, 테스트도 전부 통과합니다. 그런데 월 요금 3,000원짜리에 5,000원 쿠폰을 쓰면 **청구 금액이 -4,000원**으로 나옵니다. 이 버그를 명세와 E2E 테스트로 잡아 봅니다.

| 실습 | 시간 | 하는 일 | 카드 |
|---|---|---|---|
| ① 명세 쓰기 | 10분 | 기획 메모 → AI 인터뷰 → 규칙과 AC(인수 기준) | `prompts/01` |
| ② 눈으로 버그 찾기 | 3분 | AI 없이 코드를 읽고 버그를 찾는다 | — |
| codegen 녹화 따라 하기 | 7분 | 화면을 누르면 테스트 코드가 생긴다 — 기대값만은 명세에서 | — |
| ③ 명세로 E2E 만들기 | 15분 | AC → Playwright 테스트 → 빨간불 → 리포트 → 코드만 고친다 | `prompts/02`, `03` |
| ③-2 같은 명세를 API 로 | 3분 | 브라우저 없이 API 를 끝까지 부르는 테스트 | `prompts/06` |
| ④ 동료 PR 이 E2E 를 깨뜨렸다 | 15분 | 단위는 초록 · E2E 는 빨강 → AI 에게 분류부터 → 화면 변경은 `pages/` 만 · 제품 버그는 코드만 → `git diff` 로 사람이 판정 | `prompts/04` |
| ⑤ 우리 팀 핵심 흐름 | 15분 | 내 서비스의 흐름 하나를 AC 5개로 (앱 팀은 Maestro 흐름 초안까지) | `specs/TEMPLATE.md`, `prompts/07` |

모든 명령은 **받은 폴더(`sdd-qa-lab`)에서** 실행합니다(보너스 '테스트 에이전트 따라 하기' 만 연습용 폴더 `agents-practice` 에서). 명령은 Git Bash · PowerShell · macOS/Linux 터미널 기준입니다(윈도우 cmd 라면 `cp` 대신 `copy`). 파이썬이 `python` 이 아니라 `py` 나 `python3` 로 실행되는 PC 는 아래 `python` 을 그 이름으로 바꾸세요.

---

## 강의 전에 (Python · Node 가 있으면 10분)

**설치**: Python 3.10 이상 · **Node.js 20 이상**(LTS) · git · SourceTree(저장소 받기) · AI 코딩 도구 하나(Claude Code, Cursor, GitHub Copilot, 웹 채팅 무엇이든 — 로그인까지 해 두세요)

**버전 확인 먼저** — 터미널(윈도우는 PowerShell)에서
```bash
python --version     # 3.10 이상. 윈도우는 py --version, macOS · Linux 는 python3 --version 으로도
node -v              # v20 이상 (v22 · v24 도 됩니다)
git --version        # 판은 상관없음
```
윈도우에서 `python` 이 Microsoft Store 를 열거나 `Python was not found` 가 나오면 아직 설치가 안 된 것입니다(`py --version` 이 되면 그 PC 는 `py` 로 씁니다). macOS 에 원래 들어 있는 `python3` 는 3.9 일 수 있습니다 — 3.10 아래면 새로 설치합니다.

**맥은 `python` 명령이 없는 경우가 대부분입니다** — 아래 '받기와 확인' 의 첫 명령이 `command not found` 로 멈춥니다. 그래서 맥은 키트 폴더에서 가상환경(venv)을 한 번 만들고 켠 뒤 시작합니다(명령은 아래 '받기와 확인' 맨 위). 켠 터미널에서는 `python` 이 됩니다. **새 터미널을 열 때마다 `source .venv/bin/activate` 를 다시** 칩니다 — AI 도구(`claude`)도 venv 를 켠 터미널에서 엽니다. 안 그러면 AI 가 파일을 고칠 때마다 '`pytest` 를 찾지 못했습니다' 가 뜹니다. Node 를 nvm 으로 깐 맥은 `nvm alias default 20` 도 한 번 해 둡니다 — 새 터미널이 옛 Node 로 열리면 Playwright 가 `SyntaxError: Unexpected token '??='` 같은 글로 멈춥니다.

**없거나 낮으면 설치** — 설치 파일이 가장 무난합니다. 명령으로 깔려면 오른쪽 두 칸.

| | 설치 파일 | Windows (PowerShell) | macOS |
|---|---|---|---|
| Python 3.10+ | [python.org](https://www.python.org/downloads/) — 윈도우는 설치 첫 화면의 **'Add python.exe to PATH'** 체크 | `winget install Python.Python.3.12` | python.org 설치 파일 (아래 괄호 참고) |
| Node.js 20+ | [nodejs.org](https://nodejs.org/) 의 **LTS** | `winget install OpenJS.NodeJS.LTS` | `brew install node` |
| git | [git-scm.com](https://git-scm.com/downloads) | `winget install Git.Git` | `xcode-select --install` (또는 `brew install git`) |
| SourceTree | [sourcetreeapp.com](https://www.sourcetreeapp.com/) | `winget install Atlassian.Sourcetree` | sourcetreeapp.com 설치 파일 |

SourceTree 에 딸린 git(embedded)만 있으면 터미널에서는 `git` 이 안 잡힐 수 있습니다. 실습의 커밋 · `git diff` 는 터미널에서 치니, `git --version` 이 안 되면 위의 git 을 따로 깝니다.

설치한 뒤에는 **터미널을 새로 열고** 버전 확인을 다시 합니다. 이미 열려 있던 창은 새로 깐 프로그램을 못 찾습니다. (macOS 에서 `brew` 로 깐 파이썬은 `pip install` 이 `externally-managed-environment` 로 막힙니다 — 그때는 키트 폴더에서 `python3 -m venv .venv` → `source .venv/bin/activate` 후 다시)

**이미 옛 Node(16 · 18)가 있으면** — nvm 을 쓰는 PC 는 `nvm list` 로 깔린 판을 보고 `nvm install 24` → `nvm use 24` (지금 LTS. 최소 조건은 20) (윈도우 nvm 은 `nvm use` 때 관리자 권한 창이 뜰 수 있습니다 — 허락하면 됩니다). nvm 이 없으면 nodejs.org 의 LTS 설치 파일로 덮어 설치하고 새 터미널을 엽니다. 왜 20 인가: 키트가 고정한 Playwright 1.60 은 Node 18 에서도 돌지만, Playwright 1.62 부터는 Node 20 이상이어야 합니다(지금 최신은 1.64). 키트 폴더 밖에서 `npx playwright …` 를 치면 최신판을 받아 와 `Playwright requires Node.js 20 or higher` 로 멈춥니다. 키트의 CI 도 Node 20 입니다. 다만 Node 20 은 2026년 4월로 지원이 끝났으니 새로 깔 때는 LTS(24)를 고릅니다.

**회사 PC** 라 설치 권한이 없으면 강의 전에 미리 IT 에 요청하세요. 브라우저(약 300MB)도 아래 '받기와 확인' 에서 미리 받아 둡니다.

보너스 '테스트 에이전트 따라 하기'는 Claude Code 로 합니다 — VS Code + Claude Code 확장, 또는 터미널의 `claude`. 없으면 건너뜁니다. 앱 테스트 도구 보너스(Maestro)는 Java 17 이상 · Maestro CLI 가 필요합니다(오늘의 웹 화면에 돌리므로 에뮬레이터는 없어도 됩니다) — 무겁고 오래 걸리니 앱 팀만.

git 을 처음 쓰면 이름과 메일을 한 번 정해 둡니다. 실습에서 커밋합니다.
```bash
git config --global user.name "내 이름"
git config --global user.email "내 메일"
```

**받기와 확인** — 저장소는 SourceTree 로 받습니다(주소 `https://github.com/diqksrk/ai-auto-practice` · 받을 폴더 이름 `sdd-qa-lab`). 받은 `sdd-qa-lab` 폴더에서 터미널을 열고
```bash
# 맥은 먼저 두 줄 (처음 한 번 venv 만들기 · 켜기는 새 터미널마다)
#   python3 -m venv .venv
#   source .venv/bin/activate
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
| `[notice] A new release of pip …` (PowerShell 에서 빨갛게 보임) | 무시해도 됩니다 — 오류가 아니라 안내 |
| `node: v16...` · `npm ERR! engine` · `SyntaxError: Unexpected token '??='` · `Class extends value undefined` | Node 가 옛 판 — Node 20 이상으로 (nvm 이면 `nvm install 24` → `nvm use 24` → `nvm alias default 24`) |
| `Executable doesn't exist ... chromium` | `npx playwright install chromium` 을 다시 |
| `fatal: unable to auto-detect email address` | 위의 `git config --global user.email` |
| `'python' 은(는) ... 아닙니다` · `command not found` | 맥: `source .venv/bin/activate` (없으면 `python3 -m venv .venv` 부터). 윈도우: `py` 로 — E2E 는 `$env:PYTHON="py"; npx playwright test` (Git Bash 는 `PYTHON=py npx playwright test`) |
| `http://127.0.0.1:8000 is already used` | 따로 띄워 둔 `python web/app.py` 를 Ctrl+C 로 끄고 다시 |

**AI 도구에 카드 주는 법** — 카드는 `prompts/` 의 md 파일입니다. 회색 상자(```) 안의 글을 복사해 AI 에게 보냅니다. 상자 밖은 사람이 읽는 설명입니다.
- Claude Code · Cursor · Copilot 처럼 **폴더를 여는 도구**: `sdd-qa-lab` 폴더에서 엽니다(Claude Code 는 `cd sdd-qa-lab` → `claude`). 카드의 `(여기에 … 붙여 넣기)` 줄은 "specs/proration.md 를 읽고" 처럼 파일 이름으로 바꿔 씁니다. AI 가 파일을 고치거나 명령을 돌리려 하면 허락을 묻습니다. 무엇을 하려는지 읽고 허락하세요. 실습③ · ④ 에서는 10번 안팎 묻습니다 — `pytest` · `npx playwright test` 처럼 테스트만 돌리는 명령은 '다시 묻지 않기' 를 골라도 됩니다.
- **웹 채팅**: 그 줄 자리에 파일 내용을 붙여 넣습니다. AI 가 준 결과는 내가 파일에 붙여 넣고 저장합니다.
- 카드에 **"새 대화에서"** 라고 있으면 대화를 새로 시작합니다(Claude Code 는 `/clear`). 앞에서 본 코드를 테스트가 베끼지 않게 하려는 것입니다.

---

## 실습① 명세 쓰기 (10분)

**목표**: 기획자 메모 한 단락을 **번호 붙은 규칙 + 숫자로 된 예시(AC)** 로 바꾼다. 빈칸은 추측하지 않고 `[확인 필요]` 로 남긴다.

1. `specs/proration.md` 맨 위의 기획 메모를 읽습니다 (1분). 민원 1위가 "해지했는데 요금이 더 나왔다" 입니다.
2. `prompts/01_명세_인터뷰.md` 를 AI 에게 붙여 넣습니다. AI 가 질문을 10개쯤 합니다 — **위에서 5개만 직접 답하고**, 나머지는 카드 아래 "강사 기본값" 으로 답하세요 (5분). 기본값은 질문을 받은 **뒤에** 보냅니다. 처음부터 같이 보내면 AI 가 묻지 않고 바로 채워 버립니다. 보낼 때는 맨 앞에 "내가 이미 답한 질문은 내 답대로, 나머지만 아래 기준으로" 를 붙입니다 — 기본값 몇 줄이 AI 의 앞 질문과 겹쳐서, 안 붙이면 내 답과 부딪힙니다.
3. AI 가 채운 규칙(R1~R6)과 예시 표(8행 이상)를 확인합니다 (4분). AI 가 윤년 대신 평년 2월(2026-02)을 쓰거나 31일 달을 한 달 전체가 아닌 며칠만 넣는 일이 있습니다 — 빠졌으면 "2028년 2월 한 달 · 31일 달 한 달 예시도 넣어 줘" 라고 한 번 더 보냅니다.

**완료 기준**: [ ] 규칙에 번호 · [ ] 예시의 기대값이 숫자 · [ ] 31일 달 · 윤년 2월 · 지난달부터 이용 · 쿠폰 > 요금이 들어 있다 · [ ] 모르는 건 `[확인 필요]`

AI 가 코드를 쓰기 시작하면 카드 첫 줄 "아직 코드는 쓰지 마" 를 다시 보여 주세요. 다 못 채워도 괜찮습니다.

**끝나면 커밋** (뒤 실습의 `git diff` 확인이 깔끔해집니다)
```bash
git add specs/proration.md
git commit -m "명세"
```

---

## 실습② 눈으로 버그 찾기 (3분)

`src/billing/proration.py` 를 열어 **AI 없이** 버그를 찾아 보세요. 몇 개일까요?

(이 코드는 단위 테스트 7개를 전부 통과하고, 라인 커버리지가 93% 입니다)

---

## codegen 녹화 따라 하기 (7분)

녹화기(codegen)는 '무엇을 했나' 만 적습니다. '무엇이 맞나'(기대값)는 명세 4절 8번 줄에서 옮겨 적는다는 것을 직접 봅니다. 터미널을 두 개 씁니다.

**1) 터미널 ① — 앱 켜기** (키트 맨 위 폴더 `sdd-qa-lab` 에서. 녹화가 끝날 때까지 켜 둡니다)
```bash
python web/app.py              # py 인 PC 는 py web/app.py
```

**2) 터미널 ② — 녹화기 켜기** (터미널을 하나 더 열고)
```bash
cd e2e-ts
npm run codegen                # = npx playwright codegen http://127.0.0.1:8000 → 창 두 개
```

**3) 'Chrome for Testing' 창에서 입력 → [계산]** — 월 요금 3000 · 이용 시작일 2026-09-21 · 청구월 2026년 9월 · 쿠폰 정액(원) · 쿠폰 값 5000 (명세 4절 8번 줄의 입력). 결과 칸에 `청구 금액: -4,000원` 이 뜹니다. 누를 때마다 'Playwright Inspector' 창에 코드가 쌓입니다.

**4) 확인 줄 넣기** — ab(글자 확인, 눈 아이콘 오른쪽) → 결과 글자 클릭 → ✓. Inspector 맨 아래에 `toContainText('청구 금액: -4,000원')` 이 생깁니다. 지금 화면 값이 정답이 된 것입니다.

**5) 저장하고 앱 끄기** — Inspector 의 코드를 복사해 새 파일 `e2e-ts/tests/my-codegen.spec.ts` 에 붙여 넣고 저장합니다. 녹화 창 두 개를 닫고(터미널 ② 의 codegen 이 끝납니다), 터미널 ① 에서 **Ctrl+C 로 앱을 끕니다.** 테스트가 앱을 직접 띄우니 켜 두면 'already used' 가 납니다.

**6) 그대로 돌리기** (터미널 ②, `e2e-ts` 에서)
```bash
npx playwright test tests/my-codegen.spec.ts     # → 1 passed. 버그(-4,000원)를 정답으로 녹화했으니 초록
```

**7) 기대값 한 줄만 명세 값으로 → 저장 → 다시 돌리기**
```diff
- .toContainText('청구 금액: -4,000원');
+ .toContainText('청구 금액: 0원');   // 명세 4절 8번 줄
```
```
  x  1 tests\my-codegen.spec.ts:3:5 › test
    Expected substring: "청구 금액: 0원"
    Received string:    "청구 금액: -4,000원"
  1 failed
```
빨강 — 버그를 잡았습니다. 테스트의 기대값을 바꾸는 건 이번 한 번뿐입니다(녹화가 버그 값을 적었을 때). 명세 값으로 빨간불이 나면 그다음 고치는 건 코드입니다.

(선택) 녹화 코드를 화면 객체 모양으로 정리시키려면 8) 에서 지우기 **전에** 아래를 AI 에게 보냅니다. 카드 안의 `tests/` · `pages/` 는 `e2e-ts/` 안의 폴더입니다(키트 맨 위의 `tests/` 는 단위 테스트). 결과는 버그 코드에서 빨강이 정상입니다 — 초록이면 AI 가 기대값을 건드린 것이니 `git diff` 로 '0원' 이 그대로인지 봅니다.
```
e2e-ts/tests/my-codegen.spec.ts 는 codegen 녹화본이야.
e2e-ts/pages/charge-page.ts 의 ChargePage 로 다시 써 줘.
- 헛동작(같은 칸 반복 click · html click · Tab)은 버려
- 칸 찾는 코드는 pages/ 에만. tests/ 에는
  open → fill → calculate → expectCharge 만
- pages/ 에 없는 동작일 때만 pages/ 에 추가해
- 기대값 '0원' = specs/proration.md 4절 8번 줄.
  절대 바꾸지 마
- web/ · src/ 의 앱 코드는 읽지 마
- 테스트 이름 '명세 예시 8: 쿠폰이 요금보다 커도 0원'
- 다 쓰면 cd e2e-ts → npx playwright test 결과만.
  실패해도 고치지 마
```

**8) 끝나면 지우기** — 남기면 실습③ 의 테스트 수가 달라집니다. AI 에게 정리시킨 파일이 있으면 그것도 지웁니다.
```bash
rm tests/my-codegen.spec.ts      # e2e-ts 에서 (윈도우 cmd 라면 del tests\my-codegen.spec.ts)
```

**따라 하다 막히면**

| 이런 글이 보이면 | 왜 | 이렇게 |
|---|---|---|
| `npm error enoent` · `Could not read package.json` | 키트 맨 위 폴더에서 쳤다 — npm 명령은 `e2e-ts` 안에 있다 | `cd e2e-ts` 후 다시 |
| `Need to install … playwright@1.6x` → `did not expect test() to be called here` | 맨 위 폴더의 npx 가 다른 판을 새로 받아 키트의 1.60 과 섞였다 | n 을 누르고 `cd e2e-ts` 에서 다시 |
| `Playwright requires Node.js 20 or higher` · `SyntaxError: Unexpected token '??='` | 켜져 있는 Node 가 옛 판 (`node -v` 로 확인) — 맥은 새 터미널이 옛 Node 로 열리는 PC 가 있다 | Node 20 이상으로 — nvm 이면 `nvm use 20` → `nvm alias default 20` (새 창도 20) |
| `http://127.0.0.1:8000 is already used` | 터미널 ① 의 앱이 아직 켜져 있다 | Ctrl+C 로 끄고 다시 — 테스트가 앱을 직접 띄운다 |
| `'python'은(는) 내부 또는 외부 명령…` · `webServer was not able to start` | 이 PC 는 파이썬이 `py` 로만 잡힌다 | `$env:PYTHON='py'` 후 다시 (새 창마다. Git Bash 는 `export PYTHON=py`, 맥은 `source .venv/bin/activate`) |
| Inspector 창이 안 보인다 | 다른 창 뒤에 숨었다 | 작업 표시줄 크롬 아이콘 · Alt+Tab (macOS 는 Cmd+Tab) — 제목 'Playwright Inspector' |
| 눌러도 Inspector 에 줄이 안 생긴다 | 평소 쓰는 크롬 창에서 눌렀다 | 제목이 'Chrome for Testing' 인 창에서 |
| 키트 맨 위에 `package.json` · `playwright.config.ts` · `e2e/example.spec.ts` 가 생겼다 | 키트에서 `npm init playwright@latest` 를 쳤다 (새 프로젝트에 붙일 때 쓰는 명령) | `git status` 로 새 파일을 보고 지운 뒤 `git checkout -- .gitignore`. `e2e/` 폴더 자체는 원래 있던 파이썬 버전이니 새로 생긴 파일만 지운다 |

Playwright 명령은 전부 `e2e-ts` 안에서 — 앱은 녹화할 때만 켜고, 테스트 전엔 끕니다.

---

## 실습③ 명세로 E2E 만들기 (15분)

**목표**: 명세의 AC 를 Playwright 테스트로 옮기고, 빨간불을 보고, **테스트는 그대로 두고 코드만** 고친다.

시작 전에: 따로 띄운 `python web/app.py` 가 있으면 Ctrl+C 로 끕니다. 그리고 **모두 정답 명세로 바꾸고 시작합니다** — 리포트에 찍히는 '예시 8' 이 정답 명세의 번호이기 때문입니다. 내 명세는 앞 커밋에 그대로 남아 있습니다(`git show HEAD~1:specs/proration.md`).
```bash
cp instructor/proration_spec.md specs/proration.md
git add specs/proration.md
git commit -m "정답 명세"
```

### 1) 명세 → E2E 테스트 3개 (5분)
**새 대화**에서 `prompts/02_E2E_테스트_만들기.md` 를 붙여 넣습니다. AI 에게는 명세와 화면 객체(`e2e-ts/pages/charge-page.ts`)만 줍니다. 앱 코드를 보면 테스트가 코드의 가정을 베낍니다. **예시 8(쿠폰 > 요금)은 꼭** 넣게 합니다. 테스트를 못 만들었으면 정답 테스트를 복사해 2) 로 갑니다: `cp instructor/e2e/spec-examples.spec.ts e2e-ts/tests/`

### 2) 만든 직후 커밋 → 실행 (1분)
```bash
git add e2e-ts/tests/spec-examples.spec.ts     # AI 가 다른 이름으로 만들었으면 그 이름으로
git commit -m "명세 기반 E2E 테스트"
cd e2e-ts
npx playwright test          # 빨간불이 나오면 성공
```
빨간불 개수는 AI 가 고른 예시에 따라 1~3개입니다. 예시 8(쿠폰 > 요금)은 반드시 빨강(`Received "청구 금액: -4,000원"`)입니다.
커밋을 먼저 하는 이유: 나중에 `git diff` 로 "AI 가 테스트를 몰래 바꿨는지" 를 볼 수 있어야 하기 때문입니다.

### 3) 원인 보기 (3분)
```bash
npx playwright show-report   # 다 봤으면 터미널에서 Ctrl+C
```
실패한 테스트를 누르면 **Expected(명세) / Received(실제)** 가 나옵니다.

**View Trace** 를 누르면 테스트를 한 단계씩 되감아 그 순간의 화면을 볼 수 있습니다.

(`npx playwright test --ui` 로 열면 목록 · 단계 · 화면 · 코드를 한 창에서 봅니다)

### 4) 코드만 고치기 (5분)
`prompts/03_코드만_고치기.md` 를 붙여 넣습니다. 핵심은 **"테스트는 절대 수정하지 마"** 입니다. AI 가 '테스트가 없는 곳의 명세 위반' 목록을 보여 주고 멈추면, 읽어 보고 "고쳐 줘" 라고 답하세요. 목록만 받고 넘어가면 테스트는 초록인데 버그가 남습니다. AI 마다 다릅니다 — 목록을 내고 멈추는 AI 도, 바로 다 고치는 AI 도 있습니다. 바로 다 고쳤으면 `git diff src` 로 네 곳(30일 고정 · 청구월 1일 · 버림 · 0원 하한)이 바뀌었는지 봅니다. Claude Code 로 하면 AI 가 파일을 고칠 때마다 키트가 단위 테스트를 자동으로 돌려 중간에 빨간 줄이 보일 수 있습니다 — 마지막 결과만 봅니다.

### 5) 확인 → 커밋 (1분)
```bash
# (e2e-ts 폴더에 있다면 먼저 cd ..)
python -m pytest                          # 단위 테스트 통과?
cd e2e-ts; npx playwright test; cd ..     # E2E 통과?
git diff --stat -- tests e2e-ts/tests     # 아무것도 없어야 정상 (테스트를 안 바꿨다)
git add src/billing/proration.py
git commit -m "명세대로 코드 수정"
```

**실습③ 을 시작하고 12분이 지났는데 아직 4) 라면**: 정답 코드를 넣고 넘어가세요. 다음 실습이 이 상태에서 시작합니다.
```bash
cp instructor/proration_fixed.py src/billing/proration.py
git add src/billing/proration.py
git commit -m "정답 코드"
```

---

## 실습③-2 같은 명세를 API 로 (3분)

**목표**: 화면이 없어도(또는 앱 뒤의 서버도) **API 를 끝까지 불러서** 명세를 확인할 수 있다는 것을 본다.

```bash
cp instructor/e2e/api-examples.spec.ts e2e-ts/tests/
cd e2e-ts
npx playwright test api-examples      # 브라우저 없이 1~2초 → 2 passed (실습③ 에서 코드를 고쳤다면. 아직이면 예시 8 이 빨강 — 그게 정상)
cd ..
git add e2e-ts/tests/api-examples.spec.ts
git commit -m "API 테스트"
```
`e2e-ts/tests/api-examples.spec.ts` 를 열어 화면 테스트와 무엇이 다른지 보세요. `page` 대신 `request.post('/api/charge')`, 화면 글자 대신 **상태 코드와 JSON** 을 확인합니다. 오류 예시(종료일 < 시작일)는 400 과 `error` 가 있는지만 봅니다 — 오류 문장은 바뀔 수 있어서 통째로 비교하지 않습니다.

빨리 끝났다면 `prompts/06` 아래쪽 카드로 AI 에게 같은 테스트를 직접 만들게 해서 비교해 보세요.

---

## 실습④ 동료 PR 이 E2E 를 깨뜨렸다 — AI 에게 "분류부터" (15분)

**목표**: 동료의 PR 로 E2E 가 빨개졌을 때 AI 에게 "고쳐 줘" 가 아니라 **"분류부터"** 시킨다. 화면 변경이면 `pages/` 만, 제품 버그면 코드만 고치고, **테스트의 기대값은 그대로** 둔다.

**시작 전에** — 실습③ 의 코드 수정이 커밋돼 있어야 합니다. 못 끝냈으면 키트 맨 위 폴더에서
```bash
cp instructor/proration_fixed.py src/billing/proration.py
git add src/billing/proration.py; git commit -m "정답 코드"
```
따로 띄운 `python web/app.py` 가 있으면 Ctrl+C 로 끕니다. (맥은 새 터미널마다 `source .venv/bin/activate`, 윈도우 py PC 는 `$env:PYTHON='py'`)

**1) 동료 PR 적용 → 바로 커밋 (1분)** — 키트 맨 위 폴더에서
```bash
python tools/lab4_change.py               # → "동료의 PR 을 적용했습니다 (web/app.py 변경)."
git add web/app.py; git commit -m "동료 PR"
```
바로 커밋해야 나중에 `git diff` 로 "AI 가 고친 것" 만 보입니다. 이 PR 은 화면 문구를 '월 요금' 에서 '구독료' 로 바꾸고, 쿠폰 계산을 화면 쪽 코드로 옮기는 리팩터링을 했습니다.

**2) 두 테스트 돌리기 (1분)**
```bash
python -m pytest                          # → 7 passed   (단위 테스트는 초록)
cd e2e-ts; npx playwright test; cd ..     # → 5 failed / 1 passed   (E2E 는 빨강)
```
화면 테스트 4개는 `waiting for getByLabel('월 요금(원)')` (칸을 못 찾음), 실습③-2 의 API 예시 8 은 `"amount": -4000` 으로 실패합니다. 계산 모듈은 안 바뀌어서 단위 테스트는 못 잡고, 바깥에서 돌린 E2E 만 잡았습니다.

**3) AI 에게 분류부터 시키기 (5분)** — `prompts/04_E2E_실패분류.md` 의 상자를 그대로 붙여 넣습니다. 실패마다 넷 중 하나로 분류하고 근거(에러 메시지 · 실패 화면)를 보여 달라는 카드입니다.

| 분류 | 이렇게 보이면 | 고치는 곳 |
|---|---|---|
| 화면 변경 | 버튼 · 칸 이름이 바뀌어 요소를 못 찾음 | `e2e-ts/pages/` 의 위치 정보만 |
| 제품 버그 | 화면은 그대로인데 값이 명세와 다름 | 코드 — 테스트는 손대지 않는다 |
| 불안정 | 다시 돌리면 통과 (타이밍) | 기다리는 방법 |
| 환경 | 서버가 안 떴거나 네트워크 | 환경 |

근거 찾는 곳: 실패 폴더 `e2e-ts/test-results/<테스트 이름>/` 의 `error-context.md` 에 실패 순간의 화면 구조가 있습니다 — 첫 칸이 `spinbutton "구독료(원)"` 로 찍혀 있으면 '화면 변경' 입니다. 웹 채팅에 이 파일을 붙일 때는 맨 위의 Playwright 안내 몇 줄('Provide a snippet of code with the fix' 등)을 지우고 붙입니다 — AI 가 '테스트를 고쳐라' 로 읽을 수 있습니다.

**4) 고칠 때마다 다시 돌리고, 다시 분류 (5분)**
1. 화면 변경 → `e2e-ts/pages/charge-page.ts` 의 `'월 요금(원)'` 한 곳을 `'구독료(원)'` 로 → 다시 돌리면 `2 failed / 4 passed`
2. 숨어 있던 실패가 드러납니다 — 화면 예시 8 `Expected "청구 금액: 0원"` · `Received "청구 금액: -4,000원"`. 화면은 다 채워졌는데 값이 명세와 다르니 **제품 버그**. 테스트는 그대로 두고 `web/app.py` 를 고칩니다(동료 PR 이 쿠폰 계산을 옮기면서 0원 하한을 빠뜨렸습니다 — 쿠폰을 다시 계산 모듈에 넘기면 됩니다).
3. 다시 돌리면 단위 `7 passed` · E2E `6 passed`.

**5) 확인 (3분)**
```bash
git diff --stat                   # "동료 PR" 커밋 이후 바뀐 것
git diff -- e2e-ts/tests tests    # 아무것도 안 나와야 정상
```
```
 e2e-ts/pages/charge-page.ts | 2 +-
 web/app.py                  | 3 +--
```
바뀐 파일이 이 둘(또는 `web/app.py` 에서 옮겨 온 함수까지 지웠다면 그만큼 더)뿐이고, 테스트 폴더 diff 가 비어 있으면 성공입니다. 성공했으면 커밋합니다.
```bash
git add e2e-ts/pages web/app.py; git commit -m "분류 후 수정"
```
다시 해 보려면(선택): `git reset --hard HEAD~2` → `python tools/lab4_change.py --undo` — 두 커밋(동료 PR · 분류 후 수정)이 지워지고 실습④ 시작 상태로 돌아갑니다.

**이렇게 고쳤다면 틀린 수정입니다** — 셋 다 초록이 되지만 옳지 않습니다.
- 테스트 기대값을 `'-4,000원'` 으로 바꾼다 → 버그를 테스트로 굳힌다
- `web/app.py` 의 라벨을 "월 요금(원)" 으로 되돌린다 → 동료가 일부러 바꾼 화면을 없앤다
- 화면 쪽에 `max(0, …)` 만 덧댄다 → 정률 150% 쿠폰이 오류가 아니라 0원으로 통과한다(옳은 수정은 400 오류)

**막히면**
- `lab4_change.py` 가 "바꿀 곳을 찾지 못했습니다" → 실습③ 에서 `web/app.py` 가 바뀐 것. `git checkout origin/main -- web/app.py` → 커밋 → 다시 실행
- 제품 버그가 안 보인다 → 예시 8 테스트가 없는 것. `cp instructor/e2e/spec-examples.spec.ts e2e-ts/tests/`
- 되돌리기: `python tools/lab4_change.py --undo` → `git checkout -- e2e-ts/pages`. 백업은 `--undo` 한 번에 지워지므로, 그 뒤에 또 꼬이면 `git checkout HEAD~1 -- web/app.py`

---

## 실습⑤ 우리 팀 핵심 흐름 1개 (15분)

**목표**: 오늘 한 것을 내 서비스에. 틀리면 제일 아픈 흐름 하나(가입 · 결제 · 권한 · 알림 …)를 고른다.

1. 흐름 고르기 (1분)
2. `specs/TEMPLATE.md` 를 `specs/<내 흐름>.md` 로 복사해 4절에 AC 5개: `- [ ] AC-n: 입력 → 기대 결과` (3분)
   - AI 에게 초안을 받아도 됩니다. 단 기대값 · 경계 · `[확인 필요]` 는 내가 읽고 고칩니다 — AI 가 서로 부딪히는 AC 나 추측한 오류 문구를 확정값처럼 쓰는 일이 있습니다.
   - (선택) 큰 기능이면 2절에 우선순위 `P1 · P2` 를 나누고, 4절 줄 앞에 `[P1]` · `[P2]` 를 붙입니다(예: `- [ ] [P1] AC-1: …`). P1 만 만들어도 따로 테스트되고 쓸 수 있어야 하고, 무엇을 P1 에 둘지는 틀렸을 때의 피해 크기로 사람이 정합니다. 작은 기능이면 그 줄은 지웁니다.
3. 어디서 확인할지 나눠 같은 파일 6절 '테스트 계획' 에 적기 (4분)
   - **웹 · 백엔드**: 화면(Playwright)으로 볼 것 1~2개, 나머지는 API · 단위 테스트로
   - **앱**: `prompts/07_앱_흐름_초안.md` — **웹 채팅이나 빈 폴더에서** 보냅니다(키트 폴더에서 열면 AI 가 키트 앱을 읽고 '해지 화면이 없다' 며 표를 비웁니다). 화면 요소 **id 계약 표** 5개를 먼저 만들고, 그 id 로만 **Maestro 흐름 초안**을 쓰게 한다 (본보기: `maestro/spec-example-8.yaml`). AI 가 낸 표와 초안은 명세 6절 아래에 붙여 둔다. 실행은 팀에 돌아가서.
4. `AGENTS.md` 5줄 — 우리 팀 것을 새로: 명령 1 · 금지 2 · '왜' 2 (분류 규칙 포함). 키트의 `AGENTS.md` 는 본보기이니 덮어쓰지 말고, `specs/<내 흐름>.md` 맨 아래에 `## AGENTS.md 초안` 으로 적습니다. 사람이 직접, 짧게 (2분)
5. 나눠 보기 (5분) — 두세 명이 화면을 띄워 AC 5개를 읽고, 강사와 옆 사람이 빈칸(기대값이 숫자인가 · 경계와 오류가 있나 · 모르는 건 `[확인 필요]` 인가)을 하나씩 짚습니다. 회사 내부 서비스 이름이나 실제 고객 데이터는 화면에 띄우지 않습니다.

**숙제**: 다음 스프린트 첫 PR 에 E2E 1개 + CI 관문(키트의 `e2e-ts/` 와 `.github/` 를 복사해서 시작). 출시 전에는 `specs/RELEASE_CHECKLIST.md` 같은 점검 리스트를 QA 와 함께.

---

## 보너스

**API 테스트를 더 써 보기 (백엔드 개발자라면 여기가 본업)** — 화면 없이 명세의 규칙을 API 로 하나씩 잠급니다. AI 에게 `prompts/06` 의 API 약속과 명세를 주고 이렇게 시켜 보세요.
```
명세의 규칙마다 API 테스트를 하나씩 더 만들어 줘. e2e-ts/tests/api-rules.spec.ts 에.
- 정률 쿠폰 150% → 400 (R6), 월 요금 -1 → 400, 필수 필드(price)가 빠진 요청 → 400
- 31일 달 · 윤년 2월 · 지난달부터 이용 — 기대값은 명세 표에서만
- 오류는 상태 코드와 error 가 비어 있지 않은지만 본다. 테스트 파일만 만들고 멈춰.
```
`npx playwright test api-rules` — 1~2초에 끝납니다. 이게 계약 테스트의 시작입니다: **명세(계약) → API 테스트 → 구현**. 앱 화면이 바뀌어도 이 테스트는 깨지지 않습니다.

**같은 버그를 앱 테스트 도구 Maestro 로** — Java 17 이상과 [Maestro CLI](https://docs.maestro.dev) 가 필요합니다. `python web/app.py` 를 띄운 뒤 다른 터미널에서 `maestro test maestro/spec-example-8.yaml`. 고치기 전 코드면 마지막 줄이 FAILED, 고친 뒤면 COMPLETED.

**AI 로 엣지 케이스를 뽑고 뮤테이션으로 채점** — `prompts/보너스_엣지케이스_뮤테이션.md` 로 경계 사례를 뽑고, `python tools/mutate.py --min-score 80` 으로 "코드를 일부러 망가뜨렸을 때 테스트가 잡는 비율" 을 잽니다. 커버리지는 '실행됐다', 뮤테이션은 '잡는다' 입니다.


### 보너스 — Playwright 테스트 에이전트(planner · generator · healer) 따라 하기 (선택, 약 20분)

직접 해 보고 싶으면 아래 순서로 — Claude Code 가 필요합니다.

**목표**: AI 에게 테스트를 만들게 하고(planner → generator) 빨간불을 고치게 해 본다(healer). 고친 결과가 맞는지는 **사람이 `git diff` 로** 판정한다.

Playwright 의 AI 테스트 에이전트 3종(planner · generator · healer)을 돌려 보고, **healer 가 빨간불을 어떻게 '없애는지'** 봅니다. 이 순서는 Claude Code 기준입니다(`--loop=claude`).

**연습용 폴더에서 합니다.** 실습 키트(`sdd-qa-lab`)는 실습③ 에서 버그를 고쳤기 때문에, 거기서 하면 빨간불이 안 나서 healer 가 할 일이 없습니다. 버그가 그대로 있는 복사본이 하나 더 필요합니다. 에이전트가 만드는 `tests/seed.spec.ts` · `.claude/` · `.mcp.json` 도 실습 키트에 섞이지 않습니다.

**1) 연습용 폴더 받기** — SourceTree 로 같은 저장소를 한 번 더 받습니다. 받을 폴더 이름만 `agents-practice` 로 합니다(실습 키트와 다른 곳). 두 번째 휴식 때 미리 받아 두면 빠릅니다. 그다음 `agents-practice` 안의 `e2e-ts` 폴더에서 터미널을 열고
```bash
npm install
```
(브라우저는 이미 받아 두었으니 다시 받지 않습니다. 맥은 이 폴더에도 venv 를 만들어 켠 터미널에서 합니다 — planner 가 앱을 띄울 때 `python` 이 필요합니다: `agents-practice` 에서 `python3 -m venv .venv` → `source .venv/bin/activate`)

**2) 에이전트 만들기** — 같은 `e2e-ts` 폴더에서
```bash
npx playwright init-agents --loop=claude
```
→ `e2e-ts` 안에 `.claude/agents/` 3개 · `.mcp.json` · `specs/` · `tests/seed.spec.ts` 가 생깁니다.

**3) seed 채우기** — `tests/seed.spec.ts` 의 `// generate code here.` 자리에
```ts
test.describe('Test group', () => {
  test('seed', async ({ page }) => {
    await page.goto('/');      // ← 이 한 줄
  });
});
```

**4) 기준점 커밋** — 나중에 `git diff` 로 AI 가 바꾼 것만 보려고
```bash
git add -A; git commit -m "에이전트 + seed"
```

**5) 그 폴더에서 Claude Code** — VS Code → 파일 → 폴더 열기 → `agents-practice` 안의 `e2e-ts` → 그 창에서 Claude Code 새로 열기 → MCP 서버를 쓸지 물으면 허락 → `/agents` 에 playwright-test-planner · generator · healer 3개가 보이면 준비 끝. (터미널이라면 `e2e-ts` 에서 `claude`)

**6) planner 에게** — Claude Code 채팅창에 아래 다섯 줄 그대로(입력 넷과 기대값을 빼면 엉뚱한 시나리오를 골라 버그를 못 잡습니다)
```
playwright-test-planner 에이전트로 요금 계산 화면을 살펴보고,
월 요금 3000 · 이용 시작일 2026-09-21 · 청구월 2026-09 ·
정액 쿠폰 5000 을 넣고 계산하는 시나리오 하나만 계획해 줘.
기대 결과는 '청구 금액: 0원' 이야 (명세 4절 8번 줄, 음수 금지).
seed 는 tests/seed.spec.ts
```
"시나리오 하나만" 과 기대 결과 줄을 꼭 넣습니다. 빼고 시켰더니 계획을 18개 만들고, 기대값은 저장소에서 강사용 정답(`instructor/`)을 찾아 썼습니다.

**7) 계획 파일을 열어 기대값 확인** — `specs/` 아래에 `*.plan.md` 가 생깁니다(예: `billing-floor-zero.plan.md` — 이름은 실행마다 다릅니다). 기대값이 화면 값(-4,000원)으로 적혀 있으면 명세 값으로 고쳐 저장합니다 — 계획이 곧 정답표입니다. `e2e-ts/e2e-ts/specs/` 처럼 폴더가 한 번 더 겹친 곳에 생기기도 합니다 — `specs/` 에 없으면 그 아래를 찾습니다.

**8) generator 에게** (계획 파일 이름이 다르면 그 이름으로. `already used` 가 나오면 planner 가 띄운 앱이 남은 것이니 그 창 · 터미널부터 끕니다)
```
playwright-test-generator 에이전트로
specs/billing-floor-zero.plan.md 를 테스트 코드로 만들어 줘
```

**9) 돌려 보기** — 터미널, `e2e-ts` 에서. 빨강이면 버그를 잡은 것입니다. 다음 단계와 비교하려고 커밋해 둡니다.
```bash
npx playwright test tests/billing-floor-zero.spec.ts   # 파일 이름은 계획 이름대로 → 1 failed: Expected "청구 금액: 0원" · Received "청구 금액: -4,000원"
git add -A; git commit -m "generator 테스트"
```

**10) healer 에게** — 그리고 **반드시 `git diff`**
```
playwright-test-healer 에이전트로 실패하는 테스트를 고쳐 줘
```
```bash
git diff
npx playwright test
```
healer 는 "원인은 테스트가 아니라 앱 버그라서, 기대값은 바꾸지 않았습니다" 라고 보고했지만, `test` 를 `test.fixme` 로 바꿔 건너뛰게 했습니다.
```diff
-  test('정액 쿠폰이 요금보다 크면 청구 금액은 0원', async ({ page }) => {
+  // APP BUG: 명세 R5(청구 금액 0원 바닥)와 달리 앱이
+  //   "청구 금액: -4,000원" 을 표시한다. … 앱 수정 후 fixme 제거.
+  test.fixme('정액 쿠폰이 요금보다 크면 청구 금액은 0원', async ({ page }) => {
```
```
  -  1 tests\billing-floor-zero.spec.ts:9:8 › … 청구 금액은 0원
  ok 2 tests\smoke.spec.ts:5:5 › 9월 한 달을 다 쓰면 10,000원
  ok 3 tests\seed.spec.ts:4:7 › Test group › seed

  1 skipped
  2 passed
```
실패 0개, CI 는 초록 — 리포트에서 버그가 '건너뜀' 으로 사라집니다. 그래서 **제품 버그면 healer 를 쓰지 않습니다.** 썼다면 `git diff` 에서 `fixme` · `skip` · 기대값 변경을 보고, 앱을 고친 뒤 `fixme` 를 지워 되돌립니다. 왜 그랬는지는 `.claude/agents/playwright-test-healer.md` 에 있습니다 — "Fixing assertions and expected values", "mark this test as test.fixme()", "Do not ask user questions".

**healer 를 써도 되는 때** — 빨간불은 고치기 전에 넷으로 나눕니다. **화면 변경**(버튼 · 칸 이름이 바뀌어 못 찾음)이면 healer 가 고쳐도 됩니다 — 그래도 `git diff`. **제품 버그**(화면은 그대로인데 값이 명세와 다름)면 healer 를 쓰지 않고 코드를 고칩니다. **불안정**(다시 돌리면 통과)은 기다리는 방법을, **환경**(서버 · 네트워크)은 환경을 고칩니다.

**막히면**: `/agents` 에 없다 → 연 폴더가 `e2e-ts` 인지 확인하고 Claude Code 를 새로 연다 · MCP 연결 실패 → `node -v` 20 이상 · Playwright 1.56 이상 · `.playwright-mcp/` 가 생긴다 → 에이전트 기록이니 `.gitignore` 에 넣는다.

다 했으면 연습 폴더(`agents-practice`)를 통째로 지웁니다.

---

## 더 보기 — 지금 명세 주도(SDD)로 개발 중인 공개 저장소

명세 → 작업 → PR 이 명세를 가리키는 흐름을 실제 프로젝트에서 열어 보세요. 모두 실제 제품입니다 (2026-10-05 확인).

| 저장소 | 도구 | 열어 볼 곳 |
|---|---|---|
| [radius-project/radius](https://github.com/radius-project/radius) (CNCF, Go) | Spec Kit | 명세 `specs/004-graph-dependency-edges/spec.md` → [PR #12479](https://github.com/radius-project/radius/pull/12479) — 첫 커밋 메시지 "Phase 1 of spec 004" · Files changed 에 명세와 코드가 함께 |
| [meshtastic/Meshtastic-Android](https://github.com/meshtastic/Meshtastic-Android) (스토어 배포 앱) | Spec Kit | `specs/` 폴더에 기능 명세 16개 — 폴더 자체가 로드맵 · [PR #5939](https://github.com/meshtastic/Meshtastic-Android/pull/5939) 은 lockdown-mode 명세 10개 파일이 코드와 함께 들어왔다 |
| [safe-global/safe-wallet-monorepo](https://github.com/safe-global/safe-wallet-monorepo) (지갑) | Spec Kit | `specs/004-proposer-multisig-validation/spec.md` 의 Clarifications · Edge Cases · Out of Scope (브랜치 dev) · [PR #7028](https://github.com/safe-global/safe-wallet-monorepo/pull/7028) 은 명세 16개 파일 동반 |
| [aws-samples/eks-multi-cluster-gitops](https://github.com/aws-samples/eks-multi-cluster-gitops) | Kiro (EARS) | `.kiro/specs/component-version-upgrade/` — tasks.md 의 `_Requirements: 1.2, 1.3_` 역참조 → [PR #127](https://github.com/aws-samples/eks-multi-cluster-gitops/pull/127) |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | OpenSpec | `openspec/changes/add-version-command/` → [PR #2001](https://github.com/Fission-AI/OpenSpec/pull/2001) 변경 제안 + 코드 + 테스트 |
| [kubernetes/enhancements](https://github.com/kubernetes/enhancements) | KEP (사람이 쓰는 명세) | 사이드카 컨테이너 [KEP PR #3761](https://github.com/kubernetes/enhancements/pull/3761) → 구현 [kubernetes#116429](https://github.com/kubernetes/kubernetes/pull/116429) |

---

## 오늘의 체크리스트

- **명세** — [ ] 규칙에 번호 · [ ] AC 에 숫자 기대값 · [ ] 테스트로 못 옮기는 AC 는 고친다 · [ ] 모르면 `[확인 필요]`
- **E2E** — [ ] 핵심 흐름만 · [ ] 화면 조작은 `pages/` 에 · [ ] 사람이 보는 이름(앱은 id)으로 찾기 · [ ] 실패하면 리포트 · 트레이스부터
- **관문** — [ ] AI 편집마다 테스트 · [ ] PR 에서 CI 필수 + 브랜치 보호 · [ ] 테스트 변경은 따로 승인 · [ ] 출시 전 QA 점검 리스트 (Go / No-Go)
- **AI 검증** — [ ] 실패는 분류부터 · [ ] 제품 버그면 테스트 수정 금지 · [ ] healer 처럼 '고쳐 주는' AI 를 썼으면 `git diff` 에서 fixme · skip · 기대값 변경 · [ ] 쓴 AI ≠ 검증 AI · [ ] 최종 판단은 사람

`instructor/` 는 막혔을 때 쓰는 정답입니다. 먼저 보지 말고 막혔을 때만 여세요. 강의가 끝난 뒤 혼자 다시 해 볼 때는 [instructor/README.md](instructor/README.md) 를 보세요. 단계마다 실제 출력, AI 의 실제 답, 정답이 들어 있습니다.
