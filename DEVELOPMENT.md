# Development Guide

Diese Datei enthält interne Informationen für Entwickler und Maintainer der Ostrom Advanced Integration.

## Releasing a new version

**📖 Für eine detaillierte Schritt-für-Schritt Anleitung siehe: [RELEASE_WORKFLOW.md](RELEASE_WORKFLOW.md)**

Um eine neue Version zu veröffentlichen, folgen Sie diesen Schritten:

### 1. Entwicklung und Commits

Während der Entwicklung können Sie mehrere Commits machen, ohne dass jedes Mal ein Release erstellt wird. Verwenden Sie aussagekräftige Commit-Messages mit Präfixen:

- `feat:` oder `feature:` für neue Features
- `fix:` oder `bug:` für Bugfixes
- `docs:` für Dokumentation
- `chore:` für Wartungsaufgaben
- `refactor:` für Code-Refactoring

**Beispiel:**
```bash
git commit -m "feat: add cheapest 4h block binary sensor"
git commit -m "fix: handle missing tomorrow prices gracefully"
git commit -m "docs: update README with new sensor descriptions"
```

### 2. Release Notes generieren (mit automatischer Versionsempfehlung)

Verwenden Sie das lokale Skript, um Release Notes zu generieren:

**Windows (PowerShell):**
```powershell
.\scripts\generate-release-notes.ps1
```

**Linux/Mac (Bash):**
```bash
./scripts/generate-release-notes.sh
```

Das Skript:
- Liest die aktuelle Version aus `manifest.json`
- Findet den letzten Git-Tag
- Sammelt alle Commits seit dem letzten Tag
- **Empfiehlt automatisch die neue Version** basierend auf den Commits:
  - **MAJOR** (X.0.0): Wenn Breaking Changes vorhanden sind
  - **MINOR** (X.Y.0): Wenn neue Features (`feat:`) vorhanden sind
  - **PATCH** (X.Y.Z): Wenn nur Bugfixes (`fix:`) oder Maintenance (`chore:`, `docs:`) vorhanden sind
- Kategorisiert Commits nach Conventional Commits
- Generiert Release Notes in der Priorität: Features → Fixes → Maintenance → Docs
- Speichert die Notes in `RELEASE_NOTES.md`
- Zeigt die Notes und Copy-Paste-Befehle in der Konsole an

### 3. Version in manifest.json aktualisieren

- Öffnen Sie `custom_components/ostrom_advanced/manifest.json`
- Setzen Sie die `version` auf die **empfohlene Version** aus Schritt 2 (z.B. `"0.3.0"`)
- **Wichtig**: Die Version muss im Format `X.Y.Z` sein (ohne `v`-Präfix)
- Die empfohlene Version wird im Skript-Output angezeigt

### 4. Release auf GitHub erstellen

Das Skript zeigt Ihnen alle benötigten Befehle zum Kopieren an. Hier ist der Ablauf:

1. **Version committen:**
   ```bash
   git add custom_components/ostrom_advanced/manifest.json
   git commit -m "chore: release vX.Y.Z"
   ```
   (Ersetzen Sie `vX.Y.Z` mit der empfohlenen Version, z.B. `v0.3.0`)

2. **Git-Tag erstellen und pushen:**
   ```bash
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```
   - **Wichtig**: Der Tag muss im Format `vX.Y.Z` sein (mit `v`-Präfix)
   - Stellen Sie sicher, dass Tag (`v0.3.0`) und Manifest-Version (`0.3.0`) übereinstimmen
   - **Tipp**: Die genauen Befehle werden im Skript-Output angezeigt - einfach kopieren!

3. **Release auf GitHub erstellen:**
   - Gehen Sie zu https://github.com/Al3xand3r1987/ha-ostrom-advanced/releases/new
   - Wählen Sie den Tag `vX.Y.Z` aus (die empfohlene Version)
   - **Kopieren Sie die Release Notes** aus `RELEASE_NOTES.md` und fügen Sie sie in das Release-Formular ein
   - Klicken Sie auf "Publish release"

4. **Automatische Aktualisierung:**
   - GitHub Actions wird automatisch getriggert, wenn das Release veröffentlicht wird
   - Der Workflow generiert die Release Notes aus den Commits und aktualisiert das Release
   - Die automatisch generierten Notes haben die gleiche Struktur wie die lokalen Notes

### Workflow-Zusammenfassung

```
Entwicklung → Commits (mit Präfixen) → 
Release Notes generieren (Skript) → 
  ✓ Versionsempfehlung wird angezeigt
  ✓ Release Notes werden generiert
  ✓ Copy-Paste-Befehle werden angezeigt
Version in manifest.json aktualisieren → 
Tag erstellen & pushen (Befehle kopieren) → 
Release auf GitHub erstellen (Notes kopieren) → 
GitHub Action aktualisiert Release automatisch
```

### Versionsempfehlung

Das Skript empfiehlt automatisch die passende Version basierend auf Semantic Versioning:

- **MAJOR** (1.0.0): Breaking Changes (API-Änderungen, die bestehende Konfigurationen beeinträchtigen)
- **MINOR** (0.3.0): Neue Features (rückwärtskompatibel)
- **PATCH** (0.2.3): Bugfixes oder Maintenance (Dokumentation, Refactoring)

Sie müssen die Version nicht mehr selbst entscheiden - das Skript macht das für Sie!

## Vollständige Anleitung

Für eine detaillierte Schritt-für-Schritt Anleitung mit Checkliste und Fehlerbehebung siehe:
- **[RELEASE_WORKFLOW.md](RELEASE_WORKFLOW.md)** - Komplette Release-Anleitung
- **[HACS_RELEASE.md](HACS_RELEASE.md)** - HACS-spezifische Informationen

### Vorteile dieses Workflows

- ✅ **Mehrere Commits sammeln**: Kein automatisches Release bei jedem Commit
- ✅ **Volle Kontrolle**: Sie entscheiden, wann ein Release erstellt wird
- ✅ **Copy-Paste fähig**: Release Notes werden in Datei gespeichert
- ✅ **Automatische Kategorisierung**: Commits werden automatisch sortiert
- ✅ **Priorisiert**: Wichtige Änderungen (Features, Fixes) stehen oben

