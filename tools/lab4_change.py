"""실습④: 동료의 PR 이 들어왔다고 가정하고 web/app.py 를 바꿉니다.

PR 설명(동료가 쓴 것): "화면 문구 정리 + 쿠폰 계산 리팩터링"
무엇이 바뀌었는지는 적용한 뒤 커밋하고 git show 로 직접 보세요.

사용법:
    python tools/lab4_change.py          # PR 적용
    python tools/lab4_change.py --undo   # web/app.py 를 원래대로 (e2e-ts/pages/ 를 고쳤다면 그건 git 으로 되돌린다)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "web" / "app.py"
BACKUP = ROOT / ".lab4_backup" / "app.py"

LABEL_BEFORE = '<label>월 요금(원) <input id="price"'
LABEL_AFTER = '<label>구독료(원) <input id="price"'

CALL_BEFORE = """                month,
                coupon,
            )
"""
CALL_AFTER = """                month,
                None,
            )
            amount = _apply_coupon_quick(amount, coupon)  # 리팩터링: 쿠폰 계산을 화면 쪽으로 옮김
"""

HELPER_ANCHOR = "class Handler(BaseHTTPRequestHandler):"
HELPER = '''def _apply_coupon_quick(amount, coupon):
    """쿠폰 적용 (리팩터링하면서 계산 모듈에서 옮겨 옴)."""
    if coupon is None:
        return amount
    if coupon.kind == "fixed":
        return amount - coupon.value
    return amount - amount * coupon.value // 100


'''


def apply() -> int:
    raw = APP.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw  # 윈도우에서 git 이 줄바꿈을 CRLF 로 바꿔 놓았어도 동작하게
    source = raw.replace("\r\n", "\n")
    if LABEL_AFTER in source:
        print("이미 적용되어 있습니다. 되돌리려면 --undo")
        return 1
    for needle in (LABEL_BEFORE, CALL_BEFORE, HELPER_ANCHOR):
        if needle not in source:
            print(f"web/app.py 에서 바꿀 곳을 찾지 못했습니다: {needle.strip()[:40]}")
            return 2
    BACKUP.parent.mkdir(exist_ok=True)
    shutil.copyfile(APP, BACKUP)
    source = source.replace(LABEL_BEFORE, LABEL_AFTER, 1)
    source = source.replace(CALL_BEFORE, CALL_AFTER, 1)
    source = source.replace(HELPER_ANCHOR, HELPER + HELPER_ANCHOR, 1)
    if crlf:
        source = source.replace("\n", "\r\n")
    APP.write_bytes(source.encode("utf-8"))
    print("동료의 PR 을 적용했습니다 (web/app.py 변경).")
    print("  0) git add web/app.py 한 뒤 git commit -m \"동료 PR\"   → 먼저 커밋해 두세요")
    print("  1) python -m pytest                          → 단위 테스트는?")
    print("  2) cd e2e-ts; npx playwright test; cd ..     → E2E 는?")
    return 0


def undo() -> int:
    if not BACKUP.exists():
        print("되돌릴 백업이 없습니다.")
        return 1
    shutil.copyfile(BACKUP, APP)
    BACKUP.unlink()
    BACKUP.parent.rmdir()
    print("web/app.py 를 PR 적용 전으로 되돌렸습니다.")
    print("  e2e-ts/pages/ 를 고쳤다면 그것도 되돌리세요: git checkout -- e2e-ts/pages")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # Git Bash(cp949) 에서도 한글이 깨지지 않게
    except (AttributeError, ValueError):
        pass
    sys.exit(undo() if "--undo" in sys.argv else apply())
