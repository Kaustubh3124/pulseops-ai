

import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("pulseops.ai_engine")


def verify_grounding(extracted_quote: str, raw_sources: List[str]) -> bool:
    """Hallucination Guardrail: Verifies whether an AI-cited claim or quote

    actually exists (or is semantically grounded) in the attendee's actual
    Q&A questions or poll selections.
    """
    if not extracted_quote:
        return True  # No quote claimed, nothing to hallucinate

    cleaned_quote = extracted_quote.strip().lower()

    # Direct substring verification
    for source in raw_sources:
        if not source:
            continue
        source_clean = source.strip().lower()
        if cleaned_quote in source_clean or source_clean in cleaned_quote:
            return True

        # Fuzzy word overlap check (>65% overlapping tokens)
        quote_words = set(cleaned_quote.split())
        source_words = set(source_clean.split())
        if quote_words and len(quote_words & source_words) / len(quote_words) >= 0.65:
            return True

    return False


def blend_scores(deterministic_score: float, ai_intent_score: float) -> float:
    """Blends the deterministic score (60% weight) with the semantic AI score (40% weight).

    Deterministic score anchors reality; AI score captures hidden nuance.
    """
    blended = (deterministic_score * 0.60) + (ai_intent_score * 0.40)
    return round(min(100.0, max(0.0, blended)), 1)


def determine_intent_tier(final_score: float) -> str:
    """Maps the blended score to actionable sales tiers."""
    if final_score >= 70.0:
        return "HOT"
    elif final_score >= 45.0:
        return "WARM"
    else:
        return "COLD"


