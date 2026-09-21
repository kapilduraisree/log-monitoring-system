"""Report routes — summary, CSV, JSON, PDF export. Feature 5: trigger scheduled send."""

from typing import Literal
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.engine import get_db
from app.services import report_service
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(tags=["reports"])

Period = Literal["daily", "weekly", "monthly"]


@router.get("/report")
def get_report(
    period: Period = Query("daily"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return report_service.build_report(db, period)


@router.get("/export/csv")
def export_csv(
    period: Period = Query("daily"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    data = report_service.export_csv(db, period)
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="report_{period}.csv"'},
    )


@router.get("/export/json")
def export_json(
    period: Period = Query("daily"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    data = report_service.export_json(db, period)
    return Response(content=data, media_type="application/json")


@router.get("/export/pdf")
def export_pdf(
    period: Period = Query("daily"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    data = report_service.export_pdf(db, period)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{period}.pdf"'},
    )


# Feature 5: manually trigger scheduled report email
@router.post("/report/send-email")
def send_report_email(
    period: Period = Query("daily"),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    ok = report_service.send_scheduled_report(db, period)
    return {"sent": ok}
