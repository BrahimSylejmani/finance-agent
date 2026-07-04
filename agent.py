"""
agent.py
----------------------------------------------------------------
Root agent definition for the Personal Investment & Retirement
Planning Agent (Concierge Agents track).

Concept demonstrated: Agent / Multi-agent system (ADK)
  - A single ADK Agent equipped with domain tools that reasons about
    which tool(s) to call based on the user's natural-language request.

Concept demonstrated: Security features
  - The model name and any credentials are read from environment
    variables (.env), never hardcoded. Tool functions independently
    validate all numeric inputs (see tools.py) so the agent cannot be
    steered into producing nonsensical or unsafe financial output.
"""

import os
from google.adk import Agent

from .tools import (
    project_investment_growth,
    adjust_for_inflation,
    compare_contribution_scenarios,
)

MODEL_NAME = os.environ.get("AGENT_MODEL", "gemini-flash-latest")

root_agent = Agent(
    name="retirement_planning_agent",
    model=MODEL_NAME,
    description=(
        "A personal finance concierge agent that helps an individual "
        "understand how their monthly savings could grow toward retirement, "
        "accounting for compounding returns and inflation."
    ),
    instruction=(
        "You are a careful, encouraging personal finance assistant. "
        "You help the user understand long-term investment outcomes. "
        "Always use the provided tools to perform any calculation — never "
        "compute compound growth or inflation adjustments yourself, since "
        "the tools contain validated, tested logic. "
        "When a user gives you an age, contribution amount, or return rate, "
        "call project_investment_growth to get the nominal projection, "
        "then call adjust_for_inflation on the resulting balance so the "
        "user understands what that money is really worth today. "
        "If the user wants to compare multiple monthly contribution amounts, "
        "use compare_contribution_scenarios instead. "
        "Always clearly state assumptions (return rate, inflation rate) in "
        "your final answer, and remind the user this is an educational "
        "projection, not financial advice. "
        "If the user gives incomplete information (e.g. no current age), "
        "ask a single clarifying question before calling any tool."
    ),
    tools=[
        project_investment_growth,
        adjust_for_inflation,
        compare_contribution_scenarios,
    ],
)