class AISemanticEngine:
    """Handles semantic analysis of unstructured event transcripts and questions."""

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()

    def analyze_attendee(
        self,
        attendee_name: str,
        company: str,
        job_title: str,
        icp_tier: str,
        watch_percentage: float,
        qna_questions: List[str],
        poll_data: List[Dict[str, str]],
        event_title: str,
    ) -> Dict[str, Any]:
        """Performs semantic analysis, generates personalized follow-ups,

        and runs hallucination verification.
        """
        # Collect raw text evidence for grounding
        raw_evidence = list(qna_questions)
        for poll in poll_data:
            q = poll.get("poll_question", "")
            ans = poll.get("selected_option", "")
            if q and ans:
                raw_evidence.append(f"{q}: {ans}")

        # If live API key is provided, attempt live LLM call; otherwise use intelligent fallback
        if self.gemini_api_key:
            try:
                result = self._call_gemini_api(
                    attendee_name, company, job_title, qna_questions, poll_data, event_title
                )
                if result:
                    return self._finalize_analysis(result, raw_evidence, watch_percentage, icp_tier)
            except Exception as e:
                logger.warning(f"Live Gemini API call failed: {e}. Falling back to deterministic simulation.")

        # Intelligent Fallback Synthesizer (fully grounded and testable offline)
        result = self._synthesize_offline(
            attendee_name, company, job_title, qna_questions, poll_data, event_title, watch_percentage
        )
        return self._finalize_analysis(result, raw_evidence, watch_percentage, icp_tier)

    def _synthesize_offline(
        self,
        name: str,
        company: str,
        title: str,
        qna_questions: List[str],
        poll_data: List[Dict[str, str]],
        event_title: str,
        watch_percentage: float,
    ) -> Dict[str, Any]:
        """Offline high-fidelity synthesis engine.

        Extracts real intent from attendee questions and polls without requiring external network calls.
        """
        pain_points = []
        buying_signals = []
        cited_quote = ""
        base_ai_intent = 20.0  # Base line

        # Analyze Q&A
        if qna_questions:
            primary_question = qna_questions[0]
            cited_quote = primary_question
            base_ai_intent += 40.0

            q_lower = primary_question.lower()
            if any(term in q_lower for term in ["integrate", "crm", "hubspot", "salesforce", "api"]):
                pain_points.append("Struggling with post-event CRM & data sync integration")
                buying_signals.append("Explicit technical evaluation of integration architecture")
                base_ai_intent += 20.0
            elif any(term in q_lower for term in ["pricing", "cost", "contract", "enterprise", "budget"]):
                pain_points.append("Evaluating total cost of ownership & enterprise tiering")
                buying_signals.append("Active commercial budget consideration")
                base_ai_intent += 25.0
            elif any(term in q_lower for term in ["turnaround", "time", "hours", "lead drop", "drop-off", "follow-up"]):
                pain_points.append("Excessive lead follow-up lag causing high-intent drop-off")
                buying_signals.append("Urgent workflow optimization priority")
                base_ai_intent += 20.0
            else:
                pain_points.append(f"Interested in: {primary_question}")
                buying_signals.append("Active question asked during live broadcast")
                base_ai_intent += 15.0

        # Analyze Polls
        for poll in poll_data:
            ans = poll.get("selected_option", "")
            q = poll.get("poll_question", "")
            if "biggest challenge" in q.lower() or "drop" in ans.lower():
                pain_points.append(f"Reported challenge: {ans}")
                buying_signals.append("Acknowledged operational bottleneck in team workflow")
                base_ai_intent += 10.0

        # Factor in attendance
        if watch_percentage >= 80.0:
            buying_signals.append(f"High engagement: watched {watch_percentage}% of the session")
            base_ai_intent += 10.0

        ai_intent_score = min(100.0, max(15.0, round(base_ai_intent, 1)))

        # Generate Contextual Email Outreach
        first_name = name.split()[0] if name else "there"
        if qna_questions:
            subject = f"Your question on {event_title} & quick follow-up"
            body = (
                f"Hi {first_name},\n\n"
                f"Thanks for joining our session on '{event_title}'.\n\n"
                f"I noticed you asked during the live Q&A: \"{cited_quote}\". "
                f"This is an exact challenge we recently solved for event teams at scale by automating "
                f"post-event signal extraction directly into their sales workflow.\n\n"
                f"Would you be open to a 10-minute chat this Thursday to see how we tackle this?\n\n"
                f"Best,\nZuddl Revenue Team"
            )
            linkedin_msg = (
                f"Hi {first_name}, loved your question during the Zuddl summit regarding '{cited_quote[:50]}...'. "
                f"Would love to connect and share how we're automating this workflow!"
            )
        else:
            subject = f"Key takeaways & resources from '{event_title}'"
            body = (
                f"Hi {first_name},\n\n"
                f"Thanks for participating in '{event_title}'. Since your team at {company} is focusing on "
                f"improving event outcomes, here is the executive summary and slide deck from the session.\n\n"
                f"Let me know if you'd like to explore how other {title}s are accelerating their event ROI.\n\n"
                f"Best,\nZuddl Revenue Team"
            )
            linkedin_msg = f"Hi {first_name}, saw you attended our Zuddl session. Great to connect with fellow leaders at {company}!"

        reasoning = (
            f"Attendee showed {watch_percentage}% watch time. "
            f"Extracted {len(pain_points)} pain points and {len(buying_signals)} buying signals from live session participation."
        )

        return {
            "ai_intent_score": ai_intent_score,
            "key_pain_points": pain_points or ["General event technology modernization"],
            "buying_signals": buying_signals or ["Registered and attended live session"],
            "ground_truth_quote": cited_quote,
            "email_subject": subject,
            "email_body": body,
            "linkedin_message": linkedin_msg,
            "ai_reasoning": reasoning,
            "confidence_score": 0.95 if cited_quote else 0.82,
        }

    def _call_gemini_api(self, name, company, title, qna, polls, event_title) -> Optional[Dict[str, Any]]:
        """Makes an HTTP request to Google Gemini API if key is present."""
        import httpx

        prompt = f"""
        Analyze this webinar attendee's intent for Zuddl's B2B event platform.
        Attendee: {name}, {title} at {company}
        Event: {event_title}
        Questions Asked: {json.dumps(qna)}
        Poll Responses: {json.dumps(polls)}

        Output JSON strictly with keys:
        - "ai_intent_score": float 0-100
        - "key_pain_points": list of strings
        - "buying_signals": list of strings
        - "ground_truth_quote": exact quote string from Questions Asked
        - "email_subject": string
        - "email_body": string (hyper personalized, referencing their question)
        - "linkedin_message": string
        - "ai_reasoning": string
        - "confidence_score": float 0.0-1.0
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = httpx.post(url, json=payload, timeout=12.0)
        if response.status_code == 200:
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            # Extract JSON block
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        return None

    def _finalize_analysis(
        self,
        analysis: Dict[str, Any],
        raw_evidence: List[str],
        watch_percentage: float,
        icp_tier: str,
    ) -> Dict[str, Any]:
        """Runs the hallucination guardrail filter and confidence checks."""
        claimed_quote = analysis.get("ground_truth_quote", "")
        is_verified = verify_grounding(claimed_quote, raw_evidence)

        # If guardrail fails, penalize confidence and flag
        confidence = analysis.get("confidence_score", 0.9)
        if not is_verified:
            confidence = round(confidence * 0.4, 2)  # Severe confidence penalty
            analysis["ai_reasoning"] += " [GUARDRAIL ALERT: Claimed quote was not verified against raw session logs!]"

        analysis["hallucination_verified"] = is_verified
        analysis["confidence_score"] = confidence
        return analysis
