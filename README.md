# PulseOps AI

**Post-Event Lead Intelligence & Automated Ops Engine for Zuddl**

> Built for Zuddl's internal Revenue, Marketing, and Event Ops teams.
> Automates post-event lead qualification, synthesizes buying intent from session signals,
> and generates verified SDR outreach — turning hours of manual spreadsheet work into seconds.

---

## The Problem

After every webinar, virtual summit, or field event hosted on Zuddl, Revenue and Marketing teams face the same bottleneck:

1. **Hundreds of attendee records** land in a CSV — names, watch times, poll answers, Q&A logs.
2. A human manually reads through transcripts and chat logs to guess who is "hot."
3. SDRs draft generic follow-up emails days later.
4. By then, **60%+ of high-intent attendees have gone cold**.

The gap between "event ends" and "sales rep reaches out" is where pipeline dies.

**PulseOps AI closes that gap in under 2 seconds.**

---

## How It Works

```
                    ┌──────────────────────────┐
                    │  Zuddl Event Stream /    │
                    │  Webhook / JSON Upload    │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   FastAPI Ingestion API   │
                    └────┬───────────────┬─────┘
                         │               │
            ┌────────────▼──┐   ┌────────▼────────────┐
            │ Deterministic │   │  AI Semantic Engine  │
            │ Rules Engine  │   │  (Intent Extraction) │
            │ (60% weight)  │   │  (40% weight)        │
            └────────┬──────┘   └──────┬───────────────┘
                     │                 │
                     │    ┌────────────▼──────────────┐
                     │    │ Hallucination Guardrails   │
                     │    │ (Ground Truth Verification)│
                     │    └────────────┬──────────────┘
                     │                 │
            ┌────────▼─────────────────▼──────┐
            │         SQLite Database          │
            │  (Events → Attendees → Signals  │
            │   → Intelligence → Campaigns)   │
            └────────────────┬────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──┐  ┌───────▼───┐  ┌───────▼──────┐
     │ Web       │  │ REST API  │  │ CLI Tool     │
     │ Dashboard │  │ + Swagger │  │ (pulseops)   │
     └───────────┘  └───────────┘  └──────────────┘
```

### Dual-Engine Scoring

| Engine | Weight | What It Calculates | Why It's Separate |
|--------|--------|-------------------|-------------------|
| **Deterministic Rules** | 60% | Watch-time %, ICP role authority, poll/Q&A interaction count | These are **mathematical facts**. No LLM should hallucinate a watch-time percentage. |
| **AI Semantic Analysis** | 40% | Pain point extraction from Q&A, buying urgency, commercial intent signals | Unstructured text requires **language understanding**, not arithmetic. |

### Hallucination Guardrails

Every AI-cited quote is cross-verified against the attendee's actual Q&A questions and poll responses.
If the LLM claims the attendee said something they never said, the confidence score is **severely penalized**
and the lead is flagged for human review.

---

## Where AI Belongs vs. Where It Doesn't

This is the core engineering philosophy of PulseOps AI:

### ✅ Where AI belongs
- Synthesizing messy, unstructured Q&A transcripts into structured pain points
- Detecting commercial urgency signals in natural language ("budget allocated", "timeline is Q4")
- Generating hyper-personalized follow-up emails that reference the attendee's exact question
- Drafting contextual LinkedIn connection messages

### ❌ Where AI does NOT belong
- Calculating attendance percentages (pure division — no hallucination risk)
- Classifying ICP tiers from job titles (deterministic keyword matching)
- Computing engagement scores from poll counts (simple weighted arithmetic)
- Deduplicating attendee records (exact string matching)

**Mixing these up is the #1 mistake in AI-powered tooling.** PulseOps AI keeps them strictly separated.

---

## Quick Start

### Prerequisites
- Python 3.10+ (tested with 3.13)
- pip

### Setup & Run

```bash
# 1. Clone and enter the project
git clone https://github.com/Kaustubh3124/pulseops-ai.git
cd pulseops-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Copy and configure environment
cp .env.example .env
# Edit .env to add a Gemini or OpenAI key for live AI — or leave blank for offline demo mode

# 4. Start the server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 5. Open the dashboard
# Visit http://127.0.0.1:8000 in your browser

# 6. Or use the Swagger API docs
# Visit http://127.0.0.1:8000/docs
```

The database auto-seeds with a realistic demo scenario on first launch.

### CLI Usage

```bash
# Seed demo data
python cli.py seed

# Ingest a custom event payload
python cli.py ingest sample_event.json

# Run the scoring pipeline
python cli.py process --event-id 1

# View scored leads (filter by tier)
python cli.py list --event-id 1
python cli.py list --event-id 1 --tier HOT
```

### Run Tests

```bash
python -m pytest -v
```

All 14 tests should pass: rules engine, guardrails, and full API integration.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | Python 3.13 + FastAPI | Async-ready, automatic Swagger docs, Pydantic v2 validation |
| **Database** | SQLite + SQLAlchemy 2.0 | Zero-config relational store; ORM for clean data modeling |
| **AI Engine** | Gemini API (live) / Offline Synthesizer (demo) | Seamless fallback so reviewers can test without API keys |
| **Frontend** | Vanilla HTML5 + CSS + JavaScript | No framework overhead; purpose-built interactive dashboard |
| **Testing** | pytest + FastAPI TestClient | Unit tests for rules, guardrails, and full E2E API integration |
| **CLI** | argparse | Standard library, zero dependencies |

---

## Data Model

