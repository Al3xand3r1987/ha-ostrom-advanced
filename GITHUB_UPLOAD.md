# Anleitung: Integration auf GitHub hochladen

## Schritt 1: GitHub Repository erstellen

1. Gehe zu https://github.com und logge dich ein
2. Klicke auf das **+** Symbol oben rechts → **New repository**
3. Fülle das Formular aus:
   - **Repository name**: `ha-ostrom-advanced`
   - **Description**: "Home Assistant Integration for Ostrom dynamic electricity tariffs"
   - **Visibility**: Wähle **Public** (für HACS erforderlich)
   - **WICHTIG**: Lasse **NICHT** "Add a README file", "Add .gitignore" oder "Choose a license" aktiviert!
4. Klicke auf **Create repository**

## Schritt 2: Dateien vorbereiten

**WICHTIG**: Ersetze zuerst `YOUR_GITHUB_USERNAME` in folgenden Dateien durch deinen echten GitHub-Nutzernamen:

- `README.md` (2 Stellen)
- `info.md` (1 Stelle)
- `custom_components/ostrom_advanced/manifest.json` (2 Stellen)

## Schritt 3: Dateien hochladen (Web-Interface)

1. Auf der GitHub Repository-Seite klicke auf **uploading an existing file**
2. Ziehe alle Dateien und Ordner in das Upload-Fenster:
   ```
   .gitignore
   LICENSE
   README.md
   info.md
   hacs.json
   custom_components/
   ```
3. Scrolle nach unten und klicke auf **Commit changes**
4. Gib eine Commit-Nachricht ein: "Initial commit: Ostrom Advanced Integration"
5. Klicke auf **Commit changes**

## Option 2: Mit Git Command Line (für Fortgeschrittene)

### Schritt 1: Git initialisieren

Öffne PowerShell oder Terminal im Projektordner und führe aus:

```bash
# Git initialisieren
git init

# Alle Dateien hinzufügen
git add .

# Ersten Commit erstellen
git commit -m "Initial commit: Ostrom Advanced Integration"
```

### Schritt 2: GitHub Repository verbinden

```bash
# Ersetze YOUR_GITHUB_USERNAME mit deinem echten Nutzernamen
git remote add origin https://github.com/Al3xand3r1987/ha-ostrom-advanced.git

# Branch umbenennen (GitHub verwendet 'main')
git branch -M main

# Dateien hochladen
git push -u origin main
```

Falls du noch nicht eingeloggt bist, wird Git dich nach deinen GitHub-Credentials fragen.

## Schritt 4: Repository-URLs aktualisieren

Nach dem Hochladen musst du die Platzhalter in den Dateien ersetzen:

1. Gehe zu deinem Repository auf GitHub
2. Kopiere die Repository-URL (z.B. `https://github.com/dein-username/ha-ostrom-advanced`)
3. Ersetze in folgenden Dateien `YOUR_GITHUB_USERNAME` durch deinen echten Nutzernamen:
   - `README.md`
   - `info.md`
   - `custom_components/ostrom_advanced/manifest.json`

**Oder**: Ich kann das für dich machen, wenn du mir deinen GitHub-Nutzernamen gibst!

## Schritt 5: Erste Release erstellen (optional, aber empfohlen)

1. Gehe zu deinem Repository auf GitHub
2. Klicke auf **Releases** → **Create a new release**
3. **Tag version**: `v0.1.0`
4. **Release title**: `v0.1.0 - Initial Release`
5. **Description**: Kopiere die Features aus dem README
6. Klicke auf **Publish release**

## Schritt 6: HACS Integration testen

1. In Home Assistant: **HACS** → **Integrations**
2. Drei Punkte (⋮) → **Custom repositories**
3. Repository URL: `https://github.com/Al3xand3r1987/ha-ostrom-advanced`
4. Kategorie: **Integration**
5. Klicke **Add** und dann **Install**

## Troubleshooting

### "Repository not found"
- Stelle sicher, dass das Repository **Public** ist
- Prüfe, ob die URL korrekt ist

### "HACS kann Integration nicht finden"
- Stelle sicher, dass `hacs.json` im Root-Verzeichnis ist
- Prüfe, dass `manifest.json` korrekt ist
- Warte ein paar Minuten, HACS cached manchmal

### Git Authentication Fehler
- Verwende einen Personal Access Token statt Passwort
- Oder nutze GitHub Desktop als Alternative

