import sys
import boto3
import concurrent.futures
from pathlib import Path
from datetime import timedelta
from colorama import Fore
from botocore import UNSIGNED
from botocore.config import Config

sys.path.append(str(Path(__file__).parent.parent))
from common.config import *
from common.utility import *

DOWNLOAD_THREADS = 12

BUCKET_NAME = "met-office-atmospheric-model-data"
BUCKET_PREFIX = "uk-deterministic-2km"
BUCKET_REGION = "eu-west-2"


def create_s3_client():
    s3_config = Config(signature_version=UNSIGNED, region_name=BUCKET_REGION)
    return boto3.client('s3', config=s3_config)


def list_s3_objects(bucket, prefix, s3_client):
    objects = []

    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

        for page in pages:
            if 'Contents' in page:
                objects.extend(page['Contents'])
    except Exception as e:
        print_log_p(f"Error listing objects for prefix {prefix}: {str(e)}", Fore.RED)
    return objects


def should_download_file(run_id, filename):
    required = False

    for variable in REQUIRED_VARIABLES:
        if filename.endswith(f"-{variable}.nc"):
            required = True
            break

    if not required:
        return False

    time_str = filename.split('-PT')[0]
    valid_dt = parse_run_time(time_str)
    model_dt = parse_run_time(run_id)

    if (valid_dt - model_dt) >= timedelta(hours=FORECAST_HOURS):
        return False
    return True


def filter_download_files(run_id, s3_objects):
    files = []

    for obj in s3_objects:
        key = obj['Key']
        filename = key.split('/')[-1]

        if not should_download_file(run_id, filename):
            continue

        file_path = Path(NCDF_DIR) / run_id / filename
        files.append((key, file_path, filename, BUCKET_NAME))
    return files


def download_file(args):
    key, file_path, filename, bucket, s3_client = args

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        s3_client.download_file(bucket, key, str(file_path))
        return True, filename
    except Exception as e:
        print_log_p(f"Failed to download {filename}: {str(e)}", Fore.RED)
        return False, filename


def download_parallel(files, s3_client):
    if not files:
        return 0, [], 0

    failed = 0
    downloaded = 0
    files_downloaded = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=DOWNLOAD_THREADS) as executor:
        futures = []

        for key, file_path, filename, bucket in files:
            args = (key, file_path, filename, bucket, s3_client)
            future = executor.submit(download_file, args)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                success, filename = future.result()
                if success:
                    downloaded += 1
                    files_downloaded.append(filename)
                else:
                    failed += 1
            except Exception as e:
                failed += 1
    return downloaded, files_downloaded, failed


def download_run_data(run_id):
    s3_client = create_s3_client()

    prefix = f"{BUCKET_PREFIX}/{run_id}/"
    s3_objects = list_s3_objects(BUCKET_NAME, prefix, s3_client)

    if not s3_objects:
        print_log_p(f"No objects found for run {run_id}", Fore.YELLOW)
        return False, []

    files = filter_download_files(run_id, s3_objects)

    if not files:
        print_log_p(f"No files to download for run {run_id}", Fore.YELLOW)
        return False, []

    downloaded, files_downloaded, failed = download_parallel(files, s3_client)

    if failed > 0:
        print_log_p(f"{run_id}: downloaded {downloaded}, failed {failed}", Fore.RED)
        return False, files_downloaded
    else:
        print_log_p(f"{run_id}: downloaded {downloaded} files", Fore.GREEN)
        return True, files_downloaded
