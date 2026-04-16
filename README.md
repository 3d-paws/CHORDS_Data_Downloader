# CHORDS Data Downloader
Automated REST API client for downloading CHORDS meteorological data. Supports CSV export, dataframe export, column filtering, time windows, and all major CHORDS portals.<br><br>
Authored by Rebecca Zieber.<br><br>
NOTE: Columns are named by their shortname. To see the full sensor name, reference the associated CHORDS website.

## Prerequisites
- Python **3.7+** 
- CHORDS account with **API key** and download privileges

## Quick Start
1. **Clone/download** this repo<br>
   ```bash
   git clone https://github.com/rzieber/CHORDS_Data_Downloader.git
   ```
2. **Set up virtual environment**<br>
   ```bash
   pip install python3-venv
   python3 -m venv .venv
   source .venv/bin.activate
   ```
3. **Install dependencies**<br>
   ```bash
   pip install -r requirements.txt
   ```
4. **Copy and configure .env**<br>
   ```bash
   cp ./src/chords_downloader/resources/dev/.env_[EXAMPLE] .src/chords_downloader/.env
   ```
   See `/src/chords_downloader/resources/dev` for the template: `.env_[EXAMPLE]`.
5. **Download data**<br>
   ```bash
   chords-download
   ```
   CSV's save to your `DATA_PATH` automatically.

## Configuration
### chords_downloader.py
Create `.env` from `.env_[EXAMPLE]` and fill the required fields:
   - `PORTAL_URL` - the URL associated with your CHORDS portal (see Available Portals below)
   - `PORTAL_NAME` - the name associated with your CHORDS portal (see Available Portals below)
   - `DATA_PATH` - the path where CSV's are to be exported to your local machine
   - `INSTRUMENT_IDS` - the list of instrument id's (see available instruments on your CHORDS portal) -> comma separated integers
   - `USER_EMAIL` - the email associated with your CHORDS account
   - `API_KEY` - the API associated with your CHORDS account
   - `START` - the start of your desired data period
   - `END` -  the end of your desired data period
   - `OUTPUT` - the type of output you desire; valid selections are: csv, df, or both
### chords_dataframes.py
Create `.env` from `.env_[EXAMPLE]` and fill the required fields:
   - `PORTAL_URL` - the URL associated with your CHORDS portal (see Available Portals below)
   - `PORTAL_NAME` - the name associated with your CHORDS portal (see Available Portals below)
   - `INSTRUMENT_IDS` - the list of instrument id's (see available instruments on your CHORDS portal)
   - `USER_EMAIL` - the email associated with your CHORDS account
   - `API_KEY` - the API associated with your CHORDS account
   - `START` - the start of your desired data period
   - `END` -  the end of your desired data period

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

## Platform Setup
### Raspberry Pi 3B/4/5
Perform the following from the project root.<br>
Update the system. Install pip and Python virtual environment.
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```
Enable pinwheels for faster dependency installation.
```bash
echo "[global]" | sudo tee /etc/pip.conf
echo "extra-index-url=https://www.piwheels.org/simple" | sudo tee -a /etc/pip.conf
```
Create the virtual environment and activate it.
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Finally, install library dependencies and configure script for execution via the command line.
```bash
pip install -r requirements.txt --prefer-binary
pip install --update pip setuptools wheel
pip install -e .
```
### Windows
One-time (run as admin).
```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then set up the virtual environment.
```bash
python3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Install the library dependencies.
```bash
pip install -r requirements.txt
```
### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dependencies
For compatibility with Python 3.7
```
numpy>=1.21.0,<1.25.0
pandas==1.3.5
pytest==7.4.3
python-dotenv==0.21.1
requests==2.31.0
```

## Troubleshooting
See Windows-specific setup tips here:<br>
https://drive.google.com/file/d/1TsTg8LvilrUqBZpj7nq3RsUV5CsSwjB_/view?usp=drive_link

## For Contributors
Run the following to test changes before submitting a pull request:
```bash
pytest -v
```
You must include unit tests for your recommended changes in order for suggestions to be incorporated.
