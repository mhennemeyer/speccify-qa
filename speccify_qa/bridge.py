"""QA-Brücke (Speccify Spec 039): die laufende App von außen steuern.

Die App lauscht nur mit `--qa-bridge=<port>` auf 127.0.0.1 und verlangt ein
Bearer-Token. Beides steht in `<tmp>/speccify-qa-bridge.json`, das die App
beim Start schreibt; alternativ `SPECCIFY_QA_BRIDGE_URL` und
`SPECCIFY_QA_TOKEN` in der Umgebung. JavaScript läuft als Funktionsrumpf im
gewählten Fenster (`return …`, `await` erlaubt).
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


class BridgeError(RuntimeError):
    """Die Brücke hat eine Anfrage abgelehnt oder das Skript ist gescheitert."""


def discovery_path() -> Path:
    return Path(tempfile.gettempdir()) / "speccify-qa-bridge.json"


def discover() -> tuple[str, str] | None:
    """(URL, Token) aus Umgebung oder Discovery-Datei; `None` ohne Brücke."""
    url = os.environ.get("SPECCIFY_QA_BRIDGE_URL")
    token = os.environ.get("SPECCIFY_QA_TOKEN")
    if url and token:
        return url.rstrip("/"), token
    path = discovery_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return str(data["url"]).rstrip("/"), str(data["token"])
    except (ValueError, KeyError):
        return None


@dataclass
class Bridge:
    url: str
    token: str
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> Bridge | None:
        found = discover()
        return cls(*found) if found else None

    # --- Transport -------------------------------------------------------

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> httpx.Response:
        headers = {"authorization": f"Bearer {self.token}"}
        response = httpx.request(
            method, self.url + path, json=payload, headers=headers, timeout=self.timeout
        )
        return response

    def _json(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        response = self._request(method, path, payload)
        try:
            body = response.json()
        except ValueError as exc:
            raise BridgeError(
                f"{method} {path}: keine JSON-Antwort ({response.status_code})"
            ) from exc
        if response.status_code >= 400 or not body.get("ok", False):
            raise BridgeError(f"{method} {path}: {body.get('error', response.status_code)}")
        return body

    # --- Befehle ---------------------------------------------------------

    def alive(self) -> bool:
        try:
            return bool(self._json("GET", "/health").get("ok"))
        except (httpx.HTTPError, BridgeError):
            return False

    def health(self) -> dict[str, Any]:
        return self._json("GET", "/health")

    def windows(self) -> list[dict[str, Any]]:
        return list(self._json("GET", "/windows")["windows"])

    def eval(self, window: str, js: str, *, timeout_ms: int = 10_000) -> Any:
        """Funktionsrumpf im Fenster ausführen; Ergebnis (JSON-fähig) zurück."""
        body = self._json("POST", "/eval", {"window": window, "js": js, "timeout_ms": timeout_ms})
        return body.get("value")

    def invoke(self, window: str, command: str, args: dict[str, Any] | None = None) -> Any:
        """Tauri-Befehl aus dem Fenster heraus aufrufen (z. B. `project_current`)."""
        body = self._json(
            "POST", "/invoke", {"window": window, "command": command, "args": args or {}}
        )
        return body.get("value")

    def focus(self, window: str) -> None:
        self._json("POST", "/focus", {"window": window})

    def screenshot(self, window: str, target: Path) -> Path:
        response = self._request("POST", "/screenshot", {"window": window})
        if response.status_code != 200:
            raise BridgeError(f"screenshot: {response.text}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)
        return target

    def wait_for(
        self, window: str, js: str, *, timeout: float = 10.0, interval: float = 0.2
    ) -> Any:
        """Skript wiederholen, bis es einen wahren Wert liefert; sonst BridgeError."""
        deadline = time.monotonic() + timeout
        last: Any = None
        while time.monotonic() < deadline:
            last = self.eval(window, js)
            if last:
                return last
            time.sleep(interval)
        raise BridgeError(
            f"Bedingung nicht erfüllt nach {timeout:.0f} s: {js[:120]!r} (zuletzt {last!r})"
        )
