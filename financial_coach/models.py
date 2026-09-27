"""Pydantic schemas.

Schemas are split into two kinds:
  - "Insight" schemas (BudgetAnalysis, SavingsInsights, DebtInsights,
    GoalInsights) are what we ask the LLM agents to produce: categorization,
    narrative recommendations, and prioritization. Never raw arithmetic.
  - Plain dicts assembled in advisor.py hold the numbers computed by
    financial_coach.calculators (emergency fund size, payoff schedules,
    goal projections) and get merged with the insight schemas for display.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class SpendingCategory(BaseModel):
    category: str = Field(..., description="Expense category name")
    amount: float = Field(..., description="Amount spent in this category")
    percentage: Optional[float] = Field(None, description="Percentage of total spending")


class SpendingRecommendation(BaseModel):
    category: str = Field(..., description="Category for recommendation")
    recommendation: str = Field(..., description="Recommendation details")
    potential_savings: Optional[float] = Field(None, description="Estimated monthly savings")


class BudgetAnalysis(BaseModel):
    total_expenses: float = Field(..., description="Total monthly expenses")
    monthly_income: Optional[float] = Field(None, description="Monthly income")
    spending_categories: List[SpendingCategory] = Field(..., description="Breakdown of spending by category")
    recommendations: List[SpendingRecommendation] = Field(..., description="Spending recommendations")


class EmergencyFund(BaseModel):
    recommended_amount: float = Field(..., description="Recommended emergency fund size")
    current_amount: Optional[float] = Field(None, description="Current emergency fund (if any)")
    current_status: str = Field(..., description="Status assessment of emergency fund")


class SavingsRecommendation(BaseModel):
    category: str = Field(..., description="Savings category")
    amount: float = Field(..., description="Recommended monthly amount")
    rationale: Optional[str] = Field(None, description="Explanation for this recommendation")


class AutomationTechnique(BaseModel):
    name: str = Field(..., description="Name of automation technique")
    description: str = Field(..., description="Details of how to implement")


class SavingsInsights(BaseModel):
    """What the Savings Strategy Agent actually produces.

    The emergency fund number itself is computed deterministically in
    calculators.emergency_fund_target and merged in afterwards.
    """

    recommendations: List[SavingsRecommendation] = Field(..., description="Savings allocation recommendations")
    automation_techniques: Optional[List[AutomationTechnique]] = Field(
        None, description="Automation techniques to help save"
    )


class SavingsStrategy(BaseModel):
    emergency_fund: EmergencyFund
    recommendations: List[SavingsRecommendation]
    automation_techniques: Optional[List[AutomationTechnique]] = None


class Debt(BaseModel):
    name: str = Field(..., description="Name of debt")
    amount: float = Field(..., description="Current balance")
    interest_rate: float = Field(..., description="Annual interest rate (%)")
    min_payment: Optional[float] = Field(None, description="Minimum monthly payment")


class PayoffPlan(BaseModel):
    total_interest: float = Field(..., description="Total interest paid")
    months_to_payoff: int = Field(..., description="Months until debt-free")
    monthly_payment: Optional[float] = Field(None, description="Recommended monthly payment")


class PayoffPlans(BaseModel):
    avalanche: PayoffPlan = Field(..., description="Highest interest first method")
    snowball: PayoffPlan = Field(..., description="Smallest balance first method")


class DebtRecommendation(BaseModel):
    title: str = Field(..., description="Title of recommendation")
    description: str = Field(..., description="Details of recommendation")
    impact: Optional[str] = Field(None, description="Expected impact of this action")


class DebtInsights(BaseModel):
    """What the Debt Reduction Agent actually produces.

    The payoff plan numbers themselves are computed by
    calculators.amortize_debts (real amortization, not an LLM estimate).
    """

    recommendations: List[DebtRecommendation] = Field(..., description="Recommendations for debt reduction")


class DebtReduction(BaseModel):
    total_debt: float
    debts: List[Debt]
    payoff_plans: PayoffPlans
    recommendations: Optional[List[DebtRecommendation]] = None


class GoalInsights(BaseModel):
    """What the Goal Planning Agent produces.

    Feasibility, required contributions, and timelines are computed by
    calculators.evaluate_goals; the agent only prioritizes and explains
    tradeoffs when goals compete for limited surplus income.
    """

    prioritization_summary: str = Field(..., description="How the goals were prioritized and why")
    recommendations: List[str] = Field(..., description="Actionable recommendations for reaching the goals")
    tradeoffs: Optional[str] = Field(None, description="Tradeoffs between competing goals, if any")


class GoalProjection(BaseModel):
    name: str
    target_amount: float
    current_amount: float
    target_months: int
    required_monthly_contribution: float
    monthly_contribution_allocated: float
    projected_months_to_reach: int
    on_track: bool


class GoalPlan(BaseModel):
    available_monthly_surplus: float
    goals: List[GoalProjection]
    prioritization_summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    tradeoffs: Optional[str] = None
