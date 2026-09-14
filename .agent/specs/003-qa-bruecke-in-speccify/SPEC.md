---
station: Backlog
order: 3
created: 2026-09-14
needs_human: true
ready: false
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

## Tasks

- [ ] Spec im Speccify-Repo anlegen (auf Ansage) und Vertrag abstimmen.
- [ ] Adapter und Page-Objects hier.
- [ ] Abnahme 011 auf Stufe 2 heben; Kennzahl vorher/nachher.

## Verification

Noch nichts geprüft.

## Questions

Keine.
