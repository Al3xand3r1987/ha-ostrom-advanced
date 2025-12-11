# Release Workflow - Ostrom Advanced

Diese Dokumentation erklärt, wie Releases für Ostrom Advanced erstellt werden und wann der Cursor AI Agent aktiv wird.

## Übersicht

Das Repository verwendet einen **zweistufigen Workflow**:

1. **Normaler Entwicklungs-Workflow**: Commits werden gesammelt, ohne dass sofort ein Release erstellt wird
2. **Release-Workflow**: Wenn ein Release gewünscht ist, wird der Cursor AI Agent beauftragt, ein Release zu erstellen

## Normaler Entwicklungs-Workflow (Commits sammeln)

### Was passiert normalerweise?

Wenn du Änderungen machst und committest, werden diese **nur gesammelt**. Es wird **kein Release** erstellt.

**Beispiel:**
```bash
# Du machst Änderungen
git add .
git commit -m "feat: add new sensor"
git push

# Du machst weitere Änderungen
git add .
git commit -m "fix: handle edge case"
git push

# Du machst noch mehr Änderungen
git add .
git commit -m "docs: update README"
git push
```

**Ergebnis**: Alle Commits sind auf GitHub, aber es gibt noch kein neues Release. HACS zeigt weiterhin die letzte Version an.

### Wann wird der Cursor AI Agent aktiv?

**Der Agent wird NICHT automatisch aktiv**, wenn du nur committest. Du musst ihn **explizit beauftragen**, ein Release zu erstellen.

### Was muss ich dem Agent sagen, damit nur Commits gemacht werden?

Wenn du nur Änderungen committen möchtest, **ohne** ein Release zu erstellen, verwende diese Formulierungen:

**Beispiele für nur Commits (kein Release):**
- "Ändere X in Datei Y"
- "Füge Feature Z hinzu"
- "Korrigiere Bug in..."
- "Aktuelliere die Dokumentation"
- "Commit diese Änderungen"
- "Push die Änderungen"
- "Füge einen neuen Sensor hinzu"
- "Korrigiere den Fehler in sensor.py"

**Was passiert:**
- ✅ Agent macht die Änderungen
- ✅ Erstellt einen Commit (z.B. `feat: ...`, `fix: ...`, `docs: ...`)
- ✅ Pusht zu GitHub
- ❌ **Kein Release wird erstellt**
- ✅ Commits werden gesammelt

**Beispiel-Dialog:**
```
Du: "Füge einen neuen Sensor hinzu"
Agent: ✅ Macht Änderungen, committed, pusht
→ Kein Release, nur Commit
```

**Weitere Beispiele:**
```
Du: "Korrigiere den Bug in der Preisberechnung"
Agent: ✅ Macht Änderungen, committed mit "fix: ...", pusht
→ Kein Release, nur Commit

Du: "Aktuelliere die README mit neuen Informationen"
Agent: ✅ Macht Änderungen, committed mit "docs: ...", pusht
→ Kein Release, nur Commit
```

## Release-Workflow (Cursor AI Agent wird aktiv)

### Wann solltest du ein Release erstellen?

- Wenn du eine neue Version veröffentlichen möchtest
- Wenn HACS-Nutzer das Update erhalten sollen
- Wenn du mehrere Commits zu einem Release zusammenfassen möchtest

### Wie beauftragst du den Cursor AI Agent?

**Wichtig**: Du musst explizit "Release" erwähnen, damit ein Release erstellt wird!

**Beispiele für Release-Erstellung:**
- "Erstelle ein Release für Version 0.4.0"
- "Mache ein Release"
- "Erstelle Release v0.4.0"
- "Release Version 0.4.0 erstellen"
- "Erstelle ein neues Release"
- "Bringe ein Release raus"
- "Erstelle Release für Version 0.4.0"

