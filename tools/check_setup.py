"""강의 전 환경 점검 — 한 줄로 실행: python tools/check_setup.py

실습에 필요한 것이 다 있는지 보고, 없으면 무엇을 하면 되는지 알려 줍니다. 표준 라이브러리만 씁니다.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E2E = ROOT / "e2e-ts"
problems = 0


def report(ok: bool, what: str, fix: str = "") -> None:
    global problems
    print(("  [OK] " if ok else "  [!!] ") + what + ("" if ok or not fix else f"\n        → {fix}"))
    if not ok:
        problems += 1


def run(*cmd: str, cwd: Path = E2E) -> str:
    exe = shutil.which(cmd[0])
    if not exe:
        return ""
    try:
        # git 은 경로를 UTF-8 로 내보낸다 — 한글 폴더에서 윈도우 기본(cp949)으로 읽으면 깨진다
        result = subprocess.run([exe, *cmd[1:]], capture_output=True, encoding="utf-8", errors="replace",
                                timeout=60, cwd=cwd)
        return (result.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def is_kit_repo() -> bool:
    top = run("git", "rev-parse", "--show-toplevel", cwd=ROOT)
    if not top:
        return False
    try:
        return os.path.samefile(top, ROOT)
    except OSError:
        return False


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    print("실습 환경 점검\n")

    report(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} (3.10 이상 필요)", "python.org 에서 3.10 이상 설치")
    try:
        import pytest  # noqa: F401
        report(True, "pytest 설치됨")
    except ImportError:
        report(False, "pytest 없음", f'"{sys.executable}" -m pip install -r requirements.txt')
    has_git = shutil.which("git") is not None
    report(has_git, "git", "git-scm.com 에서 설치")
    if has_git:
        name = run("git", "config", "user.name", cwd=ROOT)
        email = run("git", "config", "user.email", cwd=ROOT)
        report(bool(name and email), "git 이름 · 이메일 설정 (실습에서 커밋합니다)",
               'git config --global user.name "내 이름"  →  git config --global user.email "내 메일"')
        report(is_kit_repo(), "키트 폴더가 git 저장소",
               "키트 폴더에서 git init → git add . → git commit -m \"시작\"")

    # E2E 는 테스트 전에 앱을 `${PYTHON:-python} ../web/app.py` 로 띄운다 (e2e-ts/playwright.config.ts)
    app_python = os.environ.get("PYTHON") or "python"
    app_major = run(app_python, "-c", "import sys; print(sys.version_info[0])", cwd=ROOT)
    report(app_major == "3", f"E2E 가 앱을 띄울 파이썬 명령 '{app_python}'",
           'python 명령이 없으면 E2E 를 PYTHON=py npx playwright test 로 (PowerShell: $env:PYTHON="py"; npx playwright test)')

    node = run("node", "-v")
    major = int(node.lstrip("v").split(".")[0]) if node.startswith("v") else 0
    report(major >= 20, f"Node.js {node or '없음'} (20 이상 필요)", "nodejs.org 에서 LTS(20 이상) 설치. nvm 을 쓰면 nvm install 20 → nvm use 20")
    report(shutil.which("npx") is not None, "npx", "Node.js 를 설치하면 같이 생깁니다")

    package = E2E / "node_modules" / "@playwright" / "test" / "package.json"
    if package.exists():
        version = json.loads(package.read_text(encoding="utf-8"))["version"]
        report(True, f"@playwright/test {version} 설치됨")
    else:
        report(False, "@playwright/test 없음", "cd e2e-ts → npm install → npx playwright install chromium (약 300MB, 미리) → 이 점검을 한 번 더")

    browsers_json = E2E / "node_modules" / "playwright-core" / "browsers.json"
    if browsers_json.exists():
        revision = next(b["revision"] for b in json.loads(browsers_json.read_text(encoding="utf-8"))["browsers"]
                        if b["name"] == "chromium")
        home = Path.home()
        caches = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""),
                  os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright"),
                  str(home / "Library" / "Caches" / "ms-playwright"), str(home / ".cache" / "ms-playwright")]
        found = any(c and (Path(c) / f"chromium-{revision}").exists() for c in caches)
        report(found, f"Playwright 브라우저 chromium-{revision}", "cd e2e-ts → npx playwright install chromium (약 300MB, 강의장 와이파이 말고 미리)")

    with socket.socket() as s:
        busy = s.connect_ex(("127.0.0.1", 8000)) == 0
    report(not busy, "8000번 포트 비어 있음", "따로 띄운 python web/app.py 가 있으면 Ctrl+C 로 끄세요 (E2E 가 앱을 직접 띄웁니다)")

    print("\n준비 끝 — python -m pytest 와 (e2e-ts 에서) npx playwright test 를 돌려 보세요." if not problems
          else f"\n고칠 것 {problems}가지가 있습니다. 위의 → 를 따라 하세요.")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
