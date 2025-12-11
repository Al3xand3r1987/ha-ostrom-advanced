![Ostrom Advanced Banner](images/social_preview.png)

# Ostrom Advanced - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Eine benutzerdefinierte Home Assistant Integration für [Ostrom](https://www.ostrom.de/) dynamische Stromtarife in Deutschland. Diese Integration bietet Echtzeit-Strompreise, Verbrauchsdaten und berechnete Kosten für die Automatisierung Ihres Energieverbrauchs.

## Funktionen

- **Echtzeit-Strompreise**: Aktuelle All-in-Strompreise (inklusive Steuern und Abgaben)
- **Umfassende Preisstatistiken**: Min-, Max- und Durchschnittspreise für heute und morgen
- **Intelligente Zeit-Sensoren**: Finden Sie die günstigste Stunde, den günstigsten 3-Stunden-Block und die teuerste Stunde für heute und morgen
- **Binärsensoren**: Zeigen an, ob der günstigste 3-Stunden-Block gerade aktiv ist (Ein/Aus) - perfekt für einfache Automatisierungen
- **Visuelle Icons**: Alle Sensoren haben intuitive Material Design Icons zur einfachen Dashboard-Identifikation
- **Verbrauchserfassung**: Heutiger und gestriger Energieverbrauch (erfordert Vertrags-ID)
- **Kostenberechnung**: Automatische Kostenberechnung basierend auf tatsächlichem Verbrauch und Preisen
- **Zeitstempel-Unterstützung**: Zeitbasierte Sensoren verwenden die korrekte Timestamp-Device-Class für ApexCharts und Automatisierungen
- **Vollständige API-Unterstützung**: Verwendet die offizielle Ostrom API mit OAuth2-Authentifizierung
- **Robuste Fehlerbehandlung**: Elegante Behandlung fehlender Daten (z.B. morgige Preise noch nicht verfügbar)

## Voraussetzungen

