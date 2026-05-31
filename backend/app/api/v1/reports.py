from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from ...repositories.repos import campaign_repo, report_repo
from ...models import User, Report
from ... import schemas
from ..dependencies import get_db, get_current_user
from ...services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports & Exporters"])


@router.post("/campaign/{campaign_id}/generate", response_model=schemas.CampaignReportOut)
def generate_campaign_report(
    campaign_id: int,
    report_type: str = Query(..., regex="^(campaign|candidate|analytics)$"),
    format: str = Query(..., regex="^(pdf|excel|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger the creation of a campaign summary report in PDF or CSV format."""
    # Verify campaign
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        # We support PDF or CSV (Excel is mapped to CSV or PDF)
        if format in ["csv", "excel"]:
            file_path = report_service.generate_campaign_csv(db, campaign_id)
            fmt = "excel" if format == "excel" else "csv"
        else:
            file_path = report_service.generate_campaign_pdf(db, campaign_id)
            fmt = "pdf"

        # Save DB record
        report = report_service.save_report_record(
            db, campaign_id=campaign_id, report_type=report_type, file_path=file_path, format=fmt
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/campaign/{campaign_id}", response_model=List[schemas.CampaignReportOut])
def list_campaign_reports(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all previously generated reports for a campaign."""
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return report_repo.get_by_campaign(db, campaign_id)


@router.get("/download/{report_id}")
def download_report_file(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a generated campaign report file securely by ID."""
    report = report_repo.get(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report record not found")

    # Verify ownership of campaign
    campaign = campaign_repo.get(db, report.campaign_id)
    if not campaign or campaign.user_id != current_user.id or campaign.deleted_at is not None:
        raise HTTPException(status_code=403, detail="Unauthorized access to this report file")

    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Physical report file missing on disk")

    # Set media type
    media_type = "application/pdf" if report.format == "pdf" else "text/csv"
    filename = os.path.basename(report.file_path)
    
    return FileResponse(
        report.file_path,
        media_type=media_type,
        filename=filename
    )
