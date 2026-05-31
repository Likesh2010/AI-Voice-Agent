import hmac
import hashlib
import json
import time
import threading
import requests
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..repositories.repos import campaign_repo, candidate_repo, voice_result_repo, whatsapp_result_repo
from ..core.config import settings

class SimulationService:
    @staticmethod
    def calculate_match_scores(candidate_skills: str, required_skills: str) -> Dict[str, int]:
        """Analyze skills compatibility to generate a realistic match score."""
        cand_words = set(re.findall(r"\w+", (candidate_skills or "").lower())) if 're' in globals() else set((candidate_skills or "").lower().split())
        req_words = set(re.findall(r"\w+", (required_skills or "").lower())) if 're' in globals() else set((required_skills or "").lower().split())
        
        # simple word overlap
        overlap = cand_words.intersection(req_words)
        match_ratio = len(overlap) / max(1, len(req_words))
        
        # Base scores
        base_interest = 55 + int(match_ratio * 40)
        base_comm = 60 + int(hash(candidate_skills or "") % 30)
        base_conf = 55 + int(hash(candidate_skills or "") % 40)
        base_speed = 50 + int(hash(candidate_skills or "") % 45)
        
        return {
            "interest": min(100, max(0, base_interest)),
            "communication": min(100, max(0, base_comm)),
            "confidence": min(100, max(0, base_conf)),
            "engagement": min(100, max(0, base_interest - 5)),
            "speed": min(100, max(0, base_speed))
        }

    @classmethod
    def trigger_agent_simulation(cls, campaign_id: int, candidate_id: int) -> None:
        """Run the simulation asynchronously in a background thread."""
        thread = threading.Thread(target=cls._run_simulation, args=(campaign_id, candidate_id))
        thread.daemon = True
        thread.start()

    @classmethod
    def _run_simulation(cls, campaign_id: int, candidate_id: int) -> None:
        """Asynchronously simulates voice and whatsapp interactions with the candidate."""
        # Wait 4 seconds to simulate latency
        time.sleep(4.0)
        
        db = SessionLocal()
        try:
            campaign = campaign_repo.get(db, campaign_id)
            candidate = candidate_repo.get(db, candidate_id)
            if not campaign or not candidate:
                return

            # Skip if campaign is paused/stopped in database
            if campaign.status not in ["active", "executing"]:
                return

            # Compute scores
            scores = cls.calculate_match_scores(candidate.skills, campaign.required_skills)

            # Webhook payloads
            voice_payload = {
                "campaign_id": campaign_id,
                "candidate_id": candidate_id,
                "interest_score": scores["interest"],
                "communication_score": scores["communication"],
                "confidence_score": scores["confidence"],
                "call_summary": f"Simulated call with {candidate.name}. They spoke clearly about their experience in {candidate.skills or 'their field'}.",
                "raw_response": {
                    "duration_seconds": 120,
                    "recording_url": "https://api.voiceagent.ai/recordings/mock_recording.mp3"
                }
            }

            whatsapp_payload = {
                "campaign_id": campaign_id,
                "candidate_id": candidate_id,
                "interest_score": scores["interest"] - 2,
                "engagement_score": scores["engagement"],
                "response_speed": scores["speed"],
                "conversation_summary": f"Simulated WhatsApp chat. Candidate responded quickly and confirmed they are in {candidate.location}.",
                "raw_response": {
                    "exchanged_messages": 6
                }
            }

            # Shared secret for security signatures
            shared_secret = getattr(settings, "webhook_shared_secret", "dev_webhook_secret_456!")
            
            # Post Webhook updates
            base_url = settings.public_base_url or "http://127.0.0.1:8000"
            base_url = base_url.rstrip("/")

            for agent_type, payload, path in [
                ("voice", voice_payload, "/api/v1/webhooks/voice/results"),
                ("whatsapp", whatsapp_payload, "/api/v1/webhooks/whatsapp/results")
            ]:
                body_bytes = json.dumps(payload).encode("utf-8")
                signature = hmac.new(
                    shared_secret.encode("utf-8"),
                    body_bytes,
                    hashlib.sha256
                ).hexdigest()

                headers = {
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature
                }

                url = f"{base_url}{path}"
                try:
                    resp = requests.post(url, data=body_bytes, headers=headers, timeout=5)
                    if resp.status_code != 200:
                        # Fallback: commit results directly if API fails
                        cls._commit_direct_fallback(db, agent_type, payload)
                except Exception:
                    # Fallback direct commit
                    cls._commit_direct_fallback(db, agent_type, payload)

        finally:
            db.close()

    @classmethod
    def _commit_direct_fallback(cls, db: Session, agent_type: str, payload: Dict[str, Any]) -> None:
        """Fallback method to insert data directly into tables if webhook endpoint is offline."""
        campaign_id = payload["campaign_id"]
        candidate_id = payload["candidate_id"]
        
        # Log fallback warning
        print(f"Simulation Webhook failed. Running fallback direct DB commit for {agent_type} candidate {candidate_id}")
        
        if agent_type == "voice":
            existing = voice_result_repo.get_by_candidate_campaign(db, candidate_id, campaign_id)
            if not existing:
                res = VoiceResult(
                    candidate_id=candidate_id,
                    campaign_id=campaign_id,
                    interest_score=payload["interest_score"],
                    communication_score=payload["communication_score"],
                    confidence_score=payload["confidence_score"],
                    call_summary=payload["call_summary"],
                    raw_response=payload["raw_response"]
                )
                db.add(res)
        else:
            existing = whatsapp_result_repo.get_by_candidate_campaign(db, candidate_id, campaign_id)
            if not existing:
                res = WhatsAppResult(
                    candidate_id=candidate_id,
                    campaign_id=campaign_id,
                    interest_score=payload["interest_score"],
                    engagement_score=payload["engagement_score"],
                    response_speed=payload["response_speed"],
                    conversation_summary=payload["conversation_summary"],
                    raw_response=payload["raw_response"]
                )
                db.add(res)

        # Update candidate campaign link status
        link = candidate_repo.get_campaign_link(db, candidate_id, campaign_id)
        if link:
            if agent_type == "voice":
                link.status = "voice_completed" if link.status != "whatsapp_completed" else "all_completed"
            else:
                link.status = "whatsapp_completed" if link.status != "voice_completed" else "all_completed"
            db.add(link)
        
        db.commit()


# Import VoiceResult & WhatsAppResult within file to avoid circular dependency
from ..models import VoiceResult, WhatsAppResult
import re
