import os
import csv
import sys
import pandas as pd
from metar import Metar
from pathlib import Path
from colorama import Fore
from multiprocessing import Pool
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *
from model.transform import *
from model.transformer import *


def generate_test():
    _START_DATE = datetime(2023, 7, 1)
    _END_DATE = datetime(2023, 7, 1)

    runs = []
    current_date = _START_DATE

    while current_date <= _END_DATE:
        for hour in RUN_HOURS:
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            runs.append(timestamp.strftime("%Y%m%dT%H00Z"))
        current_date += timedelta(days=1)
    return runs


def filter_runs(runs):
    if not Path(IGNORE_FILE).exists():
        return runs, 0

    bad_runs = set()
    with open(IGNORE_FILE, 'r') as f:
        for line in f:
            bad_runs.add(line.strip())

    _runs = []
    for run in runs:
        if run not in bad_runs:
            _runs.append(run)

    ignore = len(runs) - len(_runs)

    return _runs, ignore


def load_metar(metar_file):
    metar_data = []

    try:
        with open(metar_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                valid_dt = datetime.strptime(row['valid'], '%Y-%m-%d %H:%M')
                metar_data.append({'datetime': valid_dt, 'metar': row['metar']})
    except FileNotFoundError:
        print_log(f"Error: CSV file not found: {metar_file}", Fore.RED)
        sys.exit(1)

    metar_df = pd.DataFrame(metar_data)
    metar_df.set_index('datetime', inplace=True)
    metar_df.sort_index(inplace=True)
    return metar_df


def get_csv(file):
    if not Path(file).exists():
        print_log(f"Error: CSV file not found: {file}", Fore.RED)
        sys.exit(1)

    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_metar(run, metar_data):
    run_metar_data = []
    dt = parse_run_time(run)

    start = dt

    # off-by-one bug here but needed - if start is 03:00 and ends at 14:00
    # we miss the 14:50 report, so we extend to 15:00
    end = dt + timedelta(hours=FORECAST_HOURS)

    records = metar_data.loc[start:end]

    for dt_val, row in records.iterrows():
        # Provide month and year context to prevent day 31 parsing errors
        obs = Metar.Metar(row['metar'], month=dt_val.month, year=dt_val.year)
        if obs.temp:
            run_metar_data.append({'datetime': dt_val, 'temp': obs.temp.value()})

    return run_metar_data


def filter_metar(run, run_metar_data):
    filter_metar_data = []

    run_dt = parse_run_time(run)
    init_time = run_dt + timedelta(hours=FORECAST_PADDING)
    cutoff_time = run_dt + timedelta(hours=FORECAST_FRAME)

    # Remove first and last hour from METAR reports
    # Filter out reports if they are not from xx:20 or xx:50
    for metar_data in run_metar_data:
        if metar_data['datetime'].minute in [20, 50]:
            if init_time <= metar_data['datetime'] <= cutoff_time:
                filter_metar_data.append(metar_data)

    return filter_metar_data


def process_run(args):
    run, metar_data = args
    file = f"{CSV_DIR}/{run}.csv"

    run_csv_data = get_csv(file)
    run_metar_data = get_metar(run, metar_data)
    filter_metar_data = filter_metar(run, run_metar_data)

    run_data = {'run_id': run, 'csv_data': run_csv_data, 'metar_data': filter_metar_data}
    return run_data


def process_runs(runs, metar_data):
    num_cores = os.cpu_count()
    print_log(f"Using {num_cores} CPU cores for parallel processing")

    args_list = [(run, metar_data) for run in runs]

    with Pool(processes=num_cores) as pool:
        runs_data = pool.map(process_run, args_list)

    return runs_data


def prepare_data(runs):
    print_log(f"Generated {len(runs)} runs", Fore.GREEN)

    runs, ignore = filter_runs(runs)
    print_log(f"Ignored {ignore} runs", Fore.MAGENTA)

    metar_data = load_metar(METAR_FILE)
    print_log(f"Loaded {len(metar_data)} METAR records\n", Fore.GREEN)

    runs_data = process_runs(runs, metar_data)
    transformed_data = transform(runs_data)

    return transformed_data


def main():
    if len(sys.argv) != 2:
        print_log(f"Usage: python {sys.argv[0]} [train|test]", Fore.RED)
        sys.exit(1)

    input = sys.argv[1]

    if input not in ["train", "test"]:
        print_log(f"Usage: python {sys.argv[0]} [train|test]", Fore.RED)
        sys.exit(1)

    print_log("Starting METAR data processing\n", Fore.GREEN)

    if input == "train":
        runs = generate_runs()
        train_transformer(prepare_data(runs))
    elif input == "test":
        runs_test = generate_test()
        test_transformer(prepare_data(runs_test))


if __name__ == "__main__":
    main()
