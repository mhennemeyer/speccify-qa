"""Umgebungen aus `environments.yaml`: Adressen der Prüfziele, nie Secrets."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_ENV_RE = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


def _expand(value: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return os.environ.get(match.group(1), match.group(2) or "")

    return _ENV_RE.sub(replace, value)


@dataclass(frozen=True)
class Environment:
    name: str
    label: str
    speccify: dict[str, str]
    secrets: tuple[str, ...]
    hints: dict[str, str] = field(default_factory=dict)

    def target(self, key: str) -> str:
        try:
            return self.speccify[key]
        except KeyError as exc:
            raise KeyError(
                f"Umgebung {self.name}: kein Prüfziel `{key}` in environments.yaml"
            ) from exc

    @property
    def repo(self) -> Path:
        return Path(self.speccify.get("repo", "../speccify")).expanduser().resolve()

    def missing_secrets(self) -> list[str]:
        return [name for name in self.secrets if not os.environ.get(name)]


def load_environments(path: Path | None = None) -> tuple[str, dict[str, Environment]]:
    path = path or Path(__file__).resolve().parent.parent / "environments.yaml"
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    environments: dict[str, Environment] = {}
    for name, entry in (raw.get("environments") or {}).items():
        speccify = {k: _expand(str(v)) for k, v in (entry.get("speccify") or {}).items()}
        environments[name] = Environment(
            name=name,
            label=str(entry.get("label") or name),
            speccify=speccify,
            secrets=tuple(entry.get("secrets") or []),
            hints={k: str(v) for k, v in (entry.get("hints") or {}).items()},
        )
    return str(raw.get("default_environment") or next(iter(environments), "local")), environments


def current_environment(path: Path | None = None) -> Environment:
    default, environments = load_environments(path)
    name = os.environ.get("SPECCIFY_QA_ENV", default)
    try:
        return environments[name]
    except KeyError as exc:
        raise KeyError(
            f"Unbekannte Umgebung `{name}` (bekannt: {', '.join(environments)})"
        ) from exc
