import os
import sys
import calendar
import numpy as np
from pathlib import Path
from colorama import Fore
from multiprocessing import Pool
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *

FORECAST_PADDING = 1
FORECAST_FRAME = 15


def is_invalid(value):
    return value == DEFAULT_VALUE


def weeks_in_year(year):
    # Dec 28 is always in the last week of the year
    dec_28 = datetime(year, 12, 28)
    return dec_28.isocalendar()[1]


def cyclical_encode(value, max_value):
    angle = 2 * np.pi * value / max_value
    return np.sin(angle), np.cos(angle)


def cyclical_encode_week(date_str):
    dt = datetime.strptime(date_str, '%Y%m%d')
    week = dt.isocalendar()[1]
    total_weeks = weeks_in_year(dt.year)
    return cyclical_encode(week, total_weeks)


def cyclical_encode_hour(hour_str):
    dt = datetime.strptime(hour_str, '%H%M')
    hour_decimal = dt.hour + dt.minute / 60
    return cyclical_encode(hour_decimal, 24)


def cyclical_encode_direction(wind_dir):
    if is_invalid(wind_dir):
        return DEFAULT_VALUE, DEFAULT_VALUE
    return cyclical_encode(wind_dir, 360)


def kelvin_to_celsius(kelvin):
    if is_invalid(kelvin):
        return DEFAULT_VALUE
    return round(kelvin - 273.15, 2)


def relative_humidity(temp, temp_dew):
    if is_invalid(temp) or is_invalid(temp_dew):
        return DEFAULT_VALUE

    exp_dew = np.exp((17.625 * temp_dew) / (243.04 + temp_dew))
    exp_temp = np.exp((17.625 * temp) / (243.04 + temp))
    return round(100 * exp_dew / exp_temp, 2)


def mps_to_knots(mps):
    if is_invalid(mps):
        return DEFAULT_VALUE
    return round(mps * 1.94384, 2)


def fraction_to_percent(fraction):
    if is_invalid(fraction):
        return DEFAULT_VALUE
    return round(fraction * 100, 2)


def pascal_to_hpa(pascal):
    if is_invalid(pascal):
        return DEFAULT_VALUE
    return round(pascal / 100, 2)


def transform_row(row):
    week_sin, week_cos = cyclical_encode_week(row['date'])
    hour_sin, hour_cos = cyclical_encode_hour(row['hour'])

    temp = kelvin_to_celsius(float(row['temp']))
    temp_min = kelvin_to_celsius(float(row['temp_min']))
    temp_max = kelvin_to_celsius(float(row['temp_max']))
    temp_dew = kelvin_to_celsius(float(row['temp_dew']))
    temp_surf = kelvin_to_celsius(float(row['temp_surf']))

    humidity_rel = relative_humidity(temp, temp_dew)

    wind_speed = mps_to_knots(float(row['wind_speed']))

    wind_dir_sin, wind_dir_cos = cyclical_encode_direction(float(row['wind_dir']))

    cloud_low = fraction_to_percent(float(row['cloud_low']))
    cloud_medium = fraction_to_percent(float(row['cloud_medium']))

    sea_press = pascal_to_hpa(float(row['sea_press']))

    return {
        'week_sin': week_sin,
        'week_cos': week_cos,
        'hour_sin': hour_sin,
        'hour_cos': hour_cos,
        'temp': temp,
        'temp_min': temp_min,
        'temp_max': temp_max,
        'temp_dew': temp_dew,
        'temp_surf': temp_surf,
        'humidity_rel': humidity_rel,
        'wind_speed': wind_speed,
        'wind_dir_sin': wind_dir_sin,
        'wind_dir_cos': wind_dir_cos,
        'cloud_low': cloud_low,
        'cloud_medium': cloud_medium,
        'sea_press': sea_press,
        'rad_sw_dir_down': round(float(row['rad_sw_dir_down']), 2),
        'rad_lw_down': round(float(row['rad_lw_down']), 2),
        'heat_flux': round(float(row['heat_flux']), 2),
    }


def transform_run(run):
    run_dt = parse_run_time(run['run_id'])
    csv_data = run['csv_data']
    metar_data = run['metar_data']

    run_hour_sin, run_hour_cos = cyclical_encode_hour(run_dt.strftime('%H%M'))
    run_hour = [run_hour_sin, run_hour_cos]

    input = []
    for row in csv_data:
        c_row = []
        t_row = transform_row(row)

        for field in COLUMN_TRANSFORM:
            c_row.append(t_row[field])

        input.append(c_row)

    output = []
    for metar in metar_data:
        metar_dt = metar['datetime']

        metar_hour_sin, metar_hour_cos = cyclical_encode_hour(metar_dt.strftime('%H%M'))
        metar_hour = [metar_hour_sin, metar_hour_cos]

        output.append({'time': metar_hour, 'temp': metar['temp']})

    if len(output) != (FORECAST_FRAME - FORECAST_PADDING):
        return {}

    transformed_data = {'run_hour': run_hour, 'input': input, 'output': output}
    return transformed_data


def transform(run_data):
    transformed_data = []

    num_cores = os.cpu_count()
    print_log(f"Using {num_cores} CPU cores for parallel transform processing")

    with Pool(processes=num_cores) as pool:
        run_results = pool.map(transform_run, run_data)

    for run_result in run_results:
        if run_result:
            transformed_data.append(run_result)

    return transformed_data
