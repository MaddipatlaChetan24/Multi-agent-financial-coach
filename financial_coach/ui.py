"""Streamlit display and input-collection functions."""
import json
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from financial_coach import calculators, charts, theme
from financial_coach.csv_utils import monthly_category_trend


def _apr_badge(interest_rate: float) -> str:
    if interest_rate >= 20:
        return theme.badge("HIGH APR", "critical")
    if interest_rate >= 10:
        return theme.badge("MEDIUM APR", "warning")
    return theme.badge("LOW APR", "good")


def _status_badge(on_track: bool) -> str:
    return theme.badge("ON TRACK", "good") if on_track else theme.badge("AT RISK", "warning")


def _coerce(data, label: str):
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            st.error(f"Failed to parse {label} results")
            return None
    if not isinstance(data, dict):
        st.error(f"Invalid {label} format")
        return None
    return data


def render_sidebar():
    with st.sidebar:
        st.title("🔑 Setup & Templates")
        st.info(
            "📝 Please ensure you have your Gemini API key in the .env file:\n"
            "```\nGOOGLE_API_KEY=your_api_key_here\n```"
        )
        st.caption(
            "This application uses Google's ADK (Agent Development Kit) and Gemini AI "
            "to provide personalized financial advice. Debt payoff math and emergency-fund "
            "sizing are computed deterministically in Python, not by the LLM."
        )
        st.divider()
        st.subheader("📊 CSV Template")
        st.markdown(
            "Download the template CSV file with the required format:\n"
            "- Date (YYYY-MM-DD)\n- Category\n- Amount (numeric)"
        )
        sample_csv = (
            "Date,Category,Amount\n"
            "2024-01-01,Housing,1200.00\n"
            "2024-01-02,Food,150.50\n"
            "2024-01-03,Transportation,45.00"
        )
        st.download_button(
            label="📥 Download CSV Template",
            data=sample_csv,
            file_name="expense_template.csv",
            mime="text/csv",
        )


def render_income_and_household() -> Tuple[float, int, str]:
    income_col, dependants_col, stability_col = st.columns([2, 1, 1])
    with income_col:
        monthly_income = st.number_input(
            "Monthly Income ($)", min_value=0.0, step=100.0, value=3000.0, key="income",
            help="Enter your total monthly income after taxes",
        )
    with dependants_col:
        dependants = st.number_input(
            "Number of Dependants", min_value=0, step=1, value=0, key="dependants",
            help="Include all dependants in your household",
        )
    with stability_col:
        income_stability = st.selectbox(
            "Income Stability", ["stable", "variable"], key="income_stability",
            help="Variable/self-employed income raises the recommended emergency fund to 6+ months",
        )
    return monthly_income, dependants, income_stability


def render_emergency_savings_input() -> float:
    return st.number_input(
        "Current Emergency Fund Savings ($)", min_value=0.0, step=100.0, value=0.0,
        key="current_emergency_savings", help="How much do you already have saved for emergencies?",
    )


def display_csv_preview(df: pd.DataFrame):
    theme.section_header("📄", "CSV Data Preview")

    total_transactions = len(df)
    total_amount = df["Amount"].sum()
    df_dates = pd.to_datetime(df["Date"])
    date_range = f"{df_dates.min().strftime('%Y-%m-%d')} to {df_dates.max().strftime('%Y-%m-%d')}"

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", total_transactions)
    col2.metric("Total Amount", f"${total_amount:,.2f}")
    col3.metric("Date Range", date_range)

    theme.section_header("📊", "Spending by Category")
    category_totals = df.groupby("Category")["Amount"].agg(["sum", "count"]).reset_index()
    category_totals.columns = ["Category", "Total Amount", "Transaction Count"]
    st.dataframe(category_totals)

    trend = monthly_category_trend(df.to_dict("records"))
    if not trend.empty:
        st.plotly_chart(charts.spending_trend_line(trend), use_container_width=True)

    st.subheader("Sample Transactions")
    st.dataframe(df.head())


def display_budget_analysis(analysis: Dict[str, Any]):
    analysis = _coerce(analysis, "budget analysis")
    if analysis is None:
        return

    if analysis.get("spending_categories"):
        theme.section_header("🥧", "Spending by Category")
        st.plotly_chart(charts.spending_breakdown_bar(analysis["spending_categories"]), use_container_width=True)

    if "total_expenses" in analysis:
        theme.section_header("⚖️", "Income vs. Expenses")
        income = analysis.get("monthly_income", 0) or 0
        expenses = analysis["total_expenses"]
        surplus_deficit = income - expenses
        st.plotly_chart(charts.income_vs_expenses_bar(income, expenses), use_container_width=True)
        st.metric("Monthly Surplus/Deficit", f"${surplus_deficit:.2f}", delta=f"{surplus_deficit:.2f}")

    if analysis.get("recommendations"):
        theme.section_header("💡", "Spending Reduction Recommendations")
        for rec in analysis["recommendations"]:
            st.markdown(f"**{rec['category']}**: {rec['recommendation']}")
            if rec.get("potential_savings"):
                st.metric("Potential Monthly Savings", f"${rec['potential_savings']:.2f}")


