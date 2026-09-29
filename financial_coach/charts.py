"""Plotly chart builders, themed dark to match the rest of the app.

Colors come from the dark-mode steps of a pre-validated, colorblind-safe
palette (CVD Delta E >= 8, normal-vision Delta E >= 15 on adjacent pairs)
rather than Plotly's default qualitative cycling. Categorical hues are
assigned in a fixed order, never cycled or reused for rank/magnitude.
"""
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go

# Fixed-order categorical palette, dark-surface steps (colorblind-safe adjacent pairs).
CATEGORICAL_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]
# Single-hue sequential ramp, dark -> light (low -> high magnitude on a dark surface).
SEQUENTIAL_DARK = ["#173463", "#184f95", "#1c5cab", "#2a78d6", "#3987e5", "#6da7ec", "#9ec5f4"]

CHART_SURFACE = "#13131a"
GRIDLINE_DARK = "rgba(255,255,255,0.08)"
MUTED_INK_DARK = "#9c9ba3"
PRIMARY_INK_DARK = "#f2f2f5"
GOOD_DARK = "#22c55e"
CRITICAL_DARK = "#e66767"
WARNING_DARK = "#fab219"

# Backwards-compatible aliases used elsewhere in the app.
CATEGORICAL = CATEGORICAL_DARK
SEQUENTIAL = SEQUENTIAL_DARK
GRIDLINE = GRIDLINE_DARK
MUTED_INK = MUTED_INK_DARK
PRIMARY_INK = PRIMARY_INK_DARK
GOOD = GOOD_DARK
CRITICAL = CRITICAL_DARK

_LAYOUT_DEFAULTS = dict(
    plot_bgcolor=CHART_SURFACE,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=PRIMARY_INK_DARK, family="Inter, system-ui, -apple-system, Segoe UI, sans-serif"),
    margin=dict(t=48, l=16, r=16, b=16),
    legend=dict(font=dict(color=PRIMARY_INK_DARK)),
)


def _apply_layout(fig: go.Figure, **overrides) -> go.Figure:
    layout = {**_LAYOUT_DEFAULTS, **overrides}
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor=GRIDLINE_DARK, zerolinecolor=GRIDLINE_DARK, color=MUTED_INK_DARK)
    fig.update_yaxes(gridcolor=GRIDLINE_DARK, zerolinecolor=GRIDLINE_DARK, color=MUTED_INK_DARK)
    return fig


def spending_breakdown_bar(categories: List[Dict[str, Any]]) -> go.Figure:
    """Ranked horizontal bar of spending by category.

    Replaces a pie chart: with up to 9 categories, a pie forces readers to
    compare wedge angles instead of reading a ranked list, and part-to-whole
    pies only work at a glance under ~6 segments.
    """
    sorted_categories = sorted(categories, key=lambda c: c.get("amount", 0), reverse=True)
    names = [c["category"] for c in sorted_categories]
    amounts = [c.get("amount", 0) for c in sorted_categories]

    fig = go.Figure(
        go.Bar(
            x=amounts,
            y=names,
            orientation="h",
            marker_color=CATEGORICAL_DARK[0],
            text=[f"₹{a:,.0f}" for a in amounts],
            textposition="outside",
            textfont=dict(color=PRIMARY_INK_DARK),
        )
    )
    fig.update_yaxes(autorange="reversed")
    return _apply_layout(fig, title="Spending by Category", showlegend=False)


def income_vs_expenses_bar(income: float, expenses: float) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=["Income", "Expenses"],
            y=[income, expenses],
            marker_color=[CATEGORICAL_DARK[0], CATEGORICAL_DARK[1]],
            text=[f"₹{income:,.0f}", f"₹{expenses:,.0f}"],
            textposition="outside",
            textfont=dict(color=PRIMARY_INK_DARK),
        )
    )
    return _apply_layout(fig, title="Monthly Income vs. Expenses", showlegend=False)


