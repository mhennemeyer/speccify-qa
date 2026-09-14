---
station: Doing
order: 3
created: 2026-09-14
needs_human: true
ready: true
open_question: null
parent: null
---
# QA-Brücke: die echte Speccify-App von außen prüfen (Stufe 2)

## Why

Auf macOS gibt es keinen WebDriver für Tauri; die gebündelte App lässt sich
heute nur über Mock-UI (Stufe 0) und Verträge (Stufe 1) prüfen. Für echte
Klick-Abnahmen braucht es einen Weg in die laufende App.

## What

Gegenstück in Speccify (eigene Spec dort): Flag `--qa-bridge=<port>`, HTTP
auf Loopback, Token; Befehle: Fenster auflisten, JS in einem Fenster
ausführen und Ergebnis zurückgeben, Ereignis auslösen, Screenshot des
Fensters (macOS: `screencapture -l` mit Fenster-ID) — nie im Produktivmodus
aktiv. Hier: Adapter `speccify_qa.bridge` (Python) mit Page-Objects für
Board, Inspektor, Terminal-Eingabe, Auftrags-Vorschau, Frage-Popup; die
Abnahme 011 bekommt Stufe-2-Tests, die Checkliste schrumpft.

## Acceptance

- Wenn die App mit Brücke läuft, dann liest ein Test die Auftrags-Vorschau und den Terminal-Puffer aus der echten App.
- Wenn die App ohne Flag läuft, dann gibt es keinen Endpunkt.

## Decisions

- D1 (2026-09-14): JS-Ausführung über Tauri (`eval`) statt WebDriver; Ergebnis über einen eigenen Rückkanal.
- D2 (2026-09-14, BO): Brücke nie im Normalbetrieb; Checkliste nur für Optik und nicht Automatisierbares.
- D3 (2026-09-14): Token über Discovery-Datei `<tmp>/speccify-qa-bridge.json`, weil `open` auf macOS keine Umgebung vererbt.

## Tasks

- [x] Spec im Speccify-Repo anlegen (auf Ansage) und Vertrag abstimmen.
      Speccify Spec 039, Vertrag in `docs/qa-bridge.md` dort.
- [x] Adapter und Page-Objects hier.
      `speccify_qa/bridge.py`, `speccify_qa/pages.py`, Fixtures `bridge`/`app`/`speccify_window`.
- [x] Abnahme 011 auf Stufe 2 heben; Kennzahl vorher/nachher.
      Fünf Tests in `test_auftrag_app.py`, Checkliste von fünf auf zwei Schritte;
      Lauf: 6/6 grün in ~4 s (vorher: fünf manuelle Klickschritte).

## Verification

2026-09-14: `abnahme run speccify-011-auftrag` gegen die gebündelte App mit
`--qa-bridge=18769`: 6 passed (fünf Stufe 2, einer Stufe 0), zweimal in Folge,
Laufzeit ~4 s. Brücke ohne Token 401, Hauptthread-Blockade (macOS-Dialog) als
503 sichtbar. Werkzeug-Befunde behoben: nur sichtbare Elemente, Inspektor-Tab
zurückschalten, Karte nicht doppelt klicken (abwählen), Fenster ohne Warten
schließen, umgebrochene Terminalzeilen (Speccify-Haken). Produkt-Befund
F-QA-1 in Speccify Spec 011: Zustellung in Claudes Trust-Dialog geht verloren.
Screenshot aus dem App-Prozess braucht die Freigabe „Bildschirmaufnahme“.

## Questions

Keine.
