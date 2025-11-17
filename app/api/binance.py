# app/api/binance.py
import requests
import pandas as pd

BASE_URL = "https://api.binance.com"

def get_ticker_24h(symbol: str = "BTCUSDT") -> dict:
    """24h ticker (preço atual, variação, volume etc)."""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    params = {"symbol": symbol}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def get_daily_klines(
    symbol: str = "BTCUSDT",
    interval: str = "1d",
    limit: int = 365,
    start_time: int | None = None,
    end_time: int | None = None,
) -> pd.DataFrame:
    """
    Candles da Binance (OHLCV). Intervalo padrão = 1 dia.
    Retorna um DataFrame com open_time, open, high, low, close, volume.
    """
    url = f"{BASE_URL}/api/v3/klines"
    params: dict[str, object] = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if start_time is not None:
        params["startTime"] = start_time
    if end_time is not None:
        params["endTime"] = end_time

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(
        data,
        columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades",
            "taker_buy_volume", "taker_buy_quote", "ignore"
        ],
    )

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    return df[["open_time", "open", "high", "low", "close", "volume"]]
