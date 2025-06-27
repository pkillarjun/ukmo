import sys
import threading
import multiprocessing
from pathlib import Path
from colorama import init, Fore, Style
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *

init(autoreset=True)

print_lock_t = threading.Lock()
print_lock_p = multiprocessing.Lock()


def parse_run_time(time_str):
    return datetime.strptime(time_str, "%Y%m%dT%H%MZ")


def print_log(message, color=Fore.BLUE):
    print(f"{color}{message}{Style.RESET_ALL}")


def print_log_t(message, color=Fore.BLUE):
    with print_lock_t:
        print(f"{color}{message}{Style.RESET_ALL}")


def print_log_p(message, color=Fore.BLUE):
    with print_lock_p:
        print(f"{color}{message}{Style.RESET_ALL}")


def generate_runs():
    runs = []
    current_date = START_DATE

    while current_date <= END_DATE:
        for hour in RUN_HOURS:
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            runs.append(timestamp.strftime("%Y%m%dT%H00Z"))
        current_date += timedelta(days=1)
    return runs
