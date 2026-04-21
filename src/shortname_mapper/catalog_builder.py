import requests
from json import dumps, loads
import yaml
from pathlib import Path

def load_portals(yaml_path: str | Path) -> list[dict]:
    yaml_path = Path(yaml_path)
    with yaml_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("portals", [])

for portal in load_portals("src/shortname_mapper/chords_portals.yaml"):
    if not portal.get("enabled", True):
        continue

    name = portal["name"]
    base_url = portal["url"]
    api = portal["api"]
    api_base = f"{base_url}/api/v1/data"

    params = {
        "email": 'rzieber@ucar.edu',
        "api_key": api
    }

    print(name, '\t|\t', api_base)
    
    response = requests.get(url=api_base, params=params, timeout=30)
    print("Status:", response.status_code)
    print("First 200 chars:", response.text[:200])
    
    all_fields = loads(dumps(response.json()))
    print(f"{name}: got {len(all_fields.get('features', []))} features")
