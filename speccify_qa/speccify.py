"""Adapter zur Speccify-App: was sich von außen deterministisch prüfen lässt.

Prüfstufe 1 (Verträge): der Desktop-UI-MCP der laufenden App und das Web-Board
antworten über HTTP/JSON-RPC. Prüfstufe 2 (echte App) braucht die
QA-Brücke aus Spec 003 — bis dahin bleibt sie hier ein bewusst leerer Platz.
"""

from __future__ import annotations

from typing import Any

import httpx

MCP_HEADERS = {
    "content-type": "application/json",
    "accept": "application/json, text/event-stream",
}


def mcp_call(
    url: str,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    token: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Ein JSON-RPC-Aufruf gegen einen zustandslosen Streamable-HTTP-MCP."""
    headers = dict(MCP_HEADERS)
    if token:
        headers["authorization"] = f"Bearer {token}"
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    response = httpx.post(
        url.rstrip("/") + ("" if url.endswith("/mcp") else "/mcp"),
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    body = response.json()
    if "error" in body:
        raise RuntimeError(f"{method}: {body['error']}")
    return body.get("result", {})


def mcp_tools(url: str, *, token: str | None = None) -> list[str]:
    result = mcp_call(url, "tools/list", token=token)
    return sorted(tool["name"] for tool in result.get("tools", []))


def reachable(url: str, timeout: float = 3.0) -> bool:
    try:
        httpx.get(url, timeout=timeout)
        return True
    except httpx.HTTPError:
        return False


def mcp_reachable(url: str, *, token: str | None = None) -> bool:
    try:
        mcp_tools(url, token=token)
        return True
    except (httpx.HTTPError, RuntimeError, ValueError):
        return False
