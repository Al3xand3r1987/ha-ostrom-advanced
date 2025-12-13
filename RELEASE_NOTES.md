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
