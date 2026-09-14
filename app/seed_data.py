"""Realistic Seed Data for Zuddl PulseOps AI Demo Scenario.

Represents a high-stakes B2B event:
"Zuddl Product Summit 2026: The AI-Native Event Ops Revolution"
"""

import json
from sqlalchemy.orm import Session
from .models import Event, Attendee, EngagementSignal, LeadIntelligence, CampaignDraft, AuditLog
from .rules_engine import classify_icp, calculate_watch_percentage, compute_deterministic_score
from .ai_engine import AISemanticEngine, blend_scores, determine_intent_tier

SAMPLE_EVENT_PAYLOAD = {
    "event_title": "Zuddl Product Summit 2026: The AI-Native Event Ops Revolution",
    "event_type": "Virtual Summit",
    "total_duration_minutes": 60,
    "attendees": [
        {
            "name": "Rohan Sharma",
            "email": "rohan.sharma@atlassian.com",
            "company": "Atlassian",
            "job_title": "VP of Growth Marketing",
            "company_size": "Enterprise (10,000+)",
            "watch_time_minutes": 58,
            "poll_responses": [
                {
                    "poll_question": "What is your #1 post-event bottleneck?",
                    "selected_option": "Post-event lead drop-off and manual SDR follow-up lag",
                },
                {
                    "poll_question": "How soon do your sales reps follow up on event leads?",
                    "selected_option": "3 to 5 business days",
                },
            ],
            "qna_questions": [
                "How quickly does PulseOps sync attendee intent signals into Salesforce and HubSpot after a 5,000-person summit concludes?"
            ],
            "chat_messages_count": 8,
            "booth_visits": 2,
        },
        {
            "name": "Priya Nair",
            "email": "priya.nair@razorpay.com",
            "company": "Razorpay",
            "job_title": "Head of Global Events & Field Ops",
            "company_size": "Enterprise (3,000+)",
            "watch_time_minutes": 54,
            "poll_responses": [
                {
                    "poll_question": "What is your #1 post-event bottleneck?",
                    "selected_option": "Fragmented data between webinar platforms and CRM",
                }
            ],
            "qna_questions": [
                "Can we configure custom confidence thresholds before automated outreach emails are drafted for our field sales team?"
            ],
            "chat_messages_count": 6,
            "booth_visits": 1,
        },
        {
            "name": "Vikram Sengupta",
            "email": "vikram.s@snowflake.com",
            "company": "Snowflake",
            "job_title": "Senior Product Marketing Manager",
            "company_size": "Enterprise (5,000+)",
            "watch_time_minutes": 42,
            "poll_responses": [
                {
                    "poll_question": "What is your #1 post-event bottleneck?",
                    "selected_option": "Manual spreadsheet parsing",
                }
            ],
            "qna_questions": [
                "Does the platform support tracking multi-track webinar attendance and booth engagement separately?"
            ],
            "chat_messages_count": 3,
            "booth_visits": 0,
        },
        {
            "name": "Ananya Deshmukh",
            "email": "ananya.d@postman.com",
            "company": "Postman",
            "job_title": "Event Operations Specialist",
            "company_size": "Mid-Market (800+)",
            "watch_time_minutes": 36,
            "poll_responses": [
                {
                    "poll_question": "What is your #1 post-event bottleneck?",
                    "selected_option": "Manual spreadsheet parsing",
                }
            ],
            "qna_questions": [
                "Is there a native webhook integration for instant Slack alerts to our SDR channel?"
            ],
            "chat_messages_count": 2,
            "booth_visits": 1,
        },
        {
            "name": "Kunal Verma",
            "email": "kunal.verma@freemail.io",
            "company": "Freelance Ops",
            "job_title": "Aspiring Event Marketer",
            "company_size": "SMB (1-10)",
            "watch_time_minutes": 10,
            "poll_responses": [],
            "qna_questions": [],
            "chat_messages_count": 0,
            "booth_visits": 0,
        },
    ],
}


