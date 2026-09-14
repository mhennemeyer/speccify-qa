# Spec 011 abnehmen: „Auftrag…“ im Projektfenster

Erste Aufgabe von speccify-qa — und zugleich der Maßstab, ob das Werkzeug
etwas bringt: dieselbe Abnahme wurde am 2026-09-14 als Klick-Anleitung im
Chat formuliert (fünf Prüfungen, etwa fünf Minuten). Hier wird sie zum
Nachweis mit Ergebnisdatei.

## Worum es geht

Spec 011 (`speccify`, Register-Branch `specs`) ersetzt „Als Prompt kopieren“
durch „Auftrag…“: eine Vorschau mit Projekt, Pfad, Spec-ID/Station, Absicht
(Umsetzen/Prüfen/Lesen/Bearbeiten) und dem aktuellen Dateiinhalt, die als
ein Block ins Agent-Terminal dieses Fensters eingefügt wird — ohne Enter.
Ohne Terminal: Hinweis, Kopieren, Terminal starten. Geänderte Datei seit
Auswahl: Hinweis. Auswahl/Board schicken nie etwas.

## Was schon belegt ist

- Mock-UI-Suite `scripts/test_handover.mjs` im Speccify-Checkout (Stufe 0):
  Vorschau, Verweigerung ohne Terminal, Start, Absicht, ein Paste-Block ohne
  `\r`, Abweichungshinweis, keine Auto-Aufträge.
- Nicht belegt: Zustellung an einen echten Host (Claude Code, Codex, zsh) in
  der gebündelten App — genau das prüft diese Abnahme.

## Wie geprüft wird

- Stufe 0: die Mock-Suite hier nachgezogen (`test_auftrag_mock.py`, braucht
  Vite auf 1421 im Speccify-Checkout).
- Stufe 1: Desktop-UI-MCP erreichbar (`tests/smoke`).
- Stufe 2: echte App — erst mit der QA-Brücke (Spec 003 hier, Gegenstück in
  Speccify); bis dahin Stufe 3.
- Stufe 3: `checkliste.yaml` — fünf Prüfungen in der laufenden App, erfasst
  mit `speccify-qa abnahme checkliste speccify-011-auftrag`.

Vorbereitung: gebündelte Speccify-App läuft (Port 18768), Projektfenster für
den Speccify-Checkout mit Claude im Terminal, ein zweites Projektfenster
(z. B. itsdcloud) ohne Terminal.
