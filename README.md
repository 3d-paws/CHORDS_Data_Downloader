# CHORDS Data Downloader

This Python script automates the process of downloading data from the CHORDS database using its API. The script is configurable for different CHORDS portals and user-defined parameters. 
There are two primary data extraction options:<br><br>
`chords_local_download.py` - creates csv's on local hard drive<br>
`chords_dataframes.py` - returns a list of dataframes (more useful for automation as a part of an external workflow, less common)

## Features
- Retrieves data from the CHORDS database
- Supports customizable API parameters
  - CHORDS portal, instrument ID's, and data period in addition to other optional parameters
- Saves the downloaded data as a CSV or as a Pandas dataframe, with variable (sensor) shortnames used as column headers (see associated CHORDS portal for full sensor name)
- Includes API error handling, most noteably an exponential backoff method to reduce excess datapoints

## Requirements
To run this script, you’ll need:
- Python 3.6 or higher
- The following Python libraries:
  - `requests` for making API requests
  - `pandas` for CSV creation
  - `numpy` 

Install the required libraries with:

```bash
pip install -r requirements.txt
```
You will also need an account on the CHORDS portal you are trying to download data from. Your account must have download privileges as well as an API key.

## Utilization
To download data via the API, determine which method suits your application. See the discussion above to compare `chords_local_download.py` and `chords_dataframes.py`.
Next, simply imput your user parameters at the top of the script and run the program in your IDE.<br>
<br>
Required parameters:
- `portal_url` - The url for the CHORDS online portal.
- `portal_name` - The name of the CHORDS portal (see the section below for available portal names).
- `data_path` - The absolute folder path specifying where the CSV files should be printed to locally (only required if using `chords_local_download.py`).
- `instrument_IDs` - All the instruments to download data from. Use the Instrument Id from CHORDS portal.
- `user_email` - The email login information in order to access the CHORDS online portal.
- `api_key` - The API key which corresponds to the user's email address.
- `start` - The timestamp from which to start downloading data (MUST be in the following format: 'YYYY-MM-DD HH:MM:SS' e.g. '2023-11-25 00:00:00').
- `end` - The timestamp at which to end downloading data (MUST be in the following format: 'YYYY-MM-DD HH:MM:SS' e.g. '2023-11-31 23:59:59').
<br><br>
Optional parameters:
- `fill_empty` - Enter whatever value should be used to signal no data (e.g. 'NaN'). Empty string by default (creates smaller files).
- `include_test` - Set to True to include boolean columns next to each data column which specify whether data collected was test data (False by default).
- `columns_desired` - Enter the shortnames for the columns to include in csv (e.g. ['t1', 't2', 't3']). Includes all if left blank. Find shortnames on the CHORDS website.
- `time_window_start` - Timestamp from which to collect subset of data (MUST be in the following format: 'HH:MM:SS'). Includes all timestamps if left blank.
- `time_window_end` - Timestamp from which to stop collecting subset of data (MUST be in the following format: 'HH:MM:SS') Includes all timestamps if left blank.

## Available Portals
- `3D-PAWS`
- `Barbados`
- `Trinidad`
- `Dominican-Republic`
- `Calibration`
- `FEWSNET`
- `Kenya`
- `Zimbabwe`
- `Argentina`
- `IITM`
- `Fiji`
- `Bahamas`
- `Malawi`
- `Somalia`

## Documentation
In-depth documentation may be found at: https://docs.google.com/document/d/1qqs5X0vSslAEYBxlAh95oDgC1dG5xmBKVknz7wl1QxA/edit?usp=sharing
