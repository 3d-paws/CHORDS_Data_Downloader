"""
CHORDS Data Downloader 
Authored by Rebecca Zieber
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from chords_downloader import chords_local_download, chords_dataframes

load_dotenv()

# Required user parameters -----------------------------------------------
portal_url         = os.getenv("PORTAL_URL")
portal_name        = os.getenv("PORTAL_NAME")

data_path_raw      = os.getenv("DATA_PATH")
if data_path_raw is None:
    raise ValueError("DATA_PATH missing from .env")
data_path = Path(data_path_raw) 

instrument_ids_str = os.getenv("INSTRUMENT_IDS", "[]")
try:
    instrument_ids = eval(instrument_ids_str)
    assert isinstance(instrument_ids, list)
except:
    instrument_ids = []

user_email         = os.getenv("USER_EMAIL")
api_key            = os.getenv("API_KEY") 
start              = os.getenv("START") 
end                = os.getenv("END")

# Optional user parameters -----------------------------------------------
fill_empty         = os.getenv("FILL_EMPTY", "")
include_test       = os.getenv("INCLUDE_TEST", "False").lower() == "true"

columns_desired_str = os.getenv("COLUMNS_DESIRED", "[]")
if columns_desired_str:
    columns_desired = [col.strip() for col in columns_desired_str.split(',')]
else:
    columns_desired = []

time_window_start  = os.getenv("TIME_WINDOW_START", "")
time_window_end    = os.getenv("TIME_WINDOW_END", "")


required = [portal_url, portal_name, data_path, instrument_ids, user_email, api_key, start, end]
if not all(required):
    missing = [r for r in required if not r]
    raise ValueError(f"Missing required environment variables: {missing}.\nCheck your .env file.")

def main():
    # To download csv's locally to your machine (most common):
    chords_local_download.main(portal_url, portal_name, data_path, instrument_ids,
                                                    user_email, api_key, start, end)
    # To export pandas dataframes
    # chords_dataframes.main(PORTAL_URL, PORTAL_NAME, INSTRUMENT_IDS, 
    #                        USER_EMAIL, API_KEY, START, END)


if __name__ == '__main__':
    main()
    