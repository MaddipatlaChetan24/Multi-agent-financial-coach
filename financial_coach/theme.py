"""A dark, developer-tool-style visual layer on top of default Streamlit widgets.

Streamlit's default look (plain st.metric, flat st.subheader, unstyled
buttons) reads as a script, not a product. This module injects one CSS
block plus small HTML components (top bar, hero, stat row, section
headers, status badges, tables) so the app reads like a dashboard.
Colors are pulled from the dark-mode steps of the same validated,
colorblind-safe palette used in charts.py.
"""
from typing import List, Optional, Sequence, TypedDict

import streamlit as st

from financial_coach.charts import CATEGORICAL_DARK, CRITICAL_DARK, GOOD_DARK, WARNING_DARK

PRIMARY = CATEGORICAL_DARK[0]  # blue
ACCENT = CATEGORICAL_DARK[6]  # violet
INK = "#f2f2f5"
MUTED = "#9c9ba3"
SURFACE = "#13131a"
SURFACE_RAISED = "#181822"
PAGE_BG = "#0a0a0f"
BORDER = "rgba(255,255,255,0.08)"
BORDER_STRONG = "rgba(255,255,255,0.16)"

_TONE_COLORS = {"neutral": PRIMARY, "good": GOOD_DARK, "critical": CRITICAL_DARK, "warning": WARNING_DARK}

_BADGE_TONES = {
    "critical": (CRITICAL_DARK, "rgba(230,103,103,0.14)"),
    "warning": (WARNING_DARK, "rgba(250,178,25,0.14)"),
    "good": (GOOD_DARK, "rgba(34,197,94,0.14)"),
    "neutral": (MUTED, "rgba(255,255,255,0.06)"),
}


class StatCard(TypedDict, total=False):
    label: str
    value: str
    icon: str
    tone: str  # "neutral" | "good" | "critical" | "warning"
    caption: str


