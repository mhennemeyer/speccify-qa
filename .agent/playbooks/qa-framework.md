# QA-Framework: Vision, Prüfstufen, Abnahme-Modell

Stehende Anleitung für speccify-qa (Entwurf 2026-09-14, zum Refinen). Anlass:
die Abnahme von Speccify-Spec 011 („Auftrag…“) sollte ein umfangreicher
E2E/UI-Test werden — statt sie im Chat zu beschreiben, wird sie die erste
Aufgabe eines eigenen QA-Werkzeugs, und ihr Verlauf misst dessen Nutzen.

## Zielbild

Ein **generisches, skill-basiertes QA- und E2E-Framework**: Agenten
bedienen es vollständig (CLI heute, MCP als Nächstes), Menschen bekommen
eine Oberfläche (wie die tec-e2e-App: Setup, Inventar, Abdeckung, Befunde,
Tests, Umgebungen, Abnahmen). Der erste Zuschnitt auf Speccify ist ein
Schritt auf dem Weg; nichts Speccify-Spezifisches darf in den Kern.

## Herkunft: was aus tec-e2e übernommen wird

tec-e2e (`~/WorkLocal/Toyota/tec-e2e`) hat das Modell schon, nur
Toyota-gebunden. Übernommen werden die Ideen, nicht der Code:

- **Inventar → Marker → Abdeckung.** Einstiegspunkte aus dem Quellcode
  (Endpunkte, Routen, Kommandos) als erzeugtes Inventar; jeder Test trägt
  `covers`-Marker mit gültiger ID; unbekannte IDs lassen den Lauf scheitern.
- **Skip statt Fail**, wenn ein Prüfziel nicht läuft — ein Fehlschlag würde
  behaupten, das System sei kaputt. Nur `tests/smoke` sagt Erreichbarkeit.
- **Abnahme je Vorhaben** mit `plan.md` (Kontext), `abnahme.md`
  (Refinement), Tests mit Marker `abnahme(name, stand="erwartet")`,
  `ergebnis.json`; Abnahmen laufen nicht mit der Regression; Übernahme in die
  Regression ist ein bewusster Schritt.
- **Browserwächter** (Konsolenfehler und Ausnahmen sind Befunde),
  **Rundgang** mit Pixel-Baseline, **Befunde** als eigene Ansicht.
- **Umgebungen** in einer Datei, Secrets nur als Namen.

Toyota-Kopplung, die *nicht* mitkommt: Workspace-Layout, Maven/Angular-
Parser, Keycloak-Realm, Domänenmodule, Jira-Präfixe, Page-Objects.

## Prüfstufen

Jede Aussage über die Speccify-App hat eine Stufe; ein Bericht nennt sie.

| Stufe | Was | Werkzeug | Stand |
|---|---|---|---|
| 0 | Mock-UI des Desktop-Frontends (Vite + `dev/mock.html`) | Playwright (Python), Mock zeichnet native Aufrufe auf | vorhanden (in Speccify 15 Suiten; hier nachgezogen je Abnahme) |
| 1 | Verträge von außen: Desktop-UI-MCP, Web-Board-HTTP/MCP, CLI (`speccify verify --json`), Register-Branch | httpx/JSON-RPC, subprocess | `tests/smoke`, Adapter `speccify_qa.speccify` |
| 2 | Echte gebündelte App: DOM lesen, klicken, Zustand prüfen, Screenshots | **QA-Brücke** in Speccify (Spec 003 hier, Gegenstück dort): JS im Fenster ausführen, Ergebnis zurück | offen |
| 3 | Mensch: Sicht, Gefühl, Host-Verhalten (Claude/Codex/zsh) | `checkliste.yaml` + `speccify-qa abnahme checkliste` | vorhanden |

Regel: eine Abnahme belegt so viel wie möglich auf 0–2 und lässt für 3 nur,
was Maschinen nicht sehen. Der Anteil von Stufe 3 sinkt mit jeder Abnahme —
das ist die Kennzahl.

## Abnahme-Modell

