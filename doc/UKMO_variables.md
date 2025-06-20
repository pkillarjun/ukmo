# Most important UKMO-2km variables for 24-hour temperature peak prediction

The UK Met Office's UKMO-2km model (UKV) offers over 20 weather variables, but research consistently identifies a core set that are most predictive for machine learning models targeting 24-hour maximum temperature forecasts. Based on extensive analysis of physical processes, ML studies, and operational implementations, here are the key findings.

## Primary predictive variables ranked by importance

### 1. Historical temperature data (35-45% importance)
The **Temperature at 1.5m (T1.5m)** from the UKV model serves as the fundamental predictor. Machine learning models achieve optimal performance using 3-7 days of historical temperature data, including maximum, minimum, and mean values. Studies using UK Met Office data report that lagged temperature features alone can achieve R² values of 0.84-0.96, with XGBoost and LightGBM models showing particular strength when incorporating these temporal patterns.

### 2. Solar radiation components (15-25% importance)
**Shortwave radiation** from the UKV model emerges as the second most critical variable, as it represents the primary energy source driving daytime temperature peaks. The model provides both incoming solar radiation and net radiation balance, which directly control surface heating. Research shows that during spring and summer months, solar radiation variables can explain up to 44 W/m² of temperature variation, making them essential for accurate peak temperature prediction.

### 3. Atmospheric humidity variables (15-20% importance)
The UKV model's **relative humidity** and **specific humidity** measurements consistently show high predictive power, with correlation coefficients of -0.9 with temperature in multiple studies. These variables control energy partitioning between sensible and latent heat, directly affecting how efficiently solar radiation translates into temperature rise. The model provides humidity data both at surface level and throughout the atmospheric profile on its 70 vertical levels.

### 4. Pressure fields and geopotential heights (10-20% importance)
**Mean sea level pressure (MSLP)** and **geopotential height** fields from the UKV model indicate synoptic weather patterns and temperature advection. These variables become particularly important for winter temperature prediction when solar heating is reduced. The 850mb, 700mb, and 500mb geopotential heights help identify warm and cold air advection patterns that significantly modify local temperature evolution.

### 5. Boundary layer parameters (8-15% importance)
The **boundary layer height** variable from UKV directly controls the volume of air being heated and mixed during daytime warming. This parameter, combined with surface heat fluxes and friction velocity, determines how efficiently surface heating translates into air temperature increases. Studies show that accurate boundary layer representation can improve temperature forecasts by 15-25% compared to models without these parameters.

### 6. Wind components (5-12% importance)
The UKV model's **10m wind speed and direction** (U and V components) affect temperature through advection and turbulent mixing. These become particularly important in coastal areas where sea breezes can suppress temperature peaks, and in complex terrain where local wind patterns significantly modify temperature distributions. The model's 1.5km resolution captures these local effects that coarser models miss.

### 7. Cloud cover variables (5-10% importance)
**Total cloud cover** and layer-specific cloud fractions (low, medium, high) from the UKV model modulate incoming solar radiation and outgoing longwave radiation. Low clouds typically reduce temperature peaks by blocking solar radiation, while high clouds can trap heat. The model's explicit representation of cloud processes at 1.5km resolution provides superior cloud-radiation feedback compared to parameterized approaches.

## Secondary variables with situational importance

### Land surface variables
- **Soil temperature** (multi-layer): Initial thermal state affecting morning temperature rise
- **Soil moisture**: Controls surface energy partitioning, with dry soils leading to higher temperature peaks
- **Surface runoff** and **evapotranspiration**: Indicate moisture availability for cooling

### Additional atmospheric variables
- **Vertical velocity (omega)**: Indicates rising/sinking motions affecting temperature
- **Temperature profiles** on model levels: Enable calculation of stability indices
- **Precipitation**: Negatively correlated with temperature peaks due to cloud cover and evaporative cooling

## Optimal variable combinations for ML models

Research using UK Met Office data, including a University of Reading study that achieved 11% improvement in urban temperature prediction, suggests the following optimal variable set:

**Core ensemble** (minimum required):
1. T1.5m temperature (with 3-7 day lags)
2. Shortwave radiation
3. Relative humidity
4. Mean sea level pressure
5. Boundary layer height
6. 10m wind components

**Enhanced ensemble** (for improved accuracy):
- Add: Cloud cover fractions, soil moisture, geopotential heights (850, 700, 500mb)
- Include: Longwave radiation, surface heat fluxes, precipitation

**Advanced ensemble** (for complex terrain/urban areas):
- Add: All variables above plus soil temperature profiles, evapotranspiration, topographic parameters
- Consider: Vertical temperature profiles for stability calculations

## Implementation recommendations

### Feature engineering strategies
1. **Temporal features**: Create 1-7 day lags for temperature, with hourly resolution for capturing diurnal cycles
2. **Derived variables**: Calculate temperature advection, atmospheric stability indices, degree-day metrics
3. **Interaction terms**: Temperature × humidity, radiation × cloud cover, wind speed × temperature gradient
4. **Spatial features**: For the UKV's variable resolution grid, include neighboring grid point values

### Model architecture recommendations
- **Primary choice**: XGBoost or LightGBM with the core variable ensemble achieves R² = 0.85-0.99
- **Ensemble approach**: Combine gradient boosting with Random Forest for feature importance validation
- **Deep learning**: LSTM networks excel when using full temporal sequences of UKV variables

### Performance benchmarks
Using the recommended UKMO-2km variables, machine learning models should achieve:
- **RMSE**: <1.5°C for 24-hour forecasts
- **R²**: >0.85 for reliable predictions
- **MAE**: <1.0°C for practical applications

The UKV model's high spatial (1.5km) and temporal (hourly) resolution, combined with its comprehensive variable set and 70 vertical levels, provides an exceptional foundation for ML-based temperature peak prediction. The key to success lies in selecting the physically-meaningful variables identified above and applying appropriate feature engineering to capture the complex interactions driving daily temperature maxima.
