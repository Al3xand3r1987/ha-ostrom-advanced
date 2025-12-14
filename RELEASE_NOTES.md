# Ostrom Advanced v0.4.3

## Neue Features
- **Historische Preisdaten:** Price Coordinator holt jetzt 72-Stunden-Fenster (gestern, heute, morgen) für vollständige Preisübersicht
- **Korrekte Kostenberechnung:** Gestern-Kosten verwenden jetzt die korrekten historischen Preise statt heutiger Preise
- **Apex Charts Erweiterung:** `apex_data` Attribut enthält jetzt auch gestern-Preise für 72-Stunden-Überblick
- **Postleitzahl-Validierung:** Automatische Validierung der deutschen Postleitzahl (5-stellig, nur Ziffern) im Config Flow

## Bugfixes
- **Kritisch:** Kostenberechnung für gestern verwendet jetzt korrekte historische Preise (`yesterday_slots`)
- **Kostenberechnung:** Preis-Lookup verwendet jetzt vollständiges Datum+Stunde statt nur Stunde für präzise Zuordnung
- **Dokumentation:** README-Beispiele verwenden jetzt korrekte Entity-ID-Formatierung

## Technische Verbesserungen
- Price Coordinator erweitert: `yesterday_slots` für historische Daten
- Raw-Preis-Attribute erweitert: `yesterday_slots` in Attributen verfügbar
- Preis-Now-Attribute erweitert: `yesterday_total_prices` für separate Nutzung
- Verbesserte Fehlerbehandlung: Fallback-Logging bei fehlendem Preis-Match

---
# Ostrom Advanced v0.4.2

## Bugfixes
- **Kritisch:** Update-Loop stoppt nicht mehr dauerhaft bei Fehlern
- **Robustheit:** Exception-Handling im Timer-Callback mit Fallback-Rescheduling
- **Robustheit:** CancelledError-Behandlung in Update-Loops
- **Robustheit:** DST-sichere Zeitberechnungen mit Fallback bei DST-Übergängen
- **Robustheit:** Mitternacht-Berechnungen verwenden jetzt `dt_util.start_of_local_day()` für DST-Sicherheit
- **Robustheit:** Token-Refresh mit `asyncio.Lock` verhindert Race Conditions bei parallelen Requests

## Technische Verbesserungen
- Defensive Fehlerbehandlung in allen kritischen Code-Pfaden
- Update-Loop läuft auch nach Netzwerk-Fehlern, Token-Expiration oder DST-Übergängen weiter

---
# Ostrom Advanced v0.4.1

## Neue Features
- Neues `apex_data` Attribut am Preis-Sensor für direkte ApexCharts-Kompatibilität

## Bugfixes
- Verschiedene Bugfixes und Verbesserungen

---

# Ostrom Advanced v0.4.0

## Neue Features
- Neues `data` Attribut am Preis-Sensor für price-timeline-card Kompatibilität

## Bugfixes
- Verschiedene Bugfixes und Verbesserungen

---

# Ostrom Advanced v0.3.0

## Neue Features
- Synchronisierte Updates mit konfigurierbarem Offset
- Options-Flow für konfigurierbare Update-Intervalle

## Bugfixes
- Verschiedene Bugfixes und Verbesserungen
