"""Abnahme-Modell: anlegen, Checkliste erfassen, Bericht, Antworten parsen."""

from __future__ import annotations

from pathlib import Path

import pytest

from speccify_qa import abnahme as ab


def test_anlegen_erfassen_und_berichten(tmp_path: Path) -> None:
    item = ab.anlegen(tmp_path, "demo-1", titel="Demo", bezug={"spec": "011"}, plan="# Plan\n")
    assert (item.folder / "plan.md").read_text(encoding="utf-8") == "# Plan\n"
    (item.folder / "checkliste.yaml").write_text(
        "schritte:\n  - id: 1\n    text: Vorschau öffnen\n    erwartung: Projekt sichtbar\n"
        "  - id: 2\n    text: Einfügen\n    erwartung: Text im Terminal\n",
        encoding="utf-8",
    )
    item = ab.load(tmp_path, "demo-1")
    assert [s.id for s in item.schritte] == ["1", "2"]
    result = ab.checkliste_erfassen(
        item,
        pruefer="Anna",
        antworten={"1": "ja", "2": "nein"},
        notizen={"2": "Escape-Zeichen sichtbar"},
    )
    assert result["bestanden"] is False
    ab.ergebnis_schreiben(item, checkliste=result, tests={"exit_code": 0, "summary": {"passed": 3}})
    report = ab.bericht(item)
    assert "Automatische Prüfungen: grün" in report and "3 passed" in report
    assert "nicht bestanden" in report and "❌ 2: Einfügen — Escape-Zeichen sichtbar" in report
    assert ab.list_all(tmp_path)[0].name == "demo-1"
    with pytest.raises(ab.AbnahmeError):
        ab.anlegen(tmp_path, "demo-1", titel="doppelt")
    with pytest.raises(ab.AbnahmeError):
        ab.anlegen(tmp_path, "kein leerzeichen", titel="x")
    with pytest.raises(ab.AbnahmeError):
        ab.checkliste_erfassen(item, pruefer="", antworten={"1": "ja"})
    with pytest.raises(ab.AbnahmeError):
        ab.checkliste_erfassen(item, pruefer="Anna", antworten={"9": "ja"})


def test_antworten_und_zusammenfassung() -> None:
    assert ab.parse_antworten("1=ja, 2=NEIN,3=offen") == {"1": "ja", "2": "nein", "3": "offen"}
    with pytest.raises(ab.AbnahmeError):
        ab.parse_antworten("1=vielleicht")
    assert ab._parse_summary("...\n2 passed, 1 skipped in 0.3s\n") == {"passed": 2, "skipped": 1}
    assert ab._parse_summary("1 failed, 1 error in 1s") == {"failed": 1, "error": 1}


def test_bericht_ohne_lauf(tmp_path: Path) -> None:
    item = ab.anlegen(tmp_path, "leer", titel="Leer")
    assert "Noch kein Lauf" in ab.bericht(item)
