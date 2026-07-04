"""
tools.py
----------------------------------------------------------------
Tool functions exposed to the agent. Each function is a plain,
well-documented Python function with type hints — ADK auto-generates
the tool schema from the signature + docstring, so keep both clear.

SECURITY NOTE: these functions only accept and return numeric/string
data the user explicitly provides in the conversation. No file system,
network, or credential access happens here, so there is no injection
or data-exfiltration surface in this tool layer.
"""

from typing import Dict


def project_investment_growth(
    current_age: int,
    retirement_age: int,
    monthly_contribution: float,
    current_savings: float,
    annual_return_pct: float,
) -> Dict:
    """Projects the future value of a monthly-contribution investment plan.

    Args:
        current_age: The user's current age in years (must be 0-100).
        retirement_age: The target retirement age (must be > current_age).
        monthly_contribution: Amount invested every month, in the user's currency.
        current_savings: Amount already saved/invested today.
        annual_return_pct: Expected average annual return, e.g. 7 for 7%.

    Returns:
        A dict with the number of years invested, total contributed,
        and the projected nominal balance at retirement.
    """
    # --- input validation (security / robustness) ---
    if not (0 <= current_age <= 100):
        return {"error": "current_age must be between 0 and 100."}
    if retirement_age <= current_age:
        return {"error": "retirement_age must be greater than current_age."}
    if monthly_contribution < 0 or current_savings < 0:
        return {"error": "contribution and savings must be non-negative."}
    if not (-20 <= annual_return_pct <= 50):
        return {"error": "annual_return_pct looks unrealistic; expected -20 to 50."}

    years = retirement_age - current_age
    months = years * 12
    monthly_rate = (annual_return_pct / 100) / 12

    balance = current_savings
    total_contributed = current_savings
    for _ in range(months):
        balance *= (1 + monthly_rate)
        balance += monthly_contribution
        total_contributed += monthly_contribution

    return {
        "years_invested": years,
        "total_contributed": round(total_contributed, 2),
        "projected_balance_nominal": round(balance, 2),
        "growth_from_returns": round(balance - total_contributed, 2),
    }


def adjust_for_inflation(nominal_amount: float, years: int, inflation_pct: float = 3.0) -> Dict:
    """Converts a future nominal amount into today's purchasing power.

    Args:
        nominal_amount: The future amount in nominal (non-adjusted) terms.
        years: Number of years in the future that amount refers to.
        inflation_pct: Assumed average annual inflation rate, default 3%.

    Returns:
        A dict with the inflation-adjusted ("real") value.
    """
    if nominal_amount < 0 or years < 0:
        return {"error": "nominal_amount and years must be non-negative."}
    if not (0 <= inflation_pct <= 30):
        return {"error": "inflation_pct looks unrealistic; expected 0 to 30."}

    real_value = nominal_amount / ((1 + inflation_pct / 100) ** years)
    return {
        "nominal_amount": round(nominal_amount, 2),
        "real_value_today": round(real_value, 2),
        "inflation_pct_assumed": inflation_pct,
        "years": years,
    }


def compare_contribution_scenarios(
    current_age: int,
    retirement_age: int,
    current_savings: float,
    annual_return_pct: float,
    contribution_options: str,
) -> Dict:
    """Compares retirement outcomes across several monthly contribution levels.

    Args:
        current_age: The user's current age.
        retirement_age: Target retirement age.
        current_savings: Amount already saved today.
        annual_return_pct: Expected average annual return, e.g. 7 for 7%.
        contribution_options: Comma-separated monthly contribution amounts,
            e.g. "100,250,500".

    Returns:
        A dict mapping each contribution amount to its projected balance.
    """
    try:
        options = [float(x.strip()) for x in contribution_options.split(",") if x.strip()]
    except ValueError:
        return {"error": "contribution_options must be comma-separated numbers, e.g. '100,250,500'."}

    if not options:
        return {"error": "Provide at least one contribution amount."}

    results = {}
    for amount in options:
        result = project_investment_growth(
            current_age, retirement_age, amount, current_savings, annual_return_pct
        )
        results[f"${amount:.0f}/month"] = result

    return results
