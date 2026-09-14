from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


# Event Schemas
class EventBase(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Zuddl Product Summit 2026: AI-Native Event Ops"})
    event_type: str = Field("Webinar", json_schema_extra={"example": "Webinar"})
    total_duration_minutes: int = Field(60, json_schema_extra={"example": 60})


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: int
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


# Ingestion Schemas
class PollResponseItem(BaseModel):
    poll_question: str
    selected_option: str


class AttendeeIngestItem(BaseModel):
    name: str
    email: str
    company: str
    job_title: str
    company_size: Optional[str] = "Mid-Market"
    watch_time_minutes: int = 0
    poll_responses: List[PollResponseItem] = []
    qna_questions: List[str] = []
    chat_messages_count: int = 0
    booth_visits: int = 0


class EventIngestPayload(BaseModel):
    event_title: str
    event_type: str = "Webinar"
    total_duration_minutes: int = 60
    attendees: List[AttendeeIngestItem]


# Intelligence & Campaign Schemas
class LeadIntelligenceResponse(BaseModel):
    deterministic_score: float
    ai_intent_score: float
    final_score: float
    intent_tier: str
    key_pain_points: List[str]
    buying_signals: List[str]
    ground_truth_quote: str
    hallucination_verified: bool
    confidence_score: float
    ai_reasoning: str


class CampaignDraftResponse(BaseModel):
    id: int
    email_subject: str
    email_body: str
    linkedin_message: str
    status: str
    dispatched_at: Optional[datetime] = None


class LeadDossierResponse(BaseModel):
    id: int
    name: str
    email: str
    company: str
    job_title: str
    company_size: str
    icp_tier: str
    watch_time_minutes: int
    watch_percentage: float
    poll_data: List[PollResponseItem]
    qna_questions: List[str]
    chat_messages_count: int
    intelligence: Optional[LeadIntelligenceResponse]
    campaign: Optional[CampaignDraftResponse]


class PipelineProcessResponse(BaseModel):
    event_id: int
    total_processed: int
    hot_leads_count: int
    warm_leads_count: int
    cold_leads_count: int
    guardrail_flagged_count: int
    execution_time_ms: int


class DispatchWebhookRequest(BaseModel):
    target: str = Field("SLACK", json_schema_extra={"example": "SLACK"})
    override_email_body: Optional[str] = None


class DispatchWebhookResponse(BaseModel):
    success: bool
    target: str
    status: str
    message: str
    dispatched_payload: dict
