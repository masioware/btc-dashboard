# app/components/tabs.py
from __future__ import annotations

import pandas as pd
import streamlit as st
import altair as alt


def render_price_tab(price_df: pd.DataFrame, price_days: int) -> None:
    """Renderiza a aba de Preço (gráfico + tabela)."""
    st.subheader("BTC/USDT – preço diário (Binance)")

    if price_df is None or price_df.empty:
        st.info("Sem dados de preço diário para exibir o gráfico.")
        return

    chart_price_df = price_df[["open_time", "close"]].set_index("open_time")

    col_price_left, col_price_right = st.columns((2, 1))

    # ---- Gráfico ----
    with col_price_left:
        st.line_chart(chart_price_df, height=320)
        st.caption("Fonte: Binance /api/v3/klines (interval=1d)")

        price_min = chart_price_df["close"].min()
        price_max = chart_price_df["close"].max()
        price_mean = chart_price_df["close"].mean()

        st.markdown(
            f"""
**Resumo do período (últimos {price_days} dias):**
- Preço mínimo: `{price_min:,.2f} USDT`
- Preço máximo: `{price_max:,.2f} USDT`
- Preço médio: `{price_mean:,.2f} USDT`
"""
        )

    # ---- Tabela com scroll ----
    with col_price_right:
        table_df = price_df.copy()
        table_df = table_df.sort_values("open_time", ascending=False)
        table_df["Data"] = table_df["open_time"].dt.strftime("%d-%m-%Y")
        table_df = table_df[
            ["Data", "open", "high", "low", "close", "volume"]
        ].rename(
            columns={
                "open": "Abertura",
                "high": "Máxima",
                "low": "Mínima",
                "close": "Fechamento",
                "volume": "Volume (BTC)",
            }
        )

        st.dataframe(
            table_df,
            height=320,
            width="stretch",
        )
def render_sentiment_tab(
    fng_df: pd.DataFrame,
    days: int,
    current_fng: int | None,
    current_fng_class: str | None,
) -> None:
    """Renderiza a aba de Sentimento (Fear & Greed) + overlay com preço."""
    st.subheader("Crypto Fear & Greed Index – histórico")

    # Chip de humor atual
    if current_fng is not None and current_fng_class is not None:
        mood_emoji = "🟢"
        if current_fng < 25:
            mood_emoji = "🔴"
        elif current_fng < 50:
            mood_emoji = "🟡"
        elif current_fng > 75:
            mood_emoji = "🟣"

        st.markdown(
            f"**Humor do mercado agora:** {mood_emoji} `{current_fng}` – {current_fng_class}"
        )

    col_left, col_right = st.columns((2, 1))

    # ---- Gráfico simples de FNG + resumo ----
    with col_left:
        if not fng_df.empty:
            chart_df = fng_df[["date", "value"]].set_index("date")
            st.line_chart(chart_df, height=260)
            st.caption("Fonte: https://api.alternative.me/fng/")

            fng_min = fng_df["value"].min()
            fng_max = fng_df["value"].max()
            fng_mean = fng_df["value"].mean()

            st.markdown(
                f"""
**Resumo do período ({days} dias):**
- Mínimo: `{fng_min}`
- Máximo: `{fng_max}`
- Média: `{fng_mean:.1f}`
""")
        else:
            st.info("Sem dados de Fear & Greed para exibir o gráfico.")

    with col_right:

        if not fng_df.empty:
            show_df = fng_df[["date", "value", "value_classification"]].copy()
            show_df = show_df.sort_values("date", ascending=False).head(20)
            show_df["date"] = show_df["date"].dt.strftime("%d-%m-%Y")
            show_df = show_df.rename(
                columns={
                    "date": "Data",
                    "value": "Índice",
                    "value_classification": "Classificação",
                }
            )

            st.dataframe(
                show_df,
                height=260,
                width="stretch",
            )
        else:
            st.write("Sem dados para mostrar.")

    st.markdown("---")

def render_price_x_sentiment(
    fng_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> None:

    # -----------------------
    # Overlay Preço × FNG
    # -----------------------

    st.markdown("### 📊 Overlay Preço × Fear & Greed")

    if price_df is not None and not price_df.empty and fng_df is not None and not fng_df.empty:
        # Normaliza datas para juntar por dia
        price_daily = price_df[["open_time", "close"]].copy()
        price_daily["date"] = price_daily["open_time"].dt.normalize()

        fng_daily = fng_df[["date", "value"]].copy()
        fng_daily["date"] = fng_daily["date"].dt.normalize()

        merged = pd.merge(price_daily, fng_daily, on="date", how="inner")
        merged = merged.sort_values("date").rename(
            columns={
                "close": "Preço (BTCUSDT)",
                "value": "Fear & Greed",
            }
        )

        # Gráfico com dois eixos Y (preço e índice)
        base = alt.Chart(merged).encode(
            x=alt.X("date:T", title="Data"),
        )

        price_line = base.mark_line().encode(
            y=alt.Y(
                "Preço (BTCUSDT):Q",
                axis=alt.Axis(title="Preço BTC/USDT"),
            ),
            color=alt.value("#60a5fa"),  # azul
        )

        fng_line = base.mark_line(strokeDash=[4, 2]).encode(
            y=alt.Y(
                "Fear & Greed:Q",
                axis=alt.Axis(title="Fear & Greed", orient="right"),
            ),
            color=alt.value("#f59e0b"),  # laranja
        )

        chart = (
            alt.layer(price_line, fng_line)
            .resolve_scale(y="independent")
            .properties(height=320)
        )

        st.altair_chart(chart, width="stretch")

        st.caption(
            "Linha azul: preço BTC/USDT (Binance) · Linha tracejada laranja: índice Crypto Fear & Greed"
        )
    else:
        st.info("Não há dados suficientes para montar o overlay Preço × FNG.")


def render_debug_tab(ticker: dict, fng_df: pd.DataFrame) -> None:
    """Renderiza a aba de debug com JSON bruto."""
    st.subheader("Debug / JSON bruto")

    with st.expander("Binance /api/v3/ticker/24hr (BTCUSDT)"):
        st.json(ticker)

    if not fng_df.empty:
        with st.expander("Alternative.me /fng (últimas linhas)"):
            st.write(fng_df.tail(10))
