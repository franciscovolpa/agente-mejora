import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent   # AgenteMejora/services/
DATA_DIR = BASE_DIR.parent / "DataTest"      # AgenteMejora/DataTest/

DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def load_day(fecha):
    path = DATA_DIR / f"{fecha}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), path
    data = {
        "fecha": fecha,
        "registros": [],
        "notes": "",
        "metrics": {
            "energia": None,
            "breath": None,
            "hinchado": None,
            "bano_frio": None,
        },
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return data, path


def save_day(data, path):
    data["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
