"""
CHORDS Data Downloader 
Authored by Rebecca Zieber
"""

from pathlib import Path
from chords_downloader import chords_local_download, chords_dataframes

PORTAL_URL = r"https://3d-fewsnet.icdp.ucar.edu/"
PORTAL_NAME = "FEWSNET"
DATA_PATH = Path("/Users/rzieber/Downloads") 
INSTRUMENT_IDS = [
    1,2,3
]
USER_EMAIL = 'rzieber@ucar.edu'
API_KEY = 'QSy8irrRowbi6ys-5PHe' 
START = '2026-01-07 00:00:00' 
END = '2026-01-14 23:59:59'

def main():
    # To download csv's locally to your machine (most common):
    chords_local_download.main(PORTAL_URL, PORTAL_NAME, DATA_PATH, INSTRUMENT_IDS,
                               USER_EMAIL, API_KEY, START, END)
    # To export pandas dataframes
    # chords_dataframes.main(PORTAL_URL, PORTAL_NAME, INSTRUMENT_IDS, 
    #                        USER_EMAIL, API_KEY, START, END)


if __name__ == '__main__':
    main()
    