def display_savings_strategy(strategy: Dict[str, Any]):
    strategy = _coerce(strategy, "savings strategy")
    if strategy is None:
        return

    theme.section_header("📈", "Savings Recommendations")

    ef = strategy.get("emergency_fund")
    if ef:
        st.markdown("### Emergency Fund")
        st.markdown(f"**Recommended Size**: ${ef['recommended_amount']:.2f}")
        st.markdown(f"**Current Status**: {ef['current_status']}")
        if ef.get("recommended_amount"):
            progress = (ef.get("current_amount") or 0) / ef["recommended_amount"]
            st.progress(min(progress, 1.0))
            st.markdown(f"\\${ef.get('current_amount', 0):.2f} of \\${ef['recommended_amount']:.2f}")

    if strategy.get("recommendations"):
        st.markdown("### Recommended Savings Allocations")
        for rec in strategy["recommendations"]:
            st.markdown(f"**{rec['category']}**: ${rec['amount']:.2f}/month")
            if rec.get("rationale"):
                st.markdown(f"_{rec['rationale']}_")

    if strategy.get("automation_techniques"):
        st.markdown("### Automation Techniques")
        for technique in strategy["automation_techniques"]:
            st.markdown(f"**{technique['name']}**: {technique['description']}")


def display_debt_reduction(plan: Dict[str, Any]):
    plan = _coerce(plan, "debt reduction")
    if plan is None:
        return

    if "total_debt" in plan:
        st.metric("Total Debt", f"${plan['total_debt']:.2f}")

    if plan.get("debts"):
        theme.section_header("📋", "Your Debts")
        rows = [
            [d["name"], f"${d['amount']:,.2f}", f"{d['interest_rate']:.2f}%", _apr_badge(d["interest_rate"]), f"${d.get('min_payment', 0):,.2f}"]
            for d in plan["debts"]
        ]
        theme.render_table(["Name", "Balance", "APR", "Risk", "Min Payment"], rows)
        st.plotly_chart(charts.debt_breakdown_bar(plan["debts"]), use_container_width=True)

    payoff_plans = plan.get("payoff_plans")
    if payoff_plans and payoff_plans.get("avalanche") and payoff_plans.get("snowball"):
        theme.section_header("🧮", "Debt Payoff Plans", "Computed with real month-by-month amortization")
        avalanche, snowball = payoff_plans["avalanche"], payoff_plans["snowball"]
        tabs = st.tabs(["Avalanche Method", "Snowball Method", "Comparison"])

        with tabs[0]:
            st.markdown("### Avalanche Method (Highest Interest First)")
            st.markdown(f"**Total Interest Paid**: ${avalanche['total_interest']:.2f}")
            st.markdown(f"**Time to Debt Freedom**: {avalanche['months_to_payoff']} months")
            if avalanche.get("monthly_payment"):
                st.markdown(f"**Recommended Monthly Payment**: ${avalanche['monthly_payment']:.2f}")

        with tabs[1]:
            st.markdown("### Snowball Method (Smallest Balance First)")
            st.markdown(f"**Total Interest Paid**: ${snowball['total_interest']:.2f}")
            st.markdown(f"**Time to Debt Freedom**: {snowball['months_to_payoff']} months")
            if snowball.get("monthly_payment"):
                st.markdown(f"**Recommended Monthly Payment**: ${snowball['monthly_payment']:.2f}")

        with tabs[2]:
            st.markdown("### Method Comparison")
            interest_savings = snowball["total_interest"] - avalanche["total_interest"]
            if interest_savings > 0:
                st.info(f"💡 The avalanche method saves **${interest_savings:,.2f}** in interest versus snowball.")
            elif interest_savings < 0:
                st.info(f"💡 The snowball method saves **${-interest_savings:,.2f}** in interest versus avalanche.")
            figs = charts.payoff_comparison_charts(avalanche, snowball)
            col1, col2 = st.columns(2)
            col1.plotly_chart(figs["interest"], use_container_width=True)
            col2.plotly_chart(figs["months"], use_container_width=True)

    if plan.get("recommendations"):
        theme.section_header("💡", "Debt Reduction Recommendations")
        for rec in plan["recommendations"]:
            st.markdown(f"**{rec['title']}**: {rec['description']}")
            if rec.get("impact"):
                st.markdown(f"_Impact: {rec['impact']}_")


