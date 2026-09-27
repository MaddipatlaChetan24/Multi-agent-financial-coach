# 💰 AI Financial Coach

A multi-agent personal finance advisor built on **Google's Agent Development Kit (ADK)** and **Gemini**. It analyzes your income, expenses, debts, and goals, then produces a full financial plan: budget breakdown, savings strategy, a real debt payoff comparison, and a multi-goal funding plan — downloadable as a Markdown report.

> Forked and substantially rewritten from [Shubham Saboo's `ai_financial_coach_agent`](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_ai_agents/multi_agent_apps/ai_financial_coach_agent) example. See [NOTICE](NOTICE) for what changed and why.

## Why this fork exists

The original app asked an LLM to *compute* debt amortization schedules and emergency fund sizes from scratch. LLMs are not reliable calculators — two runs on the same inputs can produce different "total interest" numbers. This version draws a hard line:

> **Agents reason. Code computes.**

Every number that requires arithmetic — debt payoff schedules, emergency fund targets, goal contribution requirements — is computed by deterministic Python in [`financial_coach/calculators.py`](financial_coach/calculators.py) and covered by unit tests. The four Gemini-backed agents are only ever asked to categorize, prioritize, and write recommendations on top of numbers they're handed, never to invent them.

## Features

- **Four-agent pipeline (Google ADK `SequentialAgent`)**
  - 🔍 **Budget Analysis Agent** — categorizes spending, flags cost-reduction opportunities
  - 💰 **Savings Strategy Agent** — recommends savings allocations and automation techniques
  - 💳 **Debt Reduction Agent** — writes recommendations on top of a real avalanche/snowball simulation
  - 🎯 **Goal Planning Agent** *(new)* — prioritizes competing goals and explains tradeoffs when surplus income is tight

- **Real financial math, not LLM guesses**
  - True month-by-month amortization for both the avalanche and snowball debt payoff methods
  - Emergency fund sizing based on income stability and dependants
  - Compound-interest goal projections with a required-monthly-contribution solver
  - Multi-goal budgeting: goals are funded in priority order from whatever surplus is left after expenses and minimum debt payments, with realistic revised timelines for goals that don't fit

- **Expense input**
  - CSV upload (with format validation) or manual category entry
  - Multi-month CSV data now renders a spending trend chart by category — the original ignored the time dimension entirely

- **Downloadable report** — a full Markdown financial plan you can save or share

- **Accessible charts** — every chart uses a colorblind-safe, fixed-order palette; the original's pie chart (poor for 9 categories) and dual-unit grouped bar chart (mixing dollars and months on one axis) were replaced with ranked bars and single-metric small multiples

- **A dashboard, not a script** — a custom theme, gradient hero header, card-style input sections, and a 5-tile stat-card summary (income, expenses, surplus/deficit, debt, emergency fund) replace the default flat Streamlit look

- **Actually runs** — the original pinned `google-adk==0.1.0`, which imports a package it never declares as a dependency and fails on import. Pinned here to a working, tested version, with `create_session`/`get_session`/`delete_session` correctly awaited for the modern async ADK session API

## Architecture

```
app.py                      Streamlit entrypoint
financial_coach/
  models.py                 Pydantic schemas (LLM "insight" outputs vs. computed data)
  calculators.py            Deterministic finance math — unit tested
  csv_utils.py              CSV parsing, validation, monthly trend aggregation
  charts.py                 Plotly chart builders (colorblind-safe fixed palette)
  theme.py                  Custom CSS theme, hero header, stat cards, section headers
  agents.py                 The four ADK LlmAgent definitions + coordinator
  advisor.py                Orchestration: precompute -> run agents -> merge results
  report.py                 Markdown report generation
  ui.py                     Streamlit display + input-collection functions
tests/
  test_calculators.py       Unit tests for all deterministic math
```

## Setup

1. **Get a Gemini API key**: [Google AI Studio](https://aistudio.google.com/apikey)

2. **Clone and enter the project**
   ```bash
   git clone <this-repo-url>
   cd ai-financial-coach
   ```

3. **Create a `.env` file**
   ```bash
   cp .env.example .env
   # then edit .env and set GOOGLE_API_KEY
   ```

4. **Install dependencies**
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Run it**
   ```bash
   streamlit run app.py
   ```

### Run with Docker

```bash
docker build -t ai-financial-coach .
docker run -p 8501:8501 --env-file .env ai-financial-coach
```

### Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## CSV File Format

```csv
Date,Category,Amount
2024-01-01,Housing,1200.00
2024-01-02,Food,150.50
2024-01-03,Transportation,45.00
```

Required columns: `Date` (YYYY-MM-DD), `Category`, `Amount` (currency symbols/commas are stripped automatically). A template is available from the app's sidebar. Upload multiple months of data to see the spending trend chart.

## Privacy

All data is processed locally in your session; nothing is persisted to disk. Financial data is sent to Google's Gemini API only as part of generating the analysis.

## License

Apache License 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

This is an educational project, not professional financial advice.
