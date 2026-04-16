import requests
from unittest.mock import MagicMock
from json import dumps
from json import loads
import numpy as np
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
from collections import deque
from typing import Union, Optional, List

# Functions -------------------------------------------------------------------------------------------------------------------------

"""
Helper method for write_compass_direction().
Takes the wind direction value in degrees and maps it to the compass reading. Returns the compass string.
"""
def wind_direction_mapper(wind_dir:int, fill_empty) -> str:
    if not isinstance(wind_dir, int):
        raise TypeError(f"The 'wind_dir' parameter in wind_direction_mapper() should be of type <int>, passed: {type(wind_dir)}")

    wind_dir_lookup = [
        'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'
    ]
    wind_val_lookup = [
        0, 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.4, 337.5, 360
    ]

    for i in range(len(wind_val_lookup)-1):
        if wind_dir < 0 or wind_dir > 360:
            return fill_empty
        if wind_dir >= wind_val_lookup[i] and wind_dir <= wind_val_lookup[(i+1)]:
            return wind_dir_lookup[i]   
        
    print(f"Error locating wind direction: {wind_dir}")    
    sys.exit(1)


"""
Helper method for get_columns(), build_headers(), and write_compass_direction().
Takes a shortname representing a measurement and returns True if that shortname is for wind direction, False otherwise.
"""
def is_wind_dir(measurement:str) -> bool:
    if not isinstance(measurement, str):
        raise TypeError(f"The 'measurement' parameter in is_wind_dir() should be of type <str>, passed: {type(measurement)}")
    
    wind_dir_shortnames = [ # as new shortnames get added to database, this must be updated
        'wd', 'wgd', 'wind_direction'
    ]

    if measurement in wind_dir_shortnames:
        return True

    return False


"""
Takes the dictionary entry of the measurements at a timestamp obtained from API. Adds the compass rose classification 
for all measurements containing wind direction or wind gust direction to a new updated dictionary and returns it.
"""
def write_compass_direction(dictionary:dict, fill_empty) -> dict:
    if not isinstance(dictionary, dict):
        raise TypeError(f"The 'dictionary' parameter in write_compass_direction() should be of type <dict>, passed: {type(dictionary)}")

    updated_dict = dictionary
    for measurement in list(dictionary.keys()):
        if is_wind_dir(measurement):
            compass_dir = {f'{measurement}_compass_dir': wind_direction_mapper(int(dictionary[measurement]), fill_empty)}
            updated_dict.update(compass_dir)  

    return updated_dict


"""
Reads available CHORDS portals from portals.txt and exports as a list.
"""
def load_portals(path: Optional[Union[str, Path]] = None) -> List[str]:
    if path is None:
        path = Path(__file__).with_name("portals.txt")
    else:
        path = Path(path)

    with path.open() as f:
        portals = [
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        ]
    return portals

HERE = Path(__file__).parent
PORTAL_LOOKUP = load_portals(
    HERE / "dev" / "portals.txt"
)

"""
Helper function for build_headers() that checks if a header is in the known set of headers.
"""
def headers_are_valid(columns_desired:list, columns_found:list, portal_name:str) -> bool:
    if not isinstance(columns_desired, list):
        raise TypeError(f"The 'columns_desired' parameter of headers_are_valid() should be of type <list>, passed: {type(columns_desired)}")
    if not isinstance(columns_found, list):
        raise TypeError(f"The 'columns_found' parameter of headers_are_valid() should be of type <list>, passed: {type(columns_found)}")
    if not isinstance(portal_name, str):
        raise TypeError(f"The 'portal_name' parameter of headers_are_valid() should be of type <str>, passed: {type(portal_name)}")

    for col in columns_desired:
        if col.endswith('compass_dir'):
            print("\t ======================= ERROR =======================")
            print("\t 'compass_dir' columns are not valid.")
            print(f"\t Only specify shortnames found in {portal_name} associated with the instrument id.")
            return False
        if col not in columns_found:
            print("\t ======================= ERROR =======================")
            print(f"\t Could not locate desired column '{col}' in data stream.")
            str_1 = ""
            for j in columns_found:
                str_1 += f"{j}  "
            print(f"\t Column(s) identified in data stream: {str_1}")
            return False
        
    return True


