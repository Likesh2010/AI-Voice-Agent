from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from ...repositories.repos import candidate_repo, campaign_repo
from ...models import Candidate, User
from ... import schemas
from ..dependencies import get_db, get_current_user
from ...services.candidate_service import candidate_service

router = APIRouter(prefix="/candidates", tags=["Candidate Database"])


@router.get("", response_model=List[schemas.OrchestrationCandidateOut])
def get_candidates(
    campaign_id: Optional[int] = None,
    search: Optional[str] = None,
    location: Optional[str] = None,
    skills: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve and query candidates in the database. Can filter by Campaign ID, Name/Email search, Location, or Skills."""
    if campaign_id:
        # Verify campaign belongs to user
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign or campaign.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return candidate_repo.get_multi_by_campaign(db, campaign_id=campaign_id, skip=skip, limit=limit)
    
    # Generic query
    query = db.query(Candidate)
    if search:
        query = query.filter(
            (Candidate.name.ilike(f"%{search}%")) | (Candidate.email.ilike(f"%{search}%"))
        )
    if location:
        query = query.filter(Candidate.location.ilike(f"%{location}%"))
    if skills:
        query = query.filter(Candidate.skills.ilike(f"%{skills}%"))
        
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=schemas.OrchestrationCandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate_in: schemas.OrchestrationCandidateCreate,
    campaign_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new candidate profile manually and optionally link to a campaign."""
    # Check if duplicate
    existing = candidate_repo.get_by_email(db, candidate_in.email)
    if existing:
        candidate = existing
    else:
        # Create
        candidate = Candidate(
            name=candidate_in.name,
            email=candidate_in.email,
            phone_number=candidate_in.phone_number,
            phone=candidate_in.phone_number,
            experience=candidate_in.experience,
            skills=candidate_in.skills,
            location=candidate_in.location
        )
        candidate = candidate_repo.create(db, obj_in=candidate)
        
    if campaign_id:
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign or campaign.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Campaign not found")
        candidate_repo.link_candidate_to_campaign(db, candidate.id, campaign_id)
        
    return candidate


@router.post("/upload", response_model=schemas.CandidateUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_candidates_file(
    campaign_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a CSV or Excel file containing candidate contact information and link them to a campaign."""
    # Verify campaign
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    filename = file.filename.lower()
    file_bytes = await file.read()
    
    candidates_data = []
    
    try:
        if filename.endswith(".csv"):
            file_content = file_bytes.decode("utf-8")
            candidates_data = candidate_service.parse_csv(file_content)
        elif filename.endswith((".xlsx", ".xls")):
            candidates_data = candidate_service.parse_excel(file_bytes)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a CSV or Excel (.xlsx) file."
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse file: {str(e)}"
        )

    if not candidates_data:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file contains no candidate data or headers are incorrectly formatted."
        )

    # Import and link
    import_result = candidate_service.import_candidates(db, campaign_id, candidates_data)
    
    # Save upload to audit logs
    from ...models import AuditLog
    audit = AuditLog(
        user_id=current_user.id,
        action="UPLOAD_CANDIDATES",
        target_table="campaigns",
        target_id=str(campaign_id),
        details=import_result["summary"]
    )
    db.add(audit)
    db.commit()
    
    return import_result


@router.get("/{id}", response_model=schemas.OrchestrationCandidateOut)
def get_candidate_details(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve detailed candidate contact info and skill properties by ID."""
    candidate = candidate_repo.get(db, id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
