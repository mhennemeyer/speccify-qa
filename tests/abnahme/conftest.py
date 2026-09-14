"""Fixtures für Abnahmen: Marker `abnahme(name, stand=None)` registrieren."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "abnahme(name, stand=None): Abnahme-Test")