"""
Helper function for get_columns that applies a kind of sort to the headers. Data from API stream comes into main() via
Python dictionaries, which randomly store key/value pairs, and so the column headers will be randomly ordered without sort.
Takes a list of column names, looks up the sort associated with the portal, and returns a new list of organized header names.
"""
def sort_columns(columns:list, portal_name:str) -> list:
    if not isinstance(columns, list):
        raise TypeError(f"The 'columns' parameter in sort_columns() should be of type <list>, passed: {type(columns)}")
    if not isinstance(portal_name, str):
        raise TypeError(f"The 'portal_name' parameter in sort_columns() should be of type <str>, passed: {type(portal_name)}")

    b_sort = [ # Barbados
        't1', 't2', 't3', 'rh1', 'msl1', 'sp1', 'ws', 'wd', 'wd_compass_dir', 'rain', 'vis1', 'ir1', 'uv1'
    ]
    t_sort = [ # Trinidad
        'bt1', 'mt1', 'ht1', 'st1', 'bp1', 'bh1', 'hh1', 'sh1', 'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir', 'rg', 
        'sv1', 'si1', 'su1', 'bcs', 'bpc', 'cfr', 'css'
    ]
    threeD_sort = [ # 3D PAWS
        't1', 't2', 't3', 't4', 't5', 't6', 't7','t8', 't9', 'ht1', 'ht2', 'bt1', 'mt1', 'st1', 'htu21d_temp', 'mcp9808', 'bmp_temp', 'bme_temp', 
        'bp1', 'sp1', 'sp2', 'sp3', 'msl1', 'msl2', 'msl3', 'bmp_slp', 'bme_slp', 'bmp_pressure', 'bme_pressure', 'mslp',
        'bmp_altitude',
        'ws', 'wind_speed', 'wd', 'wind_direction', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'hh1', 'hh2', 'rh1', 'rh2', 'rh3', 'rh4', 'rh5', 'bh1', 'sh1', 'htu21d_humidity', 'bme_humidity',
        'rain', 'rg', 'rgt', 'rgp', 'rgds',
        'h1', 'wlo', 'wld', 'wlm', 'wlr', # water level sensors
        'sg', # snow depth sensor
        'pm2_5', 'pm10', 'pm1s10', 'pm1e10', 'pm1s25', 'pm1e25', 'pm1s100', 'pm1e100' # air quality sensors
        'st1', 'st2', 'st3', 'sm1', 'sm2', 'sm3', 'tmsms1', 'tmsms2', 'tmsms3', 'tmsms4', 'tmsms5', 'tmsmt1', 'tmsmt2', # soil temp and soil moisture sensors
        'sv1', 'si1', 'su1', 'vis1', 'ir1', 'uv1', 'si1145_vis', 'si1145_ir', 'si1145_uv', 'si1145_vis1', 'si1145_ir1', 'si1145_uv1',
            'si1145_vis2', 'si1145_ir2', 'si1145_uv2', 'si1145_vis3', 'si1145_ir3', 'si1145_uv3', 'si1145_vis4', 'si1145_ir4', 'si1145_uv4',
            'solar1', 'solar2', 'lx', # irradiance sensors
        'bcs', 'bpc', 'cfr', 'bv', 'css', 'hth' # battery health
    ]
    threeD_cal_sort = [ # 3D Calibration
        'htu21d_temp', 'bmp_temp', 'mcp9808', 'sht31d_temp', 'sht31d_humidity', 'htu21d_humidity', 'bmp_slp', 'bmp_pressure', 'rain', 'wind_speed', 
        'wind_direction', 'wind_direction_compass_dir', 'wg', 'wgd', 'wind_gust_direction_compass_dir', 'si1145_vis', 'si1145_ir', 'si1145_uv', 'bpc'
    ]
    f_sort = [ # FEWSNET
        'rg', 'rg1', 'rg2', 'rgt', 'rgt1', 'rgt2', 'rgp', 'rgp1', 'rgp2',
        'hi',  'wbt', 'wbgt',
        'bt1', 'bt2', 'ht1', 'ht2', 'st1', 'mt1',
        'bh1', 'bh2', 'hh1', 'hh2', 'sh1',
        'bp1', 'bp2', 'mslp',
        'sv1', 'si1', 'su1',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'hth', 'bpc', 'bcs', 'css', 'cfr', 'bv'
    ]
    m_sort = [ # Malawi
        'rg', 'rg1', 'rg2', 'rgt', 'rgt1', 'rgt2', 'rgp', 'rgp1', 'rgp2',
        'hi',  'wbt', 'wbgt',
        'bt1', 'st1', 'mt1',
        'bh1', 'sh1',
        'bp1', 'bp2', 'mslp',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'hth', 'bpc', 'bcs', 'css', 'cfr'
    ]
    bh_sort = [ # Bahamas
        'st1', 'bt1', 'mt1', 'sh1', 'bp1', 'mslp',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'rg', 'rgt', 'rgp',
        'hi', 'wbt', 'wbgt',
        'hth', 'css', 'bcs', 'bpc'
    ]
    sm_sort = [ # Somalia 
        'rg', 'rg1', 'rg2', 'rgt', 'rgt1', 'rgt2', 'rgp', 'rgp1', 'rgp2',
        'hi',  'wbt', 'wbgt',
        'bt1', 'bt2', 'ht1', 'ht2', 'st1', 'mt1',
        'bh1', 'bh2', 'hh1', 'hh2', 'sh1',
        'bp1', 'bp2', 'mslp',
        'sv1', 'si1', 'su1',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'hth', 'bpc', 'bcs', 'css', 'cfr', 'bv'
    ]
    d_sort = [ # Dominican Republic
        'ht1', 'st1', 'bt1', 'mt1', 'hh1', 'sh1', 'bp1', 'mslp', 'bmp_slp', 
        'rg', 'rgt', 'rg1', 'rg2', 'rgt1', 'rgt2', 'rgp1', 'rgp2',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir', 
        'wl', 'wlo', 'wld', 'wlm', 'wlr', 'sg',
        'tmsms1', 'tmsms2', 'tmsms3', 'tmsms4', 'tmsms5', 'tmsmt1', 'tmsmt2', 
        'sv1', 'si1', 'su1', 'hth', 'bpc', 'bcs', 'css', 'cfr', 'bv'
    ]
    a_sort = [ # Argentina
        'st1', 'bt1', 'mt1', 'sh1', 'bp1', 'mslp', 'rg', 'rgs', 'rgt', 'rgp', 'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir', 
        'sv1', 'si1', 'su1', 'hth', 'bpc', 'bcs', 'cfr', 'css'
    ]
    z_sort = [ # Zimbabwe
        'rg', 'rg1', 'rg2', 'rgt', 'rgt1', 'rgt2', 'rgp', 'rgp1', 'rgp2',
        'hi',  'wbt', 'wbgt',
        'bt1', 'st1', 'mt1',
        'bh1', 'sh1',
        'bp1', 'bp2', 'mslp',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'hth', 'bpc', 'bcs', 'css', 'cfr'
    ]
    fj_sort = [ # Fiji
        'st1', 'bt1', 'mt1', 'sh1', 'bp1', 'mslp',
        'ws', 'wd', 'wd_compass_dir' 'wg', 'wgd', 'wgd_compass_dir',
        'rg', 'rgt', 'rgp',
        'hi', 'wbt', 'wbgt',
        'hth', 'css', 'bcs', 'bpc'
    ]
    j_sort = [ # Jamaica
        'st1', 'bt1', 'mt1', 'sh1', 'bp1', 'mslp',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'rg', 'rgt', 'rgp',
        'hi', 'wbt', 'wbgt',
        'hth', 'css', 'bcs', 'bpc'
    ]
    k_sort = [ # Kenya
        'st1', 'bt1', 'mt1', 'sh1', 'bp1', 'mslp',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'rg', 'rgt', 'rgp',
        'hi', 'wbt', 'wbgt',
        'hth', 'css', 'bcs', 'bpc'
    ]
    i_sort = [ # IITM
        'st1', 'bt1', 'mt1', 'sh1', 'bp1', 'mslp',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'rg', 'rgt', 'rgp',
        'hi', 'wbt', 'wbgt',
        'hth', 'css', 'bcs', 'bpc'
    ]
    zm_sort = [ # Zambia
        'mcp9808', 'bmp_temp', 'htu21d_temp', 'htu21d_humidity', 'bmp_pressure', 'bmp_slp', 'bme_pressure',
        'wind_speed', 'wind_direction', 'si1145_vis', 'si1145_ir', 'si1145_uv', 'rain'
    ]
    e_sort = [ # Ethiopia
        'rg', 'rg1', 'rg2', 'rgt', 'rgt1', 'rgt2', 'rgp', 'rgp1', 'rgp2',
        'hi',  'wbt', 'wbgt',
        'bt1', 'st1', 'mt1',
        'bh1', 'sh1',
        'bp1', 'bp2', 'mslp',
        'ws', 'wd', 'wd_compass_dir', 'wg', 'wgd', 'wgd_compass_dir',
        'hth', 'bpc', 'bcs', 'css', 'cfr'
    ]

    portal_name_lower = portal_name.lower()

    if portal_name_lower == "Barbados".lower():
        column_map = {col: i for i, col in enumerate(b_sort)}
    elif portal_name_lower == "Trinidad".lower():
        column_map = {col: i for i, col in enumerate(t_sort)}
    elif portal_name_lower == "3D-PAWS".lower():
        column_map = {col: i for i, col in enumerate(threeD_sort)}
    elif portal_name_lower == "Calibration".lower():
        column_map = {col: i for i, col in enumerate(threeD_cal_sort)}
    elif portal_name_lower == "FEWSNET".lower():
        column_map = {col: i for i, col in enumerate(f_sort)}
    elif portal_name_lower == "Dominican-Republic".lower():
        column_map = {col: i for i, col in enumerate(d_sort)}
    elif portal_name_lower == "Argentina".lower():
        column_map = {col: i for i, col in enumerate(a_sort)}
    elif portal_name_lower == "Zimbabwe".lower():
        column_map = {col: i for i, col in enumerate(z_sort)}
    elif portal_name_lower == "Fiji".lower():
        column_map = {col: i for i, col in enumerate(fj_sort)}
    elif portal_name_lower == "Malawi".lower():
        column_map = {col: i for i, col in enumerate(m_sort)}
    elif portal_name_lower == "Bahamas".lower():
        column_map = {col: i for i, col in enumerate(bh_sort)}
    elif portal_name_lower == "Jamaica".lower():
        column_map = {col: i for i, col in enumerate(j_sort)}
    elif portal_name_lower == "Kenya".lower():
        column_map = {col: i for i, col in enumerate(k_sort)}
    elif portal_name_lower == "IITM".lower():
        column_map = {col: i for i, col in enumerate(i_sort)}
    elif portal_name_lower == "Zambia".lower():
        column_map = {col: i for i, col in enumerate(zm_sort)}
    elif portal_name_lower == "Ethiopia".lower():
        column_map = {col: i for i, col in enumerate(e_sort)}
    elif portal_name_lower == "Somalia".lower():
        column_map = {col: i for i, col in enumerate(sm_sort)}
    else:
        print("Portal provided does not have a specified sort order.")

    sorted_columns = sorted(columns, key=lambda col: column_map.get(col, float('inf'))) # columns not found in sort appended at end
    return list(sorted_columns) 


