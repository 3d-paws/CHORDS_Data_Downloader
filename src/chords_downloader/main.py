"""
CHORDS Data Downloader 
Authored by Rebecca Zieber
"""

from pathlib import Path
from chords_downloader import chords_local_download, chords_dataframes


PORTAL_URL = r"https://3d.chordsrt.com"
PORTAL_NAME = "3D-PAWS"
DATA_PATH = Path("/Users/rzieber/Downloads") 
INSTRUMENT_IDS = [
    1,2,3
]
USER_EMAIL = 'rzieber@ucar.edu'
API_KEY = 'pc7HQpcDipWsetaxmJ5t' 
START = '2025-02-03 00:00:00' 
END = '2025-02-03 22:59:59'

def main():
    # To download csv's locally to your machine (most common):
    chords_local_download.main(PORTAL_URL, PORTAL_NAME, DATA_PATH, INSTRUMENT_IDS,
                               USER_EMAIL, API_KEY, START, END)
    # To export pandas dataframes
    # chords_dataframes.main(PORTAL_URL, PORTAL_NAME, INSTRUMENT_IDS, 
    #                        USER_EMAIL, API_KEY, START, END)


if __name__ == '__main__':
    main()
    