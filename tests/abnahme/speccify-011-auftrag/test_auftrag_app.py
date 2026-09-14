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
    """Projektfenster ohne Terminal (dieses Repo), Terminal als reine Shell.

    Der Agent-Befehl des Fensters ist eine UI-Präferenz in localStorage
    (geteilt zwischen den Fenstern); leer heißt „Nur Shell“ — so landet die
    Zustellung in zsh und ist im Puffer vollständig lesbar. Ein schon offenes
    QA-Fenster wird vorher geschlossen; am Ende wird beides zurückgesetzt.
    """
    existing = app.project_window(QA_ROOT)
    if existing:
        app.close_window(existing.label)
    key = f"speccify.project.agentCommand:{QA_ROOT}"
    app.bridge.eval("main", f"localStorage.setItem({key!r}, ''); return true;")
    window = app.open_project(QA_ROOT)
    assert not window.terminal.ready()
    yield window
    app.close_window(window.label)
    app.bridge.eval("main", f"localStorage.removeItem({key!r}); return true;")


def _kompakt(text: str) -> str:
    return "".join(text.split())


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
    # Nur Shell: zsh zeigt den ganzen Text in der Eingabezeile (Bracketed
    # Paste) und führt keine Zeile aus — kein „command not found“, keine
    # Escape-Reste.
    last = preview.splitlines()[-1]
    text = window.wait(
        "const t = window.__speccifyQa.terminalText() || '';"
        f" return t.includes({last!r}) ? t : '';",
        timeout=20,
    )
    # zsh zeigt von einer Eingabe, die höher als das Terminal ist, nur das
    # Ende und bricht Zeilen selbst um — geprüft wird der Schluss des Textes
    # in Reihenfolge, ohne Leerraum.
    tail = [_kompakt(line) for line in preview.splitlines()[-6:] if line.strip()]
    kompakt = _kompakt(text)
    positions = [kompakt.rfind(line) for line in tail]
    assert all(pos >= 0 for pos in positions), (tail, text[-400:])
    assert positions == sorted(positions)
    assert "Projekt:" in text or len(preview.splitlines()) > 20, text[-400:]
    assert "[200~" not in text and "[201~" not in text
    assert "command not found" not in text
    assert text != vorher


def test_kopieren_legt_die_vorschau_in_die_zwischenablage(zweites_fenster: ProjectWindow) -> None:
    window = zweites_fenster
    window.board.select(_erste_doing_karte(window))
    dialog = window.board.open_handover()
    preview = dialog.preview()
    status = dialog.copy()
    assert "kopiert" in status
    dialog.close()
    assert window.clipboard() == preview


def test_geaenderte_datei_zeigt_den_neuen_inhalt(zweites_fenster: ProjectWindow) -> None:
    """Die Vorschau liest die Datei beim Öffnen — nie einen alten Stand.

    Den Hinweis „seit der Auswahl geändert“ zeigt die App nur, wenn das Board
    die Änderung noch nicht kennt; in der echten App holt der Datei-Watcher
    das Board meist schneller nach, als ein Mensch klickt. Der Hinweis ist
    deshalb Stufe 0 (Mock ohne Watcher), hier zählt der Inhalt.
    """
    window = zweites_fenster
    file = _erste_doing_karte(window)
    window.board.select(file)
    original = window.read_file(file)
    try:
        window.write_file(file, original.rstrip("\n") + "\n\nNachträglich geändert (QA).\n")
        dialog = window.board.open_handover()
        assert "Nachträglich geändert (QA)." in dialog.preview()
        dialog.close()
    finally:
        window.write_file(file, original)
    window.board.select(file)
    dialog = window.board.open_handover()
    assert "Nachträglich geändert (QA)." not in dialog.preview()
    dialog.close()
