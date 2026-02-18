"""
CHORDS Data Downloader 
Authored by Rebecca Zieber
"""

from pathlib import Path
from chords_downloader import chords_local_download, chords_dataframes

PORTAL_URL = r"https://3d-kenya.chordsrt.com/"
PORTAL_NAME = "Kenya"
DATA_PATH = Path("/Users/rzieber/Downloads") 
INSTRUMENT_IDS = list(range(45))
USER_EMAIL = 'rzieber@ucar.edu'
API_KEY = 'GbwLdKSxv8yL4Jqk4T7b' 
START = '2024-02-18 00:00:00' 
END = '2026-02-18 23:59:59'

def main():
    # To download csv's locally to your machine (most common):
    chords_local_download.main(PORTAL_URL, PORTAL_NAME, DATA_PATH, INSTRUMENT_IDS,
                               USER_EMAIL, API_KEY, START, END)
    # To export pandas dataframes
    # chords_dataframes.main(PORTAL_URL, PORTAL_NAME, INSTRUMENT_IDS, 
    #                        USER_EMAIL, API_KEY, START, END)


if __name__ == '__main__':
    main()
    