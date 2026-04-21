from services.storage_v2 import load_day, DATA_DIR


def get_available_days(n: int = 30) -> list[str]:
    """
    Returns YYYY-MM-DD strings for existing day files in DataTest/,
    sorted descending (most recent first). Returns at most n entries.
    """
    files = sorted(DATA_DIR.glob("????-??-??.json"), reverse=True)
    return [f.stem for f in files[:n]]


def load_recent_days(n: int = 7) -> list[dict]:
    """
    Returns list of day dicts for the n most recent days with actual data.
    Days without files are excluded.
    """
    return [load_day(fecha)[0] for fecha in get_available_days(n=n)]
