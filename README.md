# UKMO

Daily maximum temperature forecasting using UK Met Office 2km model.

## Time Range:
- Data collected: 12 hours of forecast data
- Model runs collected: 03z, 06z, 09z, 12z, 15z

## Met Office Hourly Data Points

Temperature:
- Temperature at screen level: Air temperature at 1.5m in °C
- Temperature at screen level max: Maximum temperature at 1.5m in °C
- Temperature at screen level min: Minimum temperature at 1.5m in °C
- Temperature of dew point at screen level: Dew point temperature at 1.5m in °C

Wind:
- Wind speed at 10m: Wind speed at 10m in knots
- Wind direction at 10m: Wind direction in degrees

Cloud Coverage:
- Cloud amount of low cloud: Low cloud cover, oktas converted to fraction (0-1)
- Cloud amount of medium cloud: Medium cloud cover, oktas converted to fraction (0-1)

Pressure:
- Pressure at mean sea level: Mean sea level pressure in hPa

Precipitation:
- Precipitation rate: Precipitation rate
- Precipitation accumulation: Precipitation accumulation

## Temporal Encoding

Hour Encoding (24-hour cycle):
```python
hour_sin = np.sin(2 * np.pi * hour / 24)
hour_cos = np.cos(2 * np.pi * hour / 24)
```

Day of Year Encoding (365-day cycle):
```python
day_sin = np.sin(2 * np.pi * day_of_year / 365)
day_cos = np.cos(2 * np.pi * day_of_year / 365)
```

Wind Direction Encoding:
```python
wind_sin = np.sin(direction_degrees * np.pi / 180)
wind_cos = np.cos(direction_degrees * np.pi / 180)
```
