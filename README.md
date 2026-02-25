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
    - `INSTRUMENT_IDS` (unique ID's from CHORDS portal)
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
pip install requests numpy pandas
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
- `3D-PAWS`            | `https:\\3d.chordsrt.com`
- `Barbados`           | `https:\\3d-barbados.chordsrt.com` 
- `Trinidad`           | `https:\\3d-trinidad.chordsrt.com`
- `Dominican-Republic` | `https:\\3d-dr.icdp.ucar.edu`
- `Calibration`        | `https:\\3d-calibration.chordsrt.com`  
- `FEWSNET`            | `https:\\3d-fewsnet.icdp.ucar.edu`
- `Kenya`              | `https:\\3d-kenya.chordsrt.com`  
- `Zimbabwe`           | `https:\\3d-zimbabwe.icdp.ucar.edu`
- `Argentina`          | `https:\\3d-argentina.icdp.ucar.edu` 
- `IITM`               | `https:\\3d-iitm.icdp.ucar.edu`
- `Fiji`               | `http:\\3d-fiji.icdp.ucar.edu`
- `Bahamas`            | `http:\\3d-bahamas.icdp.ucar.edu`
- `Malawi`             | `http:\\3d-malawi.icdp.ucar.edu`
- `Jamaica`            | `http:\\3d-jamaica.icdp.ucar.edu`
- `Ethiopia`           | `http:\\3d-ethiopia.icdp.ucar.edu`
- `Somalia`            | `http:\\3d-somalia.icdp.ucar.edu`

## Troubleshooting
See Windows-specific setup tips here:<br>
https://drive.google.com/file/d/1TsTg8LvilrUqBZpj7nq3RsUV5CsSwjB_/view?usp=drive_link
