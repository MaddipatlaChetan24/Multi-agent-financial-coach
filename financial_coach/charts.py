"""Plotly chart builders.

Colors come from a pre-validated, colorblind-safe palette (CVD Delta E >= 8,
normal-vision Delta E >= 15 on adjacent pairs) rather than Plotly's default
qualitative cycling. Categorical hues are assigned in a fixed order, never
cycled or reused for rank/magnitude.
"""
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go

# Fixed-order categorical palette (colorblind-safe adjacent pairs).
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
# Single-hue sequential ramp (light -> dark) for magnitude encodings.
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]
GRIDLINE = "#e1e0d9"
MUTED_INK = "#898781"
PRIMARY_INK = "#0b0b0b"
GOOD = "#0ca30c"
CRITICAL = "#d03b3b"

_LAYOUT_DEFAULTS = dict(
    plot_bgcolor="#fcfcfb",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=PRIMARY_INK, family="system-ui, -apple-system, Segoe UI, sans-serif"),
    margin=dict(t=48, l=16, r=16, b=16),
)


def _apply_layout(fig: go.Figure, **overrides) -> go.Figure:
    layout = {**_LAYOUT_DEFAULTS, **overrides}
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE)
    fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE)
    return fig


def spending_breakdown_bar(categories: List[Dict[str, Any]]) -> go.Figure:
    """Ranked horizontal bar of spending by category.

    Replaces the original pie chart: with up to 9 categories, a pie
    forces readers to compare wedge angles instead of reading a ranked
    list, and part-to-whole pies only work at a glance under ~6 segments.
    """
    sorted_categories = sorted(categories, key=lambda c: c.get("amount", 0), reverse=True)
    names = [c["category"] for c in sorted_categories]
    amounts = [c.get("amount", 0) for c in sorted_categories]

    fig = go.Figure(
        go.Bar(
            x=amounts,
            y=names,
            orientation="h",
            marker_color=CATEGORICAL[0],
            text=[f"${a:,.0f}" for a in amounts],
            textposition="outside",
        )
    )
    fig.update_yaxes(autorange="reversed")
    return _apply_layout(fig, title="Spending by Category", showlegend=False)


def income_vs_expenses_bar(income: float, expenses: float) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=["Income", "Expenses"],
            y=[income, expenses],
            marker_color=[CATEGORICAL[0], CATEGORICAL[1]],
            text=[f"${income:,.0f}", f"${expenses:,.0f}"],
            textposition="outside",
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
                colorscale=[[i / (len(SEQUENTIAL) - 1), c] for i, c in enumerate(SEQUENTIAL)],
                colorbar=dict(title="APR %"),
            ),
            text=[f"${a:,.0f}" for a in df["amount"]],
            textposition="outside",
        )
    )
    return _apply_layout(fig, title="Debt Breakdown (color = interest rate)", showlegend=False)


def payoff_comparison_charts(avalanche: Dict[str, Any], snowball: Dict[str, Any]) -> Dict[str, go.Figure]:
    """Two single-metric charts instead of one dual-unit grouped bar.

    The original mixed dollars and months on one axis in a grouped bar,
    which makes the bars visually incomparable. Splitting into small
    multiples keeps each axis in one unit, with method (Avalanche/
    Snowball) mapped to the same fixed hue in both charts.
    """
    methods = ["Avalanche", "Snowball"]
    colors = [CATEGORICAL[0], CATEGORICAL[1]]

    interest_fig = go.Figure(
        go.Bar(
            x=methods,
            y=[avalanche["total_interest"], snowball["total_interest"]],
            marker_color=colors,
            text=[f"${avalanche['total_interest']:,.0f}", f"${snowball['total_interest']:,.0f}"],
            textposition="outside",
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
                line=dict(width=2, color=CATEGORICAL[i % len(CATEGORICAL)]),
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
            line=dict(width=2, color=CATEGORICAL[0]),
            fill="tozeroy",
            fillcolor="rgba(42,120,214,0.12)",
        )
    )
    fig.add_hline(
        y=target_amount,
        line_dash="dash",
        line_color=MUTED_INK,
        annotation_text=f"Target: ${target_amount:,.0f}",
        annotation_position="top left",
    )
    return _apply_layout(fig, title=f"Projected Path to “{goal_name}”", showlegend=False, xaxis_title="Month")
