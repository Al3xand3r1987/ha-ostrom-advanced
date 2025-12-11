# Development Guide

Diese Datei enthält interne Informationen für Entwickler und Maintainer der Ostrom Advanced Integration.

## Releasing a new version

Um eine neue Version zu veröffentlichen, folgen Sie diesen Schritten:

1. **Version in manifest.json aktualisieren**
   - Öffnen Sie `custom_components/ostrom_advanced/manifest.json`
   - Setzen Sie die `version` auf die neue SemVer-Version (z.B. `"0.2.0"`)
   - **Wichtig**: Die Version muss im Format `X.Y.Z` sein (ohne `v`-Präfix)

2. **Änderungen committen**
   - Verwenden Sie aussagekräftige Commit-Messages mit Präfixen:
     - `feat:` oder `feature:` für neue Features
     - `fix:` oder `bug:` für Bugfixes
     - `docs:` für Dokumentation
     - `chore:` für Wartungsaufgaben
     - `refactor:` für Code-Refactoring
   - Beispiel: `chore: release v0.2.0` für den Version-Bump

3. **Git-Tag erstellen**
   ```bash
   git tag v0.2.0
   ```
   - **Wichtig**: Der Tag muss im Format `vX.Y.Z` sein (mit `v`-Präfix)
   - Stellen Sie sicher, dass Tag (`v0.2.0`) und Manifest-Version (`0.2.0`) übereinstimmen

4. **Tag pushen**
   ```bash
   git push origin v0.2.0
   ```

5. **Automatisches Release**
   - GitHub Actions wird automatisch getriggert
   - Release Drafter erstellt ein Release mit emoji-basierten Release Notes
   - Die Release Notes werden basierend auf den Commit-Präfixen kategorisiert:
     - 🚀 New Features (für `feat:`, `feature:`)
     - 🐛 Bug Fixes (für `fix:`, `bug:`)
     - 📝 Maintenance (für `docs:`, `chore:`, `refactor:`)

**Hinweis**: Für vollständige Release Notes wird empfohlen, Änderungen über Pull Requests einzubringen, da Release Drafter primär PR-basiert arbeitet.

