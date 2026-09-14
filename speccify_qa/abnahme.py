"""Abnahme — ein Ordner je Vorhaben, der nachweist, dass es tut, was es soll.

Modell (aus tec-e2e übernommen, Toyota-frei):

    tests/abnahme/<name>/
        abnahme.yaml     Name, Titel, Bezug (Spec/Ticket/Link), Anlagedatum, Stufen
        plan.md          Kontext für Mensch und Agent: worum geht es, wie wird geprüft
        abnahme.md       Ergebnis des Refinements: Prüfpunkte, was betroffen ist
        checkliste.yaml  menschliche Prüfschritte (Stufe 3) mit Erwartung
        test_*.py        automatische Prüfungen (Stufen 0–2), Marker `abnahme("<name>")`
        ergebnis.json    letzter Lauf: Tests + Checkliste (kein Quellartefakt)

Abnahmen laufen nicht mit der Regression. Ein Prüfschritt der Checkliste
wird nie erfunden: Antworten kommen vom Menschen (interaktiv) oder als
ausdrückliche Angabe (`--antworten 1=ja,2=nein`) mit Namen des Prüfers.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ABNAHME_DIR = Path("tests") / "abnahme"
STUFEN = {0: "Mock-UI", 1: "Verträge (MCP/HTTP)", 2: "echte App", 3: "Mensch"}


class AbnahmeError(Exception):
    """Ordner fehlt oder ist unvollständig."""


@dataclass
class Schritt:
    id: str
    text: str
    erwartung: str
    stufe: int = 3


@dataclass
class Abnahme:
    name: str
    folder: Path
    titel: str
    bezug: dict[str, str] = field(default_factory=dict)
    angelegt: str = ""
    stufen: list[int] = field(default_factory=list)
    schritte: list[Schritt] = field(default_factory=list)

    @property
    def ergebnis_path(self) -> Path:
        return self.folder / "ergebnis.json"

    def ergebnis(self) -> dict[str, Any] | None:
        if not self.ergebnis_path.is_file():
            return None
        return json.loads(self.ergebnis_path.read_text(encoding="utf-8"))


def _valid_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", name))


def load(root: Path, name: str) -> Abnahme:
    folder = root / ABNAHME_DIR / name
    meta_path = folder / "abnahme.yaml"
    if not meta_path.is_file():
        raise AbnahmeError(f"Keine Abnahme `{name}` unter {root / ABNAHME_DIR}")
    try:
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise AbnahmeError(f"{meta_path}: {exc}") from exc
    schritte: list[Schritt] = []
    checklist = folder / "checkliste.yaml"
    if checklist.is_file():
        try:
            raw_steps = (yaml.safe_load(checklist.read_text(encoding="utf-8")) or {}).get(
                "schritte"
            ) or []
        except yaml.YAMLError as exc:
            raise AbnahmeError(f"{checklist}: {exc}") from exc
        for raw in raw_steps:
            schritte.append(
                Schritt(
                    id=str(raw.get("id")),
                    text=str(raw.get("text", "")).strip(),
                    erwartung=str(raw.get("erwartung", "")).strip(),
                    stufe=int(raw.get("stufe", 3)),
                )
            )
    return Abnahme(
        name=name,
        folder=folder,
        titel=str(meta.get("titel") or name),
        bezug={k: str(v) for k, v in (meta.get("bezug") or {}).items()},
        angelegt=str(meta.get("angelegt") or ""),
        stufen=[int(s) for s in (meta.get("stufen") or [])],
        schritte=schritte,
    )


def list_all(root: Path) -> list[Abnahme]:
    base = root / ABNAHME_DIR
    if not base.is_dir():
        return []
    return [load(root, p.name) for p in sorted(base.iterdir()) if (p / "abnahme.yaml").is_file()]


def anlegen(
    root: Path, name: str, *, titel: str, bezug: dict[str, str] | None = None, plan: str = ""
) -> Abnahme:
    if not _valid_name(name):
        raise AbnahmeError("Name: Buchstaben, Ziffern, . _ - (max. 81 Zeichen)")
    folder = root / ABNAHME_DIR / name
    if folder.exists():
        raise AbnahmeError(f"Abnahme `{name}` gibt es schon.")
    folder.mkdir(parents=True)
    today = datetime.now(UTC).date().isoformat()
    (folder / "abnahme.yaml").write_text(
        yaml.safe_dump(
            {
                "name": name,
                "titel": titel,
                "bezug": bezug or {},
                "angelegt": today,
                "stufen": [0, 1, 2, 3],
                "uebernommen": [],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (folder / "plan.md").write_text(
        plan or f"# {titel}\n\nWorum es geht, was fertig ist, wie geprüft wird.\n", encoding="utf-8"
    )
    (folder / "abnahme.md").write_text(
        f"# Abnahme {name}\n\n## Prüfpunkte\n\n- …\n\n## Betroffen\n\n- …\n", encoding="utf-8"
    )
    (folder / "checkliste.yaml").write_text(
        "schritte:\n  - id: 1\n    text: …\n    erwartung: …\n", encoding="utf-8"
    )
    (folder / "__init__.py").write_text("", encoding="utf-8")
    return load(root, name)


def run_tests(
    root: Path, abnahme: Abnahme, *, pytest_args: list[str] | None = None
) -> dict[str, Any]:
    """`pytest` auf den Ordner; das JSON-Ergebnis kommt aus der Zusammenfassung."""
    report = abnahme.folder / ".pytest-report.json"
    cmd = [sys.executable, "-m", "pytest", str(abnahme.folder), "-q", "-rsx", *(pytest_args or [])]
    completed = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False)
    _unhide_venv_pth(root)
    summary = _parse_summary(completed.stdout)
    report.unlink(missing_ok=True)
    return {
        "exit_code": completed.returncode,
        "summary": summary,
        "output_tail": "\n".join(completed.stdout.splitlines()[-40:]),
    }


def _unhide_venv_pth(root: Path) -> None:
    """macOS: nach jedem uv-/pytest-Lauf tragen die `.pth`-Dateien des venv das
    Flag `hidden`, und Python liest sie nicht mehr (tec-e2e-Befund). Hier
    wird es zurückgesetzt, damit der nächste Aufruf nicht ins Leere läuft."""
    if sys.platform != "darwin":
        return
    files = [str(p) for p in (root / ".venv" / "lib").glob("python*/site-packages/*.pth")]
    if files:
        subprocess.run(["chflags", "nohidden", *files], check=False, capture_output=True)


_SUMMARY_RE = re.compile(r"(\d+) (passed|failed|skipped|error|errors|xfailed|xpassed)")


def _parse_summary(output: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in reversed(output.splitlines()):
        if "passed" in line or "failed" in line or "skipped" in line or "error" in line:
            for number, word in _SUMMARY_RE.findall(line):
                counts[word.rstrip("s") if word.startswith("error") else word] = int(number)
            if counts:
                break
    return counts


def parse_antworten(text: str) -> dict[str, str]:
    """`1=ja,2=nein,3=offen` → {"1": "ja", …}; erlaubt sind ja/nein/offen."""
    answers: dict[str, str] = {}
    for part in filter(None, (p.strip() for p in text.split(","))):
        step, sep, value = part.partition("=")
        value = value.strip().lower()
        if not sep or value not in {"ja", "nein", "offen"}:
            raise AbnahmeError(f"Antwort `{part}`: Form <schritt>=ja|nein|offen")
        answers[step.strip()] = value
    return answers


def checkliste_erfassen(
    abnahme: Abnahme,
    *,
    pruefer: str,
    antworten: dict[str, str],
    notizen: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Antworten je Schritt festhalten; unbekannte Schritte sind ein Fehler."""
    known = {s.id for s in abnahme.schritte}
    for step in antworten:
        if step not in known:
            raise AbnahmeError(
                f"Unbekannter Schritt `{step}` (bekannt: {', '.join(sorted(known))})"
            )
    if not pruefer.strip():
        raise AbnahmeError("Prüfer fehlt — eine Checkliste ohne Namen ist kein Nachweis.")
    entries = []
    for schritt in abnahme.schritte:
        entries.append(
            {
                "id": schritt.id,
                "text": schritt.text,
                "erwartung": schritt.erwartung,
                "antwort": antworten.get(schritt.id, "offen"),
                "notiz": (notizen or {}).get(schritt.id, ""),
            }
        )
    return {
        "pruefer": pruefer.strip(),
        "zeit": datetime.now(UTC).isoformat(timespec="seconds"),
        "schritte": entries,
        "bestanden": all(e["antwort"] == "ja" for e in entries) and bool(entries),
    }


