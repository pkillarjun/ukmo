# Data Build Process

## Overview

This document describes the process for downloading, processing, and building UKMO weather forecast data.

## Data Download Configuration

### 12-Hour Forecast Data
```python
FORECAST_HOURS = 12
RUN_HOURS = [0, 3, 6, 9, 12, 15, 18, 21]
```

### 24-Hour Forecast Data
```python
FORECAST_HOURS = 24
RUN_HOURS = [1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23]
```

## Processing Steps

### 1. Copy Downloaded Data
```bash
cp data/*.zip download/
```

### 2. Extract and Organize Data
```bash
pushd download/

# Extract 12-hour forecast data
unzip ukmo-csv-23_06-25_06.zip

# Extract 24-hour forecast data
unzip ukmo-csv-23_07-25_06_24hr.zip

# Rename directory for 12-hour data
mv ukmo-csv/ ukmo-csv-12/

popd
```

### 3. Run Processing Scripts
```bash
# Apply rolling updates to merge 12h and 24h data
python data/rolling.py

# Patch missing values (-999) in the data
python data/patch.py
```

## Directory Structure

After processing:
```
download/
├── ukmo-csv-12/        # 12-hour forecast data
├── ukmo-csv-24/        # 24-hour forecast data
├── ukmo-csv-rolling/   # Merged data (intermediate)
└── ukmo-csv/           # Final patched data
```

## Notes

- The 12-hour forecasts run every 3 hours starting from 0
- The 24-hour forecasts run on the remaining hours
- Missing values (-999) are patched using previous time steps
- The final output is in `download/ukmo-csv/`
