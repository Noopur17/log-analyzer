from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from analyzer.service import analyze_text


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = PROJECT_ROOT / "web"


def analyze_payload(payload: dict) -> dict:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise ValueError("request must include non-empty 'text'")

    raw_levels = payload.get("levels") or []
    if isinstance(raw_levels, str):
        levels = [raw_levels]
    else:
        levels = [str(level) for level in raw_levels]

    return analyze_text(
        text=text,
        levels=levels or None,
        since=payload.get("since"),
        until=payload.get("until"),
        contains=payload.get("contains"),
        top_messages=int(payload.get("top_messages", 5)),
    )


class LogAnalyzerHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(
            *args,
            directory=str(WEB_ROOT if directory is None else directory),
            **kwargs,
        )

    def do_POST(self) -> None:
        if self.path != "/api/analyze":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            response = analyze_payload(payload)
            self._send_json(HTTPStatus.OK, response)
        except json.JSONDecodeError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "request body must be valid JSON"},
            )
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), LogAnalyzerHTTPRequestHandler)
    print("Serving Log Analyzer UI on http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
