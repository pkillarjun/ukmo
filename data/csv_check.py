#!/usr/bin/env python3

import sys
import pandas as pd
from pathlib import Path
from colorama import Fore

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *


def check_value(file_path):
    found_issues = False

    df = pd.read_csv(file_path)

    for col in df.columns:
        for idx, value in df[col].items():
            if value == DEFAULT_VALUE:
                if idx == 0 and col in ['temp_min', 'temp_max', 'precip_accum']:
                    continue

                found_issues = True
                break
        if found_issues:
            break

    return found_issues


def main():
    runs = generate_runs()
    print_log(f"Generated {len(runs)} runs", Fore.GREEN)

    bad_runs = []

    for run in runs:
        file_path = f"{CSV_DIR}/{run}.csv"

        if not Path(file_path).exists():
            continue

        if check_value(file_path):
            print_log(f"Bad values found in: {run}.csv", Fore.RED)
            bad_runs.append(run)

    with open(IGNORE_FILE, 'w') as f:
        for run in bad_runs:
            f.write(f"{run}\n")

    print_log(f"Found {len(bad_runs)} runs with bad values", Fore.BLUE)


if __name__ == "__main__":
    main()
