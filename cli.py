#!/usr/bin/env python3
"""PulseOps AI Command Line Interface (CLI).

Designed for Sales Ops, Event Marketers, and Developers to run the intelligence pipeline,
ingest event payloads, and export qualified leads directly from the terminal.
"""

import sys
import json
import argparse

# Ensure cross-platform UTF-8 encoding on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from app.database import SessionLocal, init_db
from app.models import Event, Attendee, EngagementSignal, LeadIntelligence, CampaignDraft
from app.rules_engine import classify_icp, calculate_watch_percentage, compute_deterministic_score
from app.ai_engine import AISemanticEngine, blend_scores, determine_intent_tier
from app.seed_data import seed_demo_data


def run_seed(args):
    """Seed demo event data."""
    init_db()
    db = SessionLocal()
    try:
        event = seed_demo_data(db)
        print(f"[OK] Demo event successfully seeded: '{event.title}' (ID: {event.id})")
    finally:
        db.close()


def run_ingest(args):
    """Ingest event payload from a JSON file."""
    init_db()
    filepath = args.file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON file '{filepath}': {e}")
        sys.exit(1)

    db = SessionLocal()
    try:
        event = Event(
            title=data.get("event_title", "Untitled Event"),
            event_type=data.get("event_type", "Webinar"),
            total_duration_minutes=data.get("total_duration_minutes", 60),
            status="raw",
        )
        db.add(event)
        db.flush()

        attendees = data.get("attendees", [])
        for item in attendees:
            icp_tier = classify_icp(item.get("job_title", ""), item.get("company_size", "Mid-Market"))
            att = Attendee(
                event_id=event.id,
                name=item["name"],
                email=item["email"],
                company=item["company"],
                job_title=item["job_title"],
                company_size=item.get("company_size", "Mid-Market"),
                icp_tier=icp_tier,
            )
            db.add(att)
            db.flush()

            watch_pct = calculate_watch_percentage(
                item.get("watch_time_minutes", 0), event.total_duration_minutes
            )
            sig = EngagementSignal(
                attendee_id=att.id,
                watch_time_minutes=item.get("watch_time_minutes", 0),
                watch_percentage=watch_pct,
                poll_responses_count=len(item.get("poll_responses", [])),
                poll_data=json.dumps(item.get("poll_responses", [])),
                qna_questions=json.dumps(item.get("qna_questions", [])),
                chat_messages_count=item.get("chat_messages_count", 0),
                booth_visits=item.get("booth_visits", 0),
            )
            db.add(sig)

        db.commit()
        print(f"[OK] Ingested event '{event.title}' (ID: {event.id}) with {len(attendees)} attendees.")
        print(f"[INFO] Next step: Run 'python cli.py process --event-id {event.id}' to score leads.")
    finally:
        db.close()


