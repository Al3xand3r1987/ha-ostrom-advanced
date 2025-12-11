# Release Notes Generator Skripte

Diese Skripte generieren automatisch Release Notes aus Git-Commits seit dem letzten Tag.

## Verwendung

### Windows (PowerShell)

```powershell
.\scripts\generate-release-notes.ps1
```

### Linux/Mac (Bash)

```bash
chmod +x scripts/generate-release-notes.sh
./scripts/generate-release-notes.sh
```

## Was macht das Skript?

1. Liest die aktuelle Version aus `custom_components/ostrom_advanced/manifest.json`
2. Findet den letzten Git-Tag
3. Sammelt alle Commits seit dem letzten Tag
4. **Empfiehlt automatisch die neue Version** basierend auf Semantic Versioning:
   - **MAJOR** (1.0.0): Wenn Breaking Changes vorhanden sind
   - **MINOR** (0.3.0): Wenn neue Features (`feat:`) vorhanden sind
   - **PATCH** (0.2.3): Wenn nur Bugfixes (`fix:`) oder Maintenance vorhanden sind
5. Kategorisiert Commits nach Conventional Commits:
   - `feat:` / `feature:` → 🚀 New Features
   - `fix:` / `bug:` → 🐛 Bug Fixes
   - `chore:` / `refactor:` → 🔧 Maintenance
   - `docs:` → 📝 Documentation
6. Generiert Release Notes in der Priorität: Features → Fixes → Maintenance → Docs
7. Speichert die Notes in `RELEASE_NOTES.md`
8. Zeigt die Notes, Versionsempfehlung und Copy-Paste-Befehle in der Konsole an

## Ausgabe

Die Release Notes werden in `RELEASE_NOTES.md` gespeichert und können direkt kopiert und in das GitHub Release eingefügt werden.

## Weitere Informationen

Siehe [DEVELOPMENT.md](../DEVELOPMENT.md) für den vollständigen Release-Workflow.