def display_goal_plan(plan: Dict[str, Any]):
    plan = _coerce(plan, "goal plan")
    if plan is None:
        return

    goals = plan.get("goals") or []
    if not goals:
        st.info("No financial goals were entered. Add goals in the input tab to see a funding plan here.")
        return

    st.metric("Available Monthly Surplus for Goals", f"${plan.get('available_monthly_surplus', 0):,.2f}")

    for goal in goals:
        st.markdown(f"### 🎯 {goal['name']}  {_status_badge(goal['on_track'])}", unsafe_allow_html=True)
        cols = st.columns(4)
        cols[0].metric("Target", f"${goal['target_amount']:,.2f}")
        cols[1].metric("Required/mo", f"${goal['required_monthly_contribution']:,.2f}")
        cols[2].metric("Allocated/mo", f"${goal['monthly_contribution_allocated']:,.2f}")
        cols[3].metric("Projected", f"{goal['projected_months_to_reach']} mo")

        if not goal["on_track"]:
            st.warning(
                f"⚠️ At the surplus available after higher-priority goals, this will take "
                f"{goal['projected_months_to_reach']} months instead of the requested "
                f"{goal['target_months']}."
            )

        months_to_show = max(goal["projected_months_to_reach"], goal["target_months"])
        schedule = calculators.goal_projection_schedule(
            goal["current_amount"], goal["monthly_contribution_allocated"], months_to_show
        )
        st.plotly_chart(
            charts.goal_projection_chart(schedule, goal["target_amount"], goal["name"]),
            use_container_width=True,
        )

    if plan.get("prioritization_summary"):
        st.markdown("### Prioritization")
        st.markdown(plan["prioritization_summary"])

    if plan.get("recommendations"):
        st.markdown("### Recommendations")
        for rec in plan["recommendations"]:
            st.markdown(f"- {rec}")

    if plan.get("tradeoffs"):
        st.markdown("### Tradeoffs")
        st.markdown(plan["tradeoffs"])


def render_goals_input() -> List[Dict[str, Any]]:
    st.info(
        "Add savings goals (a house down payment, retirement, a big purchase). "
        "They're funded in the order listed, using whatever monthly surplus is left "
        "after expenses and minimum debt payments."
    )

    num_goals = st.number_input("How many goals do you have?", min_value=0, max_value=5, step=1, value=0, key="num_goals")

    goals = []
    for i in range(num_goals):
        st.markdown(f"##### Goal #{i + 1}")
        cols = st.columns(4)
        name = cols[0].text_input("Name", value=f"Goal {i + 1}", key=f"goal_name_{i}")
        target_amount = cols[1].number_input(
            "Target Amount ($)", min_value=0.0, step=500.0, value=10000.0, key=f"goal_amount_{i}"
        )
        current_amount = cols[2].number_input(
            "Already Saved ($)", min_value=0.0, step=100.0, value=0.0, key=f"goal_current_{i}"
        )
        target_years = cols[3].number_input(
            "Timeframe (years)", min_value=0.5, step=0.5, value=3.0, key=f"goal_years_{i}"
        )
        goals.append(
            {
                "name": name,
                "target_amount": target_amount,
                "current_amount": current_amount,
                "target_months": int(round(target_years * 12)),
                "annual_return_rate": 4.0,
            }
        )
    return goals


def render_debts_input() -> List[Dict[str, Any]]:
    st.info("Enter your debts to get personalized payoff strategies using both avalanche and snowball methods.")

    num_debts = st.number_input("How many debts do you have?", min_value=0, max_value=10, step=1, value=0, key="num_debts")

    debts = []
    if num_debts > 0:
        cols = st.columns(min(num_debts, 3))
        for i in range(num_debts):
            col_idx = i % 3
            with cols[col_idx]:
                st.markdown(f"##### Debt #{i + 1}")
                debt_name = st.text_input("Name", value=f"Debt {i + 1}", key=f"debt_name_{i}")
                debt_amount = st.number_input(
                    "Amount ($)", min_value=0.01, step=100.0, value=1000.0, key=f"debt_amount_{i}"
                )
                interest_rate = st.number_input(
                    "Interest Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=5.0, key=f"debt_rate_{i}"
                )
                min_payment = st.number_input(
                    "Minimum Payment ($)", min_value=0.0, step=10.0, value=50.0, key=f"debt_min_payment_{i}"
                )
                debts.append(
                    {"name": debt_name, "amount": debt_amount, "interest_rate": interest_rate, "min_payment": min_payment}
                )
                if col_idx == 2 or i == num_debts - 1:
                    st.markdown("---")
    return debts
