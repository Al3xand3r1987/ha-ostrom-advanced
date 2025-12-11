# HACS Release Checklist

## Wichtige Hinweise für HACS-Releases

HACS (Home Assistant Community Store) erkennt neue Versionen automatisch über:

1. **Version in `manifest.json`**: Die Version muss im Repository im `main` Branch sein
2. **GitHub Release**: Ein GitHub Release mit dem entsprechenden Tag muss existieren
3. **HACS Cache**: HACS scannt Repositories periodisch (kann einige Minuten dauern)

## Nach einem Release

### 1. Version prüfen
- Die Version in `custom_components/ostrom_advanced/manifest.json` muss im `main` Branch sein
- Der Git-Tag muss existieren (z.B. `v0.3.0`)
- Das GitHub Release muss veröffentlicht sein

### 2. HACS Cache aktualisieren
Falls HACS die neue Version nicht sofort anzeigt:

1. **In Home Assistant:**
   - Gehen Sie zu: Einstellungen → Geräte & Dienste
   - Suchen Sie nach "HACS"
   - Klicken Sie auf "Neuladen" oder "Reload"

2. **Manuelles Update prüfen:**
   - Gehen Sie zu: HACS → Integrations
   - Suchen Sie nach "Ostrom Advanced"
   - Klicken Sie auf die Integration
   - Prüfen Sie, ob ein Update verfügbar ist

3. **Falls immer noch nicht sichtbar:**
   - Warten Sie 5-10 Minuten (HACS scannt periodisch)
   - Prüfen Sie die Home Assistant Logs auf Fehler
   - Stellen Sie sicher, dass die Version in `manifest.json` wirklich `0.3.0` ist

## Workflow-Änderungen

Der GitHub Action Workflow wurde angepasst, damit:
- ✅ Manuell eingefügte Release Notes **nicht überschrieben** werden
- ✅ Release Notes nur generiert werden, wenn keine vorhanden sind
- ✅ Die Version in `manifest.json` automatisch aktualisiert wird

## Troubleshooting

### Problem: HACS zeigt noch alte Version
**Lösung:**
1. Prüfen Sie, ob die Version in `manifest.json` im `main` Branch korrekt ist
2. Prüfen Sie, ob der Git-Tag existiert: `git tag -l`
3. Prüfen Sie, ob das GitHub Release veröffentlicht ist
4. Laden Sie HACS in Home Assistant neu
5. Warten Sie 5-10 Minuten

### Problem: Release Notes wurden überschrieben
**Lösung:**
- Der Workflow wurde angepasst und überschreibt Release Notes nicht mehr, wenn sie manuell eingefügt wurden

### Problem: Version stimmt nicht überein
**Lösung:**
- Stellen Sie sicher, dass Tag (`v0.3.0`) und Manifest-Version (`0.3.0`) übereinstimmen
- Die Version in `manifest.json` muss ohne `v`-Präfix sein

