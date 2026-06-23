"""
CHORDS Data Downloader
Authored by Rebecca Zieber
"""
import ast
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from chords_downloader import chords_downloader


def _parse_instrument_ids(s: str) -> list:
    """Parse INSTRUMENT_IDS from env. Accepts a list literal or range() expression.

    Examples:
        "[1,2,3,4,5]"      -> [1, 2, 3, 4, 5]
        "range(1, 6)"      -> [1, 2, 3, 4, 5]
        "range(1, 20, 2)"  -> [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    """
    s = s.strip()
    range_match = re.fullmatch(r'range\(\s*(\d+)\s*(?:,\s*(\d+)\s*(?:,\s*(\d+)\s*)?)?\)', s)
    if range_match:
        args = [int(x) for x in range_match.groups() if x is not None]
        return list(range(*args))
    try:
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return result
    except (ValueError, SyntaxError):
        pass
    return []

# Search for 'env' (non-hidden) walking up from cwd
_cwd = Path.cwd()
for _parent in [_cwd, *_cwd.parents]:
    _candidate = _parent / "env"
    if _candidate.is_file():
        load_dotenv(dotenv_path=_candidate)
        break
else:
    load_dotenv()  # fallback: standard .env search

# Required user parameters -----------------------------------------------
portal_url         = os.getenv("PORTAL_URL")
portal_name        = os.getenv("PORTAL_NAME")

data_path_raw      = os.getenv("DATA_PATH")
if data_path_raw is None:
    raise ValueError("DATA_PATH missing from env")
data_path = Path(data_path_raw) 

instrument_ids = _parse_instrument_ids(os.getenv("INSTRUMENT_IDS", "[]"))

user_email         = os.getenv("USER_EMAIL")
api_key            = os.getenv("API_KEY") 
start              = os.getenv("START") 
end                = os.getenv("END")
output             = os.getenv("OUTPUT", "csv")

# Optional user parameters -----------------------------------------------
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
    raise ValueError(f"Missing required environment variables: {missing}.\nCheck your env file.")

def main():
    chords_downloader.main(portal_url, portal_name, data_path, instrument_ids, user_email, api_key, start, end, 
                           output=output, columns_desired=columns_desired, time_window_start=time_window_start, 
                           time_window_end=time_window_end)


cli = main

if __name__ == '__main__':
    main()
    