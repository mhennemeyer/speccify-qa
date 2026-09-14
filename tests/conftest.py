"""Gemeinsame Fixtures: Umgebung, Prüfziele, Skip statt Fail.

Abnahmen (`tests/abnahme`) laufen nicht mit der Regression — nur ausdrücklich
über `speccify-qa abnahme run <name>` oder `pytest tests/abnahme/<name>`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from speccify_qa.environments import Environment, current_environment
from speccify_qa.speccify import mcp_reachable, reachable

ROOT = Path(__file__).resolve().parent.parent


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    abnahme = ROOT / "tests" / "abnahme"
    if abnahme in collection_path.parents or collection_path == abnahme:
        # Nur wenn der Aufruf den Abnahme-Pfad selbst nennt (relativ oder absolut).
        named = [Path(str(arg).split("::")[0]).resolve() for arg in config.args]
        return not any(abnahme == path or abnahme in path.parents for path in named)
    return None


@pytest.fixture(scope="session")
def env() -> Environment:
    return current_environment()


@pytest.fixture(scope="session")
def desktop_ui(env: Environment) -> str:
    url = env.target("desktop_ui")
    if not mcp_reachable(url):
        pytest.skip(
            f"Desktop-UI-MCP nicht erreichbar unter {url} — gebündelte Speccify-App starten."
        )
    return url


@pytest.fixture(scope="session")
def mock_url(env: Environment) -> str:
    url = env.target("mock")
    if not reachable(url):
        pytest.skip(
            f"Mock-UI nicht erreichbar unter {url} — im Speccify-Checkout "
            "`pnpm exec vite --port 1421` in apps/desktop starten."
        )
    return url
