import asyncio
import logging
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from financial_coach import history, theme, ui
from financial_coach.advisor import FinanceAdvisorSystem
from financial_coach.csv_utils import parse_csv_transactions, validate_csv_format
from financial_coach.report import build_markdown_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

MANUAL_EXPENSE_CATEGORIES = [
    ("🏠 Housing", "Housing"),
    ("🔌 Utilities", "Utilities"),
    ("🍽️ Food", "Food"),
    ("🚗 Transportation", "Transportation"),
    ("🏥 Healthcare", "Healthcare"),
    ("🎭 Entertainment", "Entertainment"),
    ("👤 Personal", "Personal"),
    ("💰 Savings", "Savings"),
    ("📦 Other", "Other"),
]


def render_expenses_section():
    theme.section_header("💳", "Expenses", "Upload transactions or enter monthly totals by category")
    expense_option = st.radio(
        "How would you like to enter your expenses?",
        ("📤 Upload CSV Transactions", "✍️ Enter Manually"),
        key="expense_option",
        horizontal=True,
    )

    manual_expenses = {}
    use_manual_expenses = False
    transactions_df = None

    if expense_option == "📤 Upload CSV Transactions":
        col1, _ = st.columns([2, 1])
        with col1:
            st.markdown(
                "#### Upload your transaction data\n"
                "Your CSV file should have these columns:\n"
                "- 📅 Date (YYYY-MM-DD)\n- 📝 Category\n- 💲 Amount"
            )
            transaction_file = st.file_uploader("Choose your CSV file", type=["csv"], key="transaction_file")

        if transaction_file is not None:
            is_valid, message = validate_csv_format(transaction_file)
            if is_valid:
                try:
                    transaction_file.seek(0)
                    parsed_data = parse_csv_transactions(transaction_file.read())
                    transactions_df = pd.DataFrame(parsed_data["transactions"])
                    ui.display_csv_preview(transactions_df)
                    st.success("✅ Transaction file uploaded and validated successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing CSV file: {str(e)}")
                    transactions_df = None
            else:
                st.error(message)
    else:
        use_manual_expenses = True
        st.markdown("#### Enter your monthly expenses by category")
        cols = st.columns(3)
        for i, (emoji_cat, cat) in enumerate(MANUAL_EXPENSE_CATEGORIES):
            with cols[i % 3]:
                manual_expenses[cat] = st.number_input(
                    emoji_cat, min_value=0.0, step=50.0, value=0.0, key=f"manual_{cat}"
                )

        if manual_expenses and any(manual_expenses.values()):
            st.markdown("#### 📊 Summary of Entered Expenses")
            manual_df = pd.DataFrame({"Category": list(manual_expenses.keys()), "Amount": list(manual_expenses.values())})
            manual_df = manual_df[manual_df["Amount"] > 0]
            if not manual_df.empty:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.dataframe(
                        manual_df,
                        column_config={"Amount": st.column_config.NumberColumn("Amount", format="$%.2f")},
                        hide_index=True,
                    )
                with col2:
                    st.metric("Total Monthly Expenses", f"${manual_df['Amount'].sum():,.2f}")

    return transactions_df, manual_expenses, use_manual_expenses


_VERDICT_TONE = {"Healthy Surplus": "good", "Tight Budget": "warning", "Deficit": "critical"}


def render_history_section():
    theme.section_header("🕘", "History", "Every analysis run through this app, persisted locally on your machine")
    entries = history.load_history()
    if not entries:
        st.caption("No runs yet — click “Analyze My Finances” above to create your first entry.")
        return

    rows = [
        [
            str(i + 1),
            entry["timestamp"],
            f"${entry['monthly_income']:,.0f}",
            f"${entry['total_expenses']:,.0f}",
            f"${entry['total_debt']:,.0f}",
            theme.badge(entry["verdict"], _VERDICT_TONE.get(entry["verdict"], "neutral")),
        ]
        for i, entry in enumerate(entries)
    ]
    theme.render_table(["#", "When", "Income", "Expenses", "Total Debt", "Verdict"], rows)


