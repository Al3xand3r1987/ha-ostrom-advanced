# Ostrom Advanced v0.4.1

## New Features
- add `apex_data` attribute to price sensor for direct ApexCharts compatibility (Array-Paar Format)
- enhance `data` attribute with deduplication logic (keeps last entry for duplicate timestamps)
- ensure both `data` and `apex_data` attributes are always present (even if empty)

## Bug Fixes
- Keine Bug-Fixes

## Maintenance
- Keine Wartungsarbeiten

## Documentation
- add ApexCharts compatibility section to README
- update ApexCharts example to use new `apex_data` attribute
- clarify recommended usage: `data` for price-timeline-card, `apex_data` for ApexCharts

## Other Changes
- Keine weiteren Änderungen

---

# Ostrom Advanced v0.4.0

## New Features
- add attributes.data for price-timeline-card compatibility (a6159b3)

## Bug Fixes
- Keine Bug-Fixes

## Maintenance
- update icon@2x.png (8ad9ae8)
- update icon.png (e957509)

## Documentation
- move release workflow documentation to .cursor directory (0bf57df)
- add examples for commit vs release workflow (7dbc57d)
- add release workflow documentation and improve workflow (eb707fc)

## Other Changes
- Keine weiteren Änderungen

---

# Ostrom Advanced v0.3.0

## New Features
- add automated release workflow with version recommendation (8f9732b)
- add synchronized updates with configurable offset (9969407)
- add options flow for configurable intervals (3f4b7a8)

## Bug Fixes
- improve release workflow to generate notes from commits (d799157)
- correct OptionsFlowHandler initialization in options flow (dabe866)

## Maintenance
- Keine Wartungsarbeiten

## Documentation
- clarify practical use of 3-hour blocks for heat pumps and compressor cycling (e06bfd1)

## Other Changes
- Update copyright year and name in LICENSE file (67f428f)
