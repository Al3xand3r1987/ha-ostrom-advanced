# Ostrom Advanced

Eine umfassende Home Assistant Integration für Ostrom dynamische Stromtarife in Deutschland. Erhalten Sie Echtzeit-Strompreise, detaillierte Statistiken und intelligente zeitbasierte Sensoren für die Automatisierung Ihres Energieverbrauchs.

## Funktionen

- **Echtzeit-Strompreise**: Aktuelle All-in-Strompreise mit detaillierten stündlichen Daten
- **Umfassende Statistiken**: Min-, Max- und Durchschnittspreise für heute und morgen
- **Intelligente Zeit-Sensoren**: 
  - Startzeit der günstigsten Stunde (heute & morgen)
  - Startzeit des günstigsten 3-Stunden-Blocks (gleitendes Fenster-Algorithmus)
  - Startzeit der teuersten Stunde (heute & morgen)
- **Binärsensoren**: Zeigen an, ob der günstigste 3-Stunden-Block gerade aktiv ist (Ein/Aus)
- **Visuelle Icons**: Alle Sensoren enthalten intuitive Material Design Icons
- **Verbrauchserfassung**: Täglicher Energieverbrauch und Kostenberechnung (erfordert Vertrags-ID)
- **Zeitstempel-Unterstützung**: Zeitbasierte Sensoren verwenden die korrekte Device-Class für ApexCharts und Automatisierungen
- **Robuste Fehlerbehandlung**: Elegante Behandlung fehlender Daten (z.B. morgige Preise noch nicht verfügbar)

## Schnellstart

1. Holen Sie sich Ihre API-Anmeldedaten aus dem [Ostrom Developer Portal](https://developer.ostrom-api.io/)
2. Fügen Sie die Integration in Home Assistant hinzu
3. Geben Sie Ihre Client ID, Client Secret, Postleitzahl und optional Ihre Vertrags-ID ein
4. Beginnen Sie mit der Automatisierung basierend auf Strompreisen!

## Verfügbare Sensoren

### Preisstatistiken (Heute & Morgen)
- Aktueller Preis, Minimal-, Maximal- und Durchschnittspreise
- Alle mit intuitiven Icons (⚡ 📉 📈 📊)

### Zeitbasierte Sensoren (Timestamp Device Class)
- **Startzeit Günstigste Stunde**: Beste Zeit zum Betrieb energieintensiver Geräte
- **Startzeit Günstigster 3h-Block**: Optimales 3-Stunden-Fenster mit gleitendem Fenster-Algorithmus
- **Startzeit Teuerste Stunde**: Zeit, um hohen Verbrauch zu vermeiden

### Binärsensoren
- **Günstigster 3h-Block Heute**: Zeigt "Ein" wenn der Block aktiv ist, sonst "Aus"
- **Günstigster 3h-Block Morgen**: Zeigt "Ein" wenn der Block aktiv ist, sonst "Aus"

### Verbrauch & Kosten (Erfordert Vertrags-ID)
- Tägliche Energieverbrauchserfassung
- Automatische Kostenberechnung basierend auf tatsächlichem Verbrauch

## Automatisierungsbeispiele

### E-Auto-Ladung
```yaml
automation:
  - alias: "E-Auto im günstigsten 3h-Block laden"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_3h_block_start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

### Wärmepumpe
```yaml
automation:
  - alias: "Vorheizen während günstiger Stunden"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_3h_block_start
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.heat_pump
        data:
          temperature: 22
```

### Batterieverwaltung
```yaml
automation:
  - alias: "Batterie zur günstigsten Stunde laden"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_hour_start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
```

### Binärsensor-Automatisierung
```yaml
automation:
  - alias: "Geräte nur im günstigsten 3h-Block aktivieren"
    trigger:
      - platform: state
        entity_id: binary_sensor.ostrom_cheapest_3h_block_today_active
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.washing_machine
```

## Technische Details

- Verwendet die offizielle Ostrom API mit OAuth2-Authentifizierung
- Generische Berechnungsfunktionen gewährleisten konsistente Ergebnisse
- Sensoren für morgen werden als `unavailable` angezeigt, bis Day-Ahead-Preise veröffentlicht werden (typischerweise nach 13:00 MEZ)
- Vertrags-ID ist optional - Preissensoren funktionieren ohne sie

Für vollständige Dokumentation und weitere Automatisierungsbeispiele siehe die [README](https://github.com/Al3xand3r1987/ha-ostrom-advanced).