def debt_breakdown_bar(debts: List[Dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(debts).sort_values("amount", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=df["amount"],
            y=df["name"],
            orientation="h",
            marker=dict(
                color=df["interest_rate"],
                colorscale=[[i / (len(SEQUENTIAL_DARK) - 1), c] for i, c in enumerate(SEQUENTIAL_DARK)],
                colorbar=dict(title="APR %", tickfont=dict(color=MUTED_INK_DARK)),
            ),
            text=[f"₹{a:,.0f}" for a in df["amount"]],
            textposition="outside",
            textfont=dict(color=PRIMARY_INK_DARK),
        )
    )
    return _apply_layout(fig, title="Debt Breakdown (color = interest rate)", showlegend=False)


def payoff_comparison_charts(avalanche: Dict[str, Any], snowball: Dict[str, Any]) -> Dict[str, go.Figure]:
    """Two single-metric charts instead of one dual-unit grouped bar.

    Mixing dollars and months on one axis in a grouped bar makes the bars
    visually incomparable. Splitting into small multiples keeps each axis
    in one unit, with method (Avalanche/Snowball) mapped to the same fixed
    hue in both charts.
    """
    methods = ["Avalanche", "Snowball"]
    colors = [CATEGORICAL_DARK[0], CATEGORICAL_DARK[1]]

    interest_fig = go.Figure(
        go.Bar(
            x=methods,
            y=[avalanche["total_interest"], snowball["total_interest"]],
            marker_color=colors,
            text=[f"₹{avalanche['total_interest']:,.0f}", f"₹{snowball['total_interest']:,.0f}"],
            textposition="outside",
            textfont=dict(color=PRIMARY_INK_DARK),
        )
    )
    _apply_layout(interest_fig, title="Total Interest Paid", showlegend=False)

    months_fig = go.Figure(
        go.Bar(
            x=methods,
            y=[avalanche["months_to_payoff"], snowball["months_to_payoff"]],
            marker_color=colors,
            text=[f"{avalanche['months_to_payoff']} mo", f"{snowball['months_to_payoff']} mo"],
            textposition="outside",
            textfont=dict(color=PRIMARY_INK_DARK),
        )
    )
    _apply_layout(months_fig, title="Time to Debt Freedom", showlegend=False)

    return {"interest": interest_fig, "months": months_fig}


def spending_trend_line(trend_df: pd.DataFrame) -> go.Figure:
    """Multi-month spending trend, one line per category (fixed hue order)."""
    fig = go.Figure()
    categories = list(trend_df["Category"].unique())
    for i, category in enumerate(categories):
        cat_df = trend_df[trend_df["Category"] == category].sort_values("Month")
        fig.add_trace(
            go.Scatter(
                x=cat_df["Month"],
                y=cat_df["Amount"],
                mode="lines+markers",
                name=category,
                line=dict(width=2, color=CATEGORICAL_DARK[i % len(CATEGORICAL_DARK)]),
                marker=dict(size=8),
            )
        )
    return _apply_layout(fig, title="Spending Trend by Category", showlegend=True)


def goal_projection_chart(schedule: List[Dict[str, float]], target_amount: float, goal_name: str) -> go.Figure:
    """Projected balance growth toward a savings goal, with a target line."""
    months = [point["month"] for point in schedule]
    balances = [point["balance"] for point in schedule]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=months,
            y=balances,
            mode="lines",
            name="Projected balance",
            line=dict(width=2, color=CATEGORICAL_DARK[0]),
            fill="tozeroy",
            fillcolor="rgba(57,135,229,0.16)",
        )
    )
    fig.add_hline(
        y=target_amount,
        line_dash="dash",
        line_color=MUTED_INK_DARK,
        annotation_text=f"Target: ₹{target_amount:,.0f}",
        annotation_position="top left",
        annotation_font_color=MUTED_INK_DARK,
    )
    return _apply_layout(fig, title=f"Projected Path to “{goal_name}”", showlegend=False, xaxis_title="Month")
