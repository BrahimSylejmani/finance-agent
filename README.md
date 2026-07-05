# 💰 Personal Finance Concierge Agent

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Google ADK](https://img.shields.io/badge/Google-ADK-green)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![LLM](https://img.shields.io/badge/LLM-Groq%20%7C%20LiteLLM-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

A multi-agent personal finance assistant built with **Google Agent Development Kit (ADK)** that helps users plan for retirement through natural language conversations.

Instead of requiring complex spreadsheets or financial calculators, the system allows users to simply ask questions such as:

- *"If I invest \$300 per month until retirement, how much will I have?"*
- *"I want \$1 million by retirement. How much should I save every month?"*

The application routes each request to a specialized AI agent, performs validated financial calculations through Python tools, and explains the results in plain language.

## Problem

Most people know they *should* save for retirement, but have no easy way to
translate today's decisions into real, inflation-adjusted outcomes — and the
question flows in two directions. Sometimes you know what you can contribute
and want to know what you'll end up with. Other times you have a target
number in mind and want to know what you'd need to save to hit it.
Spreadsheets handle one direction at a time and are intimidating to build;
financial advisors are expensive and not always accessible. This is exactly
the kind of personal, recurring decision-support task a concierge agent is
well suited for — the user's financial details stay local and are only used
by the model to reason about the numbers it's given.

# Features

- 🤖 Multi-agent architecture using Google ADK
- 📈 Retirement growth projections
- 🎯 Goal-based retirement planning
- 💵 Inflation-adjusted purchasing power calculations
- 📊 Compare multiple contribution scenarios
- ✅ Input validation inside every calculation tool
- 🔒 No file system or network access inside calculation tools
- 🐳 Docker support for deployment
- 🔄 Easily switch between Groq, Gemini, OpenAI, Anthropic, etc. via LiteLLM

## Solution

A **multi-agent system**, built with Google's Agent Development Kit (ADK),
made of a root agent and two specialist sub-agents:

- **`finance_concierge_root`** — the front door. Reads the user's request and
  routes it to whichever specialist fits, asking a clarifying question first
  if it's ambiguous.
- **`retirement_planning_agent`** — handles *"what will I end up with?"*
  Projects a monthly contribution forward to a nominal balance at retirement,
  then adjusts it for inflation so the user sees what that money is really
  worth today. Can also compare several contribution levels side by side.
- **`goal_planning_agent`** — handles *"how much do I need to save?"* Solves
  backwards from a target balance to the required monthly contribution.

Neither agent does math itself — every calculation lives in independently
validated, tested Python functions (`tools.py`). Each agent's only job is to
decide which tool to call and explain the result in plain language.

## Architecture

```
User (chat)
    |
    v
finance_concierge_root (ADK Agent, routes the request)
    |
    |-- retirement_planning_agent  [AgentTool]
    |       |-- project_investment_growth(...)
    |       |-- adjust_for_inflation(...)
    |       |-- compare_contribution_scenarios(...)
    |
    |-- goal_planning_agent        [AgentTool]
    |       |-- required_monthly_contribution(...)
    |
    v
Validated numeric result -> natural-language explanation -> User
```

- **Root agent** (`agent.py`): `finance_concierge_root` holds no domain tools
  of its own — it routes to the two specialist agents, each wrapped as an
  `AgentTool`. This keeps routing explicit and reliable rather than relying
  on free-form agent-to-agent handoff.
- **Specialist agents** (`agent.py`): each owns a narrow slice of the problem
  and its own tools, so their instructions stay focused and less error-prone.
- **Tool layer** (`tools.py`): pure functions with type-hinted signatures and
  docstrings (ADK auto-generates the tool schema from these). Every function
  validates its inputs and returns a structured error rather than raising, so
  a bad or adversarial input can't crash the agent loop.
- **Security**: no file, network, or credential access happens inside the
  tools; the only external dependency is the model call itself, which reads
  its API key from `.env` (gitignored, never committed).
- **Deployability**: a `Dockerfile` packages the whole system so it can run
  identically on a laptop or a cloud container platform (e.g. Cloud Run) — no
  code changes required between environments.
- **Model**: runs on Groq (`groq/moonshotai/kimi-k2-instruct`) via ADK's
  `LiteLlm` wrapper, so the same agent code can point at Groq, OpenAI,
  Anthropic, or Gemini just by changing an environment variable.

## Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd finance_agent

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# then edit .env and add your own Groq API key
# (free, no credit card required: https://console.groq.com)

# 5. Run the agent
adk web .
# open the printed localhost URL, select finance_agent, and chat
```

### Run with Docker (deployability demo)

```bash
docker build -t finance-concierge-agent .
docker run --env-file .env -p 8000:8000 finance-concierge-agent
```

# Website Screenshots

## Home Interface

<img width="1859" height="958" alt="image" src="https://github.com/user-attachments/assets/a1137253-db6c-4605-bb3b-8f1613334889" />


## Example interactions

> **User:** I'm 28, retire at 65, $5,000 saved, $300/month, 7% return.
>
> **Agent:** *(routes to `retirement_planning_agent`, which calls
> `project_investment_growth` then `adjust_for_inflation`)* — projects a
> nominal balance of ~$695,113 at retirement, worth ~$232,851 in today's
> money after inflation, with assumptions stated clearly.

> **User:** I'm 28, retire at 65, $5,000 saved, want $1,000,000, 7% return.
>
> **Agent:** *(routes to `goal_planning_agent`, which calls
> `required_monthly_contribution`)* — reports a required monthly contribution
> of ~$445.42 to hit that target, with assumptions and disclaimers stated.

## Limitations & disclaimers

This tool produces simplified educational projections. It does not account
for taxes, fees, variable market returns, or individual circumstances, and is
not a substitute for professional financial advice.

# Team

Developed by

- **Brahim Sylejmani**
- **Enis Hoxha**
