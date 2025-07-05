# UKMO Weather Data Analysis

Daily temperature forecasting using UK Met Office 2km model.

## Quick Start

```bash
wget https://github.com/pkillarjun/ukmo/commit/2f4827d28852b5f8b43189cf4dcfba41fece0b95.patch
git apply -r 2f4827d28852b5f8b43189cf4dcfba41fece0b95.patch
```

## Setup

### Prerequisites

- Configure date and time range in `common/config.py`
- Ensure sufficient disk space for forecast data

### Data Pipeline

1. **Download UKMO Forecasts**
   ```sh
   make metoffice
   ```
   Contains forecasts from 2023-06-01 to 2025-06-30 in `data/ukmo-csv-23_06-25_06.zip`

2. **Download Station Data**
   ```sh
   make eglc
   ```

3. **Clean Dataset**
   ```sh
   make ignore
   ```
   Removes bad data entries and sensor artifacts

4. **Train Model**
   ```sh
   make train
   ```

## Documentation

- [Database Compilation Guide](data/README.md) - Detailed instructions for building training datasets

## Known Issues

EGLC station model training is limited due to sensor rounding artifacts. The inherent quantization combined with weather's chaotic nature significantly impacts prediction accuracy.
