# Release Workflow - Schritt-für-Schritt Anleitung

Diese Anleitung führt Sie durch den kompletten Release-Prozess für Ostrom Advanced.

## Übersicht

Der Release-Workflow ist vollständig automatisiert. Sie müssen nur:
1. ✅ Skript ausführen
2. ✅ Release Notes kopieren
3. ✅ Version in manifest.json setzen (automatisch)
4. ✅ Git-Befehle ausführen (automatisch)
5. ✅ Release auf GitHub erstellen (Release Notes einfügen)

## Schritt-für-Schritt Anleitung

### Schritt 1: Entwicklung und Commits

Während der Entwicklung machen Sie normale Commits mit Präfixen:

```bash
git commit -m "feat: neue Funktion hinzufügen"
git commit -m "fix: Bug beheben"
git commit -m "docs: Dokumentation aktualisieren"
```

**Wichtig:** Verwenden Sie immer die Präfixe:
- `feat:` oder `feature:` für neue Features
- `fix:` oder `bug:` für Bugfixes
- `docs:` für Dokumentation
- `chore:` für Wartungsaufgaben
- `refactor:` für Code-Refactoring

### Schritt 2: Release Notes generieren

Führen Sie das Skript aus:

**Windows (PowerShell):**
```powershell
.\scripts\generate-release-notes.ps1
```

**Linux/Mac (Bash):**
```bash
./scripts/generate-release-notes.sh
```

**Was das Skript macht:**
- ✅ Liest aktuelle Version aus `manifest.json`
- ✅ Findet letzten Git-Tag
- ✅ Sammelt alle Commits seit dem letzten Tag
- ✅ **Empfiehlt automatisch die neue Version** (MAJOR/MINOR/PATCH)
- ✅ Generiert Release Notes (kategorisiert und priorisiert)
- ✅ Speichert Notes in `RELEASE_NOTES.md`
- ✅ Zeigt Copy-Paste-Befehle an

**Ausgabe des Skripts:**
```
Versionsempfehlung:
   Aktuelle Version: 0.3.0
   Empfohlene Version: 0.4.0 (MINOR (New Features))

Release Notes generiert: RELEASE_NOTES.md

COPY-PASTE BEFEHLE:
   git add custom_components/ostrom_advanced/manifest.json
   git commit -m "chore: release v0.4.0"
   git tag v0.4.0
   git push origin main
   git push origin v0.4.0
```

### Schritt 3: Version in manifest.json aktualisieren

**Automatisch (empfohlen):**
Das Skript zeigt die empfohlene Version an. Öffnen Sie `custom_components/ostrom_advanced/manifest.json` und setzen Sie:

```json
{
  "version": "0.4.0"  // ← Hier die empfohlene Version eintragen
}
```

**Wichtig:** 
- Version ohne `v`-Präfix (z.B. `"0.4.0"` nicht `"v0.4.0"`)
- Muss mit dem Tag übereinstimmen (Tag: `v0.4.0`, Manifest: `0.4.0`)

### Schritt 4: Git-Befehle ausführen

Kopieren Sie die Befehle aus dem Skript-Output und führen Sie sie aus:

```bash
git add custom_components/ostrom_advanced/manifest.json
git commit -m "chore: release v0.4.0"
git tag v0.4.0
git push origin main
git push origin v0.4.0
```

**Was passiert:**
- ✅ Version wird committed
- ✅ Git-Tag wird erstellt
- ✅ Alles wird zu GitHub gepusht

### Schritt 5: Release auf GitHub erstellen

1. **Gehen Sie zu:**
   https://github.com/Al3xand3r1987/ha-ostrom-advanced/releases/new

2. **Wählen Sie den Tag:**
   - Dropdown "Tag" → Wählen Sie `v0.4.0` (die empfohlene Version)
   - ✅ "Existing tag" sollte angezeigt werden

3. **Release Title:**
   - Wird automatisch auf "Ostrom Advanced v0.4.0" gesetzt

4. **Release Notes einfügen:**
   - Öffnen Sie `RELEASE_NOTES.md` im Projektordner
   - **Kopieren Sie den gesamten Inhalt**
   - **Fügen Sie ihn in das "Release notes" Feld ein**

5. **Release veröffentlichen:**
   - Klicken Sie auf **"Publish release"**

