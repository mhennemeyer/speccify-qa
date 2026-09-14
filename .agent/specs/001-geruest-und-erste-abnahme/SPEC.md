---
station: Doing
order: 1
created: 2026-09-14
needs_human: true
ready: false
open_question: null
parent: null
---
# Gerüst, CLI und erste Abnahme (Speccify Spec 011)

## Why

speccify-qa soll sofort etwas leisten: die anstehende Abnahme von Speccify
Spec 011 als erste Aufgabe, mit messbarem Ergebnis gegenüber der
Chat-Anleitung. Playbook `qa-framework.md`.

## What

Python-Paket `speccify_qa` mit CLI (`env`, `abnahme list/anlegen/run/
checkliste/bericht`), Abnahme-Modell (Ordner je Vorhaben, `ergebnis.json`),
Umgebungen, Adapter zur Speccify-App (Desktop-UI-MCP, Mock-URL, Web-Board),
Tests (unit, smoke), erste Abnahme `speccify-011-auftrag` mit Stufe-0-Test
gegen den Mock und Stufe-3-Checkliste. Vollständiges Speccify-Setup
(`.agent`, Skills, MCP-Konfiguration). Nicht enthalten: Oberfläche (004),
QA-Brücke (003), Inventar (005).

## Acceptance

- Wenn `uv run pytest tests/unit` läuft, dann sind Abnahme-Modell und Umgebungen belegt.
- Wenn die Speccify-App läuft, dann bestätigt `pytest -m smoke` den Desktop-UI-MCP mit `show_ui`.
- Wenn Vite auf 1421 läuft, dann ist `speccify-qa abnahme run speccify-011-auftrag` grün; sonst wird übersprungen.
- Wenn die Checkliste mit Prüfer und Antworten erfasst wird, dann steht das Ergebnis in `ergebnis.json` und `bericht` zeigt es.

## Decisions

- D1 (2026-09-14): Modell und Regeln von tec-e2e übernommen, kein Code; flaches Paket, uv_build.
- D2 (2026-09-14): Erste Abnahme bewusst mit hohem Stufe-3-Anteil — das ist der Startwert der Kennzahl.

## Tasks

- [x] Gerüst: Paket, CLI, Umgebungen, Adapter, Tests, Speccify-Setup, Playbook.
- [x] Abnahme `speccify-011-auftrag`: plan, abnahme, checkliste, Mock-Test.
- [ ] Erste Durchführung durch den BO: Checkliste erfassen, Dauer und Befunde in `abnahme.md` nachtragen.
- [ ] Befunde als Specs im Speccify-Repo anlegen (falls welche).

## Verification

Noch nichts geprüft.

## Questions

Keine.
