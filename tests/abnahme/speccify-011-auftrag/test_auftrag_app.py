"""Stufe 2: die echte, gebündelte Speccify-App über die QA-Brücke (Spec 039).

Voraussetzung: App mit `--qa-bridge=18769` (siehe environments.yaml, hints).
Ohne Brücke überspringen die Tests mit dem Startbefehl. Das zweite Fenster
öffnet dieses QA-Repo als Projekt und schließt es am Ende wieder (samt
Terminal); im Speccify-Fenster wird nur gelesen und geklickt, nichts
zugestellt.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from speccify_qa.pages import App, ProjectWindow

pytestmark = [pytest.mark.abnahme("speccify-011-auftrag"), pytest.mark.stufe(2)]
ESC = chr(27)
QA_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def zweites_fenster(app: App):
    """Projektfenster ohne Terminal (dieses Repo); am Ende schließen."""
    window = app.open_project(QA_ROOT)
    if window.terminal.ready():
        pytest.skip("Im QA-Projektfenster läuft schon ein Terminal — bitte schließen.")
    yield window
    window.bridge.invoke(window.label, "plugin:window|close")


def _erste_doing_karte(window: ProjectWindow) -> str:
    cards = window.board.cards("Doing") or window.board.cards()
    assert cards, "Keine Spec-Karten auf dem Board"
    return cards[0]["file"]


def test_vorschau_nennt_projekt_spec_pfad_und_absicht(speccify_window: ProjectWindow) -> None:
    window = speccify_window
    file = _erste_doing_karte(window)
    window.board.select(file)
    dialog = window.board.open_handover()
    try:
        preview = dialog.preview()
        assert preview.startswith(f"Projekt: {window.root}\n")
        assert f"— Datei: {file}" in preview and "(Station " in preview
        assert "Auftrag: Arbeite diese Spec nach dem Spec-Workflow" in preview
        assert "Regeln: `.agent/agent.md`" in preview
        assert "```md\n" in preview
        assert dialog.path() == file
        assert dialog.kinds() == ["Umsetzen", "Prüfen", "Lesen und anwenden"]
        dialog.choose("Prüfen")
        assert "Prüfe diese Spec gegen ihre Acceptance-Punkte" in dialog.preview()
        dialog.choose("Lesen und anwenden")
        assert "Lies diese Spec und fasse Stand" in dialog.preview()
    finally:
        dialog.close()
    assert not dialog.is_open()


def test_ohne_terminal_keine_zustellung_und_start_aus_dem_dialog(
    zweites_fenster: ProjectWindow,
) -> None:
    window = zweites_fenster
    window.board.select(_erste_doing_karte(window))
    dialog = window.board.open_handover()
    assert dialog.terminal_ready() is False
    status = dialog.insert_into_terminal()
    assert "Kein Agent-Terminal bereit" in status
    assert dialog.has_button("Kopieren") and dialog.has_button("Terminal starten")
    assert window.terminal.text() == ""
    dialog.start_terminal()
    window.terminal.wait_ready(timeout=30)
    window.wait(
        "return dialog('Auftrag').querySelector('[data-terminal-ready]')"
        ".getAttribute('data-terminal-ready') === 'true';"
    )
    assert not dialog.has_button("Terminal starten")
    dialog.close()


def test_zustellung_ist_ein_block_ohne_enter(zweites_fenster: ProjectWindow) -> None:
    window = zweites_fenster
    window.terminal.wait_ready(timeout=30)
    vorher = window.terminal.text()
    file = _erste_doing_karte(window)
    window.board.select(file)
    dialog = window.board.open_handover()
    preview = dialog.preview()
    status = dialog.insert_into_terminal()
    assert status.startswith("Eingefügt — im Terminal mit Enter absenden")
    dialog.close()
    # Der Text liegt in der Eingabezeile: ein Host zeigt ihn ganz (Shell) oder
    # gekürzt als „Pasted text“ (Claude Code) — nie als Escape-Rest.
    text = window.wait(
        "const t = window.__speccifyQa.terminalText() || '';"
        f" return t.includes({preview.splitlines()[0]!r}) || /Pasted text/i.test(t) ? t : '';",
        timeout=20,
    )
    assert "[200~" not in text and "[201~" not in text
    assert text != vorher
    # Nichts abgeschickt: kein Spec-Workflow-Lauf, die Eingabe wartet weiter.
    assert "Auftrag angenommen" not in text


def test_kopieren_legt_die_vorschau_in_die_zwischenablage(zweites_fenster: ProjectWindow) -> None:
    window = zweites_fenster
    window.board.select(_erste_doing_karte(window))
    dialog = window.board.open_handover()
    preview = dialog.preview()
    status = dialog.copy()
    assert "kopiert" in status
    dialog.close()
    assert window.clipboard() == preview


def test_geaenderte_datei_zeigt_hinweis_und_neuen_inhalt(zweites_fenster: ProjectWindow) -> None:
    window = zweites_fenster
    file = _erste_doing_karte(window)
    window.board.select(file)
    original = window.read_file(file)
    try:
        window.write_file(file, original.rstrip("\n") + "\n\nNachträglich geändert (QA).\n")
        dialog = window.board.open_handover()
        statuses = dialog.statuses()
        assert any("seit der Auswahl geändert" in s for s in statuses), statuses
        assert "Nachträglich geändert (QA)." in dialog.preview()
        dialog.close()
    finally:
        window.write_file(file, original)