def badge(text: str, tone: str = "neutral") -> str:
    """A small colored pill, e.g. for severity/status in a table cell."""
    color, bg = _BADGE_TONES.get(tone, _BADGE_TONES["neutral"])
    return (
        f'<span class="fc-pill" style="color:{color};background:{bg};border-color:{color}55">{text}</span>'
    )


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background:
                radial-gradient(ellipse 900px 500px at 15% -10%, rgba(144,133,233,0.18), transparent 60%),
                radial-gradient(ellipse 900px 500px at 85% 0%, rgba(57,135,229,0.14), transparent 60%),
                {PAGE_BG};
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{ background: transparent; }}

        h1, h2, h3, h4, h5, p, span, label, li {{ color: {INK}; }}

        section[data-testid="stSidebar"] {{
            background: {SURFACE};
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] * {{ color: {INK} !important; }}
        section[data-testid="stSidebar"] .stAlert {{ background: {SURFACE_RAISED}; border: 1px solid {BORDER}; }}

        /* Buttons */
        .stButton > button {{
            border-radius: 10px;
            border: 1px solid {BORDER_STRONG};
            background: linear-gradient(135deg, {ACCENT} 0%, {PRIMARY} 100%);
            color: white;
            font-weight: 600;
            padding: 0.6rem 1.4rem;
            box-shadow: 0 4px 18px rgba(57,135,229,0.25);
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 22px rgba(57,135,229,0.4);
            color: white;
        }}
        .stButton > button p {{ color: white; }}

        /* Tabs */
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
        .stTabs [data-baseweb="tab"] p {{ color: inherit; }}
        .stTabs [aria-selected="true"] {{
            color: {PRIMARY} !important;
            background: rgba(57,135,229,0.12);
        }}

        div[data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 14px 18px;
        }}
        div[data-testid="stMetric"] label, div[data-testid="stMetric"] div {{ color: {INK} !important; }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 16px !important;
            background: {SURFACE};
            border-color: {BORDER} !important;
        }}

        div[data-baseweb="input"], div[data-baseweb="select"] > div, textarea, .stNumberInput input {{
            background: {SURFACE_RAISED} !important;
            border-radius: 8px !important;
            border-color: {BORDER_STRONG} !important;
            color: {INK} !important;
        }}
        div[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 10px; overflow: hidden; }}

        hr {{ border-color: {BORDER}; }}

        code {{
            font-family: 'JetBrains Mono', monospace;
            background: {SURFACE_RAISED} !important;
            color: {ACCENT} !important;
        }}

        /* --- Top bar --- */
        .fc-topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.9rem 0.2rem;
            margin-bottom: 1.4rem;
            border-bottom: 1px solid {BORDER};
        }}
        .fc-brand {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            font-size: 1.05rem;
            color: {INK};
        }}
        .fc-nav-links {{
            display: flex;
            gap: 28px;
            font-size: 0.9rem;
            color: {MUTED};
        }}
        .fc-nav-links span {{ color: {MUTED}; }}
        .fc-cta {{
            background: linear-gradient(135deg, {ACCENT} 0%, {PRIMARY} 100%);
            color: white !important;
            border-radius: 999px;
            padding: 8px 18px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
            box-shadow: 0 4px 16px rgba(57,135,229,0.3);
        }}

        /* --- Hero --- */
        .fc-hero {{
            text-align: center;
            padding: 2.4rem 1rem 1.6rem 1rem;
            margin-bottom: 1.6rem;
        }}
        .fc-eyebrow {{
            display: inline-block;
            border: 1px solid {BORDER_STRONG};
            background: {SURFACE};
            color: {ACCENT};
            border-radius: 999px;
            padding: 5px 16px;
            font-size: 0.76rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 1.2rem;
        }}
        .fc-hero h1 {{
            margin: 0 0 0.3rem 0;
            font-size: 2.6rem;
            font-weight: 800;
            line-height: 1.15;
            color: {INK};
        }}
        .fc-hero h1 .fc-gradient {{
            background: linear-gradient(135deg, {ACCENT} 0%, {PRIMARY} 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}
        .fc-hero .fc-subtitle {{
            max-width: 640px;
            margin: 0.9rem auto 1.8rem auto;
            color: {MUTED};
            font-size: 1.02rem;
            line-height: 1.55;
        }}
        .fc-hero-stats {{
            display: flex;
            justify-content: center;
            gap: 48px;
            flex-wrap: wrap;
        }}
        .fc-hero-stat .fc-hero-stat-value {{
            font-size: 1.6rem;
            font-weight: 800;
            color: {INK};
            font-family: 'JetBrains Mono', monospace;
        }}
        .fc-hero-stat .fc-hero-stat-label {{
            font-size: 0.78rem;
            color: {MUTED};
            margin-top: 2px;
        }}

        /* --- Stat cards (results dashboard) --- */
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
            border-left: 3px solid var(--fc-tone, {PRIMARY});
            border-radius: 12px;
            padding: 14px 16px;
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
            font-family: 'JetBrains Mono', monospace;
        }}
        .fc-stat-card .fc-stat-caption {{
            color: {MUTED};
            font-size: 0.76rem;
            margin-top: 2px;
        }}

        /* --- Section headers --- */
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
            background: rgba(57,135,229,0.14);
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

        /* --- Pills / badges --- */
        .fc-pill {{
            display: inline-block;
            border: 1px solid;
            border-radius: 999px;
            padding: 2px 10px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }}

        /* --- Custom dark table --- */
        .fc-table-wrap {{
            border: 1px solid {BORDER};
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 1rem;
        }}
        table.fc-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
        table.fc-table th {{
            text-align: left;
            color: {MUTED};
            font-weight: 600;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            padding: 10px 14px;
            background: {SURFACE_RAISED};
            border-bottom: 1px solid {BORDER};
        }}
        table.fc-table td {{
            padding: 10px 14px;
            border-bottom: 1px solid {BORDER};
            color: {INK};
        }}
        table.fc-table tr:last-child td {{ border-bottom: none; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(brand: str, links: Optional[List[str]] = None, cta_label: Optional[str] = None) -> None:
    links_html = "".join(f"<span>{link}</span>" for link in (links or []))
    cta_html = f'<span class="fc-cta">{cta_label}</span>' if cta_label else ""
    st.markdown(
        f'<div class="fc-topbar">'
        f'<div class="fc-brand">{brand}</div>'
        f'<div class="fc-nav-links">{links_html}</div>'
        f"{cta_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_hero(
    eyebrow: str,
    heading_line1: str,
    heading_line2_gradient: str,
    subtitle: str,
    stats: Optional[List[dict]] = None,
) -> None:
    stats_html = "".join(
        f'<div class="fc-hero-stat"><div class="fc-hero-stat-value">{s["value"]}</div>'
        f'<div class="fc-hero-stat-label">{s["label"]}</div></div>'
        for s in (stats or [])
    )
    st.markdown(
        f'<div class="fc-hero">'
        f'<span class="fc-eyebrow">{eyebrow}</span>'
        f"<h1>{heading_line1}<br><span class=\"fc-gradient\">{heading_line2_gradient}</span></h1>"
        f'<p class="fc-subtitle">{subtitle}</p>'
        f'<div class="fc-hero-stats">{stats_html}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str, subtitle: Optional[str] = None) -> None:
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="fc-section-header">'
        f'<div class="fc-section-icon">{icon}</div>'
        f"<div><h3>{title}</h3>{subtitle_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_stat_row(cards: List[StatCard]) -> None:
    # Each card is a single-line HTML fragment (no internal newlines).
    # Streamlit's markdown renderer treats a blank/whitespace-only line
    # inside an HTML block as the end of that raw-HTML block (CommonMark
    # HTML block rules) - concatenating multi-line fragments would dump
    # every card after the first as literal escaped text.
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


def render_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    """A dark-styled HTML table. Cells may contain pre-rendered HTML (e.g. badge())."""
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    body_html = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    st.markdown(
        f'<div class="fc-table-wrap"><table class="fc-table">'
        f"<thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody>"
        f"</table></div>",
        unsafe_allow_html=True,
    )
