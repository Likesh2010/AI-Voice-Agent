from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


# ==========================================
# New Campaign-Based Orchestration Schemas
# ==========================================

class UserBase(BaseModel):
    email: EmailStr
    name: str
    company: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class AgentConfigSchema(BaseModel):
    questions: List[str] = Field(default_factory=list)
    evaluation_parameters: List[str] = Field(default_factory=list)
    calling_schedule: Optional[str] = None
    message_templates: Optional[str] = None


class AgentConfigOut(BaseModel):
    id: int
    campaign_id: int
    agent_type: str
    config_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignBase(BaseModel):
    name: str
    job_title: str
    job_description: Optional[str] = None
    required_skills: Optional[str] = None
    experience_required: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    interview_date: Optional[datetime] = None
    additional_notes: Optional[str] = None


class CampaignCreate(CampaignBase):
    voice_config: Optional[AgentConfigSchema] = None
    whatsapp_config: Optional[AgentConfigSchema] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: Optional[str] = None
    experience_required: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    interview_date: Optional[datetime] = None
    additional_notes: Optional[str] = None
    status: Optional[str] = None
    voice_config: Optional[AgentConfigSchema] = None
    whatsapp_config: Optional[AgentConfigSchema] = None


class CampaignOut(CampaignBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    agent_configurations: List[AgentConfigOut] = []

    model_config = ConfigDict(from_attributes=True)


class CandidateCampaignOut(BaseModel):
    id: int
    candidate_id: int
    campaign_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateCampaignUpdate(BaseModel):
    status: str


class CampaignExecutionOut(BaseModel):
    id: int
    campaign_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VoiceResultOut(BaseModel):
    id: int
    candidate_id: int
    campaign_id: int
    interest_score: Optional[int] = None
    communication_score: Optional[int] = None
    confidence_score: Optional[int] = None
    call_summary: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WhatsAppResultOut(BaseModel):
    id: int
    candidate_id: int
    campaign_id: int
    interest_score: Optional[int] = None
    engagement_score: Optional[int] = None
    response_speed: Optional[int] = None
    conversation_summary: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrchestrationCandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    experience: Optional[str] = None
    skills: Optional[str] = None
    location: Optional[str] = None


class OrchestrationCandidateCreate(OrchestrationCandidateBase):
    pass


class OrchestrationCandidateOut(OrchestrationCandidateBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateUploadSummary(BaseModel):
    total_parsed: int
    valid: int
    duplicates_skipped: int
    inserted: int


class CandidateUploadResponse(BaseModel):
    summary: CandidateUploadSummary
    candidates: List[OrchestrationCandidateOut]


class UnifiedCandidateView(BaseModel):
    candidate_id: int
    candidate_name: str
    email: str
    phone_number: str
    skills: Optional[str] = None
    location: Optional[str] = None
    campaign_id: int
    status: str
    voice_results: Optional[VoiceResultOut] = None
    whatsapp_results: Optional[WhatsAppResultOut] = None


class CampaignAnalyticsSummary(BaseModel):
    campaign_id: int
    total_candidates: int
    completed_candidates: int
    avg_interest_score: float
    avg_voice_interest: float
    avg_whatsapp_interest: float
    avg_communication_score: float
    avg_engagement_score: float
    status_counts: Dict[str, int]


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    target_table: str
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignReportOut(BaseModel):
    id: int
    campaign_id: int
    report_type: str
    file_path: str
    format: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Legacy Schemas (Preserved for compatibility)
# ==========================================

class RecruiterBase(BaseModel):
    name: str
    email: str
    company: Optional[str] = None


class RecruiterCreate(RecruiterBase):
    pass


class RecruiterOut(RecruiterBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    remote_type: Optional[str] = None
    status: Optional[str] = "open"


class JobCreate(JobBase):
    recruiter_id: int


class JobOut(JobBase):
    id: int
    recruiter_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    question_text: str
    field_name: str
    order: int = 0
    required: bool = True


class QuestionCreate(QuestionBase):
    job_id: int


class QuestionOut(QuestionBase):
    id: int
    job_id: int

    model_config = ConfigDict(from_attributes=True)


class CandidateBase(BaseModel):
    job_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    current_role: Optional[str] = None
    expected_salary: Optional[str] = None
    notice_period: Optional[str] = None
    preferred_location: Optional[str] = None
    availability: Optional[str] = None
    job_change_intent: Optional[str] = None
    additional_fields: Dict[str, str] = Field(default_factory=dict)


class CandidateCreate(CandidateBase):
    pass


class CandidateOut(CandidateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CallCreate(BaseModel):
    candidate_id: int
    recruiter_id: int
    job_id: int
    direction: str = "outbound"


class CallOut(BaseModel):
    id: int
    candidate_id: int
    recruiter_id: int
    job_id: int
    direction: str
    status: str
    twilio_call_sid: Optional[str] = None
    recording_url: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    conversation_state: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class TranscriptCreate(BaseModel):
    call_id: int
    speaker: str
    text: str
    segment_index: int = 0


class TranscriptOut(TranscriptCreate):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportOut(BaseModel):
    call_id: int
    interest_score: int
    interest_category: str
    recommendation: str
    summary: Optional[str]
    key_observations: Optional[str]
    risk_factors: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VoiceResponseOut(BaseModel):
    prompt_text: str
    tts_path: Optional[str] = None
    call_id: int


class AnalyzeResponse(BaseModel):
    candidate_updates: Dict[str, Any]
    sentiment: str
    enthusiasm: int
    clarity: str
    follow_up: Optional[str]
    interest_reasoning: str
