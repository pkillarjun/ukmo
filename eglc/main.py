#!/usr/bin/env python3

import sys
import requests
from pathlib import Path
from colorama import Fore
from datetime import timedelta

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *


def format_date(date):
    return {'day': date.day, 'year': date.year, 'month': date.month}


def build_url():
    start = format_date(START_DATE)
    end = format_date(END_DATE + timedelta(days=2))
    base_url = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"

    params = {
        'tz': 'Etc/UTC',
        'data': 'metar',
        'elev': 'no',
        'day1': start['day'],
        'day2': end['day'],
        'trace': 'null',
        'direct': 'yes',
        'latlon': 'no',
        'year1': start['year'],
        'year2': end['year'],
        'format': 'onlycomma',
        'missing': 'null',
        'station': STATION,
        'month1': start['month'],
        'month2': end['month']
    }

    query_string = '&'.join(f"{k}={v}" for k, v in params.items())
    return f"{base_url}?{query_string}"


def download(url, path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print_log(f"Error: {e}", Fore.RED)
        return False


def main():
    url = build_url()

    if download(url, METAR_FILE):
        print_log("Download completed successfully!", Fore.GREEN)
        print_log(f"File saved to: {Fore.YELLOW}{METAR_FILE}", Fore.GREEN)
    else:
        print_log("Download failed!", Fore.RED)
        print_log("Please check your internet connection and try again.", Fore.RED)


if __name__ == "__main__":
    main()
