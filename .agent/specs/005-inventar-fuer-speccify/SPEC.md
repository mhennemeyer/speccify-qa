---
station: Backlog
order: 5
created: 2026-09-14
needs_human: true
ready: false
open_question: null
parent: null
---
# Inventar: Einstiegspunkte der Speccify-App und Abdeckung

## Why

Ohne Inventar gibt es keine Abdeckung. tec-e2e zeigt: das Inventar ist der
präzisere Index als jedes RAG.

## What

Parser-Registry mit ersten Plugins: Tauri-Commands (`#[tauri::command]`),
MCP-Tools (Desktop-UI, Board, speccify-mcp), UI-Baum aus
`stand-und-ui.md`. Erzeugtes `inventory/inventory.json`, `covers`-Marker mit
Fail-on-unknown-ID, Abdeckungsmatrix als Markdown/JSON.

## Acceptance

- Wenn ein Test eine unbekannte Inventar-ID nennt, dann scheitert der Lauf.
- Wenn `inventory scan` läuft, dann listet es Commands und Tools des Speccify-Checkouts.

## Decisions

- D1 (2026-09-14): Parser als Plugins, projektlokale `inventory.yaml` statt Konstanten (aus dem Inventar-Vorschlag der Research-Notiz).

## Tasks

- [ ] Parser Tauri-Commands und MCP-Tools.
- [ ] Marker und Matrix.
- [ ] Erste Abdeckungszahl für Speccify.

## Verification

Noch nichts geprüft.

## Questions

Keine.