**Was passiert:**
- ✅ Agent aktualisiert `manifest.json` mit neuer Version
- ✅ Erstellt Commit `chore: release vX.Y.Z`
- ✅ Erstellt Git-Tag `vX.Y.Z`
- ✅ Pusht Tag zu GitHub
- ✅ Erstellt GitHub Release (mit deinem Token)

**Der Agent wird dann automatisch:**

1. ✅ Version in `manifest.json` aktualisieren
2. ✅ Commit mit `chore: release vX.Y.Z` erstellen
3. ✅ Git-Tag `vX.Y.Z` erstellen
4. ✅ Tag zu GitHub pushen
5. ✅ GitHub Release erstellen (mit deinem Token)

### Beispiel: Release erstellen

**Du sagst:**
> "Erstelle ein Release für Version 0.4.0"

**Der Agent macht:**
```bash
# 1. Version in manifest.json ändern
# 2. Commit erstellen
git add custom_components/ostrom_advanced/manifest.json
git commit -m "chore: release v0.4.0"

# 3. Tag erstellen
git tag v0.4.0

# 4. Alles pushen
git push origin main
git push origin v0.4.0

# 5. GitHub Release erstellen (mit deinem Token)
```

**Was passiert dann automatisch:**

1. GitHub Actions Workflow wird getriggert
2. Release Notes werden automatisch aus allen Commits seit dem letzten Release generiert
3. Release Notes werden kategorisiert:
   - 🚀 New Features
   - 🐛 Bug Fixes
   - 🔧 Maintenance
   - 📝 Documentation
4. HACS erkennt das neue Release automatisch

## Befehle für manuelles Release (ohne Agent)

Falls du ein Release manuell erstellen möchtest:

### Schritt 1: Version in manifest.json aktualisieren

```bash
# Öffne custom_components/ostrom_advanced/manifest.json
# Ändere "version": "0.3.1" zu "version": "0.4.0"
```

### Schritt 2: Version commiten

```bash
git add custom_components/ostrom_advanced/manifest.json
git commit -m "chore: release v0.4.0"
git push origin main
```

### Schritt 3: Tag erstellen und pushen

```bash
git tag v0.4.0
git push origin v0.4.0
```

### Schritt 4: GitHub Release erstellen

**Option A: Über GitHub Web-Interface**
1. Gehe zu: https://github.com/Al3xand3r1987/ha-ostrom-advanced/releases/new
2. Wähle Tag: `v0.4.0`
3. Titel: `Ostrom Advanced v0.4.0` (oder leer lassen)
4. Beschreibung: **Leer lassen** (Workflow generiert automatisch)
5. Klicke "Publish release"

