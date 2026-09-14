"""Tests for Hallucination Guardrails & AI Judgement."""

import pytest
from app.ai_engine import verify_grounding, blend_scores, determine_intent_tier, AISemanticEngine


def test_verify_grounding_authentic_quote():
    raw_sources = [
        "How quickly does PulseOps sync attendee intent signals into Salesforce?",
        "What is your #1 post-event bottleneck?: Post-event lead drop-off",
    ]
    # Exact quote cited
    quote = "How quickly does PulseOps sync attendee intent signals into Salesforce?"
    assert verify_grounding(quote, raw_sources) is True


def test_verify_grounding_fuzzy_match():
    raw_sources = [
        "Can we configure custom confidence thresholds before automated outreach emails are drafted?"
    ]
    # Slight rephrasing / substring
    quote = "configure custom confidence thresholds before automated outreach"
    assert verify_grounding(quote, raw_sources) is True


def test_verify_grounding_hallucination_detected():
    raw_sources = [
        "I am looking for webinar slide downloads.",
    ]
    # LLM hallucinates that attendee wants to purchase enterprise annual plan
    hallucinated_quote = "We have allocated 50,000 dollars budget and want an enterprise contract today."
    assert verify_grounding(hallucinated_quote, raw_sources) is False


def test_blend_scores_and_tiers():
    # 60% deterministic + 40% AI
    # High: 90 * 0.6 + 95 * 0.4 = 54 + 38 = 92.0 -> HOT
    blended_hot = blend_scores(90.0, 95.0)
    assert blended_hot == 92.0
    assert determine_intent_tier(blended_hot) == "HOT"

    # Medium: 50 * 0.6 + 60 * 0.4 = 30 + 24 = 54.0 -> WARM
    blended_warm = blend_scores(50.0, 60.0)
    assert blended_warm == 54.0
    assert determine_intent_tier(blended_warm) == "WARM"

    # Low: 20 * 0.6 + 20 * 0.4 = 20.0 -> COLD
    blended_cold = blend_scores(20.0, 20.0)
    assert blended_cold == 20.0
    assert determine_intent_tier(blended_cold) == "COLD"
