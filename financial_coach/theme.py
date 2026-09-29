"""A dark, developer-tool-style visual layer on top of default Streamlit widgets.

Streamlit's default look (plain st.metric, flat st.subheader, unstyled
buttons) reads as a script, not a product. This module injects one CSS
block plus small HTML components (top bar, hero, stat row, section
headers, status badges, tables) so the app reads like a dashboard.
Colors are pulled from the dark-mode steps of the same validated,
colorblind-safe palette used in charts.py.
"""
from typing import Dict, List, Optional, Sequence, TypedDict

import streamlit as st

from financial_coach.charts import CATEGORICAL_DARK, CRITICAL_DARK, GOOD_DARK, WARNING_DARK

PRIMARY = CATEGORICAL_DARK[0]  # blue
ACCENT = CATEGORICAL_DARK[6]  # violet
INK = "#f2f2f5"
MUTED = "#9c9ba3"
SURFACE = "#13131a"
SURFACE_RAISED = "#181822"
PAGE_BG = "#08090d"
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
        div[data-testid="stToolbar"] {{ visibility: hidden; }}
        div[data-testid="stDecoration"] {{ display: none; }}
        .stApp > .main .block-container {{ padding-top: 1.2rem; max-width: 1180px; }}

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
            box-shadow: 0 1px 0 rgba(255,255,255,0.02) inset;
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
            gap: 9px;
            font-weight: 700;
            font-size: 1.05rem;
            color: {INK};
        }}
        .fc-brand-mark {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            background: linear-gradient(135deg, {ACCENT} 0%, {PRIMARY} 100%);
        }}
        .fc-nav-links {{
            display: flex;
            gap: 28px;
            font-size: 0.9rem;
            color: {MUTED};
        }}
        .fc-nav-links a {{ color: {MUTED}; text-decoration: none !important; }}
        .fc-nav-links a:hover {{ color: {INK}; }}
        .fc-cta {{
            background: linear-gradient(135deg, {ACCENT} 0%, {PRIMARY} 100%);
            color: white !important;
            border-radius: 999px;
            padding: 8px 18px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none !important;
            box-shadow: 0 4px 16px rgba(57,135,229,0.3);
        }}

        /* --- Hero --- */
        .fc-hero {{
            text-align: center;
            padding: 3.2rem 1rem 2.2rem 1rem;
            margin-bottom: 0.4rem;
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
            font-size: 3rem;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.02em;
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
            margin: 0.9rem auto 1.6rem auto;
            color: {MUTED};
            font-size: 1.05rem;
            line-height: 1.55;
        }}
        .fc-hero-actions {{
            display: flex;
            justify-content: center;
            gap: 14px;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }}
        .fc-btn-primary, .fc-btn-secondary {{
            display: inline-block;
            border-radius: 10px;
            padding: 0.7rem 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            text-decoration: none !important;
            cursor: pointer;
        }}
        .fc-btn-primary {{
            background: linear-gradient(135deg, {ACCENT} 0%, {PRIMARY} 100%);
            color: white !important;
            box-shadow: 0 4px 18px rgba(57,135,229,0.28);
        }}
        .fc-btn-primary:hover {{ box-shadow: 0 6px 22px rgba(57,135,229,0.42); }}
        .fc-btn-secondary {{
            background: {SURFACE};
            border: 1px solid {BORDER_STRONG};
            color: {INK} !important;
        }}
        .fc-btn-secondary:hover {{ border-color: {ACCENT}; }}
        .fc-hero-trust {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {MUTED};
            margin-bottom: 2.4rem;
        }}
        .fc-hero-trust span {{ margin: 0 10px; }}
        .fc-hero-stats {{
            display: flex;
            justify-content: center;
            gap: 0;
            flex-wrap: wrap;
            border: 1px solid {BORDER};
            background: {SURFACE};
            border-radius: 16px;
            padding: 1.1rem 0;
            max-width: 620px;
            margin: 0 auto;
        }}
        .fc-hero-stat {{
            flex: 1 1 140px;
            padding: 0 1.4rem;
            border-right: 1px solid {BORDER};
        }}
        .fc-hero-stat:last-child {{ border-right: none; }}
        .fc-hero-stat .fc-hero-stat-value {{
            font-size: 1.7rem;
            font-weight: 800;
            color: {INK};
            font-family: 'JetBrains Mono', monospace;
        }}
        .fc-hero-stat .fc-hero-stat-label {{
            font-size: 0.78rem;
            color: {MUTED};
            margin-top: 2px;
        }}

        /* --- Footer --- */
        .fc-footer {{
            text-align: center;
            padding: 2.2rem 1rem 1.4rem 1rem;
            margin-top: 2rem;
            border-top: 1px solid {BORDER};
            color: {MUTED};
            font-size: 0.82rem;
        }}
        .fc-footer a {{ color: {MUTED}; text-decoration: none !important; }}
        .fc-footer a:hover {{ color: {INK}; }}

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

        /* --- Product preview card --- */
        .fc-preview-wrap {{
            display: flex;
            justify-content: center;
            margin: 0 0 3rem 0;
        }}
        .fc-preview-card {{
            width: 100%;
            max-width: 640px;
            background: linear-gradient(180deg, {SURFACE_RAISED} 0%, {SURFACE} 100%);
            border: 1px solid {BORDER_STRONG};
            border-radius: 20px;
            padding: 26px 30px 22px 30px;
            box-shadow: 0 30px 70px -20px rgba(57,135,229,0.25), 0 0 0 1px rgba(255,255,255,0.02);
        }}
        .fc-preview-label {{
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {ACCENT};
            margin-bottom: 14px;
        }}
        .fc-preview-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.95rem;
            padding: 6px 0;
            color: {MUTED};
        }}
        .fc-preview-row b {{ color: {INK}; font-family: 'JetBrains Mono', monospace; }}
        .fc-preview-divider {{ border-top: 1px solid {BORDER}; margin: 12px 0; }}
        .fc-preview-projection {{
            font-size: 0.76rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: {MUTED};
            margin-bottom: 10px;
        }}
        .fc-preview-outcome {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {GOOD_DARK};
            margin-top: 8px;
        }}

        /* --- Trust bar --- */
        .fc-trust-bar {{
            text-align: center;
            font-size: 0.76rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {MUTED};
            padding: 1rem 0 2.4rem 0;
        }}
        .fc-trust-bar span.fc-dot {{ margin: 0 12px; color: {BORDER_STRONG}; }}

        /* --- Section wrapper --- */
        .fc-section {{ margin: 3.2rem 0; }}
        .fc-section-eyebrow {{
            text-align: center;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {ACCENT};
            margin-bottom: 8px;
        }}
        .fc-section-title {{
            text-align: center;
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            color: {INK};
            margin: 0 0 2rem 0;
        }}

        /* --- Numbered feature list --- */
        .fc-numbered-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .fc-numbered-item {{
            flex: 1 1 260px;
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 20px 22px;
        }}
        .fc-numbered-item .fc-num {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            font-weight: 700;
            color: {ACCENT};
            margin-bottom: 10px;
        }}
        .fc-numbered-item h4 {{ margin: 0 0 6px 0; font-size: 1rem; font-weight: 700; color: {INK}; }}
        .fc-numbered-item p {{ margin: 0; font-size: 0.86rem; line-height: 1.5; color: {MUTED}; }}

        /* --- How it works steps --- */
        .fc-steps {{
            display: flex;
            gap: 0;
            flex-wrap: wrap;
        }}
        .fc-step {{
            flex: 1 1 200px;
            text-align: center;
            padding: 0 18px;
            position: relative;
        }}
        .fc-step .fc-step-num {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.2rem;
            font-weight: 800;
            color: {BORDER_STRONG};
            margin-bottom: 6px;
        }}
        .fc-step h4 {{ margin: 0 0 6px 0; font-size: 1rem; font-weight: 700; color: {INK}; }}
        .fc-step p {{ margin: 0; font-size: 0.84rem; color: {MUTED}; line-height: 1.5; }}

        /* --- Architecture diagram --- */
        .fc-arch {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 18px;
            padding: 2.2rem 1.5rem;
            text-align: center;
        }}
        .fc-arch-node {{
            display: inline-block;
            background: {SURFACE_RAISED};
            border: 1px solid {BORDER_STRONG};
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 0.86rem;
            font-weight: 600;
            color: {INK};
        }}
        .fc-arch-node.fc-arch-primary {{
            border-color: {PRIMARY};
            background: rgba(57,135,229,0.12);
            color: {PRIMARY};
        }}
        .fc-arch-arrow {{ color: {MUTED}; font-size: 1.1rem; margin: 10px 0; }}
        .fc-arch-agents {{
            display: flex;
            justify-content: center;
            gap: 14px;
            flex-wrap: wrap;
            margin: 4px 0;
        }}
        .fc-arch-caption {{
            margin-top: 1.4rem;
            font-size: 0.9rem;
            color: {MUTED};
        }}
        .fc-arch-caption b {{ color: {INK}; }}

        /* --- Simulator --- */
        .fc-sim-card {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 1.6rem 1.8rem;
        }}
        .fc-sim-result {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 1.2rem;
        }}
        .fc-sim-col {{ text-align: center; }}
        .fc-sim-col .fc-sim-label {{
            font-size: 0.74rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: {MUTED};
            margin-bottom: 6px;
        }}
        .fc-sim-col .fc-sim-value {{
            font-size: 1.5rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: {INK};
        }}
        .fc-sim-col.fc-sim-highlight .fc-sim-value {{ color: {GOOD_DARK}; }}
        .fc-sim-arrow {{ font-size: 1.3rem; color: {MUTED}; align-self: center; }}

        /* --- Final CTA --- */
        .fc-final-cta {{
            text-align: center;
            padding: 3rem 1rem;
            margin: 3rem 0 1rem 0;
            border-radius: 22px;
            background: radial-gradient(ellipse 700px 300px at 50% 0%, rgba(144,133,233,0.16), transparent 70%), {SURFACE};
            border: 1px solid {BORDER};
        }}
        .fc-final-cta h2 {{
            font-size: 2rem;
            font-weight: 800;
            margin: 0 0 0.8rem 0;
            color: {INK};
        }}
        .fc-final-cta p {{ color: {MUTED}; margin-bottom: 1.6rem; }}
        .fc-final-cta .fc-hero-trust {{ margin-top: 1.2rem; margin-bottom: 0; }}

        /* --- Footer nav --- */
        .fc-footer-nav {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 20px;
            text-align: left;
            margin-bottom: 1.2rem;
        }}
        .fc-footer-nav .fc-footer-col h5 {{
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: {INK};
            margin: 0 0 10px 0;
        }}
        .fc-footer-nav .fc-footer-col a {{
            display: block;
            font-size: 0.84rem;
            color: {MUTED};
            text-decoration: none !important;
            margin-bottom: 6px;
        }}
        .fc-footer-nav .fc-footer-col a:hover {{ color: {INK}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(
    brand: str,
    links: Optional[List[Dict[str, str]]] = None,
    cta: Optional[Dict[str, str]] = None,
) -> None:
    links_html = "".join(f'<a href="{link["href"]}">{link["label"]}</a>' for link in (links or []))
    cta_html = f'<a class="fc-cta" href="{cta["href"]}">{cta["label"]}</a>' if cta else ""
    st.markdown(
        f'<div class="fc-topbar">'
        f'<div class="fc-brand"><span class="fc-brand-mark"></span>{brand}</div>'
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
    primary_cta: Optional[Dict[str, str]] = None,
    secondary_cta: Optional[Dict[str, str]] = None,
    trust_items: Optional[List[str]] = None,
) -> None:
    stats_html = "".join(
        f'<div class="fc-hero-stat"><div class="fc-hero-stat-value">{s["value"]}</div>'
        f'<div class="fc-hero-stat-label">{s["label"]}</div></div>'
        for s in (stats or [])
    )
    actions_html = ""
    if primary_cta or secondary_cta:
        parts = []
        if primary_cta:
            parts.append(f'<a class="fc-btn-primary" href="{primary_cta["href"]}">{primary_cta["label"]}</a>')
        if secondary_cta:
            parts.append(f'<a class="fc-btn-secondary" href="{secondary_cta["href"]}">{secondary_cta["label"]}</a>')
        actions_html = f'<div class="fc-hero-actions">{"".join(parts)}</div>'
    trust_html = ""
    if trust_items:
        trust_html = '<div class="fc-hero-trust">' + "<span>&middot;</span>".join(trust_items) + "</div>"
    st.markdown(
        f'<div class="fc-hero">'
        f'<span class="fc-eyebrow">{eyebrow}</span>'
        f"<h1>{heading_line1}<br><span class=\"fc-gradient\">{heading_line2_gradient}</span></h1>"
        f'<p class="fc-subtitle">{subtitle}</p>'
        f"{actions_html}{trust_html}"
        f'<div class="fc-hero-stats">{stats_html}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_preview_card(
    label: str,
    rows: List[Dict[str, str]],
    projection_label: str,
    outcome: str,
) -> None:
    rows_html = "".join(f'<div class="fc-preview-row"><span>{r["label"]}</span><b>{r["value"]}</b></div>' for r in rows)
    st.markdown(
        f'<div class="fc-preview-wrap"><div class="fc-preview-card">'
        f'<div class="fc-preview-label">{label}</div>'
        f"{rows_html}"
        f'<div class="fc-preview-divider"></div>'
        f'<div class="fc-preview-projection">{projection_label}</div>'
        f'<div class="fc-preview-outcome">{outcome}</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


def render_trust_bar(items: List[str]) -> None:
    html = '<span class="fc-dot">&bull;</span>'.join(items)
    st.markdown(f'<div class="fc-trust-bar">{html}</div>', unsafe_allow_html=True)


def render_section_title(eyebrow: str, title: str) -> None:
    st.markdown(
        f'<div class="fc-section-eyebrow">{eyebrow}</div><div class="fc-section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def render_numbered_grid(items: List[Dict[str, str]]) -> None:
    cards = "".join(
        f'<div class="fc-numbered-item"><div class="fc-num">{i + 1:02d}</div>'
        f'<h4>{item["title"]}</h4><p>{item["description"]}</p></div>'
        for i, item in enumerate(items)
    )
    st.markdown(f'<div class="fc-numbered-grid">{cards}</div>', unsafe_allow_html=True)


def render_steps(steps: List[Dict[str, str]]) -> None:
    cards = "".join(
        f'<div class="fc-step"><div class="fc-step-num">{i + 1:02d}</div>'
        f'<h4>{s["title"]}</h4><p>{s["description"]}</p></div>'
        for i, s in enumerate(steps)
    )
    st.markdown(f'<div class="fc-steps">{cards}</div>', unsafe_allow_html=True)


def render_architecture(agents: List[str], caption: str) -> None:
    agents_html = "".join(f'<div class="fc-arch-node">{a}</div>' for a in agents)
    st.markdown(
        f'<div class="fc-arch">'
        f'<div class="fc-arch-node fc-arch-primary">User financial data</div>'
        f'<div class="fc-arch-arrow">&darr;</div>'
        f'<div class="fc-arch-node fc-arch-primary">Deterministic finance engine (Python)</div>'
        f'<div class="fc-arch-arrow">&darr;</div>'
        f'<div class="fc-arch-agents">{agents_html}</div>'
        f'<div class="fc-arch-arrow">&darr;</div>'
        f'<div class="fc-arch-node">Personal financial plan</div>'
        f'<div class="fc-arch-caption">{caption}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_final_cta(heading: str, subtitle: str, cta: Dict[str, str], trust_items: List[str]) -> None:
    trust_html = '<div class="fc-hero-trust">' + "<span>&middot;</span>".join(trust_items) + "</div>"
    st.markdown(
        f'<div class="fc-final-cta">'
        f"<h2>{heading}</h2>"
        f"<p>{subtitle}</p>"
        f'<div class="fc-hero-actions"><a class="fc-btn-primary" href="{cta["href"]}">{cta["label"]}</a></div>'
        f"{trust_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_footer_nav(brand: str, columns: List[Dict[str, object]], copyright_text: str) -> None:
    cols_html = ""
    for col in columns:
        links_html = "".join(f'<a href="{l["href"]}">{l["label"]}</a>' for l in col["links"])
        cols_html += f'<div class="fc-footer-col"><h5>{col["title"]}</h5>{links_html}</div>'
    st.markdown(
        f'<div class="fc-footer">'
        f'<div class="fc-footer-nav"><div class="fc-footer-col"><h5>{brand}</h5></div>{cols_html}</div>'
        f"<div>{copyright_text}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="fc-section-header">'
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
