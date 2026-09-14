from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    event_type = Column(String(50), default="Webinar")  # Webinar, Virtual Summit, Field Event
    total_duration_minutes = Column(Integer, default=60)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(50), default="raw")  # raw, processing, processed

    attendees = relationship("Attendee", back_populates="event", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="event", cascade="all, delete-orphan")


class Attendee(Base):
    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    company_size = Column(String(50), default="Mid-Market")  # Enterprise, Mid-Market, SMB
    icp_tier = Column(String(50), default="Tier 2 - Medium Fit")  # Tier 1, Tier 2, Tier 3

    event = relationship("Event", back_populates="attendees")
    signal = relationship("EngagementSignal", back_populates="attendee", uselist=False, cascade="all, delete-orphan")
    intelligence = relationship("LeadIntelligence", back_populates="attendee", uselist=False, cascade="all, delete-orphan")
    campaign = relationship("CampaignDraft", back_populates="attendee", uselist=False, cascade="all, delete-orphan")


class EngagementSignal(Base):
    __tablename__ = "engagement_signals"

    id = Column(Integer, primary_key=True, index=True)
    attendee_id = Column(Integer, ForeignKey("attendees.id"), nullable=False, index=True)
    watch_time_minutes = Column(Integer, default=0)
    watch_percentage = Column(Float, default=0.0)
    poll_responses_count = Column(Integer, default=0)
    poll_data = Column(Text, default="[]")  # JSON string of responses
    qna_questions = Column(Text, default="[]")  # JSON string of questions asked
    chat_messages_count = Column(Integer, default=0)
    booth_visits = Column(Integer, default=0)

    attendee = relationship("Attendee", back_populates="signal")


class LeadIntelligence(Base):
    __tablename__ = "lead_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    attendee_id = Column(Integer, ForeignKey("attendees.id"), nullable=False, index=True)
    deterministic_score = Column(Float, default=0.0)
    ai_intent_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    intent_tier = Column(String(20), default="COLD")  # HOT, WARM, COLD
    key_pain_points = Column(Text, default="[]")  # JSON list
    buying_signals = Column(Text, default="[]")  # JSON list
    ground_truth_quote = Column(Text, default="")  # Verified exact quote from attendee
    hallucination_verified = Column(Boolean, default=True)  # Guardrail pass/fail
    confidence_score = Column(Float, default=1.0)  # 0.0 - 1.0
    ai_reasoning = Column(Text, default="")

    attendee = relationship("Attendee", back_populates="intelligence")


class CampaignDraft(Base):
    __tablename__ = "campaign_drafts"

    id = Column(Integer, primary_key=True, index=True)
    attendee_id = Column(Integer, ForeignKey("attendees.id"), nullable=False, index=True)
    email_subject = Column(String(255), default="")
    email_body = Column(Text, default="")
    linkedin_message = Column(Text, default="")
    slack_alert_payload = Column(Text, default="{}")
    status = Column(String(50), default="DRAFT")  # DRAFT, APPROVED, DISPATCHED
    dispatched_at = Column(DateTime, nullable=True)

    attendee = relationship("Attendee", back_populates="campaign")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    operation = Column(String(100), nullable=False)
    details = Column(Text, default="")
    execution_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship("Event", back_populates="audit_logs")