```text
tests/abnahme/<name>/
  abnahme.yaml     Name, Titel, Bezug (repo, spec, ticket), Anlagedatum, Stufen, uebernommen
  plan.md          Kontext für Mensch und Agent
  abnahme.md       Prüfpunkte, Betroffenes, Erfolgsmaß
  checkliste.yaml  Stufe-3-Schritte: id, text, erwartung
  test_*.py        Stufen 0–2, Marker abnahme("<name>"[, stand="erwartet"])
  ergebnis.json    letzter Lauf: Tests (exit, summary) + Checkliste (Prüfer, Zeit, Antworten)
```

`speccify-qa abnahme anlegen <name> --bezug spec=… --plan plan.md`,
`run`, `checkliste` (interaktiv oder `--antworten 1=ja,… --pruefer Name`),
`bericht`. Antworten werden nie erfunden; ohne Prüfer kein Nachweis.

## Agenten-Steuerbarkeit

- Alles über die CLI mit JSON-Ausgabe, ohne Terminal-Interaktion nötig.
- Nächster Schritt: `speccify-qa` als MCP (Tools `abnahme_list/run/bericht`,
  `env`), damit der Agent im Speccify-Terminal Abnahmen selbst startet und
  Ergebnisse als Verification in die Spec schreibt.
- Skills statt Code, wo es Urteil braucht: „Abnahme aus einer Spec ableiten“,
  „Flaky-Test triagieren“, „Rundgang-Baseline erneuern“, „Inventar-Diff
  bewerten“. Die CLIs bleiben deterministisch (Tool-Verträge).

## Oberfläche für Menschen

Wie tec-e2e: Tauri-App mit Ansichten Setup, Inventar, Abdeckung, Befunde,
Tests, Umgebungen, **Abnahmen** (Checkliste klickbar, Ergebnis speichern,
Bericht). Zuerst die Abnahmen-Ansicht, weil sie den Menschen sofort etwas
gibt; der Rest folgt dem Inventar. Alternativ als Web-Board-Erweiterung
(Speccify Spec 032) — Entscheidung offen (D-QA-02).

## Kern und Zuschnitt trennen

- Kern: Abnahme-Modell, Umgebungen, Stufen, Marker, Bericht, Browserwächter,
  Rundgang, Inventar-Registry mit Parser-Plugins, CLI/MCP, Oberfläche.
- Zuschnitt Speccify: Adapter `speccify_qa.speccify` (Desktop-UI-MCP,
  Web-Board, Mock-URL, QA-Brücke), Inventar-Parser für Tauri-Commands
  (`#[tauri::command]`) und MCP-Tools, Page-Objects für die App.
- Regel: Zuschnitt liegt in klar benannten Modulen/Ordnern, der Kern importiert
  ihn nie.

## Erfolg messen

Erste Abnahme `speccify-011-auftrag`: Dauer, Befunde, Fehlalarme, Anteil
Stufe 3 — verglichen mit der Chat-Anleitung vom 2026-09-14. Jede weitere
Abnahme hält dieselben Zahlen fest; die Richtung soll sein: weniger
Stufe 3, weniger Dauer, keine Fehlalarme.

## Offene Entscheidungen

- D-QA-01 (entschieden 2026-09-14, BO): QA-Brücke in Speccify (Spec 039 dort):
  Loopback-HTTP nur mit `--qa-bridge=<port>`, Bearer-Token aus
  `<tmp>/speccify-qa-bridge.json`, `eval`/`invoke`/Fenster/Screenshot; hier
  Adapter `speccify_qa.bridge` und Page-Objects `speccify_qa.pages`. Die
  Brücke ist nie im Normalbetrieb aktiv. Menschliche Checklisten nur für
  Optik und technisch nicht Automatisierbares; alles andere sind Tests
  (tec-e2e-Muster).
- D-QA-02: Mensch-UI als eigene Tauri-App (tec-e2e-Muster) oder als
  Web-Board-Erweiterung.
- D-QA-03: Inventar für Speccify: Tauri-Commands, MCP-Tools, UI-Baum aus
  `stand-und-ui.md` — was ist die verlässliche Quelle?
- D-QA-04: Wann wird der Kern als eigenes Paket herausgelöst (nach der
  zweiten Kundenanpassung).
