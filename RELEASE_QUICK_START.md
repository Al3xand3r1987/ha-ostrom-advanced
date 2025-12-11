# Release Quick Start - Schnellreferenz

## 🚀 Release in 5 Schritten

### 1️⃣ Skript ausführen
```powershell
.\scripts\generate-release-notes.ps1
```

### 2️⃣ Version in manifest.json setzen
Öffne `custom_components/ostrom_advanced/manifest.json` und setze die **empfohlene Version** aus Schritt 1.

### 3️⃣ Git-Befehle ausführen
Kopiere die Befehle aus dem Skript-Output:
```bash
git add custom_components/ostrom_advanced/manifest.json
git commit -m "chore: release vX.Y.Z"
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z
```

### 4️⃣ Release auf GitHub erstellen
1. Gehe zu: https://github.com/Al3xand3r1987/ha-ostrom-advanced/releases/new
2. Wähle Tag: `vX.Y.Z` (empfohlene Version)
3. Kopiere Release Notes aus `RELEASE_NOTES.md`
4. Füge Notes ein
5. Klicke "Publish release"

### 5️⃣ HACS Update prüfen
- HACS in Home Assistant neu laden
- 5-10 Minuten warten
- Update sollte verfügbar sein

## ✅ Checkliste

- [ ] Skript ausgeführt
- [ ] Version in manifest.json gesetzt
- [ ] Git-Befehle ausgeführt
- [ ] Release auf GitHub erstellt
- [ ] Release Notes eingefügt
- [ ] "Publish release" geklickt
- [ ] GitHub Action erfolgreich (grünes Häkchen)
- [ ] HACS Update verfügbar

## 📖 Vollständige Anleitung

Siehe [RELEASE_WORKFLOW.md](RELEASE_WORKFLOW.md) für detaillierte Informationen.

