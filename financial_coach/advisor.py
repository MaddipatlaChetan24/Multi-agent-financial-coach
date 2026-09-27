"""Orchestrates the agent pipeline and merges LLM insights with computed numbers."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from financial_coach import calculators
from financial_coach.agents import build_coordinator_agent

logger = logging.getLogger(__name__)

APP_NAME = "finance_advisor"
USER_ID = "default_user"


def parse_json_safely(data: Any, default_value: Any = None) -> Any:
    try:
        return json.loads(data) if isinstance(data, str) else data
    except json.JSONDecodeError:
        return default_value


class FinanceAdvisorSystem:
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.coordinator_agent = build_coordinator_agent()
        self.runner = Runner(
            agent=self.coordinator_agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )

    async def analyze_finances(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        session_id = f"finance_session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        try:
            expenses = self._resolve_expenses(financial_data)
            total_expenses = sum(expenses.values())
            monthly_income = financial_data.get("monthly_income", 0) or 0
            dependants = financial_data.get("dependants", 0) or 0
            debts = financial_data.get("debts", []) or []
            goals = financial_data.get("goals", []) or []
            current_emergency_savings = financial_data.get("current_emergency_savings", 0) or 0
            income_stability = financial_data.get("income_stability", "stable")

            computed_emergency_fund = self._compute_emergency_fund(
                total_expenses, dependants, income_stability, current_emergency_savings
            )
            computed_payoff_plans = self._compute_payoff_plans(debts)
            available_surplus = calculators.available_monthly_surplus(monthly_income, total_expenses, debts)
            computed_goal_plan = {
                "available_monthly_surplus": available_surplus,
                "goals": calculators.evaluate_goals(goals, available_surplus) if goals else [],
            }

            initial_state = {
                "monthly_income": monthly_income,
                "dependants": dependants,
                "transactions": financial_data.get("transactions", []),
                "manual_expenses": financial_data.get("manual_expenses", {}),
                "debts": debts,
                "category_spending": expenses,
                "total_spending": total_expenses,
                "computed_emergency_fund": computed_emergency_fund,
                "computed_payoff_plans": computed_payoff_plans,
                "computed_goal_plan": computed_goal_plan,
            }

            await self.session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id,
                state=initial_state,
            )

            default_results = self._create_default_results(
                financial_data, expenses, total_expenses, computed_emergency_fund,
                computed_payoff_plans, computed_goal_plan,
            )

            user_content = types.Content(role="user", parts=[types.Part(text=json.dumps(financial_data))])

            async for event in self.runner.run_async(
                user_id=USER_ID, session_id=session_id, new_message=user_content
            ):
                if event.is_final_response() and event.author == self.coordinator_agent.name:
                    break

            updated_session = await self.session_service.get_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=session_id
            )

            return self._merge_results(
                updated_session.state, default_results, computed_emergency_fund,
                computed_payoff_plans, debts, computed_goal_plan,
            )

        except Exception as e:
            logger.exception(f"Error during finance analysis: {str(e)}")
            raise
        finally:
            await self.session_service.delete_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)

    def _resolve_expenses(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        manual_expenses = financial_data.get("manual_expenses") or {}
        if manual_expenses:
            return {k: v for k, v in manual_expenses.items() if v}

        expenses: Dict[str, float] = {}
        for transaction in financial_data.get("transactions") or []:
            category = transaction.get("Category", "Uncategorized")
            amount = transaction.get("Amount", 0)
            expenses[category] = expenses.get(category, 0) + amount
        return expenses

    def _compute_emergency_fund(
        self, total_expenses: float, dependants: int, income_stability: str, current_amount: float
    ) -> Dict[str, Any]:
        recommended = calculators.emergency_fund_target(total_expenses, dependants, income_stability)
        return {
            "recommended_amount": recommended,
            "current_amount": current_amount,
            "current_status": calculators.emergency_fund_status(current_amount, recommended),
        }

    def _compute_payoff_plans(self, debts: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "avalanche": calculators.amortize_debts(debts, "avalanche"),
            "snowball": calculators.amortize_debts(debts, "snowball"),
        }

    def _merge_results(
        self,
        state: Dict[str, Any],
        default_results: Dict[str, Any],
        computed_emergency_fund: Dict[str, Any],
        computed_payoff_plans: Dict[str, Any],
        debts: List[Dict[str, Any]],
        computed_goal_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        budget_analysis = parse_json_safely(state.get("budget_analysis"), default_results["budget_analysis"])

        savings_insights = parse_json_safely(state.get("savings_insights"), {})
        savings_strategy = {
            "emergency_fund": computed_emergency_fund,
            "recommendations": savings_insights.get("recommendations", default_results["savings_strategy"]["recommendations"]),
            "automation_techniques": savings_insights.get(
                "automation_techniques", default_results["savings_strategy"]["automation_techniques"]
            ),
        }

        debt_insights = parse_json_safely(state.get("debt_insights"), {})
        debt_reduction = {
            "total_debt": sum(d.get("amount", 0) for d in debts),
            "debts": debts,
            "payoff_plans": computed_payoff_plans,
            "recommendations": debt_insights.get("recommendations", default_results["debt_reduction"]["recommendations"]),
        }

        goal_insights = parse_json_safely(state.get("goal_insights"), {})
        goal_plan = {
            **computed_goal_plan,
            "prioritization_summary": goal_insights.get("prioritization_summary"),
            "recommendations": goal_insights.get("recommendations"),
            "tradeoffs": goal_insights.get("tradeoffs"),
        }

        return {
            "budget_analysis": budget_analysis,
            "savings_strategy": savings_strategy,
            "debt_reduction": debt_reduction,
            "goal_plan": goal_plan,
        }

    def _create_default_results(
        self,
        financial_data: Dict[str, Any],
        expenses: Dict[str, float],
        total_expenses: float,
        computed_emergency_fund: Dict[str, Any],
        computed_payoff_plans: Dict[str, Any],
        computed_goal_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Fallback shown if the agent pipeline fails, using the same
        deterministic calculators as the real path (never fabricated math)."""
        monthly_income = financial_data.get("monthly_income", 0) or 0
        debts = financial_data.get("debts", []) or []

        return {
            "budget_analysis": {
                "total_expenses": total_expenses,
                "monthly_income": monthly_income,
                "spending_categories": [
                    {
                        "category": cat,
                        "amount": amt,
                        "percentage": (amt / total_expenses * 100) if total_expenses > 0 else 0,
                    }
                    for cat, amt in expenses.items()
                ],
                "recommendations": [
                    {
                        "category": "General",
                        "recommendation": "Consider reviewing your expenses carefully",
                        "potential_savings": total_expenses * 0.1,
                    }
                ],
            },
            "savings_strategy": {
                "emergency_fund": computed_emergency_fund,
                "recommendations": [
                    {"category": "Retirement", "amount": monthly_income * 0.15, "rationale": "Long-term savings"},
                ],
                "automation_techniques": [
                    {"name": "Automatic Transfer", "description": "Set up automatic transfers on payday"}
                ],
            },
            "debt_reduction": {
                "total_debt": sum(d.get("amount", 0) for d in debts),
                "debts": debts,
                "payoff_plans": computed_payoff_plans,
                "recommendations": [
                    {
                        "title": "Increase Payments",
                        "description": "Increase your monthly payments",
                        "impact": "Reduces total interest paid",
                    }
                ],
            },
            "goal_plan": computed_goal_plan,
        }
