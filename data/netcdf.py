#!/usr/bin/env python3

import sys
import pyproj
import xarray as xr
from pathlib import Path
from colorama import Fore

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *


def extract_grid_info(ds, crs, x_idx, y_idx, station_lat, station_lon):
    grid_x = float(ds.projection_x_coordinate.values[x_idx])
    grid_y = float(ds.projection_y_coordinate.values[y_idx])

    transformer_reverse = pyproj.Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    grid_lon, grid_lat = transformer_reverse.transform(grid_x, grid_y)

    print_log(f"\nStation: {station_lat:.3f}°N, {station_lon:.3f}°E", Fore.BLUE)
    print_log(f"Nearest grid point: {grid_lat:.3f}°N, {grid_lon:.3f}°E", Fore.GREEN)
    print_log(f"Grid projection coords: X={grid_x:.0f}, Y={grid_y:.0f}", Fore.YELLOW)

    distance = ((grid_lat - station_lat)**2 + (grid_lon - station_lon)**2)**0.5 * 111
    print_log(f"Distance: {distance:.1f} km", Fore.MAGENTA)


def print_metadata(ds):
    print_log("\n=== File Metadata ===", Fore.BLUE)

    print_log("\nData Variables:", Fore.BLUE)
    for var in ds.data_vars:
        if var not in ['lambert_azimuthal_equal_area', 'projection_x_coordinate_bnds', 'projection_y_coordinate_bnds']:
            attrs = ds[var].attrs
            units = attrs.get('units', 'No units')
            long_name = attrs.get('long_name', var)
            print_log(f"    Long name: {long_name}", Fore.YELLOW)
            print_log(f"    Units: {units}", Fore.YELLOW)

    print_log("\nCoordinate System:", Fore.BLUE)
    if 'lambert_azimuthal_equal_area' in ds:
        crs_attrs = ds.lambert_azimuthal_equal_area.attrs
        print_log(f"  Projection: {crs_attrs.get('grid_mapping_name', 'Unknown')}", Fore.YELLOW)
        print_log(f"  Central latitude: {crs_attrs.get('latitude_of_projection_origin', 'N/A')}°", Fore.YELLOW)
        print_log(f"  Central longitude: {crs_attrs.get('longitude_of_projection_origin', 'N/A')}°", Fore.YELLOW)

    print_log("\nGrid Dimensions:", Fore.BLUE)
    print_log(f"  X points: {len(ds.projection_x_coordinate)}", Fore.YELLOW)
    print_log(f"  Y points: {len(ds.projection_y_coordinate)}", Fore.YELLOW)

    x_spacing = abs(ds.projection_x_coordinate.values[1] - ds.projection_x_coordinate.values[0])
    y_spacing = abs(ds.projection_y_coordinate.values[1] - ds.projection_y_coordinate.values[0])
    print_log(f"  Grid spacing: {x_spacing:.0f}m × {y_spacing:.0f}m", Fore.YELLOW)


def open_and_find_grid(nc_file):
    station_lat, station_lon = STATIONS_LAT, STATIONS_LONG

    ds = xr.open_dataset(nc_file, decode_times=True, decode_timedelta=True)

    crs = pyproj.CRS.from_cf(ds.lambert_azimuthal_equal_area.attrs)
    transformer = pyproj.Transformer.from_crs("EPSG:4326", crs, always_xy=True)

    x_proj, y_proj = transformer.transform(station_lon, station_lat)

    x_idx = abs(ds.projection_x_coordinate.values - x_proj).argmin()
    y_idx = abs(ds.projection_y_coordinate.values - y_proj).argmin()

    return ds, crs, x_idx, y_idx, station_lat, station_lon


def main():
    prog_name = Path(sys.argv[0]).name

    if len(sys.argv) != 2:
        print_log(f"Usage: {prog_name} <nc_file>", Fore.RED)
        sys.exit(1)

    try:
        nc_file = sys.argv[1]

        if not Path(nc_file).exists():
            print_log(f"File not found: {nc_file}", Fore.RED)
            sys.exit(1)

        ds, crs, x_idx, y_idx, station_lat, station_lon = open_and_find_grid(nc_file)

        print_log("=== Grid Information ===", Fore.BLUE)
        extract_grid_info(ds, crs, x_idx, y_idx, station_lat, station_lon)

        print_metadata(ds)

        ds.close()

    except Exception as e:
        print_log(f"Error: {str(e)}", Fore.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
