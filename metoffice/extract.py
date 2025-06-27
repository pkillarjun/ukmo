import csv
import sys
import pyproj
import xarray as xr
from pathlib import Path
from datetime import timedelta
from colorama import Fore

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *


def create_rows(run_id):
    rows = []
    base_time = parse_run_time(run_id)

    for hour in range(FORECAST_HOURS):
        forecast_time = base_time + timedelta(hours=hour)
        row = {'date': forecast_time.strftime("%Y%m%d"), 'hour': forecast_time.strftime("%H%M")}

        for field in COLUMN_PROCESS[2:]:
            row[field] = DEFAULT_VALUE

        rows.append(row)
    return rows


def extract_value(nc_file_path):
    try:
        ds = xr.open_dataset(nc_file_path, decode_timedelta=False)

        crs = pyproj.CRS.from_cf(ds.lambert_azimuthal_equal_area.attrs)
        transformer = pyproj.Transformer.from_crs("EPSG:4326", crs, always_xy=True)

        x_proj, y_proj = transformer.transform(STATIONS_LONG, STATIONS_LAT)

        x_idx = abs(ds.projection_x_coordinate.values - x_proj).argmin()
        y_idx = abs(ds.projection_y_coordinate.values - y_proj).argmin()

        for var in ds.data_vars:
            if var not in ['lambert_azimuthal_equal_area', 'projection_x_coordinate_bnds', 'projection_y_coordinate_bnds']:
                data = ds[var]
                value = float(data.values[y_idx, x_idx])
                ds.close()
                return value

        ds.close()
        return DEFAULT_VALUE

    except Exception as e:
        print_log_p(f"Error extracting from {nc_file_path}: {str(e)}", Fore.RED)
        return DEFAULT_VALUE


def get_hour(run_id, filename):
    try:
        time_str = filename.split('-PT')[0]
        valid_dt = parse_run_time(time_str)
        model_dt = parse_run_time(run_id)

        hours_from_run = int((valid_dt - model_dt).total_seconds() / 3600)
        return hours_from_run
    except Exception:
        return -1


def update_rows(rows, run_id, files):
    run_dir = Path(NCDF_DIR) / run_id

    for filename in files:
        nc_path = run_dir / filename

        forecast_hour = get_hour(run_id, filename)

        if forecast_hour < 0 or forecast_hour >= len(rows):
            continue

        value = extract_value(nc_path)

        for suffix, field in FILE_CSV_MAPPING.items():
            if filename.endswith(suffix):
                rows[forecast_hour][field] = value
                break
    return rows


def write_csv_file(rows, run_id):
    csv_path = Path(CSV_DIR)
    csv_path.mkdir(parents=True, exist_ok=True)

    csv_file = csv_path / f"{run_id}.csv"

    try:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMN_PROCESS)
            writer.writeheader()
            writer.writerows(rows)

        print_log_p(f"{run_id}: Created {csv_file}", Fore.GREEN)
        return True, len(rows)
    except Exception as e:
        print_log_p(f"Error writing CSV file {csv_file}: {str(e)}", Fore.RED)
        return False, 0


def extract_run_data(run_id, files):
    rows = create_rows(run_id)
    rows = update_rows(rows, run_id, files)
    success, total_rows = write_csv_file(rows, run_id)
    return success, total_rows
