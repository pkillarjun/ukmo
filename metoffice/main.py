#!/usr/bin/env python3

import sys
import shutil
import multiprocessing
from pathlib import Path
from colorama import Fore

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *
from download import download_run_data
from extract import extract_run_data

CONCURRENT_RUNS = 6


def cleanup_run_files(run_id):
    run_dir = Path(NCDF_DIR) / run_id

    if run_dir.exists():
        shutil.rmtree(run_dir)


def process_single_run(run_id):
    print_log_p(f"Processing: {run_id}", Fore.BLUE)

    try:
        download_success, files = download_run_data(run_id)

        if not download_success:
            print_log_p(f"Download failed for {run_id}", Fore.RED)
            return False

        extract_success, total_rows = extract_run_data(run_id, files)

        if not extract_success:
            print_log_p(f"Extraction failed for {run_id}", Fore.RED)
            cleanup_run_files(run_id)
            return False

        cleanup_run_files(run_id)
        return True

    except Exception as e:
        print_log_p(f"Error processing {run_id}: {str(e)}", Fore.RED)
        cleanup_run_files(run_id)
        return False


def main():
    print_log_p("Starting run-by-run weather data processing", Fore.BLUE)

    runs = generate_runs()
    total_runs = len(runs)

    print_log_p(f"Processing {total_runs} runs from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}",
                Fore.BLUE)
    print

    with multiprocessing.Pool(processes=CONCURRENT_RUNS) as pool:
        results = pool.map(process_single_run, runs)

    success_runs = sum(results)
    failed_runs = total_runs - success_runs

    print()
    print_log_p(f"Processing complete!", Fore.BLUE)
    print_log_p(f"Successful: {success_runs} runs", Fore.GREEN)
    if failed_runs > 0:
        print_log_p(f"Failed: {failed_runs} runs", Fore.RED)


if __name__ == "__main__":
    main()