**Option B: Über GitHub API (mit Token)**
```powershell
$env:GITHUB_TOKEN = "dein-token-hier"
$headers = @{ "Authorization" = "token $env:GITHUB_TOKEN"; "Accept" = "application/vnd.github.v3+json" }
$body = @{ tag_name = "v0.4.0"; name = "Ostrom Advanced v0.4.0"; draft = $false; prerelease = $false } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.github.com/repos/Al3xand3r1987/ha-ostrom-advanced/releases" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

## Commit-Message Konventionen

**Wichtig**: Verwende immer Conventional Commits, damit die Release Notes korrekt kategorisiert werden:

- `feat: ...` oder `feature: ...` → 🚀 New Features
- `fix: ...` oder `bug: ...` → 🐛 Bug Fixes
- `docs: ...` → 📝 Documentation
- `chore: ...` oder `refactor: ...` → 🔧 Maintenance

**Beispiele:**
```bash
git commit -m "feat: add cheapest 4h block binary sensor"
git commit -m "fix: handle missing tomorrow prices gracefully"
git commit -m "docs: update README with new sensor descriptions"
git commit -m "chore: release v0.4.0"
```

## HACS-Erkennung

HACS erkennt neue Releases automatisch über:

1. **Git Tags**: Format `vX.Y.Z` (z.B. `v0.4.0`)
2. **manifest.json**: Version muss mit Tag übereinstimmen (ohne `v`-Präfix)
3. **hacs.json**: Konfiguration muss korrekt sein

**Wichtig**: 
- Die Version in `manifest.json` muss **exakt** mit dem Git-Tag übereinstimmen (ohne `v`)
- Beispiel: Tag `v0.4.0` → manifest.json `"version": "0.4.0"`

## Zusammenfassung: Wann wird der Agent aktiv?

### ❌ Kein Release (nur Commits)

**Formulierungen, die nur Commits erzeugen:**
- "Ändere X"
- "Füge Y hinzu"
- "Korrigiere Z"
- "Commit die Änderungen"
- "Push zu GitHub"
- "Füge einen neuen Sensor hinzu"
- "Korrigiere den Bug"

**Was passiert:**
```bash
# Agent macht Änderungen
git add .
git commit -m "feat: neue Funktion"  # oder fix:, docs:, etc.
git push
# → Kein Release, nur Commits sammeln
```

### ✅ Release wird erstellt

**Formulierungen, die ein Release erstellen:**
- "Erstelle ein Release"
- "Mache ein Release"
- "Release Version X.Y.Z"
- "Erstelle Release vX.Y.Z"
- "Erstelle ein Release für Version 0.4.0"

**Was passiert:**
```
Du: "Erstelle ein Release für Version 0.4.0"
Agent: ✅ Macht alles automatisch
→ Release wird erstellt, HACS erkennt es
```

### Übersichtstabelle

| Was du sagst | Was passiert |
|-------------|--------------|
| "Füge Feature X hinzu" | ✅ Commit wird erstellt, **kein Release** |
| "Korrigiere Bug Y" | ✅ Commit wird erstellt, **kein Release** |
| "Aktuelliere Dokumentation" | ✅ Commit wird erstellt, **kein Release** |
| "Erstelle ein Release für Version 0.4.0" | ✅ **Release wird erstellt** |
| "Mache ein Release" | ✅ **Release wird erstellt** (Agent fragt nach Version) |

### Beispiel-Szenario über mehrere Tage

```
Tag 1: "Füge neuen Sensor hinzu" 
→ ✅ Commit "feat: add new sensor", kein Release

Tag 2: "Korrigiere Bug in Preisberechnung"
→ ✅ Commit "fix: correct price calculation", kein Release

Tag 3: "Aktuelliere README"
→ ✅ Commit "docs: update README", kein Release

Tag 4: "Erstelle ein Release für Version 0.4.0"
→ ✅ Release wird erstellt
→ ✅ Alle 3 Commits werden in Release Notes zusammengefasst:
   - 🚀 New Features: add new sensor
   - 🐛 Bug Fixes: correct price calculation
   - 📝 Documentation: update README
```

### Wichtige Unterscheidung

**Tipp**: Wenn du unsicher bist, ob ein Release erstellt wird:
- **Ohne "Release" im Befehl** → nur Commit
- **Mit "Release" im Befehl** → Release wird erstellt

## Troubleshooting

### Release wird nicht in HACS angezeigt?

1. Prüfe, ob der Tag korrekt gepusht wurde: `git tag -l`
2. Prüfe, ob die Version in `manifest.json` mit dem Tag übereinstimmt
3. Warte ein paar Minuten (HACS prüft periodisch)
4. Prüfe, ob das GitHub Release erstellt wurde

### Release Notes sind leer?

- Der Workflow sammelt nur Commits zwischen dem letzten Tag und dem aktuellen Tag
- Wenn du direkt auf `main` committest, werden diese erfasst
- Prüfe die GitHub Actions Logs für Details

### Workflow schlägt fehl?

- Prüfe die GitHub Actions Logs: https://github.com/Al3xand3r1987/ha-ostrom-advanced/actions
- Stelle sicher, dass der Tag existiert und gepusht wurde
- Stelle sicher, dass es Commits zwischen den Tags gibt

