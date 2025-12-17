# AGENTS.md (custom_components/)

## Zweck
- Dieses Verzeichnis enthaelt Home Assistant **Custom Components**.
- Diese Datei ist ein kurzer Spickzettel, damit ich hier **genau nach den Cursor Rules arbeite**.

## Source of Truth (wenn etwas widerspricht)
- **Cursor Rules** in `.cursor/rules/*.mdc` sind die Source of Truth (werden von mir nicht veraendert).
- Zusaetzlich gelten die Repo-Regeln aus `AGENTS.md` im Repo-Root.

## Arbeitsmodus
- Standard ist `ANALYSE` (nur lesen/erklaeren), ausser du startest explizit mit `UMSETZEN`.
- Bei `UMSETZEN`: kleine, fokussierte Aenderungen; keine ungefragten Erweiterungen.
- Bei `UMSETZEN` in `custom_components/`: Ich schaue vorher kurz in `.cursor/rules/*.mdc`, damit ich die aktuellen Cursor Rules sicher einhalte.

## Home Assistant / Python Regeln (Spiegel aus Cursor Rules)
- Antworten und Erklaerungen immer **auf Deutsch**.
- Code-Stil beibehalten; keine grossen Refactorings ohne ausdrueckliches OK.
- Python: async/await und Type Hints dort nutzen, wo das Projekt es bereits nutzt.
- Home Assistant: typische Integrations-Patterns beachten (z. B. Config Flow, Entities, Coordinator) und robustes Error-Handling beibehalten.
- Doku aktualisieren, wenn Verhalten/Features sich aendern (z. B. `README.md`, `info.md`).

## Ausfuehrung / Tests / Netzwerk
- Keine Installationen, kein Netzwerk, keine Tests ohne dein ausdrueckliches OK (z. B. `RUN TESTS`).

## Repo-Hygiene (Spiegel aus Cursor Rules)
- Entwickler-Ordner wie `.cursor/`, `.dev/`, `brands/` sind lokal und gehoeren nicht in Commits.
