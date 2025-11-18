# app/dashboard.py
from __future__ import annotations

import time

import streamlit as st
from api import alternative_me, binance, coin_gecko
from components.metrics import inject_metric_css, render_metric_card
from components.tabs import (
    render_price_tab,
    render_sentiment_tab,
    render_price_x_sentiment
)
from utils import formaters


# -----------------------
# Config da página
# -----------------------
st.set_page_config(
    page_title="BTC Dashboard",
    page_icon="🟠",
    layout="wide",
)

# Injeta CSS global dos cards
inject_metric_css()


# -----------------------
# Funções com cache
# -----------------------
@st.cache_data(ttl=300)
def load_fng(days: int):
    """Carrega Fear & Greed da Alternative.me."""
    return alternative_me.get_fng(limit=days)


@st.cache_data(ttl=60)
def load_ticker():
    try:
        return binance.get_ticker_24h("BTCUSDT")
    except Exception:
        return coin_gecko.get_ticker_24h("BTCUSDT")


@st.cache_data(ttl=300)
def load_price_klines(days: int):
    try:
        return binance.get_daily_klines(symbol="BTCUSDT", limit=days)
    except Exception:
        return coin_gecko.get_daily_klines(symbol="BTCUSDT", limit=days)

# -----------------------
# UI – Sidebar
# -----------------------
st.title("🟠 BTC Dashboard")

with st.sidebar:
    st.header("⚙️ Configurações")

    price_days = st.slider(
        "Dias de histórico de preço",
        min_value=30,
        max_value=365,
        value=365,
        step=1,
    )

    days = st.slider(
        "Dias de histórico do Fear & Greed",
        min_value=7,
        max_value=365,
        value=365,
        step=1,
    )

    auto_refresh = st.checkbox("Atualização automática (a cada 60s)", value=False)
    if auto_refresh:
        st.caption("A página será recarregada automaticamente a cada ~60 segundos.")
        time.sleep(60)
        st.rerun()

    st.markdown("---")
    st.markdown("**APIs usadas:**")
    st.code(
        "Binance: /api/v3/ticker/24hr\n"
        "Binance: /api/v3/klines (interval=1d)\n"
        "CoinGecko: /api/v3/coins/bitcoin/simple/price\n"
        "CoinGecko: /api/v3/coins/bitcoin/market_chart\n"
        "Alternative.me: /fng/"
    )

# -----------------------
# Fetch data
# -----------------------
col_status = st.empty()
with col_status.container():
    with st.spinner("Buscando dados das APIs..."):
        try:
            ticker = load_ticker()
            fng_df = load_fng(days)
            price_df = load_price_klines(price_days)
            ok = True
        except Exception as e:
            ok = False
            st.error(f"Erro ao buscar dados: {e}")

if not ok:
    st.stop()

# -----------------------
# Parse Binance data (ticker)
# -----------------------
last_price = float(ticker["lastPrice"])
price_open = float(ticker["openPrice"])
price_high = float(ticker["highPrice"])
price_low = float(ticker["lowPrice"])
price_change_percent = float(ticker["priceChangePercent"])
volume = float(ticker["volume"])

price_change_str = formaters.format_pct(price_change_percent)

# cor dinâmica para o card de preço
if price_change_percent > 1:
    price_color = "green"
elif price_change_percent < -1:
    price_color = "red"
else:
    price_color = "neutral"

# -----------------------
# Parse FNG data
# -----------------------
if fng_df.empty:
    st.warning("Não foi possível carregar dados do Fear & Greed.")
    current_fng = None
    current_fng_class = None
    current_fng_date = None
    fng_color = "neutral"
else:
    current_fng = int(fng_df.iloc[-1]["value"])
    current_fng_class = fng_df.iloc[-1]["value_classification"]
    current_fng_date = fng_df.iloc[-1]["date"]

    # cor dinâmica para o card de sentimento
    if current_fng < 25:
        fng_color = "red"  # Medo / Medo extremo
    elif current_fng < 50:
        fng_color = "yellow"  # Zona intermediária
    elif current_fng < 75:
        fng_color = "green"  # Ganância
    else:
        fng_color = "purple"  # Ganância extrema

# -----------------------
# Header + cards
# -----------------------
st.subheader("📌 Visão geral")

col_header_left, col_header_right = st.columns([3, 1])


# Cards principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric_card(
        "BTC / USDT (agora)",
        f"{last_price:,.2f} USDT",
        subtext=f"Variação 24h: {price_change_str}",
        color=price_color,
    )

with col2:
    render_metric_card(
        "Faixa 24h",
        f"{price_low:,.2f} – {price_high:,.2f} USDT",
        subtext="Mínimo / Máximo",
        color="neutral",
    )

with col3:
    render_metric_card(
        "Volume 24h (BTC)",
        f"{volume:,.2f}",
        subtext="Volume negociado nas últimas 24h",
        color="neutral",
    )

with col4:
    if current_fng is not None:
        render_metric_card(
            "Fear & Greed (agora)",
            f"{current_fng} – {current_fng_class}",
            subtext=f"Última atualização do índice: {current_fng_date}",
            color=fng_color,
        )
    else:
        render_metric_card(
            "Fear & Greed (agora)",
            "Indisponível",
            subtext="Não foi possível carregar o índice.",
            color="neutral",
        )

# -----------------------
# Abas
# -----------------------
tab_preco, tab_sentimento, tab_preco_x_sentimento = st.tabs(
    ["📈 Preço", "🧠 Sentimento (Fear & Greed)", "🤑 Preço x Sentimento"]
)

with tab_preco:
    render_price_tab(price_df, price_days)

with tab_sentimento:
    render_sentiment_tab(
        fng_df=fng_df,
        days=days,
        current_fng=current_fng,
        current_fng_class=current_fng_class,
    )

with tab_preco_x_sentimento:
    render_price_x_sentiment(
        fng_df=fng_df,
        price_df=price_df
    )
