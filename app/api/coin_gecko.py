# app/api/coin_gecko.py
from __future__ import annotations

import requests
import pandas as pd

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def _map_symbol(symbol: str) -> tuple[str, str]:
    """
    Mapeia o símbolo no formato exchange (ex: BTCUSDT)
    para o formato CoinGecko (id, vs_currency).

    Por enquanto, só tratamos BTCUSDT -> (bitcoin, usd).
    Você pode expandir depois, se quiser.
    """
    symbol = symbol.upper()

    if symbol == "BTCUSDT" or symbol == "BTCUSD":
        return "bitcoin", "usd"

    # fallback genérico (pode ajustar mapeamento aqui)
    raise ValueError(f"Símbolo não suportado no CoinGecko fallback: {symbol}")


def get_ticker_24h(symbol: str = "BTCUSDT") -> dict:
    """
    Fallback para o ticker 24h usando CoinGecko.

    Retorna um dict no formato similar ao da Binance.
    """
    coin_id, vs_currency = _map_symbol(symbol)

    url = f"{COINGECKO_BASE}/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": vs_currency,
        "include_24hr_change": "true",
        "include_24hr_vol": "true",
        "include_24hr_high_low": "true",
    }
    r = requests.get(url, params=params, timeout=10)

    r.raise_for_status()
    data = r.json()

    if coin_id not in data:
        raise RuntimeError(f"Resposta inesperada do CoinGecko: {data}")

    info = data[coin_id]

    last_price = float(info[vs_currency])
    change_pct = float(info.get(f"{vs_currency}_24h_change", 0.0))
    high_24h = float(info.get(f"{vs_currency}_24h_high", last_price))
    low_24h = float(info.get(f"{vs_currency}_24h_low", last_price))
    vol_24h = float(info.get(f"{vs_currency}_24h_vol", 0.0))

    # monta objeto semelhante ao da Binance
    return {
        "lastPrice": last_price,
        "priceChangePercent": change_pct,
        "highPrice": high_24h,
        "lowPrice": low_24h,
        "volume": vol_24h,

        # Adicionado para compatibilidade total com sua UI
        "openPrice": last_price,
    }

def get_daily_klines(
    symbol: str = "BTCUSDT",
    interval: str = "1d",
    limit: int = 365,
    start_time: int | None = None,
    end_time: int | None = None,
) -> pd.DataFrame:
    """
    Fallback para candles diários usando CoinGecko.

    CoinGecko não retorna OHLC completo nesse endpoint, apenas preços.
    Aqui usamos o endpoint /market_chart com 'interval=daily' e
    montamos um DataFrame compatível com o da Binance:

    colunas: open_time, open, high, low, close, volume

    OBS:
    - open/high/low são aproximados (usamos o close diário)
    - volume vem de total_volumes (se disponível)
    - start_time e end_time são ignorados por enquanto
    """
    if interval != "1d":
        raise ValueError("CoinGecko fallback atualmente só suporta interval='1d'")

    coin_id, vs_currency = _map_symbol(symbol)

    # CoinGecko usa 'days' em vez de start/end; limit ~ número de dias
    days = min(limit, 365)

    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": "daily",
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])

    if not prices:
        return pd.DataFrame(
            columns=["open_time", "open", "high", "low", "close", "volume"]
        )

    # Monta DF de preços (timestamp, close)
    df_price = pd.DataFrame(prices, columns=["ts", "close"])
    df_price["open_time"] = pd.to_datetime(df_price["ts"], unit="ms")
    df_price["close"] = df_price["close"].astype(float)

    # CoinGecko não fornece OHLC nesse endpoint => aproximamos
    df_price["open"] = df_price["close"]
    df_price["high"] = df_price["close"]
    df_price["low"] = df_price["close"]

    # Volumes, se disponíveis
    if volumes and len(volumes) == len(df_price):
        df_vol = pd.DataFrame(volumes, columns=["ts_vol", "vol"])
        df_vol["vol"] = df_vol["vol"].astype(float)
        df_price["volume"] = df_vol["vol"].values
    else:
        df_price["volume"] = 0.0

    return df_price[["open_time", "open", "high", "low", "close", "volume"]]