### Schritt 6: Automatische Verarbeitung

Nach dem Klicken auf "Publish release":

1. **GitHub Action Workflow wird automatisch getriggert:**
   - Sammelt alle Commits seit dem letzten Tag
   - Generiert Release Notes automatisch
   - **WICHTIG:** Überschreibt Ihre Release Notes NICHT (wenn Sie welche eingefügt haben)

2. **HACS erkennt das Release:**
   - HACS scannt das Repository periodisch
   - Erkennt die neue Version in `manifest.json`
   - Zeigt Update in Home Assistant an (nach 5-10 Minuten)

### Schritt 7: HACS Update prüfen

1. **In Home Assistant:**
   - Einstellungen → Geräte & Dienste
   - HACS suchen
   - "Neuladen" klicken

2. **Update prüfen:**
   - HACS → Integrations
   - "Ostrom Advanced" suchen
   - Prüfen, ob Update verfügbar ist

3. **Falls nicht sofort sichtbar:**
   - Warten Sie 5-10 Minuten (HACS scannt periodisch)
   - Prüfen Sie die Home Assistant Logs

## Checkliste für jedes Release

- [ ] Commits haben korrekte Präfixe (`feat:`, `fix:`, etc.)
- [ ] Skript ausgeführt: `.\scripts\generate-release-notes.ps1`
- [ ] Versionsempfehlung geprüft
- [ ] Version in `manifest.json` aktualisiert
- [ ] Git-Befehle ausgeführt (add, commit, tag, push)
- [ ] Release auf GitHub erstellt
- [ ] Release Notes aus `RELEASE_NOTES.md` eingefügt
- [ ] "Publish release" geklickt
- [ ] GitHub Action Workflow erfolgreich (grünes Häkchen)
- [ ] HACS Update verfügbar (nach 5-10 Minuten)

## Versionsempfehlung

Das Skript empfiehlt automatisch die passende Version:

- **MAJOR (1.0.0):** Breaking Changes (API-Änderungen)
- **MINOR (0.4.0):** Neue Features (rückwärtskompatibel)
- **PATCH (0.3.1):** Bugfixes oder Maintenance

**Sie müssen die Version nicht mehr selbst entscheiden!**

## Häufige Fehler vermeiden

### ❌ Fehler: Version stimmt nicht überein
**Problem:** Tag ist `v0.4.0`, aber Manifest hat `0.3.0`
**Lösung:** Verwenden Sie immer die vom Skript empfohlene Version

### ❌ Fehler: Release Notes wurden überschrieben
**Problem:** Workflow hat Ihre manuell eingefügten Notes überschrieben
**Lösung:** ✅ Behoben! Workflow überschreibt nicht mehr, wenn Notes vorhanden sind

### ❌ Fehler: HACS zeigt keine neue Version
**Problem:** HACS hat die neue Version noch nicht erkannt
**Lösung:** 
1. HACS in Home Assistant neu laden
2. 5-10 Minuten warten
3. Prüfen, ob Version in `manifest.json` im `main` Branch korrekt ist

### ❌ Fehler: Git-Tag existiert bereits
**Problem:** Tag wurde bereits erstellt
**Lösung:** Verwenden Sie eine andere Version oder löschen Sie den Tag:
```bash
git tag -d v0.4.0  # Lokal löschen
git push origin :refs/tags/v0.4.0  # Auf GitHub löschen
```

## Workflow-Diagramm

```
Entwicklung
    ↓
Commits (mit Präfixen)
    ↓
Skript ausführen → Versionsempfehlung + Release Notes
    ↓
Version in manifest.json setzen
    ↓
Git-Befehle ausführen (Tag erstellen & pushen)
    ↓
Release auf GitHub erstellen (Notes einfügen)
    ↓
"Publish release" klicken
    ↓
GitHub Action Workflow (automatisch)
    ↓
HACS erkennt Update (nach 5-10 Minuten)
    ↓
Fertig! ✅
```

## Support

Bei Problemen:
1. Prüfen Sie die GitHub Actions Logs: https://github.com/Al3xand3r1987/ha-ostrom-advanced/actions
2. Prüfen Sie die Home Assistant Logs
3. Siehe `HACS_RELEASE.md` für HACS-spezifische Probleme