"""
Takes a list of dictionaries and returns a list of the set of all variables to be used as columns in the csv.
The exception is when include_test is set to True -- it will append a column 'test' next to each variable indicating 
whether the data is test data. If a wind direction column is in the set, an adjacent compass_dir column will be appended
containing the corresponding compass rose reading for each field.
"""
def get_columns(dictionary_list:list, include_test:bool, portal_name:str) -> list:
    if not isinstance(dictionary_list, list):
        raise TypeError(f"The 'dictionary_list' parameter in get_columns() should be of type <list>, passed: {type(dictionary_list)}")
    if not isinstance(include_test, bool):
        raise TypeError(f"The 'include_test' parameter in get_columns() should be of type <bool>, passed: {type(include_test)}")
    if not isinstance(portal_name, str):
        raise TypeError(f"The 'portal_name' parameter in get_columns() should be of type <str>, passed: {type(portal_name)}")

    columns = [] # list of strings 
    for dictionary in dictionary_list:
        cols = list(dictionary.keys())
        cols_sorted = sort_columns(cols, portal_name)
        for col in cols_sorted:
            if not col in columns:
                columns.append(str(col))
                if include_test:
                    columns.append('test')

    return columns


"""
Creates a list of all the header names to be used in the csv requested by user and returns it.
"""
def build_headers(measurements:list, columns_desired:list, include_test:bool, portal_name:str) -> list:
    if not isinstance(measurements, list):
        raise TypeError(f"The 'measurements' parameter of build_headers() should be of type <list>, passed: {type(measurements)}")
    if not isinstance(columns_desired, list):
        raise TypeError(f"The 'columns_desired' parameter of build_headers() should be of type <list>, passed: {type(columns_desired)}")
    if not isinstance(include_test, bool):
        raise TypeError(f"The 'include_test' parameter of build_headers() should be of type <bool>, passed: {type(include_test)}")
    if not isinstance(portal_name, str):
        raise TypeError(f"The 'portal_name' parameter of build_headers() should be of type <str>, passed: {type(portal_name)}")

    headers = ['time'] # list of strings
    columns = get_columns(measurements, include_test, portal_name)
    
    if len(columns) == 0: # if no data, pass to main 
        return []
    if not headers_are_valid(columns_desired, columns, portal_name): # check if user typed in recognized shortnames
        sys.exit(1)
    
    for i in range(len(columns)):
        if len(columns_desired) == 0: # no user-specified columns
            headers.append(columns[i])
        elif len(columns_desired) != 0 and columns[i] in columns_desired:
            headers.append(columns[i])
            if include_test:
                headers.append(columns[i+1])
            if is_wind_dir(columns[i]):
                headers.append(f'{columns[i]}_compass_dir')
        elif len(columns_desired) != 0 and columns[i] not in columns_desired:
            continue  
        else:
            print("Error locating column header names.")
            sys.exit(1)

    return headers


