# Ostrom Advanced - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A custom Home Assistant integration for [Ostrom](https://www.ostrom.de/) dynamic electricity tariffs in Germany. This integration provides real-time spot prices, consumption data, and calculated costs for automating your energy usage.

## Features

- **Real-time Spot Prices**: Current all-in electricity prices (including taxes and levies)
- **Price Forecasts**: Today's and tomorrow's prices with min/max/average
- **Smart Automation Support**: Cheapest hour and cheapest 3-hour block sensors
- **Consumption Tracking**: Today's and yesterday's energy consumption
- **Cost Calculation**: Automatic cost calculation based on actual consumption and prices
- **Full API Support**: Uses official Ostrom API with OAuth2 authentication

## Prerequisites

1. **Ostrom Account**: You need an active Ostrom electricity contract
2. **Ostrom Developer Portal Access**: 
   - Log in to the [Ostrom Developer Portal](https://developer.ostrom-api.io/)
   - Create an API client to get your **Client ID** and **Client Secret**
3. **Contract ID**: Your Ostrom contract identifier
4. **Zip Code**: Your German postal code for accurate tax/levy calculations

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots menu (⋮) → **Custom repositories**
4. Add repository URL: `https://github.com/Al3xand3r1987/ha-ostrom-advanced`
5. Select category: **Integration**
6. Click **Add**
7. Search for "Ostrom Advanced" and install it
8. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/ostrom_advanced` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Ostrom Advanced"
4. Fill in the configuration form:

| Field | Description |
|-------|-------------|
| Environment | `Production` for real data, `Sandbox` for testing |
| Client ID | Your OAuth2 Client ID from Developer Portal |
| Client Secret | Your OAuth2 Client Secret from Developer Portal |
| Zip Code | German postal code (e.g., `10115`) |
| Contract ID | Your Ostrom contract ID |
| Price Poll Interval | How often to fetch prices (default: 15 min) |
| Consumption Poll Interval | How often to fetch consumption (default: 60 min) |

## Entities

### Price Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| `sensor.ostrom_spot_prices_raw` | Current all-in price with detailed attributes | €/kWh |
| `sensor.ostrom_price_now` | Current hourly all-in price | €/kWh |
| `sensor.ostrom_price_today_min` | Minimum price today | €/kWh |
| `sensor.ostrom_price_today_max` | Maximum price today | €/kWh |
| `sensor.ostrom_price_today_avg` | Average price today | €/kWh |
| `sensor.ostrom_price_today_cheapest_hour_start` | Start time of cheapest hour today | Timestamp |
| `sensor.ostrom_price_today_cheapest_3h_block_start` | Start time of cheapest 3h block today | Timestamp |
| `sensor.ostrom_price_tomorrow_min` | Minimum price tomorrow | €/kWh |
| `sensor.ostrom_price_tomorrow_max` | Maximum price tomorrow | €/kWh |
| `sensor.ostrom_price_tomorrow_avg` | Average price tomorrow | €/kWh |
| `sensor.ostrom_price_tomorrow_cheapest_3h_block_start` | Start time of cheapest 3h block tomorrow | Timestamp |

### Consumption Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| `sensor.ostrom_consumption_today_kwh` | Total consumption today | kWh |
| `sensor.ostrom_consumption_yesterday_kwh` | Total consumption yesterday | kWh |

### Cost Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| `sensor.ostrom_cost_today_eur` | Total energy cost today | € |
| `sensor.ostrom_cost_yesterday_eur` | Total energy cost yesterday | € |

### Raw Price Sensor Attributes

The `sensor.ostrom_spot_prices_raw` entity includes detailed attributes:

- `today_slots`: List of hourly price slots for today
- `tomorrow_slots`: List of hourly price slots for tomorrow  
- `current_slot_start`: Start time of current price slot
- `current_slot_end`: End time of current price slot
- `last_update`: Last data update timestamp

Each slot contains:
- `start`: Slot start time (ISO format)
- `end`: Slot end time (ISO format)
- `net_price`: Net price without VAT (€/kWh)
- `taxes_price`: Taxes and levies (€/kWh)
- `total_price`: Total all-in price (€/kWh)

## Automation Examples

### Start EV Charging at Cheapest Time

```yaml
automation:
  - alias: "Start EV charging at cheapest 3h block"
    trigger:
      - platform: time
        at: sensor.ostrom_price_today_cheapest_3h_block_start
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

### Notify When Price is Below Average

```yaml
automation:
  - alias: "Notify low electricity price"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.ostrom_price_now') | float < 
             states('sensor.ostrom_price_today_avg') | float * 0.8 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Low Electricity Price"
          message: "Current price is {{ states('sensor.ostrom_price_now') }} €/kWh"
```

### Heat Pump Smart Scheduling

```yaml
automation:
  - alias: "Enable heat pump during cheap hours"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.ostrom_price_now') | float < 0.25 }}
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.heat_pump
        data:
          hvac_mode: heat
```

## Notes

### Day-Ahead Prices

- Day-ahead prices for tomorrow are typically available after 13:00 CET
- The `tomorrow_*` sensors will show as unavailable until prices are published
- Price data is based on EPEX Spot market prices

### Rate Limits

The Ostrom API has rate limits. The default polling intervals are set to be respectful of these limits:
- Price updates: Every 15 minutes
- Consumption updates: Every 60 minutes

### Price Calculation

The **total price** (all-in price) includes:
- Day-ahead spot price (gross, including VAT)
- Taxes and levies (gross, including VAT)

Formula: `total_price = (grossKwhPrice + grossKwhTaxAndLevies) / 100` (converted from cents to €/kWh)

## Troubleshooting

### Authentication Issues

1. Verify your Client ID and Client Secret in the Developer Portal
2. Check that your API client has the correct permissions
3. Ensure you're using the correct environment (Production vs Sandbox)

### Missing Tomorrow Prices

- Day-ahead prices are published daily around 13:00 CET
- Before this time, tomorrow's sensors will be unavailable

### No Consumption Data

- Consumption data depends on smart meter readings
- Data might be delayed by several hours
- Check your Ostrom app if data appears in the official interface

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration and is not affiliated with Ostrom GmbH. Use at your own risk.

## Support

- [GitHub Issues](https://github.com/Al3xand3r1987/ha-ostrom-advanced/issues)
- [Home Assistant Community](https://community.home-assistant.io/)

