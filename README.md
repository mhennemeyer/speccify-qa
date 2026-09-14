# speccify-qa

QA- und E2E-Werkzeug, das Agenten vollständig bedienen können und Menschen
eine Oberfläche gibt. Erster Zuschnitt: die Speccify-App prüfen. Ziel: ein
generisches, skill-basiertes QA-Framework (Vorbild und Modell: tec-e2e).
Vision, Prüfstufen und Abnahme-Modell: [`.agent/playbooks/qa-framework.md`](.agent/playbooks/qa-framework.md).

```bash
./scripts/setup.sh                          # uv, Playwright, Umgebung prüfen
uv run pytest tests/unit                    # ohne laufende Systeme
uv run pytest -m smoke                      # Prüfziele erreichbar?
uv run python -m speccify_qa.cli abnahme list             # Abnahmen und Stand
uv run python -m speccify_qa.cli abnahme run speccify-011-auftrag          # automatische Stufen
uv run python -m speccify_qa.cli abnahme checkliste speccify-011-auftrag   # Mensch-Schritte erfassen
uv run python -m speccify_qa.cli abnahme bericht speccify-011-auftrag      # Markdown-Bericht
```

> **macOS:** `uv` setzt auf die `.pth`-Dateien des venv das `hidden`-Flag,
> Python liest sie dann nicht (Symptom `No module named 'speccify_qa'` beim
> Konsolenskript). Deshalb `python -m speccify_qa.cli` statt `speccify-qa`;
> `scripts/setup.sh` und jeder Abnahme-Lauf setzen das Flag zurück.

Prüfziele stehen in `environments.yaml`; Secrets kommen aus der Umgebung.
Läuft ein Ziel nicht, überspringt der Test mit Begründung — nur `tests/smoke`
macht die Erreichbarkeit selbst zur Aussage.

Eine **Abnahme** ist ein Ordner je Vorhaben unter `tests/abnahme/<name>/`
mit `plan.md`, `abnahme.md`, `checkliste.yaml`, `test_*.py` und `ergebnis.json`.
Die erste: `speccify-011-auftrag` — sie misst zugleich, was das Werkzeug
gegenüber einer Klick-Anleitung im Chat bringt.