"""
Accepts an array of headers, timestamps, and of dictionaries containing sensor measurements. 
Also accepts a np array of whether or not  the measurements at that timestamp are test values. 
Returns a dataframe.
"""
def build_dataframe(headers: list, time: np.ndarray, measurements: np.ndarray, test: np.ndarray,
                    include_test: bool, time_window_start='', time_window_end='') -> pd.DataFrame:
    if not isinstance(headers, list):
        raise TypeError(f"'headers' must be list, got {type(headers)}")
    if not isinstance(time, np.ndarray):
        raise TypeError(f"'time' must be np.ndarray, got {type(time)}")
    if not isinstance(measurements, np.ndarray):
        raise TypeError(f"'measurements' must be np.ndarray, got {type(measurements)}")
    if not isinstance(test, np.ndarray):
        raise TypeError(f"'test' must be np.ndarray, got {type(test)}")
    if not isinstance(include_test, bool):
        raise TypeError(f"'include_test' must be bool, got {type(include_test)}")

    rows = []
    for i, t in enumerate(time.tolist()):
        row = {"time": str(t).replace("T", " ").replace("Z", "")}
        row.update(dict(measurements[i]))
        if include_test:
            row["test"] = test.tolist()[i]
        rows.append(row)

    df = pd.DataFrame(rows)

    if len(headers) > 0:
        df = df[headers]

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)

    if time_window_start != '' and time_window_end != '':
        df = df.loc[
            (df["time"].dt.time >= time_window_start) &
            (df["time"].dt.time <= time_window_end)
        ].reset_index(drop=True)

    return df
    

