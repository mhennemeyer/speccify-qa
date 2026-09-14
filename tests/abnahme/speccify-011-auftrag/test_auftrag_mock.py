"""Stufe 0: die Mock-Suite aus dem Speccify-Checkout, hier als Abnahme-Test.

Braucht den Vite-Dev-Server des Speccify-Frontends auf 127.0.0.1:1421
(`pnpm exec vite --port 1421 --strictPort --host 127.0.0.1` in apps/desktop);
sonst wird übersprungen. Der Mock zeichnet Terminal-Schreibvorgänge auf.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.abnahme("speccify-011-auftrag"), pytest.mark.stufe(0)]
ESC = chr(27)


@pytest.fixture
def board(mock_url: str, page):  # pytest-playwright liefert `page`
    page.set_viewport_size({"width": 1500, "height": 1000})
    page.goto(f"{mock_url}?owner=me")
    page.get_by_text("notes/zahlen.md mit Quadratzahlen 1–5 anlegen").first.wait_for()
    return page


def _writes(page) -> list[dict]:
    return page.evaluate("() => window.__SPECCIFY_MOCK__.terminalWrites")


def test_vorschau_zustellung_und_grenzen(board) -> None:
    page = board
    card = page.locator('[data-station="Doing"] [data-spec-card]').first
    file = card.get_attribute("data-spec-card")
    card.locator("button").first.click()
    page.get_by_role("button", name="Auftrag…", exact=True).click()
    dialog = page.get_by_role("dialog", name="Auftrag")
    text = dialog.get_by_label("Auftragstext")
    text.wait_for()
    preview = text.input_value()
    assert preview.startswith("Projekt: /private/tmp/claude-501/w1-projekt\n")
    assert "(Station Doing) — Datei: " + file in preview
    assert "Auftrag: Arbeite diese Spec nach dem Spec-Workflow" in preview
    assert "```md\n" in preview
    assert dialog.locator("[data-terminal-ready]").get_attribute("data-terminal-ready") == "false"

    # Ohne Terminal: nichts getippt, sichtbare Verweigerung.
    dialog.get_by_role("button", name="Ins Terminal einfügen", exact=True).click()
    dialog.get_by_role("status").filter(has_text="Kein Agent-Terminal bereit").wait_for()
    assert _writes(page) == []
    dialog.get_by_role("button", name="Terminal starten", exact=True).click()
    page.wait_for_function(
        "() => document.querySelector('[data-terminal-ready]')"
        "?.getAttribute('data-terminal-ready') === 'true'"
    )

    # Absicht Prüfen; genau ein Bracketed-Paste-Block ohne Enter.
    dialog.get_by_role("button", name="Prüfen", exact=True).click()
    assert "Prüfe diese Spec gegen ihre Acceptance-Punkte" in text.input_value()
    dialog.get_by_role("button", name="Ins Terminal einfügen", exact=True).click()
    dialog.get_by_role("status").filter(
        has_text="Eingefügt — im Terminal mit Enter absenden"
    ).wait_for()
    sent = _writes(page)
    assert len(sent) == 1
    assert sent[0]["data"].startswith(f"{ESC}[200~Projekt:") and sent[0]["data"].endswith(
        f"{ESC}[201~"
    )
    assert "\r" not in sent[0]["data"]

    # Geänderte Datei: aktueller Inhalt und Hinweis.
    dialog.get_by_role("button", name="Schließen", exact=True).click()
    page.evaluate(
        "(f) => { const s = window.__SPECCIFY_MOCK__.specs.find(x => x.file === f); "
        "s.body += '\\n\\nNachträglich geändert.'; }",
        file,
    )
    page.get_by_role("button", name="Auftrag…", exact=True).click()
    dialog.get_by_role("status").filter(has_text="seit der Auswahl geändert").wait_for()
    assert "Nachträglich geändert" in text.input_value()
