from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...repositories.repos import campaign_repo, candidate_repo, voice_result_repo, whatsapp_result_repo
from ...models import CandidateCampaign, Campaign, User, VoiceResult, WhatsAppResult
from ... import schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics Visualization"])


@router.get("/global", response_model=Dict[str, Any])
def get_global_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve global statistics summaries (totals, average scores) for the dashboard homepage."""
    # Find all campaigns owned by the user
    campaign_ids = [c.id for c in db.query(Campaign.id).filter(
        Campaign.user_id == current_user.id,
        Campaign.deleted_at.is_(None)
    ).all()]

    if not campaign_ids:
        return {
            "total_campaigns": 0,
            "active_campaigns": 0,
            "total_candidates": 0,
            "avg_voice_interest": 0,
            "avg_whatsapp_engagement": 0,
            "recent_activity": []
        }

    # Totals
    total_campaigns = len(campaign_ids)
    active_campaigns = db.query(Campaign).filter(
        Campaign.user_id == current_user.id,
        Campaign.status == "active",
        Campaign.deleted_at.is_(None)
    ).count()

    total_candidates = db.query(CandidateCampaign).filter(
        CandidateCampaign.campaign_id.in_(campaign_ids)
    ).count()

    # Averages
    avg_voice_interest = db.query(func.avg(VoiceResult.interest_score)).filter(
        VoiceResult.campaign_id.in_(campaign_ids)
    ).scalar() or 0.0

    avg_whatsapp_eng = db.query(func.avg(WhatsAppResult.engagement_score)).filter(
        WhatsAppResult.campaign_id.in_(campaign_ids)
    ).scalar() or 0.0

    # Recent activities (last 5 results across both voice and whatsapp)
    recent_activities = []
    # Voice runs
    recent_voice = db.query(VoiceResult).filter(
        VoiceResult.campaign_id.in_(campaign_ids)
    ).order_by(VoiceResult.created_at.desc()).limit(5).all()
    
    for r in recent_voice:
        recent_activities.append({
            "type": "voice",
            "candidate_name": r.candidate.name if r.candidate else "Unknown",
            "campaign_name": r.campaign.name if r.campaign else "Unknown",
            "score": r.interest_score,
            "summary": r.call_summary,
            "time": r.created_at.isoformat()
        })

    # WhatsApp runs
    recent_wa = db.query(WhatsAppResult).filter(
        WhatsAppResult.campaign_id.in_(campaign_ids)
    ).order_by(WhatsAppResult.created_at.desc()).limit(5).all()
    
    for r in recent_wa:
        recent_activities.append({
            "type": "whatsapp",
            "candidate_name": r.candidate.name if r.candidate else "Unknown",
            "campaign_name": r.campaign.name if r.campaign else "Unknown",
            "score": r.engagement_score,
            "summary": r.conversation_summary,
            "time": r.created_at.isoformat()
        })
        
    # Sort activities by time desc
    recent_activities = sorted(recent_activities, key=lambda x: x["time"], reverse=True)[:6]

    return {
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "total_candidates": total_candidates,
        "avg_voice_interest": round(float(avg_voice_interest), 1),
        "avg_whatsapp_engagement": round(float(avg_whatsapp_eng), 1),
        "recent_activity": recent_activities
    }


@router.get("/campaign/{campaign_id}", response_model=schemas.CampaignAnalyticsSummary)
def get_campaign_analytics(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve aggregate statistics (averages, statuses splits) for a single campaign."""
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Candidate splits
    total = db.query(CandidateCampaign).filter(CandidateCampaign.campaign_id == campaign_id).count()
    completed = db.query(CandidateCampaign).filter(
        CandidateCampaign.campaign_id == campaign_id,
        CandidateCampaign.status == "all_completed"
    ).count()

    # Status splits
    statuses = db.query(
        CandidateCampaign.status, func.count(CandidateCampaign.status)
    ).filter(
        CandidateCampaign.campaign_id == campaign_id
    ).group_by(CandidateCampaign.status).all()
    status_counts = {status: count for status, count in statuses}

    # Score averages
    avg_v_interest = db.query(func.avg(VoiceResult.interest_score)).filter(VoiceResult.campaign_id == campaign_id).scalar() or 0.0
    avg_v_comm = db.query(func.avg(VoiceResult.communication_score)).filter(VoiceResult.campaign_id == campaign_id).scalar() or 0.0
    avg_w_interest = db.query(func.avg(WhatsAppResult.interest_score)).filter(WhatsAppResult.campaign_id == campaign_id).scalar() or 0.0
    avg_w_eng = db.query(func.avg(WhatsAppResult.engagement_score)).filter(WhatsAppResult.campaign_id == campaign_id).scalar() or 0.0
    
    # Combined candidate average score
    avg_combined_interest = (float(avg_v_interest) + float(avg_w_interest)) / 2.0 if (avg_v_interest and avg_w_interest) else (float(avg_v_interest or avg_w_interest or 0.0))

    return {
        "campaign_id": campaign_id,
        "total_candidates": total,
        "completed_candidates": completed,
        "avg_interest_score": round(avg_combined_interest, 1),
        "avg_voice_interest": round(float(avg_v_interest), 1),
        "avg_whatsapp_interest": round(float(avg_w_interest), 1),
        "avg_communication_score": round(float(avg_v_comm), 1),
        "avg_engagement_score": round(float(avg_w_eng), 1),
        "status_counts": status_counts
    }


@router.get("/campaign/{campaign_id}/candidates", response_model=List[schemas.UnifiedCandidateView])
def get_campaign_candidates_unified(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve candidates linked to a campaign, matching voice and WhatsApp scores side-by-side."""
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get links
    links = db.query(CandidateCampaign).filter(CandidateCampaign.campaign_id == campaign_id).all()
    unified_list = []
    
    for link in links:
        cand = link.candidate
        if not cand:
            continue
            
        # Get voice results
        v_res = voice_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)
        w_res = whatsapp_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)

        unified_list.append({
            "candidate_id": cand.id,
            "candidate_name": cand.name or "",
            "email": cand.email or "",
            "phone_number": cand.phone_number or cand.phone or "",
            "skills": cand.skills or "",
            "location": cand.location or "",
            "campaign_id": campaign_id,
            "status": link.status,
            "voice_results": v_res,
            "whatsapp_results": w_res
        })
        
    return unified_list