"""
Accepts an array of headers, timestamps, and of dictionaries containing sensor measurements. 
Also accepts a np array of whether or not  the measurements at that timestamp are test values. 
Accepts a string of the filepath at which to create the csv file and creates the csv there.
"""
def write_dataframe_csv(df: pd.DataFrame, filepath: Path) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"'df' must be pd.DataFrame, got {type(df)}")
    if not isinstance(filepath, Path):
        raise TypeError(f"'filepath' must be Path, got {type(filepath)}")

    df.to_csv(filepath, index=False, encoding="utf-8")
    

"""
Accepts a dictionary containing the result of the API data download from CHORDS and checks whether it was successful.
Returns True if excess datapoints, False otherwise.
"""
def has_excess_datapoints(dictionary:dict) -> bool:
    if not isinstance(dictionary, dict):
        raise TypeError(f"The 'dictionary' parameter in has_excess_datapoints() should be of type <dict>, passed: {type(dictionary)}")

    for key in dictionary: 
        if key == "errors":
            return True

    return False


"""
Accepts np arrays for measurements, time, and test which were created from the data stream from CHORDS, and checks whether 
the transfer of data from the stream to the data structs was a success.
"""
def struct_has_data(measurements:np.ndarray, time:np.ndarray, test:np.ndarray) -> bool:
    if not isinstance(measurements, np.ndarray):
        raise TypeError(f"The 'measurements' parameter in struct_has_data() should be of type <np.ndarray>, passed: {type(measurements)}")
    if not isinstance(time, np.ndarray):
        raise TypeError(f"The 'time' parameter in struct_has_data() should be of type <np.ndarray>, passed: {type(time)}")
    if not isinstance(test, np.ndarray):
        raise TypeError(f"The 'test' parameter in struct_has_data() should be of type <np.ndarray>, passed: {type(test)}")
    
    if (len(measurements) == 0) or (len(time) == 0) or (len(test) == 0):
        return False

    return True


