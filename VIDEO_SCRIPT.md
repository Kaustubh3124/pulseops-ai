# PulseOps AI — Loom Video Script

> Record a 2-3 minute Loom video. Below is a word-for-word script with screen actions.
> Total target: **2:30 – 3:00 minutes**.

---

## Setup Before Recording

1. Open terminal in the project folder
2. Run: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
3. Open browser to `http://127.0.0.1:8000`
4. Open a second browser tab to `http://127.0.0.1:8000/docs` (Swagger)
5. Start Loom recording (screen + camera)

---

## Script

### [0:00 – 0:20] — The Hook (Browser: Dashboard)

**SHOW**: Dashboard with KPI cards visible.

**SAY**:
> "Hey Zuddl team. I'm [Your Name], and this is PulseOps AI — a post-event lead intelligence engine
> I built specifically for Zuddl's use case.
>
> The problem: after every virtual event, your Revenue and Event Ops teams get hundreds of attendee records
> and have to manually figure out who's actually interested. PulseOps automates that entire workflow."

---

### [0:20 – 0:50] — The Architecture (Browser: Dashboard → mention the split)

**SHOW**: Point to the KPI cards (total leads, hot leads, average score).

**SAY**:
> "The core idea is a dual-engine scoring pipeline. I intentionally split the scoring into two parts:
>
> A deterministic rules engine that handles watch-time percentages, ICP role matching, and interaction counts —
> these are mathematical facts that should never go through an LLM.
>
> And an AI semantic engine that reads Q&A transcripts and extracts pain points, buying urgency,
> and commercial intent — this is where language models actually add value.
>
> The deterministic engine gets 60% weight, the AI engine gets 40%.
> And on top of the AI, I added hallucination guardrails that verify every cited quote
> against the attendee's actual session data."

---

### [0:50 – 1:30] — Live Demo (Browser: Dashboard interaction)

**SHOW**: Click on a lead row to open the dossier.

**SAY**:
> "Let me show you a lead. Here's Sarah Chen — she's a VP of Marketing who watched 92% of the event,
> answered 3 polls, asked 2 questions about ROI and budget timelines.
>
> The rules engine scored her at 88. The AI engine identified buying signals like
> 'evaluating solutions for Q4 rollout' and extracted her actual question about consolidating
> event tools.
>
> The guardrail check passed — every quote you see here traces back to something she actually said."

**SHOW**: Click "Generate Campaign" button.

**SAY**:
> "And with one click, it generates a personalized follow-up email and LinkedIn message
> that reference her exact questions. Not a template — actual context from her session."

---

### [1:30 – 2:00] — Under the Hood (Browser: Swagger docs OR code editor)

**SHOW**: Switch to Swagger at `/docs`, or briefly show the project structure in your editor.

**SAY**:
> "Under the hood: Python 3.13, FastAPI with Pydantic v2 validation, SQLAlchemy with a normalized
> relational schema — Event to Attendee to Signals to Intelligence to Campaign.
>
> I chose relational over document store because sales pipelines need strict referential integrity.
> Every lead's signals and campaign drafts trace back to exactly one event and one person.
>
> There are 14 passing tests — rules engine unit tests, hallucination guardrail tests,
> and full API integration tests."

**SHOW**: (Optional) Briefly run `python -m pytest -v` in terminal to show green passes.

---

### [2:00 – 2:30] — The "Why" & Close

**SAY**:
> "I built this because Zuddl already owns the event experience — the gap is what happens
> after the event ends. PulseOps bridges that gap.
>
> The key design decision: keeping AI and deterministic logic strictly separated.
> I don't want a language model calculating watch-time percentages,
> and I don't want if-statements doing semantic reasoning. Mixing those up is
> the number one mistake in AI-powered tooling.
>
> I'm [Your Name]. I'd love to bring this kind of thinking to the Zuddl team.
> Thanks for watching."

---

## Recording Tips

- **Camera**: Keep your face cam ON (Zuddl wants to see you, not just your screen)
- **Energy**: Be enthusiastic but not scripted — practice twice, then record naturally
- **Speed**: Don't rush. 2:30 is better than a breathless 1:45
- **Clicks**: Make your mouse movements deliberate — reviewers are watching small screens
- **Audio**: Use a headset mic if available; avoid echo-y rooms
- **Blooper rule**: One small stumble is fine. Re-record if you lose your thread entirely.
