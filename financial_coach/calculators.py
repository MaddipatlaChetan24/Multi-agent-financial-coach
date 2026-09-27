"""Deterministic financial math.

The original app asked the LLM to invent debt amortization numbers
(total interest, months to payoff) from scratch. LLMs are unreliable at
multi-step arithmetic, so this module computes every hard number in plain
Python. Agents are only ever asked to reason over numbers computed here,
never to produce them.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal

Strategy = Literal["avalanche", "snowball"]


def emergency_fund_target(
    monthly_expenses: float,
    dependants: int,
    income_stability: Literal["stable", "variable"] = "stable",
) -> float:
    """Recommended emergency fund size.

    Base of 3 months (stable income) or 6 months (variable/self-employed
    income), plus half a month of coverage per dependant, capped at +3
    months so large families don't get an unrealistic target.
    """
    base_months = 3.0 if income_stability == "stable" else 6.0
    dependant_months = min(max(dependants, 0) * 0.5, 3.0)
    return round(monthly_expenses * (base_months + dependant_months), 2)


def emergency_fund_status(current_amount: float, recommended_amount: float) -> str:
    if recommended_amount <= 0:
        return "Not applicable"
    ratio = current_amount / recommended_amount
    if ratio >= 1:
        return "Fully funded"
    if ratio >= 0.5:
        return "Halfway there"
    if ratio > 0:
        return "Getting started"
    return "Not started"


def _order_debts(debts: List[Dict[str, Any]], strategy: Strategy) -> List[str]:
    if strategy == "avalanche":
        ordered = sorted(debts, key=lambda d: d.get("interest_rate", 0.0), reverse=True)
    else:
        ordered = sorted(debts, key=lambda d: d.get("amount", 0.0))
    return [d["name"] for d in ordered]


def amortize_debts(
    debts: List[Dict[str, Any]],
    strategy: Strategy,
    extra_payment: float = 0.0,
    max_months: int = 600,
) -> Dict[str, float]:
    """Simulate a real payoff schedule for the avalanche or snowball method.

    The total monthly budget (sum of minimum payments + extra_payment)
    stays constant. Every debt gets at least its minimum payment; the
    debt at the front of the strategy's order (highest rate, or smallest
    balance) receives whatever budget is left over each month, including
    minimum payments freed up by debts that have already been paid off.
    """
    active_debts = [d for d in debts if d.get("amount", 0) > 0]
    if not active_debts:
        return {"total_interest": 0.0, "months_to_payoff": 0, "monthly_payment": 0.0}

    balances = {d["name"]: float(d["amount"]) for d in active_debts}
    monthly_rates = {d["name"]: float(d.get("interest_rate", 0.0)) / 100 / 12 for d in active_debts}
    min_payments = {d["name"]: float(d.get("min_payment") or 0.0) for d in active_debts}
    order = _order_debts(active_debts, strategy)

    monthly_budget = sum(min_payments.values()) + extra_payment
    total_interest = 0.0
    months = 0

    while any(balances[n] > 0.01 for n in balances) and months < max_months:
        months += 1

        for name in order:
            if balances[name] > 0:
                interest = balances[name] * monthly_rates[name]
                total_interest += interest
                balances[name] += interest

        target = next((n for n in order if balances[n] > 0.01), None)
        remaining_budget = monthly_budget
        for name in order:
            if balances[name] <= 0 or name == target:
                continue
            pay = min(min_payments[name], balances[name])
            balances[name] -= pay
            remaining_budget -= pay

        if target is not None:
            pay = min(remaining_budget, balances[target])
            balances[target] -= pay

    return {
        "total_interest": round(total_interest, 2),
        "months_to_payoff": months,
        "monthly_payment": round(monthly_budget, 2),
    }


def required_monthly_contribution(
    target_amount: float,
    current_amount: float,
    months: int,
    annual_return_rate: float = 0.0,
) -> float:
    """Monthly contribution needed to reach target_amount in `months` months."""
    remaining = max(target_amount - current_amount, 0.0)
    if months <= 0:
        return round(remaining, 2)
    if annual_return_rate == 0:
        return round(remaining / months, 2)

    r = annual_return_rate / 100 / 12
    growth_of_current = current_amount * (1 + r) ** months
    remaining_needed = target_amount - growth_of_current
    if remaining_needed <= 0:
        return 0.0
    denom = ((1 + r) ** months - 1) / r
    return round(remaining_needed / denom, 2)


def project_goal_timeline(
    current_amount: float,
    monthly_contribution: float,
    target_amount: float,
    annual_return_rate: float = 0.0,
    max_months: int = 600,
) -> int:
    """Months until target_amount is reached at a given contribution rate."""
    if current_amount >= target_amount:
        return 0
    if monthly_contribution <= 0 and annual_return_rate <= 0:
        return max_months

    r = annual_return_rate / 100 / 12
    balance = current_amount
    for month in range(1, max_months + 1):
        balance = balance * (1 + r) + monthly_contribution
        if balance >= target_amount:
            return month
    return max_months


def goal_projection_schedule(
    current_amount: float,
    monthly_contribution: float,
    months: int,
    annual_return_rate: float = 0.0,
) -> List[Dict[str, float]]:
    """Month-by-month balance schedule, for charting."""
    r = annual_return_rate / 100 / 12
    balance = current_amount
    schedule = [{"month": 0, "balance": round(balance, 2)}]
    for month in range(1, max(months, 0) + 1):
        balance = balance * (1 + r) + monthly_contribution
        schedule.append({"month": month, "balance": round(balance, 2)})
    return schedule


def available_monthly_surplus(
    monthly_income: float,
    total_expenses: float,
    debts: List[Dict[str, Any]],
) -> float:
    """Income left over after expenses and required minimum debt payments."""
    min_payments = sum(float(d.get("min_payment") or 0.0) for d in debts)
    return round(monthly_income - total_expenses - min_payments, 2)


def evaluate_goals(
    goals: List[Dict[str, Any]],
    available_surplus: float,
    max_months: int = 600,
) -> List[Dict[str, Any]]:
    """Allocate available surplus across goals in priority (list) order.

    Each goal gets funded up to what's needed to hit its own timeframe;
    once the surplus runs out, later goals get whatever remains and a
    realistic (longer) projected timeline instead of the requested one.
    """
    results = []
    remaining_surplus = max(available_surplus, 0.0)

    for goal in goals:
        target_amount = float(goal["target_amount"])
        current_amount = float(goal.get("current_amount", 0.0))
        target_months = int(goal["target_months"])
        annual_return_rate = float(goal.get("annual_return_rate", 0.0))

        required = required_monthly_contribution(
            target_amount, current_amount, target_months, annual_return_rate
        )
        allocated = min(required, remaining_surplus)
        on_track = allocated >= required - 0.01
        remaining_surplus = max(remaining_surplus - allocated, 0.0)

        projected_months = (
            target_months
            if on_track
            else project_goal_timeline(current_amount, allocated, target_amount, annual_return_rate, max_months)
        )

        results.append(
            {
                "name": goal["name"],
                "target_amount": target_amount,
                "current_amount": current_amount,
                "target_months": target_months,
                "required_monthly_contribution": required,
                "monthly_contribution_allocated": round(allocated, 2),
                "projected_months_to_reach": projected_months,
                "on_track": on_track,
            }
        )

    return results
