# Anleitung: Privat testen, später Public machen

## Strategie: Privat → Public

Du kannst die Integration **zuerst privat testen** und später auf **public** umstellen, wenn alles funktioniert.

## Phase 1: Privates Repository erstellen und manuell testen

### Schritt 1: Privates GitHub Repository erstellen

1. Gehe zu https://github.com/new
2. **Repository name**: `ha-ostrom-advanced`
3. **Visibility**: Wähle **Private** ⚠️
4. Lasse alle Checkboxen leer (keine README, kein .gitignore, keine License)
5. Klicke **Create repository**

### Schritt 2: Dateien hochladen

**Option A: GitHub Web-Interface (einfach)**
1. Auf der Repository-Seite: Klicke **uploading an existing file**
2. Ziehe alle Dateien hoch:
   - `.gitignore`
   - `LICENSE`
   - `README.md`
   - `info.md`
   - `hacs.json`
   - `custom_components/` (ganzer Ordner)
3. Commit-Nachricht: "Initial commit"
4. Klicke **Commit changes**

**Option B: Git Command Line**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Al3xand3r1987/ha-ostrom-advanced.git
git push -u origin main
```

### Schritt 3: Manuell in Home Assistant installieren (ohne HACS)

Da das Repository privat ist, kannst du HACS **nicht** verwenden. Stattdessen:

1. **Dateien manuell kopieren:**
   - Kopiere den Ordner `custom_components/ostrom_advanced` 
   - In dein Home Assistant `config/custom_components/` Verzeichnis
   
   **Pfad-Beispiel:**
   ```
   /config/custom_components/ostrom_advanced/
   ```

2. **Home Assistant neu starten**

3. **Integration hinzufügen:**
   - Settings → Devices & Services
   - + Add Integration
   - Suche nach "Ostrom Advanced"
   - Konfiguriere die Integration

### Schritt 4: Testen

- Prüfe, ob alle Sensoren erscheinen
- Teste die API-Verbindung
- Prüfe, ob Preise und Verbrauch korrekt angezeigt werden
- Teste Automatisierungen

## Phase 2: Auf Public umstellen (wenn alles funktioniert)

### Schritt 1: Repository auf Public stellen

1. Gehe zu deinem Repository auf GitHub
2. Klicke auf **Settings** (oben im Repository)
3. Scrolle ganz nach unten zu **Danger Zone**
4. Klicke **Change visibility**
5. Wähle **Make public**
6. Bestätige mit deinem Repository-Namen

### Schritt 2: HACS Integration hinzufügen

Jetzt kannst du HACS verwenden:

1. In Home Assistant: **HACS** → **Integrations**
2. Drei Punkte (⋮) → **Custom repositories**
3. Repository URL: `https://github.com/Al3xand3r1987/ha-ostrom-advanced`
4. Kategorie: **Integration**
5. Klicke **Add**
6. Suche nach "Ostrom Advanced" und installiere es

### Schritt 3: Manuelle Installation entfernen (optional)

Wenn du HACS verwendest, kannst du die manuell kopierten Dateien entfernen:

1. Lösche `/config/custom_components/ostrom_advanced/`
2. Starte Home Assistant neu
3. Die Integration läuft jetzt über HACS

## Vorteile dieser Strategie

✅ **Privat testen**: Du kannst alles in Ruhe testen, ohne dass andere es sehen  
✅ **Keine Eile**: Nimm dir Zeit zum Testen  
✅ **Sauberer Start**: Wenn du auf Public umstellst, ist alles bereits getestet  
✅ **Flexibel**: Du kannst jederzeit zurück auf Private stellen  

## Wichtige Hinweise

⚠️ **HACS funktioniert NUR mit Public Repositories**  
- Private Repos können von HACS nicht erreicht werden
- Für HACS musst du auf Public umstellen

✅ **Manuelle Installation funktioniert immer**  
- Egal ob Private oder Public
- Einfach Dateien kopieren

🔄 **Umstellen ist jederzeit möglich**  
- Private → Public: Settings → Danger Zone → Change visibility
- Public → Private: Gleicher Weg, umgekehrt

## Zusammenfassung

1. **Jetzt**: Repository als **Private** erstellen
2. **Testen**: Manuell in Home Assistant installieren und testen
3. **Später**: Wenn alles funktioniert → **Public** stellen
4. **Dann**: HACS verwenden für einfache Updates

