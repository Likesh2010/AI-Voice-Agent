from datetime import datetime
from sqlalchemy.orm import Session
from ..repositories.repos import (
    campaign_repo, execution_repo, candidate_repo, notification_repo, audit_log_repo
)
from ..models import CampaignExecution, Notification, AuditLog
from .simulation_service import SimulationService


class AgentIntegrationService:
    @classmethod
    def start_campaign(cls, db: Session, campaign_id: int, user_id: int) -> bool:
        """Launch the campaign, changing status to 'active' and triggering agent simulation runs."""
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign or campaign.user_id != user_id:
            return False

        if campaign.status == "active":
            return True

        campaign.status = "active"
        db.add(campaign)

        # Create campaign execution record
        execution = CampaignExecution(
            campaign_id=campaign_id,
            status="running",
            triggered_by=user_id,
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        # Find candidates linked to campaign and trigger their execution
        candidates = candidate_repo.get_multi_by_campaign(db, campaign_id, limit=500)
        triggered_count = 0
        for cand in candidates:
            link = candidate_repo.get_campaign_link(db, cand.id, campaign_id)
            if link and link.status == "pending":
                link.status = "executing"
                db.add(link)
                # Trigger the simulation runs in background threads
                SimulationService.trigger_agent_simulation(campaign_id, cand.id)
                triggered_count += 1

        db.commit()

        # Add Notification
        notification = Notification(
            user_id=user_id,
            title="Campaign Launched",
            message=f"Campaign '{campaign.name}' has been successfully launched for {triggered_count} candidates."
        )
        db.add(notification)

        # Add Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="START_CAMPAIGN",
            target_table="campaigns",
            target_id=str(campaign_id),
            details={"triggered_candidates": triggered_count}
        )
        db.add(audit)
        db.commit()

        return True

    @classmethod
    def pause_campaign(cls, db: Session, campaign_id: int, user_id: int) -> bool:
        """Pause a running campaign."""
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign or campaign.user_id != user_id:
            return False

        if campaign.status != "active":
            return False

        campaign.status = "paused"
        db.add(campaign)

        # Update running execution
        active_exec = execution_repo.get_active_by_campaign(db, campaign_id)
        if active_exec:
            active_exec.status = "paused"
            active_exec.ended_at = datetime.utcnow()
            db.add(active_exec)

        db.commit()

        # Add Notification
        notification = Notification(
            user_id=user_id,
            title="Campaign Paused",
            message=f"Campaign '{campaign.name}' has been paused."
        )
        db.add(notification)

        # Add Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="PAUSE_CAMPAIGN",
            target_table="campaigns",
            target_id=str(campaign_id),
            details={}
        )
        db.add(audit)
        db.commit()

        return True

    @classmethod
    def resume_campaign(cls, db: Session, campaign_id: int, user_id: int) -> bool:
        """Resume a paused campaign, triggering any pending candidates."""
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign or campaign.user_id != user_id:
            return False

        if campaign.status != "paused":
            return False

        campaign.status = "active"
        db.add(campaign)

        # Create new execution record
        execution = CampaignExecution(
            campaign_id=campaign_id,
            status="running",
            triggered_by=user_id,
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        # Find candidates who are still 'pending' or 'executing' (if they didn't complete)
        candidates = candidate_repo.get_multi_by_campaign(db, campaign_id, limit=500)
        triggered_count = 0
        for cand in candidates:
            link = candidate_repo.get_campaign_link(db, cand.id, campaign_id)
            if link and link.status in ["pending", "executing"]:
                link.status = "executing"
                db.add(link)
                # Re-trigger simulation run
                SimulationService.trigger_agent_simulation(campaign_id, cand.id)
                triggered_count += 1

        db.commit()

        # Add Notification
        notification = Notification(
            user_id=user_id,
            title="Campaign Resumed",
            message=f"Campaign '{campaign.name}' has been resumed for {triggered_count} candidates."
        )
        db.add(notification)

        # Add Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="RESUME_CAMPAIGN",
            target_table="campaigns",
            target_id=str(campaign_id),
            details={"triggered_candidates": triggered_count}
        )
        db.add(audit)
        db.commit()

        return True

    @classmethod
    def stop_campaign(cls, db: Session, campaign_id: int, user_id: int) -> bool:
        """Stop a running or paused campaign completely."""
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign or campaign.user_id != user_id:
            return False

        if campaign.status not in ["active", "paused"]:
            return False

        campaign.status = "stopped"
        db.add(campaign)

        # Update running execution
        active_exec = execution_repo.get_active_by_campaign(db, campaign_id)
        if active_exec:
            active_exec.status = "stopped"
            active_exec.ended_at = datetime.utcnow()
            db.add(active_exec)

        # Reset candidates who are currently executing back to pending (so they can be re-run if needed)
        candidates = candidate_repo.get_multi_by_campaign(db, campaign_id, limit=500)
        for cand in candidates:
            link = candidate_repo.get_campaign_link(db, cand.id, campaign_id)
            if link and link.status == "executing":
                link.status = "pending"
                db.add(link)

        db.commit()

        # Add Notification
        notification = Notification(
            user_id=user_id,
            title="Campaign Stopped",
            message=f"Campaign '{campaign.name}' has been stopped."
        )
        db.add(notification)

        # Add Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="STOP_CAMPAIGN",
            target_table="campaigns",
            target_id=str(campaign_id),
            details={}
        )
        db.add(audit)
        db.commit()

        return True


agent_integration_service = AgentIntegrationService()
