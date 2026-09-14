# PulseOps AI — Video Demo Guide & Script (3–5 Minutes)

> **Zuddl Requirement:**
> *"One demo video — 3–6 minutes. A public Loom or YouTube link that opens without signing in (unlisted is fine, private is not). Show it working and how it's built. A screen recording with your voice is fine. Not a slide deck."*
>
> **Target Video Length:** 3:30 – 4:30 minutes.

---

## 🛠️ Setup Before You Hit Record

1. **Terminal 1 (Dev Server)**:
   Make sure the server is running:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. **Browser Window**:
   - Tab 1: `http://127.0.0.1:8000` (PulseOps AI Dashboard)
   - Tab 2: `http://127.0.0.1:8000/docs` (FastAPI Swagger Interactive Docs)
   - Tab 3: `https://github.com/Kaustubh3124/pulseops-ai` (Your GitHub Repository)
3. **Code Editor / Terminal 2**:
   - Have VS Code open to the `pulseops-ai` directory, showing:
     - `app/rules_engine.py`
     - `app/ai_engine.py`
     - `app/models.py`
   - Have a terminal ready to run `python -m pytest -v`
4. **Recording Tool**:
   - **Option A (Recommended): [Loom](https://www.loom.com/)** (Free browser extension or desktop app). Choose "Screen + Camera" (or Screen + Mic). Once recorded, copy the share link (`https://www.loom.com/share/...`). Check that the link privacy is set to **"Public"** or **"Anyone with the link can view"**.
   - **Option B: Screen Recording + YouTube**: Record with OBS / Windows Game Bar (`Win + Alt + R`), upload to YouTube as **Unlisted**, and copy the video URL (`https://youtu.be/...`).

---

## 🎬 Word-for-Word Script with Screen Actions

---

### Part 1: The Hook & The Problem [0:00 – 0:45]
**Screen**: Browser Tab 1 — PulseOps AI Dashboard (`http://127.0.0.1:8000`)

**What to do**: Have the dashboard open showing the KPI cards at the top and the lead pipeline table below. Move your cursor smoothly over the KPI summary.

**What to say**:
> "Hi team at Zuddl. My name is Kaustubh, and this is **PulseOps AI** — an automated Post-Event Lead Intelligence and Outreach Engine that I designed specifically for Zuddl's event ecosystem.
>
> The problem this solves: Right now, after any webinar or summit hosted on Zuddl, event organizers and RevOps teams get hit with a CSV containing hundreds of attendee logs — watch times, poll responses, and Q&A transcripts.
>
> Sales reps have to manually comb through spreadsheets to guess who actually has buying intent. By the time someone sends a generic follow-up 4 days later, over 60% of high-intent buyers have moved on.
>
> PulseOps AI takes that raw post-event stream, separates the deterministic math from semantic language understanding, verifies every claim against ground truth, and arms SDRs with high-conversion outreach in under 2 seconds."

---

### Part 2: Show It Working — Live Dashboard & Workflow [0:45 – 2:15]
**Screen**: Browser Tab 1 (`http://127.0.0.1:8000`)

**What to do**:
1. Click the **"Hot"** filter button above the table to show Sarah Chen and Elena Rostova.
2. Click on **Sarah Chen's row** to open her lead dossier modal.
3. Scroll through the dossier highlighting:
   - **Deterministic Score** (88/100) vs **AI Intent Score** (92/100)
   - **Key Pain Points** and **Buying Signals**
   - **Ground Truth Verification** (Green badge: `100% Grounded in Q&A session logs`)
4. Click the **"Generate Campaign"** button in the modal.
5. Point out the generated personalized email, LinkedIn invite, and Slack alert payload.
6. Click **"Dispatch to Slack"** or close the modal.

**What to say**:
> "Let's see it in action. Here on the dashboard, we have real-time KPI metrics showing pipeline conversion, hot leads, and average response times.
>
> In the pipeline table, every attendee is categorized into **Hot, Warm, or Cold** tiers based on a blended intelligence score.
>
> If I filter by **Hot leads** and open **Sarah Chen** — she's a VP of Marketing at Acme Corp.
>
> Notice the split here:
> - Her **Deterministic Score is 88** — because she attended 92% of the event, answered 3 polls, and matches our Tier-1 buyer persona.
> - Her **AI Intent Score is 92** — because our semantic engine extracted active buying signals from her Q&A questions, such as evaluating consolidation tools for a Q4 rollout.
> - Most importantly, notice this **Hallucination Verification Badge**: every quote and signal cited here was verified against the actual raw Q&A logs.
>
> Now, watch this: when an SDR needs to follow up, they don't send a generic template. I click **'Generate Campaign'**, and PulseOps instantly drafts:
> 1. A personalized email referencing her exact question about tool consolidation.
> 2. A crisp LinkedIn connection note.
> 3. A formatted Slack alert ready for immediate webhook dispatch."

---

### Part 3: Show How It's Built — Architecture & Code [2:15 – 3:45]
**Screen**: Switch to VS Code / Editor & Terminal

**What to do**:
1. Open [`app/rules_engine.py`](file:///c:/Users/hp/Desktop/Zuddl-project/app/rules_engine.py): show the deterministic scoring function.
2. Open [`app/ai_engine.py`](file:///c:/Users/hp/Desktop/Zuddl-project/app/ai_engine.py): show the hallucination guardrail verification function.
3. Open [`app/models.py`](file:///c:/Users/hp/Desktop/Zuddl-project/app/models.py): briefly highlight the relational schema.
4. Switch to Terminal and run: `python -m pytest -v` (let the 14 green passes show on screen).
5. (Quick 5 seconds) Switch to Browser Tab 2 (`/docs`) to show the Swagger API endpoints.

**What to say**:
> "Now let's talk about **how this is built under the hood**.
>
> The core architectural philosophy here is: **Don't use AI where deterministic logic belongs, and don't use if-statements where language understanding belongs.**
>
> In `app/rules_engine.py`, watch time percentage, ICP title matching, and poll participation are computed purely through deterministic mathematics. This is 60% of the lead score. There is zero risk of an LLM hallucinating math or attendance percentages.
>
> In `app/ai_engine.py`, we use the LLM specifically for semantic synthesis: understanding pain points and commercial urgency from unstructured Q&A transcripts.
>
> Crucially, I implemented a **Hallucination Guardrail Layer** here in `verify_ground_truth_quote()`. It cross-references every extracted quote against the raw attendee session logs using token containment and fuzzy matching. If an LLM fabricates a quote, the confidence score is penalized and flagged for human review.
>
> The data layer in `models.py` is built with **FastAPI and SQLAlchemy** using a normalized relational schema: Event, Attendee, EngagementSignal, LeadIntelligence, and CampaignDraft. Sales pipelines require strict referential integrity — every campaign draft must trace back to exactly one lead and one event.
>
> Let's run the test suite: `python -m pytest -v`... As you can see, all 14 tests pass — covering the rules engine, the guardrails, and full API integration."

---

### Part 4: Conclusion & Builder Philosophy [3:45 – 4:20]
**Screen**: Switch to GitHub Repo tab (`https://github.com/Kaustubh3124/pulseops-ai`) or your Camera / Dashboard

**What to say**:
> "To wrap up: I built PulseOps AI because it solves a genuine bottleneck in the post-event lifecycle that Zuddl's customers face every day.
>
> The entire repository is published on GitHub at `Kaustubh3124/pulseops-ai` — complete with a full README, architecture diagrams, zero exposed secrets, and a clean CLI tool.
>
> I'm excited about Zuddl's builder philosophy and would love to bring this combination of pragmatic AI judgment and robust software engineering to the team as an intern.
>
> Thank you for your time, and I look forward to hearing from you!"

---

## 💡 Quick Tips for a 10/10 Video

- **Voice & Tone**: Speak clearly with natural confidence. Don't worry if you pause for half a second.
- **Mouse Clicks**: Keep cursor movements smooth; avoid erratic clicks.
- **Link Check**: Once you upload to Loom or YouTube:
  - Open an **Incognito / Private browser window**.
  - Paste your video link.
  - Make sure the video plays **without requiring a login**!
