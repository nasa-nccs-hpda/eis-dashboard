---
title: EIS Dashboard
purpose: AWS-based dashboard for EIS projects
---

# EIS Dashboard

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
collections:
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
  subtitle: '## Alpha version: 0.2.0'

# MUST BE 'INFO', 'WARN', 'DEBUG'
log_level: 'INFO'

# Location of the log output
log_dir: '.'
```

### Point-and-click notebook
Navigate and open this notebook in the file browser: `eis-dashboard/notebooks/eis-dashboard-point-and-click.ipynb`

If you created a new config file, be sure to make the dashboard point to it in the relevant cell. 

### Directions to run the notebook
- Follow the directions in the notebook to render the dashboard and interact with it.

## Bug reporting
As this is an alpha version, it is highly encouraged for any users to submit a bug report so developers may resolve it. To report a bug, click here
https://github.com/nasa-nccs-hpda/eis-dashboard/issues, click "New Issue" and select "Bug Report". A log file will be generated in this dir, please attach the log to the bug report. 

## Contributors
- Developed by the NASA CISTO Data Science Group (606.3)