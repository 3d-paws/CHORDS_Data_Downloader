import requests
from json import dumps
from json import loads
import numpy as np
from datetime import datetime, timedelta
from chords_downloader import resources
from pathlib import Path
import argparse

def main(
        portal_url:str, portal_name:str, instrument_IDs:list[int], user_email:str, api_key:str, start:str, end:str,
        fill_empty='', include_test:bool=False, columns_desired:list=[], time_window_start:str='', time_window_end:str='' 
    ) -> list: 

    # user input validation -----------------------------------------------------------------------------------------------------------
    format_str = "%Y-%m-%d %H:%M:%S"
    timestamp_start = datetime.strptime(start, format_str) 
    timestamp_end = datetime.strptime(end, format_str)
    if timestamp_start > timestamp_end:
            raise ValueError(f"Starting time cannot be after end time.\n\t\t\tStart: {timestamp_start}\t\tEnd: {timestamp_end}")
    if timestamp_start < datetime.now() - timedelta(days=365*2):
        print("\t ========================= WARNING =========================")
        print(f"\t timestamp_start before CHORDS cutoff (2 years): {timestamp_start}\n\t Will pull 2 year archive only.\n")
    if timestamp_end > datetime.now():
        print("\t ========================= WARNING =========================")
        print(f"\t timestamp_end in the future: {timestamp_end}\n\t Will pull up to today's date only.\n")

    if time_window_start != "" or time_window_end != "":
        format_str = "%H:%M:%S"
        timestamp_window_start = datetime.strptime(time_window_start, format_str).time()
        timestamp_window_end = datetime.strptime(time_window_end, format_str).time()
        if time_window_start > time_window_end:
            raise ValueError(f"The start time for the time window is after the end time: {time_window_start} > {time_window_end}")
        if time_window_start == "" or time_window_end == "":
            raise ValueError(f"Both the 'time_window_start' and 'time_window_end' variables must be populated to specify a collection timeframe.")

    portal_lookup = [
        'barbados', 'trinidad', '3d-paws', 'calibration', 'fewsnet', 'kenya', 
        'zimbabwe', 'dominican-republic', 'argentina', 'zambia', 'iitm', 'fiji',
        'malawi', 'bahamas', 'somalia'
    ]
    if portal_name.lower() not in portal_lookup:
        raise ValueError(f"Please enter one of the following portal names (case insensitive):\n\t \
                            Barbados, Trinidad, 3D-PAWS, Calibration, FEWSNET, Kenya, Zimbabwe, Zambia, Argentina, IITM, Dominican-Republic, Fiji, "\
                            "Malawi, Bahamas, Somalia")
    
    # processing loop ------------------------------------------------------------------------------------------------------------------
    dataframes = []

    for iD in instrument_IDs:
        if not isinstance(iD, int):
            raise TypeError(f"The instrument id's must be integers, passed {type(iD)} for id {iD}")

        print(f"---> Reading instrument ID {iD}\t\t\t\t\t\t\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if time_window_start == "" and time_window_end == "":
            time = [] # list of strings  (e.g. '2023-12-17T00:00:04Z')
            measurements = [] # list of dictionaries  (e.g. {'t1': 25.3, 'uv1': 2, 'rh1': 92.7, 'sp1': 1007.43, 't2': 26.9, 'vis1': 260, 'ir1': 255, 'msl1': 1013.01, 't3': 26.1})
            test = [] # list of strings of whether data point is a test value (either 'true' or 'false')

            total_num_measurements = 0
            total_num_timestamps = 0

            url = f"{portal_url}/api/v1/data/{iD}?start={start}&end={end}&email={user_email}&api_key={api_key}"
            response = requests.get(url=url)
            all_fields = loads(dumps(response.json())) # dictionary containing deep copy of JSON-formatted CHORDS data

            if resources.has_errors(all_fields, portal_name, iD):
                continue
            
            if resources.has_excess_datapoints(all_fields): # reduce timeframe in API call
                print("\t Large data request -- reducing.")
                reduced_data = resources.reduce_datapoints(all_fields['errors'][0], int(iD), timestamp_start, timestamp_end, \
                                                    portal_url, user_email, api_key, fill_empty)    # list
                                                                                        # e.g. [time, measurements, test, total_num_measurements]
                time = reduced_data[0]
                measurements = reduced_data[1]
                test = reduced_data[2]
                total_num_measurements = reduced_data[3]
            else:
                data = all_fields['features'][0]['properties']['data']  # list of dictionaries 
                                                                        # ( e.g. {'time': '2023-12-17T18:45:56Z', 'test': 'false', 'measurements': {'ws': 1.55, 'rain': 1}} )
                for i in range(len(data)):
                    time.append(str(data[i]['time']))
                    total_num_measurements += len(data[i]['measurements'].keys())
                    total_num_timestamps += 1
                    to_append = resources.write_compass_direction(dict(data[i]['measurements']), fill_empty)
                    measurements.append(to_append)
                    test.append(str(data[i]['test']))

                        
        else: # if a time window was specified by user
            print(f"\t\t Time window specified.\n\t\t Returning data from {time_window_start} -> {time_window_end}")
            
            window_data = resources.time_window(int(iD), timestamp_start, timestamp_end, timestamp_window_start, timestamp_window_end, \
                                            portal_url, user_email, api_key, portal_name, fill_empty)
            time = window_data[0]
            measurements = window_data[1]
            test = window_data[2]
            total_num_measurements = window_data[3]

        headers = resources.build_headers(measurements, columns_desired, include_test, portal_name) # list of strings 
        time = np.array(time)
        measurements = np.array(measurements)
        test = np.array(test)
        
        if resources.struct_has_data(measurements, time, test): 
            dataframes.append(resources.df_builder(headers, time, measurements, test, include_test, fill_empty))
            print(f"\t Finished writing to file.\t\t\t\t\t\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\t Total number of measurements: {total_num_measurements}")
        else:
            print("\t ========================= WARNING =========================")
            print(f"\t No data found at specified timeframe for {portal_name} Instrument ID {iD}. Skipping.\n")

    return dataframes


def parse_args() -> tuple[str, str, Path, list[int], str, str, str, str]:
    parser = argparse.ArgumentParser(
        description="Process API user parameters: portal_url, portal_name, instrument_IDs, user_email, api_key, start, and end."
    )

    parser.add_argument("portal_url",           type=str,   help="The url for the CHORDS online portal.")
    parser.add_argument("portal_name",          type=str,   help="The name of the CHORDS portal.")
    parser.add_argument("instrument_IDs",       type=Path,  help="All the instruments to download data from. Use the Instrument Id from CHORDS portal.")
    parser.add_argument("user_email",           type=str,   help="The email login information in order to access the CHORDS online portal.")
    parser.add_argument("api_key",              type=str,   help="The API key which corresponds to the user's email address.")
    parser.add_argument("start",                type=str,   help="The timestamp from which to start downloading data (MUST be in the following format: YYYY-MM-DD HH:MM:SS).")
    parser.add_argument("end",                  type=str,   help="The timestamp at which to stop downloading data (MUST be in the following format: YYYY-MM-DD HH:MM:SS).")
    parser.add_argument("-fill_empty",                      help="Enter whatever value should be used to signal no data (e.g. -999.99 or 'NaN'). Empty string by default (creates smaller files).")
    parser.add_argument("-include_test",        type=bool,  help="Set to True to include boolean columns next to each data column which specify whether data collected was test data (False by default). ")
    parser.add_argument("-columns_desired",     type=list,  help="Enter the shortnames for the columns to include in csv (e.g. ['t1', 't2', 't3']). Includes all if left blank.")
    parser.add_argument("-time_window_start",   type=str,   help="Timestamp from which to collect subset of data (MUST be in the following format: 'HH:MM:SS'). Includes all timestamps if left blank.")
    parser.add_argument("-time_window_end",     type=str,   help="Timestamp from which to stop collecting subset of data (MUST be in the following format: 'HH:MM:SS') Includes all timestamps if left blank.")

    args = parser.parse_args()
    return (
        args.portal_url, 
        args.portal_name, 
        args.instrument_IDs, 
        args.user_email, 
        args.api_key, 
        args.start, 
        args.end, 
        args.fill_empty, 
        args.include_test,
        args.columns_desired,
        args.time_window_start,
        args.time_window_end
    )


if __name__ == "__main__":
    main(*parse_args())
