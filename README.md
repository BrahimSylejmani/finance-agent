# Retirement Planning Agent

**Track:** Concierge Agents
**Course concepts demonstrated:** Agent (ADK), Security features, Deployability

## Problem

Most people know they *should* save for retirement, but have no easy way
to see how today's decisions (age, monthly contribution, expected return)
translate into real, inflation-adjusted purchasing power decades from now.
Spreadsheets are intimidating and static; financial advisors are expensive
and not always accessible. This is exactly the kind of personal, recurring
decision-support task a concierge agent is well suited for — the user's
financial details stay local and are never sent anywhere except to the
model for reasoning about the numbers it's given.

## Solution

A single conversational agent, built with Google's Agent Development Kit
(ADK), that:

1. Asks the user for their current age, target retirement age, current
   savings, monthly contribution, and expected annual return.
2. Calls a validated calculation tool to project the nominal balance at
   retirement.
3. Calls a second tool to convert that nominal figure into today's
   purchasing power, accounting for inflation.
4. Optionally compares several contribution levels side by side, so the
   user can see the impact of saving $100 vs $250 vs $500/month.

The agent never performs the math itself — all financial calculations
live in independently-tested, input-validated Python functions
(`tools.py`), and the agent's only job is to reason about *which* tool to
call and *how to explain the result* in plain language.

## Architecture

```
User (chat)
    |
    v
root_agent (ADK Agent, Gemini model)
    |
    |-- project_investment_growth(...)         [tool]
    |-- adjust_for_inflation(...)               [tool]
    |-- compare_contribution_scenarios(...)     [tool]
    |
    v
Validated numeric result -> natural-language explanation -> User
```

- **Agent layer** (`agent.py`): defines the `root_agent`, its instructions,
  and which tools it can call. Model name is read from an environment
  variable, not hardcoded.
- **Tool layer** (`tools.py`): pure functions with type-hinted signatures
  and docstrings (ADK auto-generates the tool schema from these). Every
  function validates its inputs and returns a structured error rather than
  raising, so a bad or adversarial input can't crash the agent loop.
- **Security**: no file, network, or credential access happens inside the
  tools; the only external dependency is the model call itself, which uses
  a key loaded from `.env` (gitignored, never committed).
- **Deployability**: a `Dockerfile` packages the whole agent so it can run
  identically on a laptop or on a cloud container platform (e.g. Cloud
  Run) — no code changes required between environments.

## Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd finance-agent

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# then edit .env and paste your Gemini API key
# (get one free at https://aistudio.google.com/apikey)

# 5. Run the agent
adk web .
# open the printed localhost URL and chat with the agent
```

### Run with Docker (deployability demo)

```bash
docker build -t retirement-agent .
docker run --env-file .env -p 8000:8000 retirement-agent
```

## Example interaction

> **User:** I'm 28, want to retire at 65, have $5,000 saved, and can put
> away $300/month. Assume 7% average annual return.
>
> **Agent:** *(calls `project_investment_growth`, then
> `adjust_for_inflation`)* — projects the nominal balance at 65, then
> explains what that's actually worth in today's money after inflation,
> and reminds the user this is an educational estimate, not financial
> advice.

## Limitations & disclaimers

This tool produces simplified educational projections. It does not
account for taxes, fees, variable market returns, or individual
circumstances, and is not a substitute for professional financial advice.