def run_process(args):
    """Run deterministic & AI scoring pipeline on an event."""
    init_db()
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == args.event_id).first()
        if not event:
            print(f"[ERROR] Event with ID {args.event_id} not found.")
            sys.exit(1)

        attendees = db.query(Attendee).filter(Attendee.event_id == event.id).all()
        ai_engine = AISemanticEngine()
        print(f"[RUNNING] Processing PulseOps Pipeline for '{event.title}' ({len(attendees)} attendees)...")

        hot, warm, cold = 0, 0, 0
        for att in attendees:
            sig = att.signal
            if not sig:
                continue

            qna = json.loads(sig.qna_questions or "[]")
            polls = json.loads(sig.poll_data or "[]")

            det_score, _ = compute_deterministic_score(
                sig.watch_percentage,
                att.icp_tier,
                sig.poll_responses_count,
                len(qna),
                sig.chat_messages_count,
                sig.booth_visits,
            )

            ai_res = ai_engine.analyze_attendee(
                attendee_name=att.name,
                company=att.company,
                job_title=att.job_title,
                icp_tier=att.icp_tier,
                watch_percentage=sig.watch_percentage,
                qna_questions=qna,
                poll_data=polls,
                event_title=event.title,
            )

            final = blend_scores(det_score, ai_res["ai_intent_score"])
            tier = determine_intent_tier(final)

            if tier == "HOT":
                hot += 1
            elif tier == "WARM":
                warm += 1
            else:
                cold += 1

            intel = db.query(LeadIntelligence).filter(LeadIntelligence.attendee_id == att.id).first()
            if not intel:
                intel = LeadIntelligence(attendee_id=att.id)
                db.add(intel)

            intel.deterministic_score = det_score
            intel.ai_intent_score = ai_res["ai_intent_score"]
            intel.final_score = final
            intel.intent_tier = tier
            intel.key_pain_points = json.dumps(ai_res["key_pain_points"])
            intel.buying_signals = json.dumps(ai_res["buying_signals"])
            intel.ground_truth_quote = ai_res["ground_truth_quote"]
            intel.hallucination_verified = ai_res["hallucination_verified"]
            intel.confidence_score = ai_res["confidence_score"]
            intel.ai_reasoning = ai_res["ai_reasoning"]

            camp = db.query(CampaignDraft).filter(CampaignDraft.attendee_id == att.id).first()
            if not camp:
                camp = CampaignDraft(attendee_id=att.id)
                db.add(camp)

            camp.email_subject = ai_res["email_subject"]
            camp.email_body = ai_res["email_body"]
            camp.linkedin_message = ai_res["linkedin_message"]
            camp.status = "APPROVED" if tier == "HOT" else "DRAFT"

        event.status = "processed"
        db.commit()
        print(f"[OK] Pipeline Execution Complete!")
        print(f"     [HOT Leads]: {hot} | [WARM Leads]: {warm} | [COLD Leads]: {cold}")
    finally:
        db.close()



def run_list(args):
    """List scored leads in a formatted terminal table."""
    init_db()
    db = SessionLocal()
    try:
        query = db.query(Attendee)
        if args.event_id:
            query = query.filter(Attendee.event_id == args.event_id)

        attendees = query.all()
        if not attendees:
            print("No attendees found.")
            return

        rows = []
        for att in attendees:
            intel = att.intelligence
            if not intel:
                continue
            if args.tier and intel.intent_tier.upper() != args.tier.upper():
                continue
            rows.append((
                att.name,
                att.company,
                att.job_title[:24],
                f"{intel.final_score:.1f}",
                intel.intent_tier,
                "PASS" if intel.hallucination_verified else "FLAGGED",
            ))

        rows.sort(key=lambda x: float(x[3]), reverse=True)

        print("-" * 88)
        print(f"{'NAME':<18} | {'COMPANY':<14} | {'TITLE':<24} | {'SCORE':<5} | {'TIER':<5} | {'GUARDRAIL'}")
        print("-" * 88)
        for r in rows:
            print(f"{r[0]:<18} | {r[1]:<14} | {r[2]:<24} | {r[3]:<5} | {r[4]:<5} | {r[5]}")
        print("-" * 88)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="PulseOps AI CLI - Post-Event Lead Intelligence & Automation Engine for Zuddl."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Seed command
    subparsers.add_parser("seed", help="Seed database with demo event scenario.")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest an event JSON payload.")
    ingest_parser.add_argument("file", help="Path to event JSON file (e.g. sample_event.json)")

    # Process command
    proc_parser = subparsers.add_parser("process", help="Run scoring pipeline on an event.")
    proc_parser.add_argument("--event-id", type=int, default=1, help="ID of event to process")

    # List command
    list_parser = subparsers.add_parser("list", help="Display scored leads table.")
    list_parser.add_argument("--event-id", type=int, default=1, help="ID of event")
    list_parser.add_argument("--tier", choices=["HOT", "WARM", "COLD"], help="Filter by tier")

    args = parser.parse_args()

    if args.command == "seed":
        run_seed(args)
    elif args.command == "ingest":
        run_ingest(args)
    elif args.command == "process":
        run_process(args)
    elif args.command == "list":
        run_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
