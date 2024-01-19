---
title: EIS Dashboard
purpose: AWS-based dashboard for EIS projects
---

# EIS Dashboard

![CI Workflow](https://github.com/nasa-nccs-hpda/eis-dashboard/actions/workflows/ci.yml/badge.svg)
![Code style: PEP8](https://github.com/nasa-nccs-hpda/eis-dashboard/actions/workflows/lint.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage Status](https://coveralls.io/repos/github/nasa-nccs-hpda/eis-dashboard/badge.svg?branch=main)](https://coveralls.io/github/nasa-nccs-hpda/eis-dashboard?branch=main)

Version: v0.3.0

This application implements notebooks which make visualizing data from EarthData easier by allowing for user interaction with the data.

## Quickstart
### Navigate to your EIS project's daskhub
- Min requirements for memory is 4GB, ideally 8GB.

### EarthData credentials
These notebooks access data via variou DAAC's s3 buckets, in order to do this you must first put your NASA EarthData credentials in your `~/.netrc` file.

To do this in daskhub, click File -> New -> Terminal and run the following command:

```bash
echo "machine urs.earthdata.nasa.gov login USERNAME password PASSWD" > ~/.netrc ; > ~/.urs_cookies
chmod  0600 ~/.netrc
```

where USERNAME and PASSWD are your [EarthData](http://urs.earthdata.nasa.gov/) credentials.

### Getting the code:
The code is located in this git repo, accessible to clone via:
```bash
git clone https://github.com/nasa-nccs-hpda/eis-dashboard.git
```

### Configuration:
An example config file is in `configs/example_config.yaml`. Users may create their own or edit this config to use data desired by the user. The general setup of the config file is as follows:

```yaml
nasa_earthdata_collections:
  ids:
    - 'GLDAS_NOAH025_3H' # The application only supports collectionID shortnames

# Must be a bounding box, narrows the search CMR performs to see what data is necessary
# you may find these short-names via EarthData search. 
# IMPORTANT: Currently the collections must be gridded and be able to be read by xarray.
bounds:
  -  [-76.6, 38.8, -76.5, 38.9]

# Must be in YYYY-MM-DD
time_bounds:
  start: '2019-05-18'
  end: '2019-06-18'

title:
  title: '# My EIS Dashboard'
  subtitle: '## Beta version: 0.3.0'

# MUST BE 'INFO', 'WARN', 'DEBUG'
log_level: 'INFO'

# Location of the log output
log_dir: '.'
```

### Point-and-click notebook
Navigate and open this notebook in the file browser: `eis-dashboard/notebooks/eis-dashboard-point-and-click.ipynb`

If you created a new config file, be sure to make the dashboard point to it in the relevant cell. 

### Polygon-draw notebook
Navigate and open this notebook in the file browser: `eis-dashboard/notebooks/eis-dashboard-polygon.ipynb`

This notebook allows users to draw polygons inside the map and see spatially averaged time series for variables according to the drawn polygon. See markdown in the notebook for further information.

### Raster viewer notebook
Navigate and open this notebook in the file browser: `eis-dashboard/notebooks/eis-dashboard-raster.ipynb`

This notebook allows users to view rasters inside the notebook. User the Variable widget to select which variables to view in the map viewer. Use the time-stamp widget to select which time stamp to view.

See `configs/dev_configs/example_config_raster.yaml` for an example configuration file to use with this notebook.

## Features and requirements

### <b>Format Requirements</b>
- point-and-click notebook, polygon notebook
  - Xarray-readable datasets
  - Must have `lat, lon, and time` variables
- raster notebook
  - Xarray-readable datasets

  To test datasets for compatibility try:
  ```python
  import xarray as xr

  s3_path_to_dataset: list = ['s3://my-example/dataset.zarr']
  # or
  s3_path_to_dataset: list = ['s3://my-example/dataset.time.0.nc', 's3://my-example/dataset.time.1.nc']

  data_array = xr.open_mfdataset(s3_path_to_dataset)

  print(data_array)
  ```
### <b>Notes</b>

- Dataset Size
  - There is no hard limit placed on how much data can be loaded in. Larger amounts of data will cause the notebooks to not function as intended
- Dimension Variables
  - Datasets must container either `lat, lon, time` or `latitude, longitude, time` variables. For now, xarray is case-sensitive on these variables. `Latitude, Longitude, Time` will result in an error

### <b>Data Ingest</b>

Data Retrieval Methods:
- NASA Earthdata Cloud datasets (see [NASA Earthdata Search](https://search.earthdata.nasa.gov/search?ff=Available%20in%20Earthdata%20Cloud&fl=3%2B-%2BGridded%2BObservations!4%2B-%2BGridded%2BModel%2BOutput))
  - Notebooks supported: all
  - Supported DAACs: GES DISC, PO DAAC and PO CLOUD, LP DAAC, ORNL DAAC, GHRC DAAC
  - See `configs/dev_configs/test_nasaed_only.yaml` and the example config for examples on adding NASA ED Cloud datasets to the dashboard
  - Collection name should be the collection short-name in order for CMR queries to function
- Custom S3 datasets (raster notebook currently not supported)
  - Notebooks supported: point-and-click, polygon
  - Zarr format
  - See `configs/dev_configs/test_custom_only.yaml` and `configs/dev_configs/test_config_both.yaml` for examples on adding custom S3 locations to the dashboard.

### Directions to run the notebook
- Follow the directions in the notebook to render the dashboard and interact with it.

## Bug reporting
As this is a beta version, it is highly encouraged for any users to submit a bug report so developers may resolve it. To report a bug, click here
https://github.com/nasa-nccs-hpda/eis-dashboard/issues, click "New Issue" and select "Bug Report". A log file will be generated in this dir, please attach the log to the bug report. 

## Contributors
- Developed by the NASA CISTO Data Science Group (606.3)
