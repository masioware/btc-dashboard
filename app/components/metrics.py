# app/components/metrics.py
from __future__ import annotations

import streamlit as st


def inject_metric_css() -> None:
    """Injeta CSS global para os cards de métricas."""
    st.markdown(
        """
<style>
.metric-card {
    border-radius: 0.9rem;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.75rem;
    color: #f9fafb;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.metric-card .metric-title {
    font-size: 0.85rem;
    opacity: 0.9;
}
.metric-card .metric-value {
    font-size: 1.35rem;
    font-weight: 700;
    margin-top: 0.25rem;
}
.metric-card .metric-sub {
    font-size: 0.78rem;
    opacity: 0.9;
    margin-top: 0.45rem;
}

/* Cores de fundo */
.metric-bg-neutral { background: #111827; }
.metric-bg-green   { background: #166534; }
.metric-bg-red     { background: #ff4b4b; }
.metric-bg-yellow  { background: #92400e; }
.metric-bg-purple  { background: #6b21a8; }
</style>
""",
        unsafe_allow_html=True,
    )


def render_metric_card(
    title: str,
    value: str,
    subtext: str | None = None,
    color: str = "neutral",
) -> None:
    """
    Renderiza um card de métrica com cor dinâmica.

    color: "neutral", "green", "red", "yellow", "purple"
    """
    color_class = {
        "neutral": "metric-bg-neutral",
        "green": "metric-bg-green",
        "red": "metric-bg-red",
        "yellow": "metric-bg-yellow",
        "purple": "metric-bg-purple",
    }.get(color, "metric-bg-neutral")

    sub_html = f'<div class="metric-sub">{subtext}</div>' if subtext else ""
    st.markdown(
        f"""
<div class="metric-card {color_class}">
  <div class="metric-title">{title}</div>
  <div class="metric-value">{value}</div>
  {sub_html}
</div>
""",
        unsafe_allow_html=True,
    )
