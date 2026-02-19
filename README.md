# CHORDS Data Downloader
This Python script automates downloading data from CHORDS portals via API. Supports CSV export `chords_local_download.py` or Pandas DataFrames `chords_dataframes.py`.<br>
NOTE: Columns are named by their shortname. To see the full sensor name, reference 
the associated CHORDS website.

## Prerequisites
- Python **3.8+** 
- CHORDS account with **API key** and download privileges

## Quick Start
1. **Clone/download** this repo
2. **Open terminal** in project root
3. **Create & activate virtual environment**<br>
   PC 
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   macOS/Linux
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. **Install dependencies**<br>
   ```pip install -r requirements.txt```
5. **Edit `src/chords_downloader/main.py` with your**
    - `PORTAL_NAME` (see list of available portals below)
    - `INSTRUMENT_IDS` (list from CHORDS portal)
    - `USER_EMAIL` and `API_KEY`
    - `START`/`END` timestamps
6. **Run**
   ```python src/chords_downloader/main.py```

## Platform-Specific Setup
#### Windows
For Windows, set the execution policy by running the following ONCE as administrator:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Create and activate the virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Install dependencies:
```powershell
pip install -r requirements.txt
```
Verify installation:
```powershell
requests --version
numpy --version
pandas --version
```
#### MacOS/Linux
For macOS/Linux, set up a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Verify installation:
```bash
requests --version
numpy --version
pandas --version
```

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
- `Jamaica`
- `Somalia`
