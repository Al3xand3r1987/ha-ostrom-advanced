![Ostrom Advanced Banner](images/social_preview.png)

# Ostrom Advanced - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Was ist Ostrom Advanced?

Eine benutzerdefinierte Home Assistant Integration für [Ostrom](https://www.ostrom.de/) dynamische Stromtarife in Deutschland. Die Integration verbindet sich mit der offiziellen Ostrom API und stellt umfassende Sensoren für Preisüberwachung, Verbrauchserfassung und Kostenberechnung bereit.

### Kern-Entitäten

Die Integration liefert folgende Hauptkategorien von Sensoren:

- **Aktueller Preis**: Echtzeit-Strompreise mit detaillierten Attributen für Charts und Automatisierungen
- **Preisstatistiken**: Minimal-, Maximal-, Durchschnitts- und Medianpreise für heute und morgen
- **Zeitbasierte Sensoren**: Günstigste Stunde, günstigster 3-Stunden-Block und teuerste Stunde (heute und morgen)
- **Binärsensoren**: Zeigen an, ob der günstigste 3-Stunden-Block gerade aktiv ist
- **Verbrauch und Kosten**: Täglicher Energieverbrauch und berechnete Kosten (erfordert Vertrags-ID und Smart Meter Gateway)

### Praktische Anwendungen

Mit dieser Integration können Sie:

- **Wärmepumpen** im günstigsten Zeitfenster betreiben
- **E-Autos** zu optimalen Zeiten laden
- **Haushaltsgeräte** (Waschmaschine, Trockner) in günstigen Zeiträumen starten
- **Batteriespeicher** intelligent laden und entladen
- **Preisverläufe** in Dashboards visualisieren
- **Kosten** basierend auf tatsächlichem Verbrauch berechnen

### Unterstützung / Buy Me a Coffee ☕

Dieses Projekt entsteht in meiner Freizeit.  
Wenn dir die Ostrom Advanced Integration hilft und du mich unterstützen möchtest, kannst du mir hier freiwillig einen „Coffee" spendieren:

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/alexanderb8k)

Unterstützung ist komplett optional, die Integration bleibt natürlich kostenlos und open source.

---
### Unterstützung & Ostrom Bonus (optional)

> 💡 **Hinweis:** Dieses Projekt ist ein privates Open-Source-Projekt und steht in keiner offiziellen Beziehung zur Ostrom GmbH. Wenn dir die Integration hilft und du Ostrom-Neukund:in werden möchtest, kannst du das Ostrom-Empfehlungsprogramm nutzen und dabei auch mich unterstützen.

- Ostrom bietet aktuell ein Empfehlungsprogramm mit Bonus für Neukund:innen  
  (z. B. Rechnungs­gutschrift oder Guthaben für den Ostrom Store – Details stehen auf der Ostrom-Webseite).
- Alle Konditionen, Bonusbeträge und Auszahlungen werden ausschließlich von Ostrom geregelt.
- Die Integration funktioniert vollständig, auch wenn du kein Empfehlungsprogramm nutzt.

👉 Wenn du mich unterstützen möchtest, kannst du dich gern bei mir melden (z. B. über GitHub Issues).  
Ich teile dir dann einen persönlichen Empfehlungscode mit, sofern er verfügbar und gültig ist.  
Ich prüfe den Code nicht vor jeder Nutzung, daher kann es vorkommen, dass er künftig nicht mehr akzeptiert wird.
---

## Installation

## Voraussetzungen