1. **Ostrom-Konto**: Sie benötigen einen aktiven Ostrom-Stromvertrag
2. **Ostrom Developer Portal Zugang**: 
   - Melden Sie sich im [Ostrom Developer Portal](https://developer.ostrom-api.io/) an
   - Erstellen Sie einen API-Client, um Ihre **Client ID** und **Client Secret** zu erhalten
3. **Vertrags-ID**: Ihre Ostrom-Vertragsnummer (optional, nur für Verbrauchsdaten erforderlich)
4. **Postleitzahl**: Ihre deutsche Postleitzahl für genaue Steuer-/Abgabenberechnungen

## Installation

### HACS (Empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Gehen Sie zu **Integrations**
3. Klicken Sie auf das Drei-Punkte-Menü (⋮) → **Custom repositories**
4. Fügen Sie die Repository-URL hinzu: `https://github.com/Al3xand3r1987/ha-ostrom-advanced`
5. Wählen Sie die Kategorie: **Integration**
6. Klicken Sie auf **Add**
7. Suchen Sie nach "Ostrom Advanced" und installieren Sie es
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie die neueste Version herunter
2. Kopieren Sie den Ordner `custom_components/ostrom_advanced` in Ihr Home Assistant `config/custom_components/` Verzeichnis
3. Starten Sie Home Assistant neu

## Konfiguration

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **+ Integration hinzufügen**
3. Suchen Sie nach "Ostrom Advanced"
4. Füllen Sie das Konfigurationsformular aus:

| Feld | Beschreibung | Erforderlich |
|------|--------------|-------------|
| Environment | `Production` für echte Daten, `Sandbox` zum Testen | Ja |
| Client ID | Ihre OAuth2 Client ID vom Developer Portal | Ja |
| Client Secret | Ihr OAuth2 Client Secret vom Developer Portal | Ja |
| Postleitzahl | Deutsche Postleitzahl (z.B. `10115`) | Ja |
| Vertrags-ID | Ihre Ostrom-Vertragsnummer (optional, nur für Verbrauchsdaten) | Nein |
| Preis-Aktualisierungsintervall | Wie oft Preise abgerufen werden (5-120 Minuten, Standard: 15 Min) | Ja |
| Verbrauch-Aktualisierungsintervall | Wie oft Verbrauch abgerufen wird (15-1440 Minuten, Standard: 60 Min) | Ja |

**Hinweis**: Die Vertrags-ID ist optional. Wenn sie nicht angegeben wird, sind nur Preis-Sensoren verfügbar. Verbrauchs- und Kosten-Sensoren erfordern eine Vertrags-ID.

## Entitäten

Die Integration bietet umfassende Sensoren für Preisüberwachung, Verbrauchserfassung und Kostenberechnung. Alle Sensoren enthalten intuitive Material Design Icons zur einfachen visuellen Identifikation in Ihrem Dashboard.

### Preis-Sensoren

#### Aktueller Preis
| Entität | Beschreibung | Einheit | Icon |
|---------|--------------|---------|------|
| `sensor.ostrom_spot_prices_raw` | Aktueller All-in-Preis mit detaillierten Attributen (enthält alle stündlichen Slots) | €/kWh | ⚡ |
| `sensor.ostrom_price_now` | Aktueller stündlicher All-in-Preis mit Zeitreihen-Attributen für Charts (z.B. Apex Charts) | €/kWh | ⚡ |

#### Preisstatistiken für Heute
| Entität | Beschreibung | Einheit | Icon |
|---------|--------------|---------|------|
| `sensor.ostrom_price_today_min` | Minimalpreis heute | €/kWh | 📉 |
| `sensor.ostrom_price_today_max` | Maximalpreis heute | €/kWh | 📈 |
| `sensor.ostrom_price_today_avg` | Durchschnittspreis heute | €/kWh | 📊 |
| `sensor.ostrom_price_today_median` | Medianpreis heute | €/kWh | 📊 |

#### Zeitbasierte Sensoren für Heute
| Entität | Beschreibung | Typ | Icon |
|---------|--------------|-----|------|
| `sensor.ostrom_price_today_cheapest_hour_start` | Startzeit der günstigsten Stunde heute | Timestamp | 🕐 |
| `sensor.ostrom_price_today_cheapest_3h_block_start` | Startzeit des günstigsten 3-Stunden-Blocks heute (gleitendes Fenster) | Timestamp | ⏱️ |
| `sensor.ostrom_price_today_most_expensive_hour_start` | Startzeit der teuersten Stunde heute | Timestamp | ⚠️ |

#### Preisstatistiken für Morgen
| Entität | Beschreibung | Einheit | Icon |
|---------|--------------|---------|------|
| `sensor.ostrom_price_tomorrow_min` | Minimalpreis morgen | €/kWh | 📉 |
| `sensor.ostrom_price_tomorrow_max` | Maximalpreis morgen | €/kWh | 📈 |
| `sensor.ostrom_price_tomorrow_avg` | Durchschnittspreis morgen | €/kWh | 📊 |
| `sensor.ostrom_price_tomorrow_median` | Medianpreis morgen | €/kWh | 📊 |

#### Zeitbasierte Sensoren für Morgen
| Entität | Beschreibung | Typ | Icon |
|---------|--------------|-----|------|
| `sensor.ostrom_price_tomorrow_cheapest_hour_start` | Startzeit der günstigsten Stunde morgen | Timestamp | 🕐 |
| `sensor.ostrom_price_tomorrow_cheapest_3h_block_start` | Startzeit des günstigsten 3-Stunden-Blocks morgen (gleitendes Fenster) | Timestamp | ⏱️ |
| `sensor.ostrom_price_tomorrow_most_expensive_hour_start` | Startzeit der teuersten Stunde morgen | Timestamp | ⚠️ |

**Hinweis**: Die Sensoren für morgen werden als `unavailable` angezeigt, bis die Day-Ahead-Preise veröffentlicht werden (typischerweise nach 13:00 MEZ).

### Verbrauchs-Sensoren

| Entität | Beschreibung | Einheit |
|---------|--------------|---------|
| `sensor.ostrom_consumption_today_kwh` | Gesamtverbrauch heute | kWh |
| `sensor.ostrom_consumption_yesterday_kwh` | Gesamtverbrauch gestern | kWh |

### Kosten-Sensoren

| Entität | Beschreibung | Einheit |
|---------|--------------|---------|
| `sensor.ostrom_cost_today_eur` | Gesamtenergiekosten heute | € |
| `sensor.ostrom_cost_yesterday_eur` | Gesamtenergiekosten gestern | € |

### Binärsensoren

| Entität | Beschreibung | Status | Icon |
|---------|--------------|--------|------|
| `binary_sensor.ostrom_cheapest_3h_block_today_active` | Günstigster 3h-Block heute aktiv | Ein/Aus | 🔄 |
| `binary_sensor.ostrom_cheapest_3h_block_tomorrow_active` | Günstigster 3h-Block morgen aktiv | Ein/Aus | 🔄 |
| `binary_sensor.ostrom_cheapest_4h_block_today_active` | Günstigster 4h-Block heute aktiv | Ein/Aus | 🔄 |

**Hinweis**: Die Binärsensoren zeigen "Ein" (ON), wenn die aktuelle Zeit innerhalb des günstigsten 3-Stunden- bzw. 4-Stunden-Blocks liegt, sonst "Aus" (OFF). Sie enthalten Attribute mit Start- und Endzeit des Blocks.

### Raw-Preis-Sensor Attribute

Die Entität `sensor.ostrom_spot_prices_raw` enthält detaillierte Attribute:

- `today_slots`: Liste der stündlichen Preisslots für heute
- `tomorrow_slots`: Liste der stündlichen Preisslots für morgen  
- `current_slot_start`: Startzeit des aktuellen Preisslots
- `current_slot_end`: Endzeit des aktuellen Preisslots
- `last_update`: Zeitstempel der letzten Datenaktualisierung

Jeder Slot enthält:
- `start`: Slot-Startzeit (ISO-Format)
- `end`: Slot-Endzeit (ISO-Format)
- `net_price`: Nettopreis ohne MwSt. (€/kWh)
- `taxes_price`: Steuern und Abgaben (€/kWh)
- `total_price`: Gesamt All-in-Preis (€/kWh)

### Aktueller Preis-Sensor Attribute (für Zeitreihen)

Die Entität `sensor.ostrom_price_now` enthält speziell für Zeitreihen-Darstellungen optimierte Attribute:

- `today_total_prices`: Liste der Endpreise (total_price) für heute mit Timestamps
- `tomorrow_total_prices`: Liste der Endpreise (total_price) für morgen mit Timestamps (wenn verfügbar)
- `last_update`: Zeitstempel der letzten Datenaktualisierung

Jeder Eintrag in den Preislisten enthält:
- `timestamp`: Zeitstempel im ISO-Format (z.B. "2024-01-15T10:00:00+01:00")
- `total_price`: Gesamt All-in-Preis (€/kWh)

Diese Attribute sind ideal für die Verwendung mit Chart-Bibliotheken wie **Apex Charts**, um Preisdaten für die Zukunft (heute und morgen) visuell darzustellen. Die Daten sind bereits im richtigen Format für Zeitreihen-Diagramme aufbereitet.

## Automatisierungsbeispiele

### E-Auto-Ladung zur günstigsten Zeit starten

```yaml
automation:
  - alias: "E-Auto-Ladung im günstigsten 3h-Block starten"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_3h_block_start
    condition:
      - condition: state
        entity_id: sensor.ostrom_price_today_cheapest_3h_block_start
        state: "unavailable"
        invert: true
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
      - service: notify.mobile_app
        data:
          title: "E-Auto-Ladung gestartet"
          message: "Ladung im günstigsten 3h-Block: {{ states('sensor.ostrom_price_today_min') }} €/kWh"
```

### Ladung während teurer Stunden vermeiden

```yaml
automation:
  - alias: "E-Auto-Ladung während teurer Stunde stoppen"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_most_expensive_hour_start
    condition:
      - condition: state
        entity_id: switch.ev_charger
        state: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.ev_charger
      - service: notify.mobile_app
        data:
          title: "E-Auto-Ladung pausiert"
          message: "Pausiert während teurer Stunde: {{ states('sensor.ostrom_price_today_max') }} €/kWh"
```

### Benachrichtigung bei niedrigem Preis

```yaml
automation:
  - alias: "Benachrichtigung bei niedrigem Strompreis"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.ostrom_price_now') | float < 
             states('sensor.ostrom_price_today_avg') | float * 0.8 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Niedriger Strompreis"
          message: "Aktueller Preis ist {{ states('sensor.ostrom_price_now') }} €/kWh"
```

### Wärmepumpe intelligente Steuerung

```yaml
automation:
  - alias: "Wärmepumpe während günstiger Stunden aktivieren"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.ostrom_price_now') | float < 
             states('sensor.ostrom_price_today_avg') | float * 0.9 }}
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.heat_pump
        data:
          hvac_mode: heat

  - alias: "Vorheizen im günstigsten 3h-Block"
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

### Batterie-Ladestrategie

```yaml
automation:
  - alias: "Batterie zur günstigsten Stunde laden"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_hour_start
    condition:
      - condition: numeric_state
        entity_id: sensor.battery_soc
        below: 80
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
      - service: input_number.set_value
        target:
          entity_id: input_number.battery_charge_power
        data:
          value: 100

  - alias: "Batterie während teurer Stunde entladen"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_most_expensive_hour_start
    condition:
      - condition: numeric_state
        entity_id: sensor.battery_soc
        above: 20
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_discharge
```

### Automatisierung mit Binärsensor

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
          entity_id: 
            - switch.washing_machine
            - switch.dryer
      - service: notify.mobile_app
        data:
          title: "Günstigster Zeitraum aktiv"
          message: "Geräte wurden eingeschaltet"

  - alias: "Geräte außerhalb des günstigsten Blocks ausschalten"
    trigger:
      - platform: state
        entity_id: binary_sensor.ostrom_cheapest_3h_block_today_active
        to: "off"
    condition:
      - condition: state
        entity_id: switch.washing_machine
        state: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: 
            - switch.washing_machine
            - switch.dryer
```

## Sensordetails

### Zeitbasierte Sensoren (Timestamp Device Class)

Alle zeitbasierten Sensoren verwenden die `timestamp` Device-Class, was bedeutet:
- Sie geben ISO-formatierte Datums-/Zeitstrings zurück (z.B. `2024-01-15T14:00:00+01:00`)
- Sie funktionieren nahtlos mit ApexCharts zur Visualisierung
- Sie können direkt in zeitbasierten Automatisierungen verwendet werden
- Sie werden als `unavailable` angezeigt, wenn Daten fehlen (z.B. morgige Preise noch nicht veröffentlicht)

### Preisberechnungslogik

Die Integration verwendet generische Hilfsfunktionen zur Berechnung von Statistiken, was sicherstellt:
- **Konsistente Berechnungen** für heute und morgen
- **Robuste Fehlerbehandlung** bei fehlenden Daten
- **Effizienter Code** ohne Duplikation

#### 3-Stunden-Block-Berechnung

Der günstigste 3-Stunden-Block verwendet einen **gleitendes Fenster**-Algorithmus:
1. Alle möglichen 3-Stunden-Fenster werden ausgewertet
2. Der Durchschnittspreis für jedes Fenster wird berechnet
3. Das Fenster mit dem niedrigsten Durchschnittspreis wird ausgewählt
4. Die Startzeit dieses Fensters wird zurückgegeben

Dies stellt sicher, dass Sie den wirklich optimalen 3-Stunden-Zeitraum erhalten, nicht nur drei aufeinanderfolgende günstige Stunden.

### Icons

Alle Sensoren enthalten Material Design Icons zur visuellen Identifikation:
- ⚡ `mdi:flash` - Aktuelle Preissensoren
- 📉 `mdi:trending-down` - Minimalpreis-Sensoren
- 📈 `mdi:trending-up` - Maximalpreis-Sensoren
- 📊 `mdi:chart-bell-curve-cumulative` - Durchschnittspreis-Sensoren
- 🕐 `mdi:clock-start` - Startzeit günstigste Stunde
- ⏱️ `mdi:timer-outline` - Startzeit günstigster 3h-Block
- ⚠️ `mdi:clock-alert` - Startzeit teuerste Stunde

## Hinweise

### Day-Ahead-Preise

- Day-Ahead-Preise für morgen sind typischerweise nach 13:00 MEZ verfügbar
- Die `tomorrow_*` Sensoren werden als `unavailable` angezeigt, bis Preise veröffentlicht werden
- Preisdaten basieren auf EPEX Spot-Marktpreisen
- Die Integration behandelt fehlende morgige Daten elegant ohne Fehler

### Rate Limits

Die Ostrom API hat Rate Limits. Die Standard-Aktualisierungsintervalle sind so eingestellt, dass sie diese Limits respektieren:
- Preisaktualisierungen: Alle 15 Minuten
- Verbrauchsaktualisierungen: Alle 60 Minuten

### Preisberechnung

Der **Gesamtpreis** (All-in-Preis) enthält:
- Day-Ahead Spot-Preis (brutto, inklusive MwSt.)
- Steuern und Abgaben (brutto, inklusive MwSt.)

Formel: `total_price = (grossKwhPrice + grossKwhTaxAndLevies) / 100` (von Cent in €/kWh umgerechnet)

## Fehlerbehebung

### Authentifizierungsprobleme

1. Überprüfen Sie Ihre Client ID und Client Secret im Developer Portal
2. Stellen Sie sicher, dass Ihr API-Client die korrekten Berechtigungen hat
3. Stellen Sie sicher, dass Sie die korrekte Umgebung verwenden (Production vs Sandbox)

### Fehlende morgige Preise

- Day-Ahead-Preise werden täglich gegen 13:00 MEZ veröffentlicht
- Vor dieser Zeit werden die Sensoren für morgen als unavailable angezeigt

### Keine Verbrauchsdaten

- Verbrauchsdaten hängen von Smart-Meter-Ablesungen ab
- Daten können um mehrere Stunden verzögert sein
- Überprüfen Sie Ihre Ostrom-App, ob Daten in der offiziellen Oberfläche erscheinen

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

## Mitwirken

Beiträge sind willkommen! Bitte:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch
3. Nehmen Sie Ihre Änderungen vor
4. Reichen Sie einen Pull Request ein

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.

## Haftungsausschluss

Dies ist eine inoffizielle Integration und steht nicht in Verbindung mit Ostrom GmbH. Nutzung auf eigenes Risiko.

## Support

- [GitHub Issues](https://github.com/Al3xand3r1987/ha-ostrom-advanced/issues)
- [Home Assistant Community](https://community.home-assistant.io/)