def seed_demo_data(db: Session) -> Event:
    """Seeds the database with the pre-populated demo event scenario."""
    # Check if demo event already exists
    existing = db.query(Event).filter(Event.title == SAMPLE_EVENT_PAYLOAD["event_title"]).first()
    if existing:
        return existing

    event = Event(
        title=SAMPLE_EVENT_PAYLOAD["event_title"],
        event_type=SAMPLE_EVENT_PAYLOAD["event_type"],
        total_duration_minutes=SAMPLE_EVENT_PAYLOAD["total_duration_minutes"],
        status="processed",
    )
    db.add(event)
    db.flush()

    ai_engine = AISemanticEngine()

    for item in SAMPLE_EVENT_PAYLOAD["attendees"]:
        icp_tier = classify_icp(item["job_title"], item["company_size"])
        watch_pct = calculate_watch_percentage(
            item["watch_time_minutes"], event.total_duration_minutes
        )

        attendee = Attendee(
            event_id=event.id,
            name=item["name"],
            email=item["email"],
            company=item["company"],
            job_title=item["job_title"],
            company_size=item["company_size"],
            icp_tier=icp_tier,
        )
        db.add(attendee)
        db.flush()

        signal = EngagementSignal(
            attendee_id=attendee.id,
            watch_time_minutes=item["watch_time_minutes"],
            watch_percentage=watch_pct,
            poll_responses_count=len(item["poll_responses"]),
            poll_data=json.dumps(item["poll_responses"]),
            qna_questions=json.dumps(item["qna_questions"]),
            chat_messages_count=item["chat_messages_count"],
            booth_visits=item["booth_visits"],
        )
        db.add(signal)

        # Deterministic Score
        det_score, det_breakdown = compute_deterministic_score(
            watch_percentage=watch_pct,
            icp_tier=icp_tier,
            poll_count=len(item["poll_responses"]),
            qna_count=len(item["qna_questions"]),
            chat_count=item["chat_messages_count"],
            booth_visits=item["booth_visits"],
        )

        # AI Semantic Extraction
        ai_res = ai_engine.analyze_attendee(
            attendee_name=item["name"],
            company=item["company"],
            job_title=item["job_title"],
            icp_tier=icp_tier,
            watch_percentage=watch_pct,
            qna_questions=item["qna_questions"],
            poll_data=item["poll_responses"],
            event_title=event.title,
        )

        final_score = blend_scores(det_score, ai_res["ai_intent_score"])
        intent_tier = determine_intent_tier(final_score)

        intel = LeadIntelligence(
            attendee_id=attendee.id,
            deterministic_score=det_score,
            ai_intent_score=ai_res["ai_intent_score"],
            final_score=final_score,
            intent_tier=intent_tier,
            key_pain_points=json.dumps(ai_res["key_pain_points"]),
            buying_signals=json.dumps(ai_res["buying_signals"]),
            ground_truth_quote=ai_res["ground_truth_quote"],
            hallucination_verified=ai_res["hallucination_verified"],
            confidence_score=ai_res["confidence_score"],
            ai_reasoning=ai_res["ai_reasoning"],
        )
        db.add(intel)

        # Campaign Draft
        slack_payload = {
            "channel": "#leads-high-intent",
            "text": f"🚨 Hot Lead Alert: *{item['name']}* ({item['job_title']} @ {item['company']}) scored *{final_score}/100*!",
            "details": {
                "key_pain_point": ai_res["key_pain_points"][0] if ai_res["key_pain_points"] else "N/A",
                "quote": ai_res["ground_truth_quote"],
            },
        }

        campaign = CampaignDraft(
            attendee_id=attendee.id,
            email_subject=ai_res["email_subject"],
            email_body=ai_res["email_body"],
            linkedin_message=ai_res["linkedin_message"],
            slack_alert_payload=json.dumps(slack_payload),
            status="APPROVED" if intent_tier == "HOT" else "DRAFT",
        )
        db.add(campaign)

    # Add audit log
    audit = AuditLog(
        event_id=event.id,
        operation="PIPELINE_INIT_DEMO_SEED",
        details=f"Ingested and analyzed {len(SAMPLE_EVENT_PAYLOAD['attendees'])} attendees for demo.",
        execution_time_ms=142,
    )
    db.add(audit)
    db.commit()
    return event
