from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...repositories.repos import campaign_repo, agent_config_repo, candidate_repo
from ...models import Campaign, AgentConfiguration, User
from ... import schemas
from ..dependencies import get_db, get_current_user
from ...services.agent_integration import agent_integration_service

router = APIRouter(prefix="/campaigns", tags=["Campaign Management"])


@router.get("", response_model=List[schemas.CampaignOut])
def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all campaigns created by the authenticated user."""
    return campaign_repo.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("", response_model=schemas.CampaignOut, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign_in: schemas.CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a campaign and define configurations for Voice and WhatsApp agents."""
    # 1. Create campaign
    campaign = Campaign(
        user_id=current_user.id,
        name=campaign_in.name,
        job_title=campaign_in.job_title,
        job_description=campaign_in.job_description,
        required_skills=campaign_in.required_skills,
        experience_required=campaign_in.experience_required,
        salary_range=campaign_in.salary_range,
        location=campaign_in.location,
        interview_date=campaign_in.interview_date,
        additional_notes=campaign_in.additional_notes,
        status="draft"
    )
    campaign = campaign_repo.create(db, obj_in=campaign)

    # 2. Add configurations
    if campaign_in.voice_config:
        voice = AgentConfiguration(
            campaign_id=campaign.id,
            agent_type="voice",
            config_data=campaign_in.voice_config.dict()
        )
        db.add(voice)

    if campaign_in.whatsapp_config:
        whatsapp = AgentConfiguration(
            campaign_id=campaign.id,
            agent_type="whatsapp",
            config_data=campaign_in.whatsapp_config.dict()
        )
        db.add(whatsapp)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/{id}", response_model=schemas.CampaignOut)
def get_campaign(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve detailed campaign status and configurations by ID."""
    campaign = campaign_repo.get(db, id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{id}", response_model=schemas.CampaignOut)
def update_campaign(
    id: int,
    campaign_in: schemas.CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update campaign parameters and agent configuration values."""
    campaign = campaign_repo.get(db, id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Update basic details
    campaign_data = campaign_in.dict(exclude={"voice_config", "whatsapp_config"}, exclude_unset=True)
    campaign = campaign_repo.update(db, db_obj=campaign, obj_in=campaign_data)

    # Update configurations if provided
    if campaign_in.voice_config:
        cfg = agent_config_repo.get_by_campaign_and_type(db, campaign_id=id, agent_type="voice")
        if cfg:
            cfg.config_data = campaign_in.voice_config.dict()
            db.add(cfg)
        else:
            cfg = AgentConfiguration(campaign_id=id, agent_type="voice", config_data=campaign_in.voice_config.dict())
            db.add(cfg)

    if campaign_in.whatsapp_config:
        cfg = agent_config_repo.get_by_campaign_and_type(db, campaign_id=id, agent_type="whatsapp")
        if cfg:
            cfg.config_data = campaign_in.whatsapp_config.dict()
            db.add(cfg)
        else:
            cfg = AgentConfiguration(campaign_id=id, agent_type="whatsapp", config_data=campaign_in.whatsapp_config.dict())
            db.add(cfg)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{id}")
def delete_campaign(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a campaign."""
    success = campaign_repo.soft_delete(db, campaign_id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
    return {"status": "success", "detail": "Campaign successfully deleted"}


# ==========================================
# Orchestration Action Endpoints
# ==========================================

@router.post("/{id}/start")
def start_campaign_execution(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Launch the recruitment agents for all campaign candidates."""
    success = agent_integration_service.start_campaign(db, campaign_id=id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to start campaign. Verify status or ownership.")
    return {"status": "success", "detail": "Campaign started successfully"}


@router.post("/{id}/pause")
def pause_campaign_execution(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause agent calling/texting operations."""
    success = agent_integration_service.pause_campaign(db, campaign_id=id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to pause campaign. Verify it is running.")
    return {"status": "success", "detail": "Campaign paused successfully"}


@router.post("/{id}/resume")
def resume_campaign_execution(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resume a paused campaign execution."""
    success = agent_integration_service.resume_campaign(db, campaign_id=id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to resume campaign. Verify it is paused.")
    return {"status": "success", "detail": "Campaign resumed successfully"}


@router.post("/{id}/stop")
def stop_campaign_execution(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Force stop the execution run."""
    success = agent_integration_service.stop_campaign(db, campaign_id=id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to stop campaign. Verify it is active/paused.")
    return {"status": "success", "detail": "Campaign stopped successfully"}


@router.post("/{id}/candidates/link")
def link_candidates_to_campaign(
    id: int,
    link_data: schemas.CandidateBase, # reuse candidate_ids list if we make it custom
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Associate a list of candidate IDs to this campaign."""
    campaign = campaign_repo.get(db, id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    # Link candidates
    linked = []
    # If using custom post payload for ids
    candidate_ids = getattr(link_data, "candidate_ids", [])
    for cand_id in candidate_ids:
        link = candidate_repo.link_candidate_to_campaign(db, candidate_id=cand_id, campaign_id=id)
        linked.append(link.id)
        
    return {"status": "success", "linked_count": len(linked), "link_ids": linked}
