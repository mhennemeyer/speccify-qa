# Abnahme speccify-011-auftrag

## Prüfpunkte

1. Vorschau: `Projekt: <Pfad>`, Spec mit Nummer und Station, Dateipfad,
   Absatz „Auftrag: Arbeite diese Spec …“, Regelverweis, Datei als
   Markdown-Block; rechts oben „Agent-Terminal bereit“. „Prüfen“ wechselt den
   Auftragsabsatz.
2. Einfügen: Meldung „Eingefügt — im Terminal mit Enter absenden“, Terminal
   kommt nach vorn, der ganze Text steht als ein Block in der Eingabezeile
   von Claude, nichts wurde abgeschickt; Enter startet den Auftrag mit
   Projekt, Spec und Inhalt.
3. Kein Terminal (zweites Fenster): gelbe Meldung „Kein Agent-Terminal
   bereit“, „Kopieren“ und „Terminal starten“; im ersten Fenster kommt
   nichts an; „Terminal starten“ startet es, danach „Agent-Terminal bereit“.
4. Geänderte Datei: nach Bearbeiten und Speichern ohne Auswahlwechsel zeigt
   „Auftrag…“ den Hinweis „seit der Auswahl geändert“ und den neuen Inhalt.
5. Nur Shell: mehrzeiliger Text steht in der zsh-Eingabezeile, ohne dass
   Zeilen ausgeführt wurden (Bracketed Paste).

## Betroffen

- Speccify Desktop: `lib/handover.ts`, `HandoverSheet.tsx`, `TerminalPanel.tsx`,
  Board/Playbooks/Skills/Tools/Agent-Tabs, Git-Tab, Skill-Import.
- Hosts: Claude Code (Bracketed Paste im TUI), zsh ≥ 5.1.

## Erfolgsmaß für das Werkzeug

Dauer der Abnahme, Zahl der Befunde, Fehlalarme; Vergleich mit der
Chat-Anleitung vom 2026-09-14.
