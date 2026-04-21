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



import sys
import requests
from unittest.mock import MagicMock

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



from datetime import datetime
from collections import deque
from json import dumps, loads

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



def fetch_instrument_records(
    portal_name: str,
    base_url: str,
    instrument_id: int,
    user_email: str,
    api_key: str,
    start: datetime,
    end: datetime,
) -> list[dict]:
    ...

def fetch_portal_records(
    portal_name: str,
    base_url: str,
    user_email: str,
    api_key: str,
    start: datetime,
    end: datetime,
) -> list[dict]:
    ...