def ergebnis_schreiben(
    abnahme: Abnahme,
    *,
    tests: dict[str, Any] | None = None,
    checkliste: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = abnahme.ergebnis() or {"name": abnahme.name}
    current["aktualisiert"] = datetime.now(UTC).isoformat(timespec="seconds")
    if tests is not None:
        current["tests"] = tests
    if checkliste is not None:
        current["checkliste"] = checkliste
    abnahme.ergebnis_path.write_text(
        json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return current


def bericht(abnahme: Abnahme) -> str:
    """Markdown-Zusammenfassung des letzten Standes."""
    lines = [f"# Abnahme {abnahme.name} — {abnahme.titel}", ""]
    if abnahme.bezug:
        lines.append("Bezug: " + " · ".join(f"{k}: {v}" for k, v in abnahme.bezug.items()))
        lines.append("")
    result = abnahme.ergebnis()
    if not result:
        lines.append("Noch kein Lauf.")
        return "\n".join(lines) + "\n"
    tests = result.get("tests")
    if tests:
        summary = tests.get("summary") or {}
        verdict = "grün" if tests.get("exit_code") == 0 else "rot"
        lines.append(f"## Automatische Prüfungen: {verdict}")
        lines.append("")
        lines.append(", ".join(f"{v} {k}" for k, v in summary.items()) or "keine Zusammenfassung")
        lines.append("")
    check = result.get("checkliste")
    if check:
        lines.append(
            f"## Checkliste ({check.get('pruefer')}, {check.get('zeit')}): "
            f"{'bestanden' if check.get('bestanden') else 'nicht bestanden'}"
        )
        lines.append("")
        for entry in check.get("schritte", []):
            mark = {"ja": "✅", "nein": "❌"}.get(entry.get("antwort"), "⬜")
            note = f" — {entry['notiz']}" if entry.get("notiz") else ""
            lines.append(f"- {mark} {entry['id']}: {entry['text']}{note}")
        lines.append("")
    return "\n".join(lines) + "\n"
