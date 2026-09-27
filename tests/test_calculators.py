import pytest

from financial_coach import calculators


def test_emergency_fund_target_stable_income():
    assert calculators.emergency_fund_target(2000, dependants=0, income_stability="stable") == 6000.0


def test_emergency_fund_target_variable_income():
    assert calculators.emergency_fund_target(2000, dependants=0, income_stability="variable") == 12000.0


def test_emergency_fund_target_caps_dependant_bonus():
    # 10 dependants * 0.5 = 5 months, capped at +3 -> 6 total months for stable income
    assert calculators.emergency_fund_target(1000, dependants=10, income_stability="stable") == 6000.0


def test_emergency_fund_status_thresholds():
    assert calculators.emergency_fund_status(0, 6000) == "Not started"
    assert calculators.emergency_fund_status(1000, 6000) == "Getting started"
    assert calculators.emergency_fund_status(3000, 6000) == "Halfway there"
    assert calculators.emergency_fund_status(6000, 6000) == "Fully funded"


def test_amortize_debts_zero_interest_single_debt():
    debts = [{"name": "Card", "amount": 1200.0, "interest_rate": 0.0, "min_payment": 100.0}]
    plan = calculators.amortize_debts(debts, "avalanche")
    assert plan["months_to_payoff"] == 12
    assert plan["total_interest"] == 0.0
    assert plan["monthly_payment"] == 100.0


def test_amortize_debts_extra_payment_speeds_payoff():
    debts = [{"name": "Card", "amount": 1200.0, "interest_rate": 0.0, "min_payment": 100.0}]
    baseline = calculators.amortize_debts(debts, "avalanche")
    with_extra = calculators.amortize_debts(debts, "avalanche", extra_payment=100.0)
    assert with_extra["months_to_payoff"] < baseline["months_to_payoff"]


def test_avalanche_never_pays_more_interest_than_snowball_when_high_rate_is_largest():
    # High-rate debt is also the largest balance: avalanche and snowball agree on
    # order here, so interest should be identical.
    debts = [
        {"name": "A", "amount": 500.0, "interest_rate": 25.0, "min_payment": 25.0},
        {"name": "B", "amount": 2000.0, "interest_rate": 5.0, "min_payment": 50.0},
    ]
    avalanche = calculators.amortize_debts(debts, "avalanche", extra_payment=100.0)
    snowball = calculators.amortize_debts(debts, "snowball", extra_payment=100.0)
    assert avalanche["total_interest"] <= snowball["total_interest"]


def test_amortize_debts_no_debts_returns_zeroed_plan():
    plan = calculators.amortize_debts([], "avalanche")
    assert plan == {"total_interest": 0.0, "months_to_payoff": 0, "monthly_payment": 0.0}


def test_required_monthly_contribution_zero_return_rate():
    contribution = calculators.required_monthly_contribution(target_amount=12000, current_amount=0, months=24)
    assert contribution == 500.0


def test_required_monthly_contribution_already_met():
    contribution = calculators.required_monthly_contribution(target_amount=1000, current_amount=1500, months=12)
    assert contribution == 0.0


def test_required_monthly_contribution_with_return_rate_reaches_target():
    contribution = calculators.required_monthly_contribution(
        target_amount=10000, current_amount=0, months=36, annual_return_rate=6.0
    )
    schedule = calculators.goal_projection_schedule(0, contribution, 36, annual_return_rate=6.0)
    assert schedule[-1]["balance"] == pytest.approx(10000, abs=1.0)


def test_project_goal_timeline_already_reached():
    assert calculators.project_goal_timeline(current_amount=5000, monthly_contribution=100, target_amount=4000) == 0


def test_available_monthly_surplus():
    debts = [{"name": "Card", "amount": 1000, "interest_rate": 10, "min_payment": 50}]
    surplus = calculators.available_monthly_surplus(monthly_income=3000, total_expenses=2000, debts=debts)
    assert surplus == 950.0


def test_evaluate_goals_funds_in_priority_order():
    goals = [
        {"name": "Emergency top-up", "target_amount": 1200, "current_amount": 0, "target_months": 12},
        {"name": "Vacation", "target_amount": 6000, "current_amount": 0, "target_months": 12},
    ]
    # Only enough surplus for the first goal's required $100/mo, nothing for the second.
    results = calculators.evaluate_goals(goals, available_surplus=100.0)

    assert results[0]["on_track"] is True
    assert results[0]["monthly_contribution_allocated"] == 100.0

    assert results[1]["on_track"] is False
    assert results[1]["monthly_contribution_allocated"] == 0.0
    assert results[1]["projected_months_to_reach"] > results[1]["target_months"]
