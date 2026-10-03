from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True, slots=True)
class HttpResult:
    status_code: int
    payload: Mapping[str, Any]


class JsonHttpTransportError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = {} if payload is None else payload


class JsonHttpTransport(Protocol):
    def post_json(
        self,
        url: str,
        payload: Mapping[str, Any],
        *,
        headers: Mapping[str, str],
        timeout_s: float,
    ) -> HttpResult:
        """POST a JSON payload without logging headers or secrets."""


class UrllibJsonTransport:
    def post_json(
        self,
        url: str,
        payload: Mapping[str, Any],
        *,
        headers: Mapping[str, str],
        timeout_s: float,
    ) -> HttpResult:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", **dict(headers)},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout_s) as response:
                status_code = int(response.status)
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            parsed = _safe_json(raw)
            raise JsonHttpTransportError(
                f"HTTP {exc.code}",
                status_code=int(exc.code),
                payload=parsed,
            ) from None
        except URLError as exc:
            reason = type(exc.reason).__name__
            raise JsonHttpTransportError(f"Network transport error: {reason}") from None

        return HttpResult(status_code=status_code, payload=_safe_json(raw))


def _safe_json(raw: str) -> Mapping[str, Any]:
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw[:512]}
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {"data": value}
