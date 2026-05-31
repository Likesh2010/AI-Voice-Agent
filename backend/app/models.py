from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from .db.base import Base


# ==========================================
# New Campaign-Based Orchestration Models
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    campaigns = relationship("Campaign", back_populates="user")
    executions = relationship("CampaignExecution", back_populates="triggered_by_user")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=True)
    required_skills = Column(Text, nullable=True)
    experience_required = Column(Text, nullable=True)
    salary_range = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    interview_date = Column(DateTime, nullable=True)
    additional_notes = Column(Text, nullable=True)
    status = Column(String(50), default="draft")  # draft, active, paused, stopped, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="campaigns")
    agent_configurations = relationship("AgentConfiguration", back_populates="campaign", cascade="all, delete-orphan")
    executions = relationship("CampaignExecution", back_populates="campaign", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="campaign", cascade="all, delete-orphan")
    
    # Many-to-many relationship with Candidate via CandidateCampaign
    candidate_links = relationship("CandidateCampaign", back_populates="campaign", cascade="all, delete-orphan")
    voice_results = relationship("VoiceResult", back_populates="campaign", cascade="all, delete-orphan")
    whatsapp_results = relationship("WhatsAppResult", back_populates="campaign", cascade="all, delete-orphan")


class CandidateCampaign(Base):
    __tablename__ = "candidate_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending")  # pending, executing, voice_completed, whatsapp_completed, all_completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="campaign_links")
    campaign = relationship("Campaign", back_populates="candidate_links")


class AgentConfiguration(Base):
    __tablename__ = "agent_configurations"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(String(50), nullable=False)  # voice, whatsapp
    config_data = Column(JSON, nullable=False)  # questions, evaluation parameters, schedule, message templates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="agent_configurations")


class CampaignExecution(Base):
    __tablename__ = "campaign_executions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)  # running, paused, stopped, completed
    triggered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="executions")
    triggered_by_user = relationship("User", back_populates="executions")


class VoiceResult(Base):
    __tablename__ = "voice_results"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    interest_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    call_summary = Column(Text, nullable=True)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="voice_results")
    campaign = relationship("Campaign", back_populates="voice_results")


class WhatsAppResult(Base):
    __tablename__ = "whatsapp_results"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    interest_score = Column(Integer, nullable=True)
    engagement_score = Column(Integer, nullable=True)
    response_speed = Column(Integer, nullable=True)
    conversation_summary = Column(Text, nullable=True)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="whatsapp_results")
    campaign = relationship("Campaign", back_populates="whatsapp_results")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)
    target_table = Column(String(100), nullable=False)
    target_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


# ==========================================
# Legacy Models (Preserved for compatibility)
# ==========================================

class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    company = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="recruiter")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(128), nullable=True)
    remote_type = Column(String(64), nullable=True)
    status = Column(String(64), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)

    recruiter = relationship("Recruiter", back_populates="jobs")
    questions = relationship("Question", back_populates="job", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="job")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    field_name = Column(String(128), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    required = Column(Integer, default=1)

    job = relationship("Job", back_populates="questions")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    # job_id is kept nullable for legacy calls, optional for new orchestration
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    name = Column(String(256), nullable=True)
    email = Column(String(256), nullable=True)
    phone = Column(String(64), nullable=True)
    # new orchestration phone_number mapping
    phone_number = Column(String(64), nullable=True)
    education = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    current_role = Column(String(256), nullable=True)
    expected_salary = Column(String(128), nullable=True)
    notice_period = Column(String(128), nullable=True)
    preferred_location = Column(String(256), nullable=True)
    availability = Column(String(256), nullable=True)
    job_change_intent = Column(String(128), nullable=True)
    location = Column(String(256), nullable=True) # new orchestration location field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="candidates")
    fields = relationship("CandidateField", back_populates="candidate", cascade="all, delete-orphan")
    calls = relationship("Call", back_populates="candidate")

    # new associations
    campaign_links = relationship("CandidateCampaign", back_populates="candidate", cascade="all, delete-orphan")
    voice_results = relationship("VoiceResult", back_populates="candidate", cascade="all, delete-orphan")
    whatsapp_results = relationship("WhatsAppResult", back_populates="candidate", cascade="all, delete-orphan")


class CandidateField(Base):
    __tablename__ = "candidate_fields"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    field_key = Column(String(128), nullable=False)
    field_value = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="fields")


class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), nullable=False)
    direction = Column(String(32), nullable=False)
    twilio_call_sid = Column(String(128), nullable=True)
    status = Column(String(64), default="initiated")
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    recording_url = Column(Text, nullable=True)
    conversation_state = Column(JSON, nullable=True, default=dict)
    call_metadata = Column(JSON, nullable=True, default=dict)

    candidate = relationship("Candidate", back_populates="calls")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    speaker = Column(String(32), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    segment_index = Column(Integer, default=0)


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    response_time_avg = Column(Integer, nullable=True)
    engagement_score = Column(Integer, nullable=True)
    sentiment_score = Column(Integer, nullable=True)
    enthusiasm_score = Column(Integer, nullable=True)
    curiosity_score = Column(Integer, nullable=True)
    cooperation_score = Column(Integer, nullable=True)
    questions_asked = Column(Integer, nullable=True)
    job_change_intent_score = Column(Integer, nullable=True)
    risk_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    # call_id is nullable now, to support campaign reports too
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    # campaign_id is added for new dashboard reporting
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)
    
    interest_score = Column(Integer, nullable=False)
    interest_category = Column(String(64), nullable=False)
    recommendation = Column(String(64), nullable=False)
    summary = Column(Text, nullable=True)
    key_observations = Column(Text, nullable=True)
    risk_factors = Column(Text, nullable=True)
    
    # new report configurations
    report_type = Column(String(50), nullable=True)  # campaign, candidate, analytics
    file_path = Column(String(512), nullable=True)
    format = Column(String(50), nullable=True)       # pdf, excel
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="reports")
