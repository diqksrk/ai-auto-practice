"""아주 작은 뮤테이션 테스트 도구 (표준 라이브러리만 사용).

"테스트가 버그를 정말 잡는가?" 를 확인합니다.
대상 파일의 연산자·숫자를 하나씩 일부러 바꾼 뒤(=변이) 테스트를 돌립니다.
  - 테스트가 실패하면  → 변이를 잡았다 (killed)  : 좋은 테스트
  - 테스트가 통과하면  → 변이가 살아남았다 (survived) : 테스트가 그 줄을 제대로 검증하지 않는다

사용법:
    python tools/mutate.py                          # 기본 대상: src/billing/proration.py
    python tools/mutate.py --min-score 80           # 점수가 80% 미만이면 실패(exit 1) — CI 게이트용
    python tools/mutate.py --target src/billing/proration.py --tests tests

실제 프로젝트에서는 mutmut(Python), PIT(Java), Stryker(JS/TS) 같은 도구를 씁니다.
이 파일은 원리를 보여주는 실습용입니다.
"""
from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

COMPARE_SWAP = {
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
}
BINOP_SWAP = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.FloorDiv,
    ast.FloorDiv: ast.Mult,
    ast.Div: ast.FloorDiv,
}
CALL_SWAP = {"min": "max", "max": "min"}
OP_TEXT = {
    ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!=",
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.FloorDiv: "//", ast.Div: "/",
}


@dataclass
class Mutant:
    node_index: int
    lineno: int
    description: str


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """docstring 은 변이 대상에서 뺀다."""
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                ids.add(id(body[0].value))
    return ids


def find_mutants(source: str) -> list[Mutant]:
    tree = ast.parse(source)
    skip = _docstring_nodes(tree)
    mutants: list[Mutant] = []
    for index, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in COMPARE_SWAP:
            before = type(node.ops[0])
            after = COMPARE_SWAP[before]
            mutants.append(Mutant(index, node.lineno, f"'{OP_TEXT[before]}' → '{OP_TEXT[after]}'"))
        elif isinstance(node, ast.BinOp) and type(node.op) in BINOP_SWAP:
            before = type(node.op)
            after = BINOP_SWAP[before]
            mutants.append(Mutant(index, node.lineno, f"'{OP_TEXT[before]}' → '{OP_TEXT[after]}'"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in CALL_SWAP:
            mutants.append(Mutant(index, node.lineno, f"{node.func.id}() → {CALL_SWAP[node.func.id]}()"))
        elif (
            isinstance(node, ast.Constant)
            and type(node.value) is int
            and id(node) not in skip
        ):
            mutants.append(Mutant(index, node.lineno, f"숫자 {node.value} → {node.value + 1}"))
    return mutants


def apply_mutant(source: str, mutant: Mutant) -> str:
    tree = ast.parse(source)
    for index, node in enumerate(ast.walk(tree)):
        if index != mutant.node_index:
            continue
        if isinstance(node, ast.Compare):
            node.ops[0] = COMPARE_SWAP[type(node.ops[0])]()
        elif isinstance(node, ast.BinOp):
            node.op = BINOP_SWAP[type(node.op)]()
        elif isinstance(node, ast.Call):
            node.func.id = CALL_SWAP[node.func.id]
        elif isinstance(node, ast.Constant):
            node.value = node.value + 1
        break
    return ast.unparse(tree) + "\n"


def run_tests(tests: str, cwd: Path) -> bool:
    """테스트가 전부 통과하면 True."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", tests],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False  # 무한 루프 등 → 잡힌 것으로 본다
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="실습용 뮤테이션 테스트")
    parser.add_argument("--target", default="src/billing/proration.py", help="변이를 넣을 파일")
    parser.add_argument("--tests", default="tests", help="돌릴 테스트 경로")
    parser.add_argument("--min-score", type=float, default=None, help="이 점수(%%) 미만이면 exit 1")
    args = parser.parse_args()

    root = Path.cwd()
    target = root / args.target
    original_bytes = target.read_bytes()  # 되돌릴 때는 바이트 그대로 (줄바꿈 보존)
    original = original_bytes.decode("utf-8")

    if not run_tests(args.tests, root):
        print("변이 전 테스트가 이미 실패합니다. 먼저 테스트를 통과시키세요.")
        return 2

    mutants = find_mutants(original)
    survived: list[Mutant] = []
    print(f"대상: {args.target} · 변이 {len(mutants)}개 · 테스트: {args.tests}\n")
    try:
        for number, mutant in enumerate(mutants, start=1):
            target.write_bytes(apply_mutant(original, mutant).encode("utf-8"))
            passed = run_tests(args.tests, root)
            mark = "살아남음" if passed else "잡힘"
            print(f"  [{number:2d}] {args.target}:{mutant.lineno:<4d} {mutant.description:<22s} {mark}")
            if passed:
                survived.append(mutant)
    finally:
        target.write_bytes(original_bytes)  # 반드시 원래대로 되돌린다

    killed = len(mutants) - len(survived)
    score = 100.0 * killed / len(mutants) if mutants else 100.0
    print(f"\n점수: {killed}/{len(mutants)} 잡힘 = {score:.0f}%")
    if survived:
        print("살아남은 변이 (테스트가 이 줄을 제대로 확인하지 않음):")
        for mutant in survived:
            print(f"  - {mutant.lineno}번째 줄: {mutant.description}")

    if args.min_score is not None and score < args.min_score:
        print(f"\n기준 {args.min_score:.0f}% 미달 → 실패")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
