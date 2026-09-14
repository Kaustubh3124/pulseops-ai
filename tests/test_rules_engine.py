"""Tests for Deterministic Rules Engine (Where AI DOES NOT belong)."""

import pytest
from app.rules_engine import classify_icp, calculate_watch_percentage, compute_deterministic_score


def test_classify_icp_tier_1():
    assert classify_icp("VP of Marketing", "Enterprise (1000+)") == "Tier 1 - High Fit"
    assert classify_icp("Director of Field Marketing", "Mid-Market") == "Tier 1 - High Fit"
    assert classify_icp("Chief Revenue Officer", "Enterprise") == "Tier 1 - High Fit"


def test_classify_icp_tier_2():
    assert classify_icp("Event Operations Manager", "Enterprise") == "Tier 2 - Medium Fit"
    assert classify_icp("Senior Field Specialist", "Mid-Market") == "Tier 2 - Medium Fit"


def test_classify_icp_tier_3():
    assert classify_icp("Student / Freelancer", "SMB (1-10)") == "Tier 3 - Low Fit"
    assert classify_icp("Intern", "Mid-Market") == "Tier 3 - Low Fit"


def test_calculate_watch_percentage():
    assert calculate_watch_percentage(60, 60) == 100.0
    assert calculate_watch_percentage(30, 60) == 50.0
    assert calculate_watch_percentage(75, 60) == 100.0  # Clamped to 100%
    assert calculate_watch_percentage(0, 60) == 0.0
    assert calculate_watch_percentage(10, 0) == 0.0


def test_compute_deterministic_score_weights():
    # Max score case: 100% watch (40 pts) + Tier 1 ICP (30 pts) + high participation (30 pts max)
    score, breakdown = compute_deterministic_score(
        watch_percentage=100.0,
        icp_tier="Tier 1 - High Fit",
        poll_count=3,     # 15 pts
        qna_count=2,      # 14 pts
        chat_count=10,    # 5 pts
        booth_visits=1,   # 5 pts
    )
    assert score == 100.0
    assert breakdown["watch_points"] == 40.0
    assert breakdown["icp_points"] == 30.0
    assert breakdown["participation_points"] == 30.0


def test_compute_deterministic_score_low_engagement():
    score, breakdown = compute_deterministic_score(
        watch_percentage=10.0,
        icp_tier="Tier 3 - Low Fit",
        poll_count=0,
        qna_count=0,
        chat_count=0,
        booth_visits=0,
    )
    # 10% watch = 4 pts, Tier 3 = 6 pts, participation = 0
    assert score == 10.0
    assert breakdown["total"] == 10.0
