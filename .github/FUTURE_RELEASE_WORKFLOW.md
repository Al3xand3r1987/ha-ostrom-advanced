# Zukünftiger Release-Workflow: Gesammelte Releases

## Ziel

Statt bei jedem Tag automatisch ein Release zu erstellen, sollen mehrere Commits gesammelt werden. Der Benutzer kann dann manuell einen Release erstellen, der alle gesammelten Änderungen zusammenfasst.

## Anforderungen

1. **Mehrere Commits sammeln**: Der Benutzer kann 4-5 Mal committen/pushen, ohne dass jedes Mal ein Release erstellt wird
2. **Manueller Release-Trigger**: Der Benutzer erstellt manuell einen Release auf GitHub
3. **Automatische Zusammenfassung**: Der Workflow sammelt alle Commits seit dem letzten Tag/Release
4. **Kategorisierte Release Notes**: Commits werden nach Conventional Commits kategorisiert (feat, fix, docs, etc.)
5. **Ein-Klick-Veröffentlichung**: Der Benutzer drückt nur einen Button, der Workflow macht den Rest

## Technische Umsetzung

### Option 1: Workflow auf `release` Event
```yaml
on:
  release:
    types: [published]  # Triggert nur bei manuell erstellten Releases
```

**Vorteile:**
- Benutzer erstellt Release auf GitHub UI
- Workflow generiert automatisch Release Notes aus Commits
- Einfach zu implementieren

**Nachteile:**
- Release muss manuell erstellt werden (aber das ist gewünscht)

### Option 2: Workflow auf `workflow_dispatch` mit Tag-Auswahl
```yaml
on:
  workflow_dispatch:
    inputs:
      tag:
        description: 'Tag to release (e.g. v0.3.0)'
        required: true
```

**Vorteile:**
- Workflow kann manuell gestartet werden
- Tag kann ausgewählt werden
- Flexibler

**Nachteile:**
- Mehr Schritte für den Benutzer

## Empfohlene Lösung

**Kombination aus beiden:**
- Workflow triggert auf `release: published` Event
- Wenn ein Release manuell auf GitHub erstellt wird:
  1. Workflow wird getriggert
  2. Findet den letzten Tag/Release
  3. Sammelt alle Commits dazwischen
  4. Generiert kategorisierte Release Notes
  5. Aktualisiert das Release mit den generierten Notes

## Workflow-Struktur

```yaml
name: Release

on:
  release:
    types: [published]  # Nur bei manuell erstellten Releases

jobs:
  update-release-notes:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Get previous release tag
        # Findet den letzten Tag vor diesem Release
      
      - name: Generate release notes
        # Sammelt Commits zwischen letztem Tag und aktuellem Release
        # Kategorisiert nach Conventional Commits
      
      - name: Update release
        # Aktualisiert das manuell erstellte Release mit generierten Notes
```

## Vorteile dieses Ansatzes

1. ✅ Mehrere Commits können gemacht werden ohne Releases
2. ✅ Benutzer hat volle Kontrolle über Release-Zeitpunkt
3. ✅ Automatische Zusammenfassung aller Änderungen
4. ✅ Kategorisierte Release Notes
5. ✅ Einfache Bedienung: Release erstellen → Workflow macht den Rest

## Offene Fragen

- Soll der Workflow das Release automatisch veröffentlichen oder nur die Notes aktualisieren?
- Sollen Tags automatisch erstellt werden oder nur bei manuellem Release?
- Wie sollen Breaking Changes behandelt werden?

## Status

🟡 **Geplant für zukünftige Implementierung**

Aktuell: Automatische Releases bei Tag-Push  
Zukünftig: Manuelle Releases mit automatischer Note-Generierung

