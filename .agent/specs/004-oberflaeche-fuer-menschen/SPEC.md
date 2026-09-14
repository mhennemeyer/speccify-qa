---
station: Backlog
order: 4
created: 2026-09-14
needs_human: true
ready: false
open_question: null
parent: null
---
# Oberfläche für Menschen: Abnahmen, Checkliste, Bericht

## Why

Menschen sollen Abnahmen ohne Terminal durchführen: Prüfschritte lesen,
abhaken, Notizen, Bericht — wie in der tec-e2e-App.

## What

Erste Ansicht „Abnahmen“: Liste, Plan/abnahme.md lesen, Checkliste mit
ja/nein/offen und Notiz, Tests starten und Ausgabe mitlesen, Bericht.
Technik nach D-QA-02 (Tauri-App wie tec-e2e oder Web-Board-Erweiterung).
Später Setup, Inventar, Abdeckung, Befunde, Umgebungen.

## Acceptance

- Wenn eine Checkliste in der Oberfläche ausgefüllt wird, dann entsteht dieselbe `ergebnis.json` wie über die CLI.

## Decisions

- D1 (2026-09-14): Ergebnisdateien bleiben die Wahrheit; die Oberfläche schreibt nur über den Kern.

## Tasks

- [ ] D-QA-02 entscheiden.
- [ ] Ansicht Abnahmen.
- [ ] Tests starten und mitlesen.

## Verification

Noch nichts geprüft.

## Questions

Keine.
