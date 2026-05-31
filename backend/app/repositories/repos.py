from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .base import BaseRepository
from ..models import (
    User, Campaign, Candidate, CandidateCampaign, AgentConfiguration,
    CampaignExecution, VoiceResult, WhatsAppResult, Notification, AuditLog, Report
)


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self):
        super().__init__(Campaign)

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Campaign]:
        return db.query(Campaign).filter(
            Campaign.user_id == user_id, 
            Campaign.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

    def soft_delete(self, db: Session, campaign_id: int) -> bool:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            from datetime import datetime
            campaign.deleted_at = datetime.utcnow()
            campaign.status = "stopped"
            db.commit()
            return True
        return False


class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self):
        super().__init__(Candidate)

    def get_by_email(self, db: Session, email: str) -> Optional[Candidate]:
        return db.query(Candidate).filter(Candidate.email == email).first()

    def get_by_phone_number(self, db: Session, phone_number: str) -> Optional[Candidate]:
        return db.query(Candidate).filter(Candidate.phone_number == phone_number).first()

    def get_multi_by_campaign(
        self, db: Session, campaign_id: int, skip: int = 0, limit: int = 100
    ) -> List[Candidate]:
        return db.query(Candidate).join(CandidateCampaign).filter(
            CandidateCampaign.campaign_id == campaign_id
        ).offset(skip).limit(limit).all()

    def link_candidate_to_campaign(
        self, db: Session, candidate_id: int, campaign_id: int
    ) -> CandidateCampaign:
        # Check if already linked
        link = db.query(CandidateCampaign).filter(
            and_(
                CandidateCampaign.candidate_id == candidate_id,
                CandidateCampaign.campaign_id == campaign_id
            )
        ).first()
        if link:
            return link
            
        link = CandidateCampaign(candidate_id=candidate_id, campaign_id=campaign_id, status="pending")
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    def get_campaign_link(self, db: Session, candidate_id: int, campaign_id: int) -> Optional[CandidateCampaign]:
        return db.query(CandidateCampaign).filter(
            and_(
                CandidateCampaign.candidate_id == candidate_id,
                CandidateCampaign.campaign_id == campaign_id
            )
        ).first()

    def update_campaign_link_status(self, db: Session, candidate_id: int, campaign_id: int, status: str) -> Optional[CandidateCampaign]:
        link = self.get_campaign_link(db, candidate_id, campaign_id)
        if link:
            link.status = status
            db.add(link)
            db.commit()
            db.refresh(link)
        return link


class AgentConfigurationRepository(BaseRepository[AgentConfiguration]):
    def __init__(self):
        super().__init__(AgentConfiguration)

    def get_by_campaign(self, db: Session, campaign_id: int) -> List[AgentConfiguration]:
        return db.query(AgentConfiguration).filter(AgentConfiguration.campaign_id == campaign_id).all()

    def get_by_campaign_and_type(self, db: Session, campaign_id: int, agent_type: str) -> Optional[AgentConfiguration]:
        return db.query(AgentConfiguration).filter(
            and_(
                AgentConfiguration.campaign_id == campaign_id,
                AgentConfiguration.agent_type == agent_type
            )
        ).first()


class CampaignExecutionRepository(BaseRepository[CampaignExecution]):
    def __init__(self):
        super().__init__(CampaignExecution)

    def get_active_by_campaign(self, db: Session, campaign_id: int) -> Optional[CampaignExecution]:
        return db.query(CampaignExecution).filter(
            and_(
                CampaignExecution.campaign_id == campaign_id,
                CampaignExecution.status == "running"
            )
        ).order_by(CampaignExecution.started_at.desc()).first()


class VoiceResultRepository(BaseRepository[VoiceResult]):
    def __init__(self):
        super().__init__(VoiceResult)

    def get_by_candidate_campaign(self, db: Session, candidate_id: int, campaign_id: int) -> Optional[VoiceResult]:
        return db.query(VoiceResult).filter(
            and_(
                VoiceResult.candidate_id == candidate_id,
                VoiceResult.campaign_id == campaign_id
            )
        ).first()


class WhatsAppResultRepository(BaseRepository[WhatsAppResult]):
    def __init__(self):
        super().__init__(WhatsAppResult)

    def get_by_candidate_campaign(self, db: Session, candidate_id: int, campaign_id: int) -> Optional[WhatsAppResult]:
        return db.query(WhatsAppResult).filter(
            and_(
                WhatsAppResult.candidate_id == candidate_id,
                WhatsAppResult.campaign_id == campaign_id
            )
        ).first()


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self):
        super().__init__(Notification)

    def get_unread_by_user(self, db: Session, user_id: int) -> List[Notification]:
        return db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        ).order_by(Notification.created_at.desc()).all()

    def get_by_user(self, db: Session, user_id: int, limit: int = 50) -> List[Notification]:
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_all_as_read(self, db: Session, user_id: int) -> None:
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).update({Notification.read: True})
        db.commit()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def get_by_user(self, db: Session, user_id: int, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc()).limit(limit).all()


class ReportRepository(BaseRepository[Report]):
    def __init__(self):
        super().__init__(Report)

    def get_by_campaign(self, db: Session, campaign_id: int) -> List[Report]:
        return db.query(Report).filter(Report.campaign_id == campaign_id).all()


# Global Repository Instances
user_repo = UserRepository()
campaign_repo = CampaignRepository()
candidate_repo = CandidateRepository()
agent_config_repo = AgentConfigurationRepository()
execution_repo = CampaignExecutionRepository()
voice_result_repo = VoiceResultRepository()
whatsapp_result_repo = WhatsAppResultRepository()
notification_repo = NotificationRepository()
audit_log_repo = AuditLogRepository()
report_repo = ReportRepository()
