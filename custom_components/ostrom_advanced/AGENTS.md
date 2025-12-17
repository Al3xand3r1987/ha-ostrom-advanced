# AGENTS.md (custom_components/ostrom_advanced/)

## Zweck
- Regeln und Orientierung fuer den **Hauptcode** der Integration.
- Ziel: Ich arbeite hier konsistent nach den Cursor Rules, ohne Dinge "nebenbei" zu aendern.

## Source of Truth (wenn etwas widerspricht)
- **Cursor Rules** in `.cursor/rules/*.mdc` sind die Source of Truth (werden von mir nicht veraendert).
- Zusaetzlich gelten die Repo-Regeln aus `AGENTS.md` im Repo-Root und `custom_components/AGENTS.md`.

## Wichtige Dateien in diesem Ordner
- `manifest.json`: Metadaten + Version (Versioning/Release-Regeln beachten).
- `config_flow.py`: UI/Setup in Home Assistant.
- `coordinator.py`: zentrale Datenbeschaffung/Aktualisierung (robust bei Fehlern/fehlenden Daten).
- `sensor.py`, `binary_sensor.py`: Entitaeten fuer Home Assistant.
- `api.py`, `utils.py`, `const.py`: Hilfslogik/Kommunikation/Konstanten.
- `translations/` und `strings.json`: Texte/UEbersetzungen.

## Umsetzung (Spiegel aus Cursor Rules)
- Kleine, zusammenhaengende Aenderungen (max. 1-3 pro Aufgabe).
- Bestehende Patterns und Stil beibehalten (Home Assistant + Python).
- Fehlerbehandlung fuer API/fehlende Daten nicht "vereinfachen", sondern stabil halten.
- Wenn sich Verhalten/Features aendern: `README.md`/`info.md` mit anpassen.

## Release/Versioning (Spiegel aus Cursor Rules)
- SemVer `X.Y.Z`, Git Tag `vX.Y.Z`, Manifest-Version ohne `v`.
- Releases nur, wenn du explizit "Release" beauftragst.

## Ausfuehrung / Tests / Netzwerk
- Keine Installationen, kein Netzwerk, keine Tests ohne dein ausdrueckliches OK (z. B. `RUN TESTS`).
- Hinweis: Im Repo-Root `tests/` liegen aktuell keine lauffaehigen `.py` Tests (nur `__pycache__`); in `custom_components/ostrom_advanced/tests/test_utils.py` ist aktuell kein Testinhalt.

