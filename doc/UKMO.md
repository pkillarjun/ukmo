# ukmo
ukmo-2km ml model

## Model Configuration

### Initialization Times
The model uses the following UKMO-2km model runs:
- **03Z** (04:00 UK) - Early morning
- **06Z** (07:00 UK) - Morning transition 
- **09Z** (10:00 UK) - Active morning heating
- **12Z** (13:00 UK) - Near-peak heating
- **15Z** (16:00 UK) - Peak/post-peak temperatures

### Forecast Hours
- **Training and forecasting window**: 12 hours from the run
- This window captures the diurnal temperature cycle for accurate maximum temperature prediction

## Primary Predictive Variables (Ranked by Importance)

### 1. Historical Temperature Data (35-45% importance)
- `temperature_at_screen_level`
- `temperature_at_screen_level_max`
- `temperature_at_screen_level_min`

### 2. Solar Radiation Components (15-25% importance)
- `radiation_flux_in_shortwave_total_downward_at_surface`
- `radiation_flux_in_shortwave_direct_downward_at_surface`
- `radiation_flux_in_shortwave_diffuse_downward_at_surface`

### 3. Atmospheric Humidity (15-20% importance)
- `relative_humidity_at_screen_level`
- `temperature_of_dew_point_at_screen_level`

### 4. Pressure Fields (10-20% importance)
- `pressure_at_mean_sea_level`
- `height_ASL_on_pressure_levels`

### 5. Wind Components (5-12% importance)
- `wind_speed_at_10m`
- `wind_direction_at_10m`
- `wind_gust_at_10m`

### 6. Cloud Cover (5-10% importance)
- `cloud_amount_of_total_cloud`
- `cloud_amount_of_low_cloud`
- `cloud_amount_of_medium_cloud`
- `cloud_amount_of_high_cloud`


## Optimal variable combinations for ML models

### Core ensemble (minimum required):
```
temperature_at_screen_level
temperature_at_screen_level_max
temperature_at_screen_level_min
radiation_flux_in_shortwave_total_downward_at_surface
relative_humidity_at_screen_level
pressure_at_mean_sea_level
wind_speed_at_10m
wind_direction_at_10m
```

### Enhanced ensemble (improved accuracy):
Add to core:
```
radiation_flux_in_shortwave_direct_downward_at_surface
radiation_flux_in_shortwave_diffuse_downward_at_surface
radiation_flux_in_longwave_downward_at_surface
cloud_amount_of_total_cloud
cloud_amount_of_low_cloud
temperature_of_dew_point_at_screen_level
precipitation_rate
precipitation_accumulation
wind_gust_at_10m
```

### Advanced ensemble (complex terrain/urban):
Add all above plus:
```
temperature_on_pressure_levels
temperature_on_height_levels
relative_humidity_on_pressure_levels
height_ASL_on_pressure_levels
wind_speed_on_pressure_levels
wind_direction_on_pressure_levels
sensible_heat_flux_at_surface
temperature_at_surface
fog_fraction_at_screen_level
visibility_at_screen_level
```