1. **Ostrom-Konto**: Sie benötigen einen aktiven Ostrom-Stromvertrag
2. **Ostrom Developer Portal Zugang**: 
   - Melden Sie sich im [Ostrom Developer Portal](https://developer.ostrom-api.io/) an
   - Erstellen Sie einen API-Client, um Ihre **Client ID** und **Client Secret** zu erhalten
3. **Vertrags-ID**: Ihre Ostrom-Vertragsnummer (optional, nur für Verbrauchsdaten erforderlich)
4. **Postleitzahl**: Ihre deutsche Postleitzahl für genaue Steuer-/Abgabenberechnungen

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

| Feld | Beschreibung | Erforderlich | Standard |
|------|--------------|-------------|---------|
| Environment | `Production` für echte Daten, `Sandbox` zum Testen | Ja | Production |
| Client ID | Ihre OAuth2 Client ID vom Developer Portal | Ja | - |
| Client Secret | Ihr OAuth2 Client Secret vom Developer Portal | Ja | - |
| Postleitzahl | Deutsche Postleitzahl (z.B. `10115`) | Ja | - |
| Vertrags-ID | Ihre Ostrom-Vertragsnummer (optional, nur für Verbrauchsdaten) | Nein | - |
| Preis-Aktualisierungsintervall | Wie oft Preise abgerufen werden (5-120 Minuten) | Ja | 15 Min |
| Verbrauch-Aktualisierungsintervall | Wie oft Verbrauch abgerufen wird (15-1440 Minuten) | Nein | 60 Min |
| Update Offset | Sekunden nach Intervall-Raster für synchronisierte Updates (5-60 Sekunden) | Nein | 15 Sek |

**Hinweis zur Vertrags-ID**: Die Vertrags-ID ist optional. Wenn sie nicht angegeben wird, sind nur Preis-Sensoren verfügbar. Verbrauchs- und Kosten-Sensoren erfordern eine Vertrags-ID.

### Hinweis zu Verbrauchsdaten

Verbrauchsdaten sind optional und werden nur angezeigt, wenn Ostrom stündliche Messwerte bereitstellt. Das ist typischerweise der Fall, wenn ein Smart Meter mit Gateway aktiv ist und die Messwerte bei Ostrom freigeschaltet sind.

Wenn keine stündlichen Verbrauchsdaten verfügbar sind, bleiben die Verbrauchsentitäten auf `unknown` oder `unavailable`. Das ist normal und kann ignoriert werden. Sobald Ostrom Verbrauchsdaten liefert, werden die Werte automatisch bei den nächsten Updates sichtbar.

### Synchronisierte Updates: Intervall und Offset

Die Integration unterstützt synchronisierte Updates mit einem konfigurierbaren Offset. Der Offset ist eine feste Verschiebung nach dem Intervall-Raster, die sicherstellt, dass Updates zu konstanten Zeiten erfolgen.

**Beispiele:**

- **15 Minuten Intervall + 15 Sekunden Offset**: Updates erfolgen um 00:00:15, 00:15:15, 00:30:15, 00:45:15
- **60 Minuten Intervall + 10 Sekunden Offset**: Updates erfolgen um 01:00:10, 02:00:10, 03:00:10

**Vorteile:**
- Konstante Update-Zeiten, kein Drift über die Zeit
- Vermeidung von Lastspitzen durch gleichmäßige Verteilung
- Vorhersagbare Zeiten für Automatisierungen

### Standardwerte

- **Preis-Aktualisierungsintervall: 15 Minuten**: Dieser Wert ist als Vorbereitung für mögliche feinere Preis-Raster gewählt. Falls Ostrom in Zukunft feinere Preisintervalle anbietet, ist die Integration bereits darauf vorbereitet.
- **Verbrauch-Aktualisierungsintervall: 60 Minuten**: Verbrauchsdaten ändern sich langsamer als Preise, daher ist ein 60-Minuten-Intervall ausreichend und respektiert API-Rate-Limits.

### Optionen später ändern

Sie können die Konfigurationsoptionen jederzeit ändern, ohne die Integration zu entfernen oder neu zu installieren:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Suchen Sie nach "Ostrom Advanced" und klicken Sie auf die Integration
3. Klicken Sie auf **Optionen**
4. Ändern Sie die gewünschten Werte (Preis-Intervall, Verbrauch-Intervall, Update Offset)
5. Klicken Sie auf **Absenden**

Die Änderungen werden sofort wirksam, ein Neustart von Home Assistant ist nicht erforderlich.

## Entitäten

Die Integration bietet umfassende Sensoren für Preisüberwachung, Verbrauchserfassung und Kostenberechnung. Alle Sensoren enthalten intuitive Material Design Icons zur einfachen visuellen Identifikation in Ihrem Dashboard.

### Wichtigste Entitäten für normale Nutzer

- **Aktueller Preis**: Zeigt den aktuellen stündlichen Strompreis mit Zeitreihen-Daten für Charts
- **Günstigster 3-Stunden-Block**: Startzeit des günstigsten zusammenhängenden 3-Stunden-Zeitraums (heute und morgen) - ideal für Wärmepumpen und Haushaltsgeräte
- **Günstigste und teuerste Stunde**: Beste und schlechteste Zeitpunkte für energieintensive Aktivitäten
- **Preisstatistiken**: Minimal-, Maximal-, Durchschnitts- und Medianpreise für heute und morgen
- **Binärsensoren**: Zeigen an, ob der günstigste 3-Stunden-Block gerade aktiv ist (Ein/Aus) - perfekt für einfache Automatisierungen
- **Verbrauch und Kosten**: Täglicher Energieverbrauch und berechnete Kosten (erfordert Vertrags-ID und Smart Meter Gateway)

<details>
<summary>Alle Entitäten im Detail</summary>

#### 1. Preis-Sensoren

**Zweck**: Zeigen den aktuellen Strompreis mit verschiedenen Detailgraden für unterschiedliche Anwendungsfälle.

| Entität | Beschreibung | Einheit | Update | Icon |
|---------|--------------|---------|--------|------|
| `sensor.ostrom_spot_prices_raw` | Aktueller All-in-Preis mit detaillierten Attributen (enthält alle stündlichen Slots mit Netto- und Steuerpreisen) | €/kWh | Alle 15 Min (Standard) | ⚡ |
| `sensor.ostrom_price_now` | Aktueller stündlicher All-in-Preis mit Zeitreihen-Attributen optimiert für Charts (z.B. Apex Charts) | €/kWh | Alle 15 Min (Standard) | ⚡ |

#### 2. Statistik-Sensoren

**Zweck**: Berechnen statistische Werte (Minimal-, Maximal-, Durchschnitts- und Medianpreis) für heute und morgen.

**Heute:**
| Entität | Beschreibung | Einheit | Update | Icon |
|---------|--------------|---------|--------|------|
| `sensor.ostrom_price_today_min` | Minimalpreis heute | €/kWh | Alle 15 Min (Standard) | 📉 |
| `sensor.ostrom_price_today_max` | Maximalpreis heute | €/kWh | Alle 15 Min (Standard) | 📈 |
| `sensor.ostrom_price_today_avg` | Durchschnittspreis heute | €/kWh | Alle 15 Min (Standard) | 📊 |
| `sensor.ostrom_price_today_median` | Medianpreis heute | €/kWh | Alle 15 Min (Standard) | 📊 |

**Morgen:**
| Entität | Beschreibung | Einheit | Update | Icon |
|---------|--------------|---------|--------|------|
| `sensor.ostrom_price_tomorrow_min` | Minimalpreis morgen | €/kWh | Alle 15 Min (Standard) | 📉 |
| `sensor.ostrom_price_tomorrow_max` | Maximalpreis morgen | €/kWh | Alle 15 Min (Standard) | 📈 |
| `sensor.ostrom_price_tomorrow_avg` | Durchschnittspreis morgen | €/kWh | Alle 15 Min (Standard) | 📊 |
| `sensor.ostrom_price_tomorrow_median` | Medianpreis morgen | €/kWh | Alle 15 Min (Standard) | 📊 |

**Hinweis**: Die Sensoren für morgen werden als `unavailable` angezeigt, bis die Day-Ahead-Preise veröffentlicht werden (typischerweise nach 13:00 MEZ).

#### 3. Zeit-Sensoren

**Zweck**: Finden die optimalen Zeitpunkte für energieintensive Aktivitäten. Verwenden die `timestamp` Device-Class für direkte Verwendung in Automatisierungen.

**Heute:**
| Entität | Beschreibung | Typ | Update | Icon |
|---------|--------------|-----|--------|------|
| `sensor.ostrom_price_today_cheapest_hour_start` | Startzeit der günstigsten Stunde heute (ISO-Format, z.B. `2024-01-15T14:00:00+01:00`) | Timestamp | Alle 15 Min (Standard) | 🕐 |
| `sensor.ostrom_price_today_cheapest_3h_block_start` | Startzeit des günstigsten 3-Stunden-Blocks heute (gleitendes Fenster-Algorithmus) | Timestamp | Alle 15 Min (Standard) | ⏱️ |
| `sensor.ostrom_price_today_most_expensive_hour_start` | Startzeit der teuersten Stunde heute | Timestamp | Alle 15 Min (Standard) | ⚠️ |

**Morgen:**
| Entität | Beschreibung | Typ | Update | Icon |
|---------|--------------|-----|--------|------|
| `sensor.ostrom_price_tomorrow_cheapest_hour_start` | Startzeit der günstigsten Stunde morgen | Timestamp | Alle 15 Min (Standard) | 🕐 |
| `sensor.ostrom_price_tomorrow_cheapest_3h_block_start` | Startzeit des günstigsten 3-Stunden-Blocks morgen (gleitendes Fenster-Algorithmus) | Timestamp | Alle 15 Min (Standard) | ⏱️ |
| `sensor.ostrom_price_tomorrow_most_expensive_hour_start` | Startzeit der teuersten Stunde morgen | Timestamp | Alle 15 Min (Standard) | ⚠️ |

**Zeitzone**: Alle Zeitstempel verwenden die lokale Zeitzone (MEZ/MESZ) im ISO-Format.

#### 4. Binary-Sensoren

**Zweck**: Zeigen an, ob der günstigste Zeitblock gerade aktiv ist. Ideal für einfache Automatisierungen ohne Zeitberechnungen.

| Entität | Beschreibung | Status | Update | Icon |
|---------|--------------|--------|--------|------|
| `binary_sensor.ostrom_cheapest_3h_block_today_active` | Günstigster 3h-Block heute aktiv | Ein/Aus | Alle 15 Min (Standard) | 🔄 |
| `binary_sensor.ostrom_cheapest_3h_block_tomorrow_active` | Günstigster 3h-Block morgen aktiv | Ein/Aus | Alle 15 Min (Standard) | 🔄 |
| `binary_sensor.ostrom_cheapest_4h_block_today_active` | Günstigster 4h-Block heute aktiv | Ein/Aus | Alle 15 Min (Standard) | 🔄 |

**Verhalten**: Die Binärsensoren zeigen "Ein" (ON), wenn die aktuelle Zeit innerhalb des entsprechenden Blocks liegt, sonst "Aus" (OFF). Sie enthalten Attribute mit Start- und Endzeit des Blocks im ISO-Format.

**Attribute:**
- `block_start`: Startzeit des Blocks (ISO-Format, z.B. `2024-01-15T14:00:00+01:00`)
- `block_end`: Endzeit des Blocks (ISO-Format)

#### 5. Verbrauchs-Sensoren

**Zweck**: Erfassen den täglichen Energieverbrauch basierend auf Smart Meter Daten von Ostrom.

| Entität | Beschreibung | Einheit | Update | Voraussetzung |
|---------|--------------|---------|--------|---------------|
| `sensor.ostrom_consumption_today_kwh` | Gesamtverbrauch heute | kWh | Alle 60 Min (Standard) | Vertrags-ID + Smart Meter Gateway |
| `sensor.ostrom_consumption_yesterday_kwh` | Gesamtverbrauch gestern | kWh | Alle 60 Min (Standard) | Vertrags-ID + Smart Meter Gateway |

**Hinweis zu Verbrauchsdaten**: Diese Sensoren werden angelegt, wenn eine Vertrags-ID konfiguriert ist. Sie zeigen `unknown` oder `unavailable`, wenn keine stündlichen Messwerte von Ostrom verfügbar sind. Das ist normal und kann ignoriert werden, wenn kein Smart Meter mit Gateway aktiv ist oder die Messwerte bei Ostrom noch nicht freigeschaltet sind. Sobald Ostrom Verbrauchsdaten liefert, werden die Werte automatisch bei den nächsten Updates sichtbar.

#### 6. Kosten-Sensoren

**Zweck**: Berechnen die tatsächlichen Energiekosten basierend auf Verbrauch und Preisen.

| Entität | Beschreibung | Einheit | Update | Voraussetzung |
|---------|--------------|---------|--------|---------------|
| `sensor.ostrom_cost_today_eur` | Gesamtenergiekosten heute | € | Bei Preis- und Verbrauchs-Updates | Vertrags-ID + Smart Meter Gateway |
| `sensor.ostrom_cost_yesterday_eur` | Gesamtenergiekosten gestern | € | Bei Preis- und Verbrauchs-Updates | Vertrags-ID + Smart Meter Gateway |

**Berechnung**: Kosten = Verbrauch (kWh) × Preis (€/kWh) für jede Stunde, summiert über den Tag.

</details>

### Attribute und Datenstrukturen

#### Raw-Preis-Sensor (`sensor.ostrom_spot_prices_raw`)

**Zweck**: Enthält alle detaillierten Preisdaten mit Netto- und Steuerpreisen für erweiterte Analysen.

**Attribute:**
- `today_slots`: Liste der stündlichen Preisslots für heute
- `tomorrow_slots`: Liste der stündlichen Preisslots für morgen (wenn verfügbar)
- `current_slot_start`: Startzeit des aktuellen Preisslots (ISO-Format, z.B. `2024-01-15T14:00:00+01:00`)
- `current_slot_end`: Endzeit des aktuellen Preisslots (ISO-Format)
- `last_update`: Zeitstempel der letzten Datenaktualisierung (ISO-Format)

**Slot-Struktur** (jeder Eintrag in `today_slots` und `tomorrow_slots`):
```json
{
  "start": "2024-01-15T14:00:00+01:00",
  "end": "2024-01-15T15:00:00+01:00",
  "net_price": 0.12345,
  "taxes_price": 0.05678,
  "total_price": 0.18023
}
```

#### Preis-Now-Sensor (`sensor.ostrom_price_now`)

**Zweck**: Optimiert für Zeitreihen-Darstellungen in Charts (z.B. Apex Charts). Enthält nur die für Visualisierungen notwendigen Daten.

**Attribute:**
- `today_total_prices`: Liste der Endpreise für heute mit Timestamps
- `tomorrow_total_prices`: Liste der Endpreise für morgen mit Timestamps (wenn verfügbar)
- `last_update`: Zeitstempel der letzten Datenaktualisierung (ISO-Format)

**Preislisten-Struktur** (jeder Eintrag in `today_total_prices` und `tomorrow_total_prices`):
```json
{
  "timestamp": "2024-01-15T14:00:00+01:00",
  "total_price": 0.18023
}
```

**Verwendung**: Diese Attribute sind ideal für Chart-Bibliotheken wie **Apex Charts**, um Preisdaten für die Zukunft (heute und morgen) visuell darzustellen. Die Daten sind bereits im richtigen Format für Zeitreihen-Diagramme aufbereitet.

## Praxis-Beispiele

### Wärmepumpe im günstigsten 3-Stunden-Block

Der günstigste 3-Stunden-Block ist ideal für Wärmepumpen, da ein zusammenhängender Zeitraum mit stabil niedrigen Preisen wichtiger ist als einzelne kurze Preistiefs.

```yaml
automation:
  - alias: "Wärmepumpe im günstigsten 3h-Block aktivieren"
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

### Haushaltsgeräte mit Binärsensor

Einfache Automatisierung ohne Zeitberechnungen - nutzt den Binärsensor, der automatisch prüft, ob der günstigste Block aktiv ist.

```yaml
automation:
  - alias: "Geräte im günstigsten Block starten"
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
```

### Dashboard Charts mit Apex Charts

Der `sensor.ostrom_price_now` Sensor enthält bereits optimierte Zeitreihen-Daten in den Attributen `today_total_prices` und `tomorrow_total_prices`. Diese können direkt in Apex Charts verwendet werden:

```yaml
type: custom:apexcharts-card
entity: sensor.ostrom_price_now
data_generator: |
  return [
    {
      name: "Heute",
      data: entity.attributes.today_total_prices.map(item => [item.timestamp, item.total_price])
    },
    {
      name: "Morgen",
      data: (entity.attributes.tomorrow_total_prices || []).map(item => [item.timestamp, item.total_price])
    }
  ]
```

### E-Auto-Ladung zur optimalen Zeit

```yaml
automation:
  - alias: "E-Auto im günstigsten Block laden"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_3h_block_start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

<details>
<summary>Details für Power User</summary>

### Update-Mechanismus

Die Integration verwendet Home Assistant's Coordinator-Pattern für Datenaktualisierungen:

- **Preis-Coordinator**: Verwaltet Preis-Updates mit konfigurierbarem Intervall und Offset
- **Verbrauchs-Coordinator**: Verwaltet Verbrauchs-Updates separat (nur wenn Vertrags-ID vorhanden)
- **Synchronisierte Updates**: Updates erfolgen zu konstanten Zeiten basierend auf Intervall + Offset
- **Automatische Neusynchronisation**: Bei Änderung der Konfiguration werden Timer automatisch neu berechnet

### Rate Limits und API-Nutzung

Die Ostrom API hat Rate Limits. Die Standard-Aktualisierungsintervalle sind so gewählt, dass sie diese Limits respektieren:

- **Preisaktualisierungen**: Standard 15 Minuten (konfigurierbar: 5-120 Minuten)
- **Verbrauchsaktualisierungen**: Standard 60 Minuten (konfigurierbar: 15-1440 Minuten)

Bei häufigeren Updates kann es zu Rate-Limit-Fehlern kommen. Die Integration behandelt diese Fehler elegant und versucht es beim nächsten Update erneut.

### Preisberechnung

Der **Gesamtpreis** (All-in-Preis) wird wie folgt berechnet:

```
total_price = (grossKwhPrice + grossKwhTaxAndLevies) / 100
```

- `grossKwhPrice`: Day-Ahead Spot-Preis (brutto, inklusive MwSt.)
- `grossKwhTaxAndLevies`: Steuern und Abgaben (brutto, inklusive MwSt.)
- Ergebnis: Umrechnung von Cent in €/kWh

### 3-Stunden-Block-Algorithmus

Der günstigste 3-Stunden-Block verwendet einen **gleitendes Fenster**-Algorithmus:

1. Alle möglichen 3-Stunden-Fenster werden ausgewertet
2. Der Durchschnittspreis für jedes Fenster wird berechnet
3. Das Fenster mit dem niedrigsten Durchschnittspreis wird ausgewählt
4. Die Startzeit dieses Fensters wird zurückgegeben

**Vorteil**: Sie erhalten den wirklich optimalen 3-Stunden-Zeitraum, nicht nur drei aufeinanderfolgende günstige Stunden. Dies ist besonders wichtig für Wärmepumpen, da ein zusammenhängender Zeitraum mit stabil niedrigen Preisen wichtiger ist als einzelne kurze Preistiefs.

### Zeitbasierte Sensoren (Timestamp Device Class)

Alle zeitbasierten Sensoren verwenden die `timestamp` Device-Class:

- ISO-formatierte Datums-/Zeitstrings (z.B. `2024-01-15T14:00:00+01:00`)
- Lokale Zeitzone (MEZ/MESZ)
- Direkte Verwendung in zeitbasierten Automatisierungen möglich
- Nahtlose Integration mit ApexCharts zur Visualisierung
- `unavailable` Status, wenn Daten fehlen (z.B. morgige Preise noch nicht veröffentlicht)

### Preisberechnungslogik

Die Integration verwendet generische Hilfsfunktionen zur Berechnung von Statistiken:

- **Konsistente Berechnungen** für heute und morgen
- **Robuste Fehlerbehandlung** bei fehlenden Daten
- **Effizienter Code** ohne Duplikation

### Tipps für Automatisierungen

- **Binärsensoren nutzen**: Für einfache Ein/Aus-Logik ohne Zeitberechnungen
- **Timestamp-Sensoren**: Direkt in `time`-Triggern verwenden (`at: sensor.ostrom_price_today_cheapest_3h_block_start`)
- **Template-Bedingungen**: Preisvergleiche mit Durchschnittspreis für dynamische Schwellenwerte
- **Verzögerungen vermeiden**: Nutzen Sie die synchronisierten Updates für vorhersagbare Zeiten

### Day-Ahead-Preise

- Day-Ahead-Preise für morgen sind typischerweise nach 13:00 MEZ verfügbar
- Die `tomorrow_*` Sensoren werden als `unavailable` angezeigt, bis Preise veröffentlicht werden
- Preisdaten basieren auf EPEX Spot-Marktpreisen
- Die Integration behandelt fehlende morgige Daten elegant ohne Fehler

### Icons

Alle Sensoren enthalten Material Design Icons zur visuellen Identifikation:

- ⚡ `mdi:flash` - Aktuelle Preissensoren
- 📉 `mdi:trending-down` - Minimalpreis-Sensoren
- 📈 `mdi:trending-up` - Maximalpreis-Sensoren
- 📊 `mdi:chart-bell-curve-cumulative` - Durchschnittspreis-Sensoren
- 📊 `mdi:chart-bell-curve` - Medianpreis-Sensoren
- 🕐 `mdi:clock-start` - Startzeit günstigste Stunde
- ⏱️ `mdi:timer-outline` - Startzeit günstigster 3h-Block
- ⚠️ `mdi:clock-alert` - Startzeit teuerste Stunde
- 🔄 `mdi:toggle-switch` / `mdi:toggle-switch-off` - Binary-Sensoren

</details>

## Fehlerbehebung

### Authentifizierungsprobleme

1. Überprüfen Sie Ihre Client ID und Client Secret im Developer Portal
2. Stellen Sie sicher, dass Ihr API-Client die korrekten Berechtigungen hat
3. Stellen Sie sicher, dass Sie die korrekte Umgebung verwenden (Production vs Sandbox)

### Fehlende morgige Preise

- Day-Ahead-Preise werden täglich gegen 13:00 MEZ veröffentlicht
- Vor dieser Zeit werden die Sensoren für morgen als unavailable angezeigt

### Warum ist mein Verbrauch unknown oder unavailable?

Verbrauchssensoren werden angelegt, wenn eine Vertrags-ID konfiguriert ist. Sie zeigen `unknown` oder `unavailable`, wenn keine stündlichen Messwerte von Ostrom verfügbar sind. Das ist normal und kann ignoriert werden.

**Checkliste:**
- ✅ Smart Meter mit Gateway vorhanden und aktiv?
- ✅ Stündliche Messwerte bei Ostrom aktiviert und freigeschaltet?
- ✅ Vertrags-ID korrekt in der Integration konfiguriert?
- ✅ Daten erscheinen in der offiziellen Ostrom-App?

**Hinweis**: Wenn keine der Voraussetzungen erfüllt ist, bleiben die Sensoren auf `unknown`/`unavailable`. Das ist erwartetes Verhalten. Sobald Ostrom Verbrauchsdaten liefert, werden die Werte automatisch bei den nächsten Updates sichtbar.

## Release-Workflow

Für Entwickler: Informationen zum Release-Workflow, Commit-Konventionen und wie Releases erstellt werden, finden Sie in [RELEASE_WORKFLOW.md](RELEASE_WORKFLOW.md).

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
