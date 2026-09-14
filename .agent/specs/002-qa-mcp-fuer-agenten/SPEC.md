---
station: Backlog
order: 2
created: 2026-09-14
needs_human: true
ready: false
open_question: null
parent: null
---
# speccify-qa als MCP: Abnahmen aus dem Agent-Terminal steuern

## Why

Der Agent im Speccify-Terminal soll Abnahmen selbst anlegen, laufen lassen
und Ergebnisse als Verification in die Spec schreiben — ohne Shell-Umwege.

## What

Streamable-HTTP-MCP (FastMCP) über denselben Kern wie die CLI: Tools
`env`, `abnahme_list`, `abnahme_anlegen`, `abnahme_run`, `abnahme_bericht`,
`checkliste_erfassen` (nur mit ausdrücklichem Prüfer). Eintrag in `.mcp.json`
der Speccify-Projekte. Nicht enthalten: Schreiben in fremde Specs (das macht
der Agent selbst).

## Acceptance

- Wenn der Agent `abnahme_run` ruft, dann kommt dieselbe Zusammenfassung wie in der CLI.
- Wenn `checkliste_erfassen` ohne Prüfer gerufen wird, dann lehnt das Tool ab.

## Decisions

- D1 (2026-09-14): MCP als dünner Adapter über `speccify_qa.abnahme`; kein zweiter Weg.

## Tasks

- [ ] FastMCP-Server und Tools.
- [ ] Tests mit echtem MCP-Client.
- [ ] Eintrag in `.mcp.json`-Vorlage und Doku.

## Verification

Noch nichts geprüft.

## Questions

Keine.
