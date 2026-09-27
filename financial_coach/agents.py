"""Google ADK agent definitions.

Each agent's job is narrowed to what LLMs are actually good at: reading
context, categorizing, and writing recommendations. Numbers that require
arithmetic (emergency fund size, debt payoff schedules, goal timelines)
are computed in financial_coach.calculators and handed to the agents as
context rather than asked of them.
"""
from google.adk.agents import LlmAgent, SequentialAgent

from financial_coach.models import BudgetAnalysis, DebtInsights, GoalInsights, SavingsInsights

MODEL = "gemini-2.5-flash"


def build_budget_analysis_agent() -> LlmAgent:
    return LlmAgent(
        name="BudgetAnalysisAgent",
        model=MODEL,
        description="Analyzes financial data to categorize spending patterns and recommend budget improvements",
        instruction="""You are a Budget Analysis Agent specialized in reviewing financial transactions and expenses.
You are the first agent in a sequence of four financial advisor agents.

The exact spending-by-category totals are already computed and provided to you in
state['category_spending'] (or state['manual_category_spending']) and state['total_spending']
(or state['total_manual_spending']). Use those numbers exactly as given for amounts and
percentages - do not recompute or invent totals. Percentages must add up to 100%.

Your tasks:
1. Group the provided categories into a clear, well-labeled breakdown
2. Identify spending patterns and trends across categories
3. Suggest specific areas where spending could be reduced with concrete suggestions
4. Provide actionable recommendations with specific, quantified potential savings amounts

Consider:
- Number of dependants when evaluating household expenses
- Typical spending ratios for the income level (housing 30%, food 15%, etc.)
- Essential vs discretionary spending with clear separation
- Seasonal spending patterns if data spans multiple months

For recommendations:
- Provide at least 3-5 specific, actionable recommendations with estimated savings
- Explain the reasoning behind each recommendation
- Consider the impact on quality of life and long-term financial health
- Suggest specific implementation steps for each recommendation

IMPORTANT: Store your analysis in state['budget_analysis'] for use by subsequent agents.""",
        output_schema=BudgetAnalysis,
        output_key="budget_analysis",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )


def build_savings_strategy_agent() -> LlmAgent:
    return LlmAgent(
        name="SavingsStrategyAgent",
        model=MODEL,
        description="Recommends savings allocations and automation techniques based on budget analysis",
        instruction="""You are a Savings Strategy Agent specialized in creating personalized savings plans.
You are the second agent in the sequence. READ the budget analysis from state['budget_analysis'] first.

The recommended emergency fund size is already computed and provided in
state['computed_emergency_fund']['recommended_amount']. Do not recalculate it - reference it
in your reasoning if useful, but do not include it in your own output.

Your tasks:
1. Review the budget analysis results from state['budget_analysis']
2. Suggest appropriate savings allocation across different purposes (beyond the emergency fund)
3. Recommend practical automation techniques for saving consistently

Consider:
- Risk factors based on job stability and dependants
- Balancing immediate needs with long-term financial health
- Progressive savings rates as discretionary income increases
- Multiple savings goals (retirement, specific purchases)
- Areas of potential savings identified in the budget analysis

IMPORTANT: Store your output in state['savings_insights'] for use by the Debt Reduction Agent.""",
        output_schema=SavingsInsights,
        output_key="savings_insights",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )


def build_debt_reduction_agent() -> LlmAgent:
    return LlmAgent(
        name="DebtReductionAgent",
        model=MODEL,
        description="Writes debt reduction recommendations on top of precomputed avalanche/snowball payoff plans",
        instruction="""You are a Debt Reduction Agent specialized in debt payoff strategy recommendations.
You are the third agent in the sequence. READ state['budget_analysis'] and state['savings_insights'] first.

The actual avalanche and snowball payoff schedules (total interest, months to payoff) are
already computed with real amortization math and provided in state['computed_payoff_plans'].
Do not recalculate or restate these numbers - your job is recommendations only.

Your tasks:
1. Review the budget analysis, savings insights, and computed payoff plans in state
2. Suggest debt consolidation or refinancing opportunities where relevant
3. Provide specific recommendations to accelerate debt payoff
4. Note psychological factors (quick wins vs mathematical optimization) where relevant

Consider:
- Cash flow constraints from the budget analysis
- Emergency fund and savings goals from the savings insights
- Credit score impact and improvement opportunities

IMPORTANT: Store your output in state['debt_insights'].""",
        output_schema=DebtInsights,
        output_key="debt_insights",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )


def build_goal_planning_agent() -> LlmAgent:
    return LlmAgent(
        name="GoalPlanningAgent",
        model=MODEL,
        description="Prioritizes financial goals and explains tradeoffs given limited surplus income",
        instruction="""You are a Goal Planning Agent specialized in helping people balance multiple financial goals.
You are the final agent in the sequence. READ state['budget_analysis'], state['savings_insights'],
and state['debt_insights'] first.

The required monthly contribution, feasibility, and projected timeline for each goal are already
computed and provided in state['computed_goal_plan']['goals']. Do not recalculate these numbers.

Your tasks:
1. Explain how the goals were prioritized (they are funded in the order provided, using
   state['computed_goal_plan']['available_monthly_surplus'])
2. Give actionable recommendations for reaching the goals faster or making room in the budget
3. If any goal is not on_track, explain the tradeoff and what would need to change
   (e.g. reduce spending elsewhere, extend timeline, pay off debt faster first)

If there are no goals in state['computed_goal_plan']['goals'], say so briefly and skip
recommendations.

IMPORTANT: Store your output in state['goal_insights'].""",
        output_schema=GoalInsights,
        output_key="goal_insights",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )


def build_coordinator_agent() -> SequentialAgent:
    return SequentialAgent(
        name="FinanceCoordinatorAgent",
        description="Coordinates specialized finance agents to provide comprehensive financial advice",
        sub_agents=[
            build_budget_analysis_agent(),
            build_savings_strategy_agent(),
            build_debt_reduction_agent(),
            build_goal_planning_agent(),
        ],
    )