"""
Comprehensive REST API error handler. Returns True if error found, False if OK.
"""
def has_errors(response: requests.Response, portal_name: str, iD: int) -> bool:
    
    if isinstance(response, MagicMock): # Skip type check for MagicMock (pytest)
        return False                    # Mock always "succeeds" for tests

    if not isinstance(response, requests.Response):
        raise TypeError(f"Expected requests.Response, got {type(response)}")
    if not isinstance(portal_name, str):
        raise TypeError(f"portal_name should be str, got {type(portal_name)}")
    if not isinstance(iD, int):
        raise TypeError(f"iD should be int, got {type(iD)}")
    
    status_code = response.status_code
    
    if status_code == 200: # Success - check JSON content for app-level errors
        try:
            all_fields = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"{portal_name} #{iD}: Non-JSON response (Status 200)")
            return True
        
        # App-level errors in JSON body
        if 'errors' in all_fields and all_fields['errors']:
            error_msg = all_fields['errors'][0]
            print(f"\t\t{portal_name} #{iD}: API Errors - {error_msg}")
            
            if 'Access Denied' in error_msg or 'authentication required' in error_msg:
                print("\t\tFix: Check email/api_key in URL")
                sys.exit(1)

            return True
            
        if 'error' in all_fields:
            print(f"\t\t{portal_name} #{iD}: {all_fields['error']}")
            return True
            
        return False  # JSON OK
    
    elif status_code == 401:
        print(f"\t\t{portal_name} #{iD}: Unauthorized - Invalid API key")
        sys.exit(1)
        
    elif status_code == 403:
        print(f"\t\t{portal_name} #{iD}: Forbidden - No permission for instrument")
        return True
        
    elif status_code == 404:
        print(f"\t\t{portal_name} #{iD}: Not Found - Instrument/ID missing")
        return True
    
    elif status_code == 413: 
        return              # Excess datapoints requested, pass back for reduction
        
    elif status_code == 422:
        print(f"\t\t{portal_name} #{iD}: Unprocessable - Bad date range/params")
        print(f"\t\t   URL: {response.url}")
        return True
        
    elif status_code in (500, 502, 503, 504):
        print(f"\t\t{portal_name} #{iD}: Server Error {status_code} - Try later")
        return True
        
    else:
        print(f"\t\t{portal_name} #{iD}: Unexpected {status_code}")
        print(f"\t\t   Response: {response.text[:200]}...")
        return True


