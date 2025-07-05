import os
import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *

ukmo_csv_rolling = 'ukmo-csv-rolling'
ukmo_csv_output = 'ukmo-csv'
download = 'download'
initial_file = 'ukmo-csv-12/20230630T2300Z.csv'


def get_csv_files(directory):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            files.append(filename)
    files.sort()
    return files


def read_csv_data(filepath):
    data = {}
    header = None
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                key = (row[0], row[1])
                data[key] = row
    return header, data


def find_missing_values(row):
    missing_indices = []
    for i, value in enumerate(row):
        if value == str(DEFAULT_VALUE):
            missing_indices.append(i)
    return missing_indices


def patch_row(current_row, previous_data, key):
    patched_row = current_row.copy()
    missing_indices = find_missing_values(current_row)

    if missing_indices and key in previous_data:
        previous_row = previous_data[key]
        for idx in missing_indices:
            if idx < len(previous_row) and previous_row[idx] != str(DEFAULT_VALUE):
                patched_row[idx] = previous_row[idx]

    return patched_row


def write_csv_data(filepath, header, data):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        sorted_keys = sorted(data.keys())
        for key in sorted_keys:
            writer.writerow(data[key])


def process_files():
    source_dir = os.path.join(download, ukmo_csv_rolling)
    output_dir = os.path.join(download, ukmo_csv_output)
    initial_path = os.path.join(download, initial_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_files = get_csv_files(source_dir)

    if not csv_files:
        print_log("No CSV files found", Fore.RED)
        return

    print_log(f"Found {len(csv_files)} files to process", Fore.CYAN)

    if os.path.exists(initial_path):
        _, previous_data = read_csv_data(initial_path)
        print_log(f"Loaded initial base file: {initial_file}", Fore.YELLOW)
    else:
        print_log(f"Error: Initial base file not found: {initial_file}", Fore.RED)
        return

    for filename in csv_files:
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(output_dir, filename)

        header, current_data = read_csv_data(source_path)

        patched_data = {}
        patches_made = 0

        for key, row in current_data.items():
            original_row = row.copy()
            patched_row = patch_row(row, previous_data, key)
            patched_data[key] = patched_row

            if original_row != patched_row:
                patches_made += 1

        write_csv_data(dest_path, header, patched_data)
        if patches_made > 0:
            print_log(f"{filename} - processed ({patches_made} rows patched)", Fore.GREEN)
        else:
            print_log(f"{filename} - processed (no patches needed)", Fore.BLUE)

        previous_data = patched_data


if __name__ == '__main__':
    process_files()
