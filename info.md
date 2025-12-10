# Ostrom Advanced

A comprehensive Home Assistant integration for Ostrom dynamic electricity tariffs in Germany. Get real-time spot prices, detailed statistics, and smart time-based sensors for automating your energy consumption.

## Features

- **Real-time Spot Prices**: Current all-in electricity prices with detailed hourly data
- **Comprehensive Statistics**: Min, max, and average prices for today and tomorrow
- **Smart Time Sensors**: 
  - Cheapest hour start time (today & tomorrow)
  - Cheapest 3-hour block start time (sliding window algorithm)
  - Most expensive hour start time (today & tomorrow)
- **Visual Icons**: All sensors include intuitive Material Design Icons
- **Consumption Tracking**: Daily energy consumption and cost calculation (requires Contract ID)
- **Timestamp Support**: Time-based sensors use proper device class for ApexCharts and automation
- **Robust Error Handling**: Gracefully handles missing data (e.g., tomorrow prices not yet available)

## Quick Start

1. Get your API credentials from the [Ostrom Developer Portal](https://developer.ostrom-api.io/)
2. Add the integration in Home Assistant
3. Enter your Client ID, Client Secret, Zip Code, and optionally your Contract ID
4. Start automating based on electricity prices!

## Available Sensors

### Price Statistics (Today & Tomorrow)
- Current price, minimum, maximum, and average prices
- All with intuitive icons (⚡ 📉 📈 📊)

### Time-Based Sensors (Timestamp Device Class)
- **Cheapest Hour Start**: Best time to run energy-intensive devices
- **Cheapest 3h Block Start**: Optimal 3-hour window using sliding window algorithm
- **Most Expensive Hour Start**: Time to avoid high consumption

### Consumption & Costs (Requires Contract ID)
- Daily energy consumption tracking
- Automatic cost calculation based on actual usage

## Example Automations

### EV Charging
```yaml
automation:
  - alias: "Charge EV at cheapest 3h block"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_3h_block_start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

### Heat Pump
```yaml
automation:
  - alias: "Pre-heat during cheapest hours"
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

### Battery Management
```yaml
automation:
  - alias: "Charge battery at cheapest hour"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_hour_start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charger
```

## Technical Details

- Uses official Ostrom API with OAuth2 authentication
- Generic calculation functions ensure consistent results
- Tomorrow sensors show as `unavailable` until day-ahead prices are published (typically after 13:00 CET)
- Contract ID is optional - price sensors work without it

For full documentation and more automation examples, see the [README](https://github.com/Al3xand3r1987/ha-ostrom-advanced).

