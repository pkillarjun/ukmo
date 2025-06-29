from datetime import datetime

START_DATE = datetime(2023, 6, 1)
END_DATE = datetime(2025, 6, 30)

FORECAST_HOURS = 12
RUN_HOURS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

STATION = "EGLC"
STATIONS_LAT = 51.505
STATIONS_LONG = 0.055

DEFAULT_VALUE = -999

DOWNLOAD_DIR = "download"

CSV_DIR = f"{DOWNLOAD_DIR}/ukmo-csv"
NCDF_DIR = f"{DOWNLOAD_DIR}/ukmo-ncdf"

METAR_FILE = f"{(DOWNLOAD_DIR)}/eglc.csv"
IGNORE_FILE = f"{(DOWNLOAD_DIR)}/run.ignore"

REQUIRED_VARIABLES = [
    # Temperature
    "temperature_at_screen_level",
    "temperature_at_screen_level_min-PT01H",
    "temperature_at_screen_level_max-PT01H",
    "temperature_of_dew_point_at_screen_level",
    "temperature_at_surface",

    # Wind
    "wind_speed_at_10m",
    "wind_direction_at_10m",

    # Cloud
    "cloud_amount_of_low_cloud",
    "cloud_amount_of_medium_cloud",

    # Pressure
    "pressure_at_mean_sea_level",

    # Flux
    "radiation_flux_in_shortwave_direct_downward_at_surface",
    "radiation_flux_in_longwave_downward_at_surface",
    "sensible_heat_flux_at_surface",
]

COLUMN_PROCESS = [
    # YYMMDD
    'date',

    # HH:MM
    'hour',

    # Kelvin
    'temp',
    'temp_min',
    'temp_max',
    'temp_dew',
    'temp_surf',

    # Metre per second
    'wind_speed',

    # Degrees
    'wind_dir',

    # Fraction %
    'cloud_low',
    'cloud_medium',

    # Pa
    'sea_press',

    # Watt per square metre
    'rad_sw_dir_down',
    'rad_lw_down',
    'heat_flux',
]

FILE_CSV_MAPPING = {
    # Temperature
    'temperature_at_screen_level.nc': 'temp',
    'temperature_at_screen_level_min-PT01H.nc': 'temp_min',
    'temperature_at_screen_level_max-PT01H.nc': 'temp_max',
    'temperature_of_dew_point_at_screen_level.nc': 'temp_dew',
    'temperature_at_surface.nc': 'temp_surf',

    # Wind
    'wind_speed_at_10m.nc': 'wind_speed',
    'wind_direction_at_10m.nc': 'wind_dir',

    # Cloud Coverage
    'cloud_amount_of_low_cloud.nc': 'cloud_low',
    'cloud_amount_of_medium_cloud.nc': 'cloud_medium',

    # Pressure
    'pressure_at_mean_sea_level.nc': 'sea_press',

    # Flux
    'radiation_flux_in_shortwave_direct_downward_at_surface.nc': 'rad_sw_dir_down',
    'radiation_flux_in_longwave_downward_at_surface.nc': 'rad_lw_down',
    'sensible_heat_flux_at_surface.nc': 'heat_flux',
}

COLUMN_TRANSFORM = [
    # Week (Cyclical encoding)
    'week_sin',
    'week_cos',

    # Hour (Cyclical encoding)
    'hour_sin',
    'hour_cos',

    # Temperature (°C) - Convert from Kelvin: T - 273.15
    'temp',
    'temp_min',
    'temp_max',
    'temp_dew',
    'temp_surf',

    # Humidity (Percentage) - RH = 100 × exp((17.625 × TD)/(243.04 + TD)) / exp((17.625 × T)/(243.04 + T))
    'humidity_rel',

    # Wind - Convert from m/s to knots: × 1.94384
    'wind_speed',

    # Wind direction (Cyclical encoding)
    'wind_dir_sin',
    'wind_dir_cos',

    # Cloud (Percentage) - Convert from fraction: × 100
    'cloud_low',
    'cloud_medium',

    # Sea pressure (hPa) - Convert from Pa: ÷ 100
    'sea_press',

    # Flux (W/m²)
    'rad_sw_dir_down',
    'rad_lw_down',
    'heat_flux',
]
