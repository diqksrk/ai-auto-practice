"""요금 계산 화면 (E2E 시연용, 표준 라이브러리만 사용).

실행:  python web/app.py   →  브라우저에서 http://127.0.0.1:8000
"""
from __future__ import annotations

import json
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from billing.proration import Coupon, calculate_charge  # noqa: E402

PAGE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>구독 요금 계산</title>
<style>
  body { font-family: sans-serif; max-width: 420px; margin: 40px auto; }
  label { display: block; margin-top: 12px; }
  input, select { width: 100%; padding: 6px; box-sizing: border-box; }
  button { margin-top: 16px; padding: 8px 16px; }
  #result { margin-top: 16px; font-size: 20px; font-weight: bold; }
</style>
</head>
<body>
<h1>구독 요금 계산</h1>
<label>월 요금(원) <input id="price" type="number" value="10000"></label>
<label>이용 시작일 <input id="start" type="date"></label>
<label>이용 종료일 (해지 안 했으면 비움) <input id="end" type="date"></label>
<label>청구월 <input id="month" type="month"></label>
<label>쿠폰
  <select id="coupon-kind">
    <option value="">없음</option>
    <option value="fixed">정액(원)</option>
    <option value="percent">정률(%)</option>
  </select>
</label>
<label>쿠폰 값 <input id="coupon-value" type="number" value="0"></label>
<button id="calc">계산</button>
<div id="result" role="status"></div>
<script>
document.getElementById("calc").addEventListener("click", async () => {
  const body = {
    price: Number(document.getElementById("price").value),
    start: document.getElementById("start").value,
    end: document.getElementById("end").value || null,
    month: document.getElementById("month").value,
    coupon_kind: document.getElementById("coupon-kind").value || null,
    coupon_value: Number(document.getElementById("coupon-value").value),
  };
  const res = await fetch("/api/charge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  const result = document.getElementById("result");
  if (res.ok) {
    result.textContent = "청구 금액: " + data.amount.toLocaleString("ko-KR") + "원";
  } else {
    result.textContent = "오류: " + data.error;
  }
});
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/charge":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            request = json.loads(self.rfile.read(length))
            year, month = (int(part) for part in request["month"].split("-"))
            coupon = None
            if request.get("coupon_kind"):
                coupon = Coupon(kind=request["coupon_kind"], value=int(request["coupon_value"]))
            amount = calculate_charge(
                int(request["price"]),
                date.fromisoformat(request["start"]),
                date.fromisoformat(request["end"]) if request.get("end") else None,
                year,
                month,
                coupon,
            )
        except (KeyError, ValueError) as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(200, {"amount": amount})

    def _send_json(self, status, payload):
        self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # 실습 중 콘솔을 조용하게


def make_server(port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    server = make_server()
    print("http://127.0.0.1:8000 에서 실행 중 (종료: Ctrl+C)")
    server.serve_forever()
