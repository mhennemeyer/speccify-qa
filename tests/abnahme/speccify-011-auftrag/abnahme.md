# Abnahme speccify-011-auftrag

## Was die Abnahme prüft

| Verhalten | Test |
|---|---|
| Vorschau nennt Projektwurzel, Spec mit Station, Dateipfad, Auftragsabsatz, Regelverweis und die Datei als Markdown-Block; die drei Absichten wechseln den Absatz | Stufe 2 `test_auftrag_app.py::test_vorschau_nennt_projekt_spec_pfad_und_absicht` · Stufe 0 `test_auftrag_mock.py` |
| Ohne Terminal: keine Eingabe, Meldung „Kein Agent-Terminal bereit“, „Kopieren“ und „Terminal starten“; nach dem Start „bereit“ | Stufe 2 `…::test_ohne_terminal_keine_zustellung_und_start_aus_dem_dialog` · Stufe 0 |
| Einfügen: Meldung „Eingefügt — im Terminal mit Enter absenden“, Text liegt als ein Block in der Eingabezeile (Shell ganz, Claude Code als „Pasted text“), keine Escape-Reste, nichts abgeschickt | Stufe 2 `…::test_zustellung_ist_ein_block_ohne_enter` · Stufe 0 (Bracketed-Paste-Rahmen ohne `\r`) |
| Kopieren legt genau den Vorschautext in die Zwischenablage | Stufe 2 `…::test_kopieren_legt_die_vorschau_in_die_zwischenablage` |
| Geänderte Datei ohne Auswahlwechsel: Vorschau zeigt den neuen Inhalt (Stufe 2); der Hinweis „seit der Auswahl geändert“ nur ohne Watcher sichtbar (Stufe 0) | Stufe 2 `…::test_geaenderte_datei_zeigt_den_neuen_inhalt` · Stufe 0 |
| Terminal kommt sichtbar nach vorn; Claude beginnt nach Enter mit dem Auftrag | Checkliste 1 (Optik, echter Agentenlauf) |
| „Nur Shell“: zsh zeigt den mehrzeiligen Text, führt nichts aus | Checkliste 2 (Shell-Modus hängt von der Agent-Einstellung des Fensters ab) |

Stufe 2 läuft gegen die gebündelte App mit QA-Brücke (Speccify Spec 039):
`./scripts/dev.sh --app --prepared --skip-engine --ui-port=18768 --qa-bridge=18769`
im Speccify-Checkout, dann hier `uv run python -m speccify_qa.cli abnahme run speccify-011-auftrag`.
Die Tests öffnen dieses Repo als zweites Projektfenster (mit Terminalstart) und
schließen es wieder; im Speccify-Fenster wird nichts zugestellt.

## Betroffen

- Speccify Desktop: `lib/handover.ts`, `HandoverSheet.tsx`, `TerminalPanel.tsx`,
  Board/Playbooks/Skills/Tools/Agent-Tabs, Git-Tab, Skill-Import.
- Hosts: Claude Code (Bracketed Paste im TUI), zsh ≥ 5.1.

## Erfolgsmaß für das Werkzeug

Dauer der Abnahme, Zahl der Befunde, Fehlalarme; Vergleich mit der
Chat-Anleitung vom 2026-09-14.