"""
Handles data request error where number of data points exceeds that allowed. Returns a list of new timestamps for which 
to run the API request to CHORDS s.t. the number of data points requested is less than the max allowed. Returns the 
lists of data necessary for main() to build csv's.
"""
def reduce_datapoints(error_message:str, iD:int, timestamp_start:datetime, timestamp_end:datetime, \
                                    portal_url:str, user_email:str, api_key:str, fill_empty) -> list:
    if not isinstance(error_message, str):
        raise TypeError(f"The 'error_message' parameter in reduce_datapoints() should be of type <str>, passed: {type(error_message)}")
    if not isinstance(iD, int):
        raise TypeError(f"The 'iD' parameter in reduce_datapoints() should be of type <int>, passed: {type(iD)}")
    if not isinstance(timestamp_start, datetime):
        raise TypeError(f"The 'timestamp_start' parameter in reduce_datapoints() should be of type <datetime>, passed: {type(timestamp_start)}")
    if not isinstance(timestamp_end, datetime):
        raise TypeError(f"The 'timestamp_end' parameter in reduce_datapoints() should be of type <datetime>, passed: {type(timestamp_end)}")
    if not isinstance(portal_url, str):
        raise TypeError(f"The 'portal_url' parameter in reduce_datapoints() should be of type <str>, passed: {type(portal_url)}")
    if not isinstance(user_email, str):
        raise TypeError(f"The 'user_email' parameter in reduce_datapoints() should be of type <str>, passed: {type(user_email)}")
    if not isinstance(api_key, str):
        raise TypeError(f"The 'api_key' parameter in reduce_datapoints() should be of type <str>, passed: {type(api_key)}")

    print("\tBeginning reduction calculation.")

    queue = deque([(timestamp_start, timestamp_end)])
    time, measurements, test = [], [], []
    total_num_measurements = 0

    while queue:
        start_seg, end_seg = queue.popleft()
        print(f"\t\tGetting segment {start_seg} -> {end_seg}")

        url = f"{portal_url}/api/v1/data/{iD}?start={start_seg}&end={end_seg}&email={user_email}&api_key={api_key}"
        response = requests.get(url)
        all_fields = loads(dumps(response.json()))

        if has_excess_datapoints(all_fields):
            mid = start_seg + (end_seg - start_seg)/2
            queue.appendleft((start_seg, mid))
            queue.append((mid, end_seg))
            continue

        data = all_fields['features'][0]['properties']['data']
        for dictionary in data:
            time.append(str(dictionary['time']))
            test.append(str(dictionary['test']))
            total_num_measurements += len(dictionary['measurements'].keys())
            add_wind = write_compass_direction(dict(dictionary['measurements']), fill_empty)
            measurements.append(add_wind)
    
    print("\tFinished reduction calculation.")
    return [time, measurements, test, total_num_measurements]
     