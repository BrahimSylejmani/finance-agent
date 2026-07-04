"""
agent.py
----------------------------------------------------------------
Multi-agent system for the Personal Finance Concierge (Concierge
Agents track).

Concept demonstrated: Multi-agent system (ADK)
  - root_agent orchestrates two specialist sub-agents and routes the
    user's question to whichever one fits: projecting forward from a
    contribution amount, or solving backwards from a savings target.

Concept demonstrated: Security features
  - Model name and credentials are read from environment variables
    (.env), never hardcoded. Every tool function independently
    validates its numeric inputs (see tools.py).
"""

import os
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool

from .tools import (
    project_investment_growth,
    adjust_for_inflation,
    compare_contribution_scenarios,
    required_monthly_contribution,
)

MODEL_NAME = os.environ.get("AGENT_MODEL", "groq/moonshotai/kimi-k2-instruct")


def _model():
    return LiteLlm(model=MODEL_NAME)


retirement_planning_agent = Agent(
    name="retirement_planning_agent",
    model=_model(),
    description=(
        "Projects how a given monthly contribution will grow by retirement, "
        "and shows what that balance is worth in today's money after inflation."
    ),
    instruction=(
        "You handle 'what will I end up with' questions. "
        "Given current age, retirement age, current savings, monthly "
        "contribution, and expected return, call project_investment_growth, "
        "then call adjust_for_inflation on the resulting nominal balance. "
        "If the user also wants to compare several contribution levels, use "
        "compare_contribution_scenarios instead. "
        "Never do the math yourself, always use the tools. "
        "State your assumptions clearly and note this is an educational "
        "estimate, not financial advice. "
        "Ask one clarifying question if information is missing."
    ),
    tools=[
        project_investment_growth,
        adjust_for_inflation,
        compare_contribution_scenarios,
    ],
)

goal_planning_agent = Agent(
    name="goal_planning_agent",
    model=_model(),
    description=(
        "Solves backwards from a savings goal: given a target amount, "
        "calculates the monthly contribution required to reach it."
    ),
    instruction=(
        "You handle 'how much do I need to save' questions. "
        "Given current age, retirement age, current savings, a target "
        "amount, and expected return, call required_monthly_contribution "
        "to find the needed monthly contribution. "
        "Never do the math yourself, always use the tool. "
        "State your assumptions clearly and note this is an educational "
        "estimate, not financial advice. "
        "Ask one clarifying question if information is missing, "
        "especially the target amount."
    ),
    tools=[required_monthly_contribution],
)

root_agent = Agent(
    name="finance_concierge_root",
    model=_model(),
    description=(
        "A personal finance concierge that routes retirement-planning "
        "questions to the right specialist: projecting forward from a "
        "contribution, or solving backwards from a savings goal."
    ),
    instruction=(
        "You are the front door for a personal finance concierge. "
        "If the user gives a monthly contribution amount and wants to know "
        "the resulting balance, call the retirement_planning_agent tool. "
        "If the user gives a target savings goal and wants to know the "
        "required monthly contribution, call the goal_planning_agent tool. "
        "If it's unclear which one fits, ask one short clarifying question "
        "before calling either tool. Pass the user's full request as the "
        "input to whichever tool you call."
    ),
    tools=[
        AgentTool(agent=retirement_planning_agent),
        AgentTool(agent=goal_planning_agent),
    ],
)