# UKMO

Daily temperature forecasting using UK Met Office 2km model.

## Download Training Data

First, setup the date and time in `common/config.py`, then run:

```sh
make metoffice
```

**Note:** The `data/ukmo-csv-23_06-25_06.zip` file contains forecasts from `2023-06-01` to `2025-06-30`.

## Download EGLC Data

```sh
make eglc
```

## Remove Bad Data

To clean up bad data entries:

```sh
make ignore
```

## Model Training

```sh
make train
```
