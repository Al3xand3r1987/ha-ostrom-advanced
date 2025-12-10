# Ostrom Advanced

A Home Assistant integration for Ostrom dynamic electricity tariffs in Germany.

## Features

- Real-time spot prices with all-in costs
- Price forecasts for today and tomorrow
- Cheapest hour and 3-hour block sensors for smart automations
- Consumption tracking and cost calculation
- Full support for EV charging, heat pump, and battery automation

## Quick Start

1. Get your API credentials from the [Ostrom Developer Portal](https://developer.ostrom-api.io/)
2. Add the integration in Home Assistant
3. Enter your Client ID, Client Secret, Contract ID, and Zip Code
4. Start automating based on electricity prices!

## Sensors

- **Price Sensors**: Current price, min/max/avg for today and tomorrow
- **Cheapest Time**: Find the best times to run energy-intensive devices
- **Consumption**: Track daily energy usage
- **Costs**: Automatic cost calculation

## Example Automation

```yaml
automation:
  - alias: "Charge EV at cheapest time"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_3h_block_start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

For full documentation, see the [README](https://github.com/Al3xand3r1987/ha-ostrom-advanced).

