# Ostrom Advanced - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A custom Home Assistant integration for [Ostrom](https://www.ostrom.de/) dynamic electricity tariffs in Germany. This integration provides real-time spot prices, consumption data, and calculated costs for automating your energy usage.

## Features

- **Real-time Spot Prices**: Current all-in electricity prices (including taxes and levies)
- **Comprehensive Price Statistics**: Min, max, and average prices for today and tomorrow
- **Smart Time Sensors**: Find the cheapest hour, cheapest 3-hour block, and most expensive hour for both today and tomorrow
- **Visual Icons**: All sensors have intuitive Material Design Icons for easy dashboard identification
- **Consumption Tracking**: Today's and yesterday's energy consumption (requires Contract ID)
- **Cost Calculation**: Automatic cost calculation based on actual consumption and prices
- **Timestamp Support**: Time-based sensors use proper timestamp device class for ApexCharts and automation
- **Full API Support**: Uses official Ostrom API with OAuth2 authentication
- **Robust Error Handling**: Gracefully handles missing data (e.g., tomorrow prices not yet available)

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

| Field | Description | Required |
|-------|-------------|----------|
| Environment | `Production` for real data, `Sandbox` for testing | Yes |
| Client ID | Your OAuth2 Client ID from Developer Portal | Yes |
| Client Secret | Your OAuth2 Client Secret from Developer Portal | Yes |
| Zip Code | German postal code (e.g., `10115`) | Yes |
| Contract ID | Your Ostrom contract ID (optional, only for consumption data) | No |
| Price Poll Interval | How often to fetch prices (5-120 minutes, default: 15 min) | Yes |
| Consumption Poll Interval | How often to fetch consumption (15-1440 minutes, default: 60 min) | Yes |

**Note**: The Contract ID is optional. If not provided, only price sensors will be available. Consumption and cost sensors require a Contract ID.

## Entities

The integration provides comprehensive sensors for price monitoring, consumption tracking, and cost calculation. All sensors include intuitive Material Design Icons for easy visual identification in your dashboard.

### Price Sensors

#### Current Price
| Entity | Description | Unit | Icon |
|--------|-------------|------|------|
| `sensor.ostrom_spot_prices_raw` | Current all-in price with detailed attributes (includes all hourly slots) | €/kWh | ⚡ |
| `sensor.ostrom_price_now` | Current hourly all-in price | €/kWh | ⚡ |

#### Today's Price Statistics
| Entity | Description | Unit | Icon |
|--------|-------------|------|------|
| `sensor.ostrom_price_today_min` | Minimum price today | €/kWh | 📉 |
| `sensor.ostrom_price_today_max` | Maximum price today | €/kWh | 📈 |
| `sensor.ostrom_price_today_avg` | Average price today | €/kWh | 📊 |

#### Today's Time-Based Sensors
| Entity | Description | Type | Icon |
|--------|-------------|------|------|
| `sensor.ostrom_price_today_cheapest_hour_start` | Start time of cheapest hour today | Timestamp | 🕐 |
| `sensor.ostrom_price_today_cheapest_3h_block_start` | Start time of cheapest 3-hour block today (sliding window) | Timestamp | ⏱️ |
| `sensor.ostrom_price_today_most_expensive_hour_start` | Start time of most expensive hour today | Timestamp | ⚠️ |

#### Tomorrow's Price Statistics
| Entity | Description | Unit | Icon |
|--------|-------------|------|------|
| `sensor.ostrom_price_tomorrow_min` | Minimum price tomorrow | €/kWh | 📉 |
| `sensor.ostrom_price_tomorrow_max` | Maximum price tomorrow | €/kWh | 📈 |
| `sensor.ostrom_price_tomorrow_avg` | Average price tomorrow | €/kWh | 📊 |

#### Tomorrow's Time-Based Sensors
| Entity | Description | Type | Icon |
|--------|-------------|------|------|
| `sensor.ostrom_price_tomorrow_cheapest_hour_start` | Start time of cheapest hour tomorrow | Timestamp | 🕐 |
| `sensor.ostrom_price_tomorrow_cheapest_3h_block_start` | Start time of cheapest 3-hour block tomorrow (sliding window) | Timestamp | ⏱️ |
| `sensor.ostrom_price_tomorrow_most_expensive_hour_start` | Start time of most expensive hour tomorrow | Timestamp | ⚠️ |

**Note**: Tomorrow's sensors will show as `unavailable` until day-ahead prices are published (typically after 13:00 CET).

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
          title: "EV Charging Started"
          message: "Charging at cheapest 3h block: {{ states('sensor.ostrom_price_today_min') }} €/kWh"
```

### Avoid Charging During Expensive Hours

```yaml
automation:
  - alias: "Stop EV charging during expensive hour"
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
          title: "EV Charging Paused"
          message: "Paused during expensive hour: {{ states('sensor.ostrom_price_today_max') }} €/kWh"
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
          {{ states('sensor.ostrom_price_now') | float < 
             states('sensor.ostrom_price_today_avg') | float * 0.9 }}
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.heat_pump
        data:
          hvac_mode: heat

  - alias: "Pre-heat during cheapest 3h block"
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

### Battery Charging Strategy

```yaml
automation:
  - alias: "Charge battery at cheapest hour"
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

  - alias: "Discharge battery during expensive hour"
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

## Sensor Details

### Time-Based Sensors (Timestamp Device Class)

All time-based sensors use the `timestamp` device class, which means:
- They return ISO-formatted datetime strings (e.g., `2024-01-15T14:00:00+01:00`)
- They work seamlessly with ApexCharts for visualization
- They can be used directly in time-based automations
- They show as `unavailable` when data is missing (e.g., tomorrow prices not yet published)

### Price Calculation Logic

The integration uses generic helper functions to calculate statistics, ensuring:
- **Consistent calculations** across today and tomorrow
- **Robust error handling** when data is missing
- **Efficient code** without duplication

#### 3-Hour Block Calculation

The cheapest 3-hour block uses a **sliding window** algorithm:
1. All possible 3-hour windows are evaluated
2. The average price for each window is calculated
3. The window with the lowest average price is selected
4. The start time of that window is returned

This ensures you get the truly optimal 3-hour period, not just three consecutive cheap hours.

### Icons

All sensors include Material Design Icons for visual identification:
- ⚡ `mdi:flash` - Current price sensors
- 📉 `mdi:trending-down` - Minimum price sensors
- 📈 `mdi:trending-up` - Maximum price sensors
- 📊 `mdi:chart-bell-curve-cumulative` - Average price sensors
- 🕐 `mdi:clock-start` - Cheapest hour start time
- ⏱️ `mdi:timer-outline` - Cheapest 3h block start time
- ⚠️ `mdi:clock-alert` - Most expensive hour start time

## Notes

### Day-Ahead Prices

- Day-ahead prices for tomorrow are typically available after 13:00 CET
- The `tomorrow_*` sensors will show as `unavailable` until prices are published
- Price data is based on EPEX Spot market prices
- The integration gracefully handles missing tomorrow data without errors

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

