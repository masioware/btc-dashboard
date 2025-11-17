import time
from datetime import datetime

import pandas as pd
import requests
from streamlit import cache_data

FNG_URL = "https://api.alternative.me/fng/"


@cache_data(ttl=60)
def get_fng(limit: int = 30):
    """
    Fetch Fear & Greed Index data.
    limit = number of days (max 2000) – newest first.
    """
    params = {
        "limit": limit,
        "format": "json",
        "date_format": "world",  # e.g. 17-11-2025
    }

    resp = requests.get(FNG_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    # Convert to DataFrame (newest first → we invert for chart)
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    # Columns: value (string), value_classification, timestamp, time_until_update
    df["value"] = df["value"].astype(int)

    # API returns timestamp as unix or date string depending on format, but we have a "timestamp" (string).
    # Let's try to parse it smartly:
    def parse_date(x):
        # try unix int
        try:
            # some responses come as unix string
            return datetime.fromtimestamp(int(x))
        except Exception:
            # fallback: try common string formats
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(x, fmt)
                except Exception:
                    continue
        return pd.NaT

    df["date"] = df["timestamp"].apply(parse_date)
    df = df.sort_values("date")
    df = df.reset_index(drop=True)
    return df
