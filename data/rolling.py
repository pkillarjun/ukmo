import os
import csv
import shutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from common.utility import *

ukmo_csv_12 = 'ukmo-csv-12'
ukmo_csv_24 = 'ukmo-csv-24'
ukmo_csv_rolling = 'ukmo-csv-rolling'
download = 'download'


def get_csv_files(directory):
    files = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                files.append(filename)
        files.sort()
    return files


def merge_file_lists(files_12h, files_24h):
    merged = {}

    for filename in files_12h:
        merged[filename] = ukmo_csv_12

    for filename in files_24h:
        merged[filename] = ukmo_csv_24

    return merged


def read_csv_to_dict(filepath):
    data_dict = {}
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                key = (row[0], row[1])
                data_dict[key] = row
    return header, data_dict


def write_csv_from_dict(filepath, header, data_dict):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        sorted_keys = sorted(data_dict.keys())
        for key in sorted_keys:
            writer.writerow(data_dict[key])


def process_files():
    dir_12h = os.path.join(download, ukmo_csv_12)
    dir_24h = os.path.join(download, ukmo_csv_24)
    output_dir = os.path.join(download, ukmo_csv_rolling)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files_12h = get_csv_files(dir_12h)
    files_24h = get_csv_files(dir_24h)

    merged_files = merge_file_lists(files_12h, files_24h)
    sorted_files = sorted(merged_files.keys())

    found_24h = False
    last_24h_file = None
    last_24h_data = None

    for filename in sorted_files:
        source = merged_files[filename]

        if source == ukmo_csv_24:
            found_24h = True
            last_24h_file = filename

            source_path = os.path.join(dir_24h, filename)
            dest_path = os.path.join(output_dir, filename)
            shutil.copy2(source_path, dest_path)

            _, last_24h_data = read_csv_to_dict(source_path)
            print_log(f'{filename} (from {source}) -> copied directly', Fore.GREEN)

        elif found_24h and source == ukmo_csv_12:
            source_path = os.path.join(dir_12h, filename)
            header, temp_data = read_csv_to_dict(source_path)

            updated_data = last_24h_data.copy()

            update_count = 0
            for key in temp_data:
                updated_data[key] = temp_data[key]
                update_count += 1

            dest_path = os.path.join(output_dir, filename)
            write_csv_from_dict(dest_path, header, updated_data)

            print_log(f'{filename} (from {source}) -> rolling update from {last_24h_file} ({update_count} rows updated)',
                      Fore.MAGENTA)


if __name__ == '__main__':
    process_files()
