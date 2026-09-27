"""A light SaaS-style visual layer on top of default Streamlit widgets.

Streamlit's default look (plain st.metric, flat st.subheader, unstyled
buttons) reads as a script, not a product. This module injects one CSS
block plus a few small HTML components (hero header, stat cards, section
headers) so the app reads like a dashboard instead. Colors are pulled from
the same validated, colorblind-safe palette used in charts.py.
"""
from typing import List, Optional, TypedDict

import streamlit as st

from financial_coach.charts import CATEGORICAL, CRITICAL, GOOD

PRIMARY = CATEGORICAL[0]
ACCENT = CATEGORICAL[2]
INK = "#0b0b0b"
MUTED = "#6b6a66"
SURFACE = "#ffffff"
PAGE_BG = "#f7f8fa"
BORDER = "rgba(11,11,11,0.08)"

_TONE_COLORS = {"neutral": PRIMARY, "good": GOOD, "critical": CRITICAL}


class StatCard(TypedDict, total=False):
    label: str
    value: str
    icon: str
    tone: str  # "neutral" | "good" | "critical"
    caption: str


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background: {PAGE_BG};
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        section[data-testid="stSidebar"] {{
            background: {SURFACE};
            border-right: 1px solid {BORDER};
        }}

        /* Buttons */
        .stButton > button {{
            border-radius: 10px;
            border: none;
            background: linear-gradient(135deg, {PRIMARY} 0%, #1c5cab 100%);
            color: white;
            font-weight: 600;
            padding: 0.6rem 1.4rem;
            box-shadow: 0 2px 8px rgba(42,120,214,0.28);
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 14px rgba(42,120,214,0.38);
            color: white;
        }}

        /* Tabs -> pill style */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid {BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            color: {MUTED};
        }}
        .stTabs [aria-selected="true"] {{
            color: {PRIMARY} !important;
            background: rgba(42,120,214,0.08);
        }}

        /* Native metric styling */
        div[data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 14px 18px;
            box-shadow: 0 1px 3px rgba(11,11,11,0.04);
        }}

        /* Bordered containers used as cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 16px !important;
        }}

        input, textarea, .stSelectbox div[data-baseweb="select"] {{
            border-radius: 8px !important;
        }}

        .fc-hero {{
            background: linear-gradient(135deg, #1c5cab 0%, {PRIMARY} 55%, {ACCENT} 130%);
            border-radius: 20px;
            padding: 2.2rem 2.4rem;
            color: white;
            margin-bottom: 1.6rem;
            box-shadow: 0 8px 24px rgba(28,92,171,0.25);
        }}
        .fc-hero h1 {{
            margin: 0 0 0.4rem 0;
            font-size: 1.9rem;
            font-weight: 800;
            color: white;
        }}
        .fc-hero p {{
            margin: 0 0 0.9rem 0;
            font-size: 1rem;
            opacity: 0.92;
        }}
        .fc-badge-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .fc-badge {{
            background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.35);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.01em;
        }}

        .fc-stat-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            margin-bottom: 1.2rem;
        }}
        .fc-stat-card {{
            flex: 1 1 180px;
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-left: 4px solid var(--fc-tone, {PRIMARY});
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 1px 3px rgba(11,11,11,0.04);
        }}
        .fc-stat-card .fc-stat-icon {{ font-size: 1.2rem; }}
        .fc-stat-card .fc-stat-label {{
            color: {MUTED};
            font-size: 0.82rem;
            font-weight: 600;
            margin-top: 4px;
        }}
        .fc-stat-card .fc-stat-value {{
            color: {INK};
            font-size: 1.5rem;
            font-weight: 800;
            margin-top: 2px;
        }}
        .fc-stat-card .fc-stat-caption {{
            color: {MUTED};
            font-size: 0.76rem;
            margin-top: 2px;
        }}

        .fc-section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0.2rem 0 0.8rem 0;
        }}
        .fc-section-icon {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            border-radius: 10px;
            background: rgba(42,120,214,0.12);
            font-size: 1.05rem;
        }}
        .fc-section-header h3 {{
            margin: 0;
            font-size: 1.15rem;
            font-weight: 700;
            color: {INK};
        }}
        .fc-section-header p {{
            margin: 0;
            font-size: 0.85rem;
            color: {MUTED};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, badges: Optional[List[str]] = None) -> None:
    badge_html = "".join(f'<span class="fc-badge">{b}</span>' for b in (badges or []))
    st.markdown(
        f"""
        <div class="fc-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div class="fc-badge-row">{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str, subtitle: Optional[str] = None) -> None:
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="fc-section-header">
            <div class="fc-section-icon">{icon}</div>
            <div><h3>{title}</h3>{subtitle_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_row(cards: List[StatCard]) -> None:
    # Each card is built as a single line (no internal newlines). Streamlit's
    # markdown renderer treats a blank/whitespace-only line inside an HTML
    # block as the end of that raw-HTML block (CommonMark HTML block rules),
    # which would otherwise dump every card after the first as literal text.
    card_html = []
    for card in cards:
        tone_color = _TONE_COLORS.get(card.get("tone", "neutral"), PRIMARY)
        caption_html = f'<div class="fc-stat-caption">{card["caption"]}</div>' if card.get("caption") else ""
        card_html.append(
            f'<div class="fc-stat-card" style="--fc-tone: {tone_color}">'
            f'<div class="fc-stat-icon">{card.get("icon", "")}</div>'
            f'<div class="fc-stat-label">{card["label"]}</div>'
            f'<div class="fc-stat-value">{card["value"]}</div>'
            f"{caption_html}</div>"
        )
    st.markdown(f'<div class="fc-stat-row">{"".join(card_html)}</div>', unsafe_allow_html=True)
