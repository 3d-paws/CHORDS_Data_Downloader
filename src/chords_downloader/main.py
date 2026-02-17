"""
CHORDS Data Downloader 
Authored by Rebecca Zieber
"""

from pathlib import Path
from chords_downloader import chords_local_download, chords_dataframes

PORTAL_URL = r"https://chords.url.com/"
PORTAL_NAME = "Portal Name"
DATA_PATH = Path("C://path//to//local//storage//") 
INSTRUMENT_IDS = [
    1,2,3
]
USER_EMAIL = 'your@email.com'
API_KEY = 'your-api-key' 
START = 'YYYY-MM-DD HH:MM:SS' 
END = 'YYYY-MM-DD HH:MM:SS'

def main():
    # To download csv's locally to your machine (most common):
    chords_local_download.main(PORTAL_URL, PORTAL_NAME, DATA_PATH, INSTRUMENT_IDS,
                               USER_EMAIL, API_KEY, START, END)
    # To export pandas dataframes
    # chords_dataframes.main(PORTAL_URL, PORTAL_NAME, INSTRUMENT_IDS, 
    #                        USER_EMAIL, API_KEY, START, END)


if __name__ == '__main__':
    main()
    