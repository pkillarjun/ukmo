#!/usr/bin/env python3

import sys
import pandas as pd
from pathlib import Path
from colorama import Fore

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *


def get_all_files(directory):
    path = Path(directory)
    if not path.exists():
        print_log(f"Directory {directory} does not exist", Fore.RED)
        sys.exit(1)

    files = []
    for file_path in path.iterdir():
        if file_path.is_file():
            files.append(file_path)
    return files


def check_value(file_path):
    issues = []
    found_issues = False

    df = pd.read_csv(file_path)

    for col in df.columns:
        for idx, value in df[col].items():
            if value == DEFAULT_VALUE:
                if idx == 0 and col in ['temp_min', 'temp_max', 'precip_accum']:
                    continue

                found_issues = True
                issues.append((col, idx))

    if found_issues:
        print_log(f"\nFile: {file_path.name}", Fore.RED)
        for col, idx in issues:
            print_log(f"  Found {DEFAULT_VALUE} in column '{col}' at row {idx}", Fore.YELLOW)


def main():
    files = get_all_files(Path(CSV_DIR))

    print_log("Checking CSV files", Fore.GREEN)

    if not files:
        print_log("No files found to process", Fore.RED)
        return

    print_log(f"Found {len(files)} files to check", Fore.BLUE)

    for file_path in files:
        check_value(file_path)


if __name__ == "__main__":
    main()
