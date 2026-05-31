import hmac
import hashlib
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from ...core.config import settings
from ...repositories.repos import (
    candidate_repo, voice_result_repo, whatsapp_result_repo, campaign_repo, notification_repo
)
from ...models import VoiceResult, WhatsAppResult, Notification
from ..dependencies import get_db

router = APIRouter(prefix="/webhooks", tags=["Webhooks Callback System"])


async def verify_webhook_signature(request: Request, x_webhook_signature: str = Header(None)):
    """Verifies that the webhook request payload is signed by the verified AI Agents."""
    body_bytes = await request.body()
    
    # Shared secret
    shared_secret = getattr(settings, "webhook_shared_secret", "dev_webhook_secret_456!")
    
    # Compute signature
    computed = hmac.new(
        shared_secret.encode("utf-8"),
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # Verification checks
    if not x_webhook_signature:
        # Developer bypass in development mode
        is_dev = getattr(settings, "environment", "development") == "development"
        if is_dev:
            print("WARNING: Webhook signature header missing. Bypassing check in development mode.")
            return body_bytes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Webhook-Signature header missing"
        )
        
    if not hmac.compare_digest(computed, x_webhook_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature hash"
        )
        
    return body_bytes


@router.post("/voice/results")
async def receive_voice_results(
    request: Request,
    body: bytes = Depends(verify_webhook_signature),
    db: Session = Depends(get_db)
):
    """Callback endpoint for the Voice Agent to post candidate interview evaluation scores."""
    import json
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
        
    campaign_id = data.get("campaign_id")
    candidate_id = data.get("candidate_id")
    interest_score = data.get("interest_score")
    comm_score = data.get("communication_score")
    conf_score = data.get("confidence_score")
    summary = data.get("call_summary")
    raw_response = data.get("raw_response", {})
    
    if not campaign_id or not candidate_id:
        raise HTTPException(status_code=422, detail="Missing campaign_id or candidate_id")

    # Log/Save result
    existing = voice_result_repo.get_by_candidate_campaign(db, candidate_id, campaign_id)
    if existing:
        existing.interest_score = interest_score
        existing.communication_score = comm_score
        existing.confidence_score = conf_score
        existing.call_summary = summary
        existing.raw_response = raw_response
        db.add(existing)
    else:
        v_result = VoiceResult(
            candidate_id=candidate_id,
            campaign_id=campaign_id,
            interest_score=interest_score,
            communication_score=comm_score,
            confidence_score=conf_score,
            call_summary=summary,
            raw_response=raw_response
        )
        db.add(v_result)

    # Progress link status
    link = candidate_repo.get_campaign_link(db, candidate_id, campaign_id)
    if link:
        # If whatsapp is also completed, mark all as completed, else voice_completed
        if link.status == "whatsapp_completed":
            link.status = "all_completed"
        else:
            link.status = "voice_completed"
        db.add(link)

    # Auto trigger Notification for client user
    campaign = campaign_repo.get(db, campaign_id)
    candidate = candidate_repo.get(db, candidate_id)
    if campaign and candidate:
        notif = Notification(
            user_id=campaign.user_id,
            title="Voice Evaluation Received",
            message=f"Voice agent completed call for '{candidate.name}' in campaign '{campaign.name}'. Interest Score: {interest_score}/100."
        )
        db.add(notif)

    db.commit()
    return {"status": "success", "detail": "Voice result recorded successfully"}


@router.post("/whatsapp/results")
async def receive_whatsapp_results(
    request: Request,
    body: bytes = Depends(verify_webhook_signature),
    db: Session = Depends(get_db)
):
    """Callback endpoint for the WhatsApp Agent to post candidate conversation evaluation scores."""
    import json
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
        
    campaign_id = data.get("campaign_id")
    candidate_id = data.get("candidate_id")
    interest_score = data.get("interest_score")
    engagement_score = data.get("engagement_score")
    response_speed = data.get("response_speed")
    summary = data.get("conversation_summary")
    raw_response = data.get("raw_response", {})
    
    if not campaign_id or not candidate_id:
        raise HTTPException(status_code=422, detail="Missing campaign_id or candidate_id")

    # Log/Save result
    existing = whatsapp_result_repo.get_by_candidate_campaign(db, candidate_id, campaign_id)
    if existing:
        existing.interest_score = interest_score
        existing.engagement_score = engagement_score
        existing.response_speed = response_speed
        existing.conversation_summary = summary
        existing.raw_response = raw_response
        db.add(existing)
    else:
        w_result = WhatsAppResult(
            candidate_id=candidate_id,
            campaign_id=campaign_id,
            interest_score=interest_score,
            engagement_score=engagement_score,
            response_speed=response_speed,
            conversation_summary=summary,
            raw_response=raw_response
        )
        db.add(w_result)

    # Progress link status
    link = candidate_repo.get_campaign_link(db, candidate_id, campaign_id)
    if link:
        if link.status == "voice_completed":
            link.status = "all_completed"
        else:
            link.status = "whatsapp_completed"
        db.add(link)

    # Trigger notification
    campaign = campaign_repo.get(db, campaign_id)
    candidate = candidate_repo.get(db, candidate_id)
    if campaign and candidate:
        notif = Notification(
            user_id=campaign.user_id,
            title="WhatsApp Evaluation Received",
            message=f"WhatsApp agent completed chat with '{candidate.name}' in campaign '{campaign.name}'. Engagement Score: {engagement_score}/100."
        )
        db.add(notif)

    db.commit()
    return {"status": "success", "detail": "WhatsApp result recorded successfully"}
