

from typing import Tuple


def classify_icp(job_title: str, company_size: str) -> str:
    """Classifies an attendee into an ICP (Ideal Customer Profile) tier

    based on organizational authority and company scale.
    """
    title_lower = (job_title or "").lower()
    size_lower = (company_size or "").lower()

    tier_1_keywords = [
        "vp",
        "vice president",
        "director",
        "head of",
        "chief",
        "cxo",
        "cmo",
        "cro",
        "founder",
        "lead",
        "principal",
    ]
    tier_2_keywords = [
        "manager",
        "specialist",
        "senior",
        "strategist",
        "consultant",
        "architect",
    ]

    is_tier_1_title = any(kw in title_lower for kw in tier_1_keywords)
    is_tier_2_title = any(kw in title_lower for kw in tier_2_keywords)

    is_enterprise = "enterprise" in size_lower or "1000" in size_lower or "large" in size_lower
    is_midmarket = "mid" in size_lower or "250" in size_lower or "500" in size_lower

    if is_tier_1_title and (is_enterprise or is_midmarket):
        return "Tier 1 - High Fit"
    elif is_tier_1_title or (is_tier_2_title and (is_enterprise or is_midmarket)):
        return "Tier 2 - Medium Fit"
    else:
        return "Tier 3 - Low Fit"


def calculate_watch_percentage(watch_time_minutes: int, total_duration_minutes: int) -> float:
    """Calculates attendance ratio clamped between 0.0% and 100.0%."""
    if total_duration_minutes <= 0:
        return 0.0
    ratio = (watch_time_minutes / total_duration_minutes) * 100.0
    return min(100.0, max(0.0, round(ratio, 1)))


def compute_deterministic_score(
    watch_percentage: float,
    icp_tier: str,
    poll_count: int,
    qna_count: int,
    chat_count: int,
    booth_visits: int,
) -> Tuple[float, dict]:
    """Computes an auditable, deterministic score from 0.0 to 100.0.

    Component Breakdown:
    - Watch Duration: Max 40 pts
    - ICP Authority: Max 30 pts (Tier 1 = 30, Tier 2 = 18, Tier 3 = 6)
    - Active Participation: Max 30 pts
      - Polls: 5 pts each (max 15 pts)
      - Q&A: 7 pts each (max 14 pts)
      - Booth visits: 5 pts (max 5 pts)
      - Chat activity: 1 pt per 2 messages (max 5 pts)
    """
    # 1. Watch duration points (Max 40)
    watch_pts = round((watch_percentage / 100.0) * 40.0, 1)

    # 2. ICP tier points (Max 30)
    if "Tier 1" in icp_tier:
        icp_pts = 30.0
    elif "Tier 2" in icp_tier:
        icp_pts = 18.0
    else:
        icp_pts = 6.0

    # 3. Active participation points (Max 30)
    poll_pts = min(15.0, poll_count * 5.0)
    qna_pts = min(14.0, qna_count * 7.0)
    booth_pts = min(5.0, booth_visits * 5.0)
    chat_pts = min(5.0, (chat_count // 2) * 1.0)
    participation_pts = min(30.0, poll_pts + qna_pts + booth_pts + chat_pts)

    total_score = min(100.0, max(0.0, round(watch_pts + icp_pts + participation_pts, 1)))

    breakdown = {
        "watch_points": watch_pts,
        "icp_points": icp_pts,
        "participation_points": participation_pts,
        "poll_points": poll_pts,
        "qna_points": qna_pts,
        "booth_points": booth_pts,
        "chat_points": chat_pts,
        "total": total_score,
    }

    return total_score, breakdown
