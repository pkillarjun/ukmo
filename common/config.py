from datetime import datetime

START_DATE = datetime(2023, 6, 1)
END_DATE = datetime(2025, 5, 31)

FORECAST_HOURS = 12
RUN_HOURS = [0, 3, 6, 9, 12, 15, 18, 21]

PRECIP_INTERVALS = [0, 15, 30, 45]

STATION = "EGLC"
STATIONS_LAT = 51.505
STATIONS_LONG = 0.055

FORECAST_FRAME = 3
DEFAULT_VALUE = -999

DOWNLOAD_DIR = "download"

CSV_DIR = f"{DOWNLOAD_DIR}/ukmo-csv"
NCDF_DIR = f"{DOWNLOAD_DIR}/ukmo-ncdf"

METAR_FILE = f"{(DOWNLOAD_DIR)}/eglc.csv"
IGNORE_FILE = f"{(DOWNLOAD_DIR)}/eglc.ignore"

REQUIRED_VARIABLES = [
    "temperature_at_screen_level",
    "temperature_at_screen_level_min-PT01H",
    "temperature_at_screen_level_max-PT01H",
    "temperature_of_dew_point_at_screen_level",
    "temperature_at_surface",
    "wind_speed_at_10m",
    "wind_gust_at_10m",
    "wind_direction_at_10m",
    "fog_fraction_at_screen_level",
    "precipitation_rate",
    "precipitation_accumulation-PT01H",
    "cloud_amount_of_low_cloud",
    "cloud_amount_of_medium_cloud",
    "cloud_amount_of_high_cloud",
    "pressure_at_mean_sea_level",
    "radiation_flux_in_shortwave_direct_downward_at_surface",
    "radiation_flux_in_shortwave_diffuse_downward_at_surface",
    "radiation_flux_in_longwave_downward_at_surface",
    "sensible_heat_flux_at_surface",
]

COLUMN_PROCESS = [
    'date',
    'hour',
    'temp',
    'temp_min',
    'temp_max',
    'temp_dew',
    'temp_surf',
    'wind_speed',
    'wind_gust',
    'wind_dir',
    'fog_frac',
    'precip_00',
    'precip_15',
    'precip_30',
    'precip_45',
    'precip_accum',
    'cloud_low',
    'cloud_medium',
    'cloud_high',
    'sea_press',
    'rad_sw_dir_down',
    'rad_sw_diff_down',
    'rad_lw_down',
    'heat_flux',
]

FILE_CSV_MAPPING = {
    'temperature_at_screen_level.nc': 'temp',
    'temperature_at_screen_level_min-PT01H.nc': 'temp_min',
    'temperature_at_screen_level_max-PT01H.nc': 'temp_max',
    'temperature_of_dew_point_at_screen_level.nc': 'temp_dew',
    'temperature_at_surface.nc': 'temp_surf',
    'wind_speed_at_10m.nc': 'wind_speed',
    'wind_gust_at_10m.nc': 'wind_gust',
    'wind_direction_at_10m.nc': 'wind_dir',
    'fog_fraction_at_screen_level.nc': 'fog_frac',
    '00M-precipitation_rate.nc': 'precip_00',
    '15M-precipitation_rate.nc': 'precip_15',
    '30M-precipitation_rate.nc': 'precip_30',
    '45M-precipitation_rate.nc': 'precip_45',
    'precipitation_accumulation-PT01H.nc': 'precip_accum',
    'cloud_amount_of_low_cloud.nc': 'cloud_low',
    'cloud_amount_of_medium_cloud.nc': 'cloud_medium',
    'cloud_amount_of_high_cloud.nc': 'cloud_high',
    'pressure_at_mean_sea_level.nc': 'sea_press',
    'radiation_flux_in_shortwave_direct_downward_at_surface.nc': 'rad_sw_dir_down',
    'radiation_flux_in_shortwave_diffuse_downward_at_surface.nc': 'rad_sw_diff_down',
    'radiation_flux_in_longwave_downward_at_surface.nc': 'rad_lw_down',
    'sensible_heat_flux_at_surface.nc': 'heat_flux',
}

COLUMN_TRANSFORM = [
    'date_sin',
    'date_cos',
    'hour_sin',
    'hour_cos',
    'temp',
    'temp_min',
    'temp_max',
    'temp_dew',
    'temp_surf',
    'humidity_rel',
    'wind_speed',
    'wind_gust',
    'wind_dir_sin',
    'wind_dir_cos',
    'fog_frac',
    'precip_00',
    'precip_15',
    'precip_30',
    'precip_45',
    'precip_accum',
    'cloud_low',
    'cloud_medium',
    'cloud_high',
    'cloud_total',
    'sea_press',
    'rad_sw_dir_down',
    'rad_sw_diff_down',
    'rad_lw_down',
    'heat_flux',
    'rad_sw_total',
    'rad_total',
]

FORECAST = COLUMN_TRANSFORM * FORECAST_FRAME + [
    'f_date_sin',
    'f_date_cos',
    'f_hour_sin',
    'f_hour_cos',
]