def main():
    st.set_page_config(page_title="AI Financial Coach with Google ADK", layout="wide", initial_sidebar_state="expanded")
    theme.apply_theme()

    ui.render_sidebar()

    theme.render_topbar(
        brand="🛡️ AI Financial Coach",
        links=["Product", "How it works", "GitHub"],
        cta_label="Analyze Now",
    )

    if not GEMINI_API_KEY:
        st.error("🔑 GOOGLE_API_KEY not found in environment variables. Please add it to your .env file.")
        return

    theme.render_hero(
        eyebrow="Multi-Agent · Deterministic Finance Math",
        heading_line1="Get a financial plan your",
        heading_line2_gradient="own math would approve.",
        subtitle=(
            "AI Financial Coach pairs a deterministic Python finance engine with four Gemini agents "
            "via Google ADK — budgeting, savings, debt payoff, and goal planning, with every dollar "
            "figure computed, never guessed."
        ),
        stats=[
            {"value": "4", "label": "AI agents"},
            {"value": "100%", "label": "deterministic math"},
            {"value": "0", "label": "guessed numbers"},
        ],
    )

    input_tab, about_tab = st.tabs(["💼 Financial Information", "ℹ️ About"])

    with input_tab:
        st.caption("All data is processed locally and not stored anywhere.")

        with st.container(border=True):
            theme.section_header("💰", "Income & Household")
            monthly_income, dependants, income_stability = ui.render_income_and_household()
            current_emergency_savings = ui.render_emergency_savings_input()

        with st.container(border=True):
            transactions_df, manual_expenses, use_manual_expenses = render_expenses_section()

        with st.container(border=True):
            theme.section_header("🏦", "Debt Information", "Get avalanche and snowball payoff comparisons")
            debts = ui.render_debts_input()

        with st.container(border=True):
            theme.section_header("🎯", "Financial Goals", "Funded in priority order from your monthly surplus")
            goals = ui.render_goals_input()

        st.write("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button("🔄 Analyze My Finances", key="analyze_button", use_container_width=True)

        if analyze_button:
            expense_option = st.session_state.get("expense_option")
            if expense_option == "📤 Upload CSV Transactions" and transactions_df is None:
                st.error("Please upload a valid transaction CSV file or choose manual entry.")
                return
            if use_manual_expenses and (not manual_expenses or not any(manual_expenses.values())):
                st.warning("No manual expenses entered. Analysis might be limited.")

            st.divider()
            theme.section_header("📊", "Financial Analysis Results")
            with st.spinner("🤖 AI agents are analyzing your financial data..."):
                financial_data = {
                    "monthly_income": monthly_income,
                    "dependants": dependants,
                    "income_stability": income_stability,
                    "current_emergency_savings": current_emergency_savings,
                    "transactions": transactions_df.to_dict("records") if transactions_df is not None else None,
                    "manual_expenses": manual_expenses if use_manual_expenses else None,
                    "debts": debts,
                    "goals": goals,
                }

                finance_system = FinanceAdvisorSystem()

                try:
                    results = asyncio.run(finance_system.analyze_finances(financial_data))

                    budget = results.get("budget_analysis") or {}
                    debt = results.get("debt_reduction") or {}
                    ef = (results.get("savings_strategy") or {}).get("emergency_fund") or {}
                    surplus = (budget.get("monthly_income") or 0) - (budget.get("total_expenses") or 0)

                    theme.render_stat_row(
                        [
                            {"icon": "💵", "label": "Monthly Income", "value": f"${budget.get('monthly_income', 0):,.0f}"},
                            {"icon": "💳", "label": "Monthly Expenses", "value": f"${budget.get('total_expenses', 0):,.0f}"},
                            {
                                "icon": "📈" if surplus >= 0 else "📉",
                                "label": "Surplus / Deficit",
                                "value": f"${surplus:,.0f}",
                                "tone": "good" if surplus >= 0 else "critical",
                            },
                            {"icon": "🏦", "label": "Total Debt", "value": f"${debt.get('total_debt', 0):,.0f}"},
                            {
                                "icon": "🛟",
                                "label": "Emergency Fund",
                                "value": ef.get("current_status", "Unknown"),
                                "caption": f"Target: ${ef.get('recommended_amount', 0):,.0f}",
                            },
                        ]
                    )

                    tabs = st.tabs(["💰 Budget Analysis", "📈 Savings Strategy", "💳 Debt Reduction", "🎯 Goals"])

                    with tabs[0]:
                        ui.display_budget_analysis(results.get("budget_analysis"))
                    with tabs[1]:
                        ui.display_savings_strategy(results.get("savings_strategy"))
                    with tabs[2]:
                        ui.display_debt_reduction(results.get("debt_reduction"))
                    with tabs[3]:
                        ui.display_goal_plan(results.get("goal_plan"))

                    st.divider()
                    report_md = build_markdown_report(financial_data, results)
                    st.download_button(
                        "📄 Download Full Report (Markdown)",
                        data=report_md,
                        file_name="financial_plan.md",
                        mime="text/markdown",
                    )

                    history.append_history(
                        monthly_income=budget.get("monthly_income", 0) or 0,
                        total_expenses=budget.get("total_expenses", 0) or 0,
                        total_debt=debt.get("total_debt", 0) or 0,
                    )
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")

    st.divider()
    render_history_section()

    with about_tab:
        st.markdown(
            """
        ### About AI Financial Coach

        This application uses Google's Agent Development Kit (ADK) to provide comprehensive financial
        analysis through four specialized AI agents, each backed by deterministic Python math for
        anything that requires real arithmetic:

        1. **🔍 Budget Analysis Agent** — categorizes spending and identifies cost-reduction opportunities
        2. **💰 Savings Strategy Agent** — recommends savings allocations and automation techniques
           (emergency fund size is computed deterministically)
        3. **💳 Debt Reduction Agent** — writes payoff recommendations on top of a real amortization
           simulation of the avalanche and snowball methods
        4. **🎯 Goal Planning Agent** — prioritizes competing financial goals and explains tradeoffs
           (required contributions and timelines are computed deterministically)

        ### Privacy & Security

        - All data is processed locally
        - No financial information is stored or transmitted beyond the Gemini API call
        - Secure API communication with Google's services

        ### Need Help?

        For support or questions, open an issue on this project's GitHub repository.
        """
        )


if __name__ == "__main__":
    main()
