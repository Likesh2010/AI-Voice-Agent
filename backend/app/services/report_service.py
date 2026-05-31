import os
import csv
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..repositories.repos import campaign_repo, candidate_repo, voice_result_repo, whatsapp_result_repo, report_repo
from ..models import Report

# Directory to store reports
REPORTS_DIR = "./static/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


class ReportService:
    @classmethod
    def generate_campaign_csv(cls, db: Session, campaign_id: int) -> str:
        """Generate a CSV report of candidates and their scores for a campaign."""
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")

        filename = f"campaign_{campaign_id}_{int(datetime.utcnow().timestamp())}.csv"
        file_path = os.path.join(REPORTS_DIR, filename)

        # Retrieve candidates
        candidates = candidate_repo.get_multi_by_campaign(db, campaign_id, limit=1000)

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Headers
            writer.writerow([
                "Campaign ID", "Campaign Name", "Job Title", 
                "Candidate ID", "Candidate Name", "Candidate Email", "Phone Number", 
                "Status", "Voice Interest Score", "Voice Communication Score", "Voice Confidence Score", 
                "WhatsApp Interest Score", "WhatsApp Engagement Score", "WhatsApp Response Speed",
                "Voice Summary", "WhatsApp Summary"
            ])

            for cand in candidates:
                # Get statuses
                link = candidate_repo.get_campaign_link(db, cand.id, campaign_id)
                status = link.status if link else "pending"

                # Get voice results
                v_res = voice_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)
                w_res = whatsapp_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)

                writer.writerow([
                    campaign.id, campaign.name, campaign.job_title,
                    cand.id, cand.name, cand.email, cand.phone_number or cand.phone or "",
                    status,
                    v_res.interest_score if v_res else "", 
                    v_res.communication_score if v_res else "", 
                    v_res.confidence_score if v_res else "",
                    w_res.interest_score if w_res else "", 
                    w_res.engagement_score if w_res else "", 
                    w_res.response_speed if w_res else "",
                    v_res.call_summary if v_res else "",
                    w_res.conversation_summary if w_res else ""
                ])

        return file_path

    @classmethod
    def generate_campaign_pdf(cls, db: Session, campaign_id: int) -> str:
        """Generate a text/HTML-formatted markdown report converted to PDF (or structured text report for fallback)."""
        campaign = campaign_repo.get(db, campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")

        filename = f"campaign_{campaign_id}_{int(datetime.utcnow().timestamp())}.pdf"
        file_path = os.path.join(REPORTS_DIR, filename)

        # For production PDF export without heavy GUI servers, we use ReportLab to construct a clean, beautiful PDF document.
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0F172A'), # Slate 900
                spaceAfter=15
            )
            subtitle_style = ParagraphStyle(
                'ReportSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#475569'), # Slate 600
                spaceAfter=20
            )
            body_style = ParagraphStyle(
                'ReportBody',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#334155'), # Slate 700
                spaceAfter=8
            )

            story.append(Paragraph(f"Recruitment Campaign Report", title_style))
            story.append(Paragraph(f"Campaign: {campaign.name} ({campaign.job_title})", subtitle_style))
            story.append(Spacer(1, 10))

            # Job details
            story.append(Paragraph(f"<b>Job Description:</b> {campaign.job_description or 'N/A'}", body_style))
            story.append(Paragraph(f"<b>Skills:</b> {campaign.required_skills or 'N/A'} | <b>Location:</b> {campaign.location or 'N/A'}", body_style))
            story.append(Paragraph(f"<b>Salary:</b> {campaign.salary_range or 'N/A'} | <b>Interview Date:</b> {campaign.interview_date or 'N/A'}", body_style))
            story.append(Spacer(1, 15))

            # Candidates list table
            candidates = candidate_repo.get_multi_by_campaign(db, campaign_id, limit=1000)
            table_data = [[
                "Candidate", "Email", "Status", "Voice Int.", "Voice Comm.", "WhatsApp Int.", "WhatsApp Eng."
            ]]

            for cand in candidates:
                link = candidate_repo.get_campaign_link(db, cand.id, campaign_id)
                status = link.status if link else "pending"
                v_res = voice_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)
                w_res = whatsapp_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)

                v_score = str(v_res.interest_score) if v_res else "-"
                v_comm = str(v_res.communication_score) if v_res else "-"
                w_score = str(w_res.interest_score) if w_res else "-"
                w_eng = str(w_res.engagement_score) if w_res else "-"

                table_data.append([
                    cand.name, cand.email, status, v_score, v_comm, w_score, w_eng
                ])

            t = Table(table_data, colWidths=[100, 150, 80, 50, 50, 50, 50])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')), # Slate 800
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('FONTSIZE', (0,1), (-1,-1), 8),
            ]))
            story.append(t)

            doc.build(story)
        except ImportError:
            # Fallback text PDF simulation if ReportLab is not available
            with open(file_path, mode="w", encoding="utf-8") as f:
                f.write(f"CAMPAIGN REPORT: {campaign.name}\n")
                f.write(f"Job Title: {campaign.job_title}\n")
                f.write(f"Job Description: {campaign.job_description or ''}\n\n")
                f.write("CANDIDATES:\n")
                candidates = candidate_repo.get_multi_by_campaign(db, campaign_id)
                for cand in candidates:
                    v_res = voice_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)
                    w_res = whatsapp_result_repo.get_by_candidate_campaign(db, cand.id, campaign_id)
                    v_score = v_res.interest_score if v_res else "-"
                    w_score = w_res.interest_score if w_res else "-"
                    f.write(f"- {cand.name} ({cand.email}) | Voice Score: {v_score} | WhatsApp Score: {w_score}\n")

        return file_path

    @classmethod
    def save_report_record(
        cls, db: Session, campaign_id: int, report_type: str, file_path: str, format: str
    ) -> Report:
        """Create and commit a report metadata record in the database."""
        report = Report(
            campaign_id=campaign_id,
            report_type=report_type,
            file_path=file_path,
            format=format,
            interest_score=0, # legacy fields placeholder
            interest_category="N/A",
            recommendation="N/A"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report


report_service = ReportService()
