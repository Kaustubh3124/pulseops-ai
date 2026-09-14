# PulseOps AI — Zuddl AI Internship Submission Guide

> Pre-drafted answers for every form field. Copy, personalize with your details, paste.

---

## Page 1: Basic Information

| Field | What to Enter |
|-------|--------------|
| **First name** | _Your first name_ |
| **Last name** | _Your last name_ |
| **Email** | _Your email_ |
| **Phone** | _+91 Your number_ |
| **Current city** | _Your city_ |
| **LinkedIn** | _Your LinkedIn URL_ |
| **GitHub** | `https://github.com/Kaustubh3124/pulseops-ai` |
| **Resume** | Upload the PDF from `RESUME_TIPS.md` below |

---

## Page 2: Education

Fill in your actual education details:
- **Degree**: B.Tech / B.E. in Computer Science (or your actual degree)
- **University**: _Your university name_
- **Year**: _Your current year or graduation year_

---

## Page 3: The Project

### Project Name
```
PulseOps AI — Post-Event Lead Intelligence & Automated Ops Engine
```

### GitHub Repository Link
```
https://github.com/Kaustubh3124/pulseops-ai
```

### Live Demo Link
```
(If deployed) https://pulseops-ai.onrender.com
OR
See video demo below — runs locally with one command (python -m uvicorn app.main:app)
```

### What problem does it solve? Who has this problem?

> **Copy this (then personalize):**
>
> After every virtual event hosted on Zuddl, Revenue and Marketing teams face a painful bottleneck: hundreds of attendee records land in a CSV — names, watch times, poll answers, Q&A logs — and a human manually reads through them to guess who's "hot." SDRs draft generic follow-ups days later. By then, 60%+ of high-intent attendees have gone cold.
>
> PulseOps AI automates the entire post-event lead qualification pipeline. It ingests event stream data (attendees, engagement signals, Q&A transcripts), runs a dual-engine scoring pipeline — deterministic rules for mathematical facts (watch-time, ICP fit) and AI semantic analysis for unstructured intent signals (buying urgency in Q&A) — and generates verified, hyper-personalized outreach within seconds.
>
> The people who have this problem: Zuddl's own Revenue Ops, Event Ops, and Customer Success teams. Every Zuddl customer running events has this problem too.

---

## Page 4: What It Does & How You Built It

### Detailed Description of Functionality

> **Copy this (then personalize):**
>
> PulseOps AI is a full-stack intelligence engine with three interfaces:
>
> **1. REST API (FastAPI + Swagger)** — Ingest event payloads via webhook-style POST, trigger the scoring pipeline, retrieve scored leads filtered by tier (HOT/WARM/COLD), and dispatch alerts to Slack/CRM.
>
> **2. Interactive Web Dashboard** — Real-time KPI cards (total leads, hot leads, average score), searchable lead pipeline table with tier badges, and deep-dive lead dossiers showing AI-extracted pain points, buying signals, and one-click campaign generation (personalized email + LinkedIn message).
>
> **3. CLI Tool** — Terminal interface for ops engineers: seed demo data, ingest custom JSON payloads, run the pipeline, and export lead tables.
>
> The core innovation is the **dual-engine architecture**:
> - A **Deterministic Rules Engine** (60% weight) handles watch-time percentage, ICP role authority, and interaction counts — pure math with zero hallucination risk.
> - An **AI Semantic Engine** (40% weight) synthesizes Q&A transcripts for pain point extraction, buying urgency signals, and commercial intent detection.
> - A **Hallucination Guardrail Filter** cross-verifies every AI-cited quote against the attendee's actual session data. If the LLM fabricates something the attendee never said, the confidence score is penalized and the lead is flagged for human review.
>
> The scoring formula: `final_score = (0.6 × deterministic_score) + (0.4 × ai_intent_score × guardrail_penalty)`
>
> This separation is intentional: I don't want AI doing arithmetic, and I don't want if-statements doing semantic reasoning.

### Tech Stack & Architecture

> **Copy this:**
>
> - **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0
> - **Database**: SQLite (normalized relational schema: Event → Attendee → EngagementSignal → LeadIntelligence → CampaignDraft → AuditLog)
> - **AI**: Google Gemini API (live mode) with offline fallback synthesizer for demo/review
> - **Frontend**: Vanilla HTML5 + CSS + JavaScript (no framework overhead — purpose-built dashboard)
> - **Testing**: pytest with 14 passing tests (rules engine, guardrails, full API integration)
> - **CLI**: Python argparse (zero external dependencies)
>
> Data model is normalized because sales pipelines have strict referential integrity — an attendee's signals, AI intelligence, and campaign drafts must always trace back to exactly one event and one person.

### AI Tools Used

> **Copy this (then personalize):**
>
> I built this using **Antigravity IDE (Google)** as my primary AI coding assistant, combining rapid agentic generation with strict engineering oversight.
>
> In line with Zuddl's builder philosophy, I used AI aggressively for boilerplate, scaffolding, and test generation, but retained full judgment over where the model got things wrong:
>
> 1. **SQLite concurrency failure in async FastAPI**: The agent generated naive synchronous DB sessions that threw `ProgrammingError: SQLite objects created in a thread can only be used in that same thread` under concurrent requests. Instead of blindly re-prompting, I diagnosed the thread affinity bottleneck and reconfigured the engine with `connect_args={"check_same_thread": False}` and clean scoped sessions.
> 2. **Pydantic V1/V2 syntax drift**: The AI initially used deprecated Pydantic v1 `class Config: orm_mode = True`, which triggered warnings and serialization failures. I refactored the models to modern Pydantic v2 `model_config = ConfigDict(from_attributes=True)` with proper schema extras.
> 3. **Terminal Unicode crash**: The agent put Unicode emojis into CLI output, which crashed Windows CP1252 consoles with `UnicodeEncodeError`. I reconfigured standard output to UTF-8 and replaced fragile emojis with cross-platform ASCII status tags (`[HOT]`, `[OK]`, `[PASS]`).
> 4. **Hallucinated attribution**: When summarizing transcripts, LLMs frequently attribute comments to the wrong attendee or hallucinate budget quotes. I designed a deterministic citation verification layer (`verify_grounding`) that enforces token containment against raw logs before any quote is surfaced to sales reps.

### Video Demo Link

```
https://www.loom.com/share/YOUR_VIDEO_ID
```

_(Record using the VIDEO_SCRIPT.md guide below)_

---

## Page 5: When You Can Start

> **Personalize and copy:**
>
> - **Earliest start date**: _Immediately / [Your date]_
> - **Duration**: Available for the full 3-month internship, extendable to 6 months
> - **Remote work**: Ready to work remotely from _[Your city]_, India

---

## Resume Tips for This Application

Zuddl says: **"PDF. One page is plenty."**

### What to include on your one-page resume:
1. **Name, Email, GitHub, LinkedIn** at the top
2. **Education** — College, degree, year
3. **Projects Section** — Lead with PulseOps AI:
   - "PulseOps AI — Post-Event Lead Intelligence Engine"
   - 2-3 bullet points: dual-engine scoring, hallucination guardrails, 14 passing tests
   - Link to GitHub repo
4. **Technical Skills** — Python, FastAPI, SQLAlchemy, LLM APIs (Gemini), pytest, Git
5. **AI Tools Experience** — Antigravity IDE, Claude, Cursor (whatever you've actually used)

### What NOT to include:
- Generic skills like "Microsoft Office" or "Team Player"
- Projects that are tutorial clones
- More than one page