```
Event (1) ──→ (N) Attendee
                    │
                    ├── (1) EngagementSignal
                    │       watch_time, polls, Q&A, chat, booth visits
                    │
                    ├── (1) LeadIntelligence
                    │       deterministic_score, ai_intent_score, final_score
                    │       intent_tier (HOT/WARM/COLD)
                    │       key_pain_points, buying_signals
                    │       ground_truth_quote, hallucination_verified
                    │
                    └── (1) CampaignDraft
                            email_subject, email_body, linkedin_message
                            slack_alert_payload, status (DRAFT/APPROVED/DISPATCHED)

Event (1) ──→ (N) AuditLog
                    operation, execution_time_ms
```

### Why relational?

Sales pipelines have **strict referential integrity requirements**. An attendee's engagement signals,
AI-generated intelligence, and campaign drafts must always trace back to exactly one event and one person.
Document stores make this error-prone. A normalized relational schema prevents orphaned records,
makes joins efficient, and keeps the audit trail clean.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/events` | List all events |
| `POST` | `/api/events` | Create new event |
| `POST` | `/api/events/ingest` | Ingest event stream with attendees |
| `POST` | `/api/events/{id}/process` | Run dual-engine scoring pipeline |
| `GET` | `/api/events/{id}/leads` | Get scored leads (filter by tier) |
| `GET` | `/api/leads/{id}/dossier` | Deep lead dossier |
| `POST` | `/api/leads/{id}/dispatch` | Dispatch to Slack/CRM webhook |
| `GET` | `/api/analytics/summary` | Aggregate KPIs |
| `POST` | `/api/seed-demo` | Reset demo scenario |

Full interactive documentation at **`/docs`** (Swagger UI).

---

## Project Structure

```
pulseops-ai/
├── app/
│   ├── __init__.py          # Package marker
│   ├── database.py          # SQLAlchemy engine, sessions, Base
│   ├── models.py            # ORM models (Event, Attendee, Signal, Intel, Campaign, Audit)
│   ├── schemas.py           # Pydantic v2 request/response schemas
│   ├── rules_engine.py      # Deterministic scoring (NO AI)
│   ├── ai_engine.py         # Semantic extraction + hallucination guardrails
│   ├── seed_data.py         # Demo scenario generator
│   └── main.py              # FastAPI application + REST endpoints
├── static/
│   ├── index.html           # Interactive web dashboard
│   ├── css/styles.css        # Design system (Zuddl aesthetic)
│   └── js/app.js            # Client-side controller
├── tests/
│   ├── test_rules_engine.py # Deterministic scoring tests
│   ├── test_guardrails.py   # Hallucination detection tests
│   └── test_api.py          # Full API integration tests
├── cli.py                   # Terminal CLI tool
├── sample_event.json        # Sample ingest payload
├── requirements.txt         # Python dependencies
├── .env.example             # Environment config template
├── .gitignore               # Git exclusions (no secrets!)
└── README.md                # This file
```

---

## AI Tooling & Engineering Journal

This project was built using **Antigravity IDE (Google)** as the primary AI coding assistant. The agent was used aggressively for rapid scaffolding, test generation, and boilerplate. However, the architectural decisions, data model normalization, and critical bug fixes came from human judgment and deep-dive debugging.

### Where AI Got It Wrong & How I Debugged It

#### 1. SQLite Concurrency Crash in Async FastAPI
- **What the AI did**: Generated standard synchronous SQLAlchemy session handlers without considering FastAPI's threadpool dispatcher.
- **How it broke**: Under concurrent API calls, SQLite raised `ProgrammingError: SQLite objects created in a thread can only be used in that same thread`.
- **The fix**: Diagnosed the thread affinity issue. Configured `connect_args={"check_same_thread": False}` on the engine, ensured thread-safe scoped sessions, and verified database lifecycle with FastAPI's `lifespan` handler.

#### 2. Pydantic V1 vs V2 Deprecation Drift
- **What the AI did**: Generated schemas using outdated Pydantic v1 idioms (`class Config: orm_mode = True`, `schema_extra`).
- **How it broke**: FastAPI raised deprecation warnings and failed serialization on certain nested relationships.
- **The fix**: Audited `app/schemas.py`, migrated all schemas to Pydantic v2 `model_config = ConfigDict(from_attributes=True)`, and moved examples to `json_schema_extra`.

#### 3. Windows Terminal UnicodeEncodeError Crash
- **What the AI did**: Littered CLI print statements with fancy Unicode emojis (`🚀`, `🔥`, `📊`).
- **How it broke**: On standard Windows command prompts (`cp1252` encoding), the CLI immediately crashed with `UnicodeEncodeError: 'charmap' codec can't encode character`.
- **The fix**: Reconfigured `sys.stdout` encoding to UTF-8 and replaced fragile emojis with standardized ASCII status tags (`[HOT]`, `[OK]`, `[ERROR]`, `[PASS]`) that render reliably across any OS or CI/CD runner.

#### 4. Hallucinated Quote Attribution in Lead Scoring
- **What the AI did**: Left unconstrained, LLMs tend to invent quotes or attribute one attendee's question to another when summarizing event transcripts.
- **How it broke**: Reviewing raw LLM outputs revealed "hallucinated quotes" that sounded persuasive but never occurred in the actual event logs.
- **The fix**: Designed and implemented `verify_grounding()` in `app/ai_engine.py`. It performs deterministic token overlap and substring verification against raw attendee inputs. If an LLM fabricates a quote, the confidence score is penalized and flagged for human review.

---



