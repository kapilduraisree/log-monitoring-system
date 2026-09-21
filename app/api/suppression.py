"""Feature 7: Alert Suppression Rules routes."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.engine import get_db
from app.schemas.suppression import SuppressionRuleCreate, SuppressionRuleOut
from app.services import suppression_service
from app.services.audit_service import record as audit
from app.api.deps import require_admin, get_current_user, get_client_ip
from app.models.user import User

router = APIRouter(prefix="/suppression", tags=["suppression"])


@router.get("", response_model=list[SuppressionRuleOut])
def list_rules(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return suppression_service.list_rules(db)


@router.post("", response_model=SuppressionRuleOut, status_code=201)
def create_rule(
    body: SuppressionRuleCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    rule = suppression_service.create_rule(
        db, body.rule_type, body.value, body.reason, admin.id
    )
    audit(db, "CREATE_SUPPRESSION", admin.id, admin.username,
          f"suppression/{rule.id}", detail=f"{body.rule_type}:{body.value}",
          ip_address=get_client_ip(request))
    return rule


@router.patch("/{rule_id}/toggle")
def toggle_rule(
    rule_id: int,
    active: bool,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    rule = suppression_service.toggle_rule(db, rule_id, active)
    if not rule:
        raise HTTPException(404, "Rule not found")
    audit(db, "TOGGLE_SUPPRESSION", admin.id, admin.username,
          f"suppression/{rule_id}", detail=f"active={active}",
          ip_address=get_client_ip(request))
    return rule


@router.delete("/{rule_id}")
def delete_rule(
    rule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    ok = suppression_service.delete_rule(db, rule_id)
    if not ok:
        raise HTTPException(404, "Rule not found")
    audit(db, "DELETE_SUPPRESSION", admin.id, admin.username,
          f"suppression/{rule_id}", ip_address=get_client_ip(request))
    return {"detail": "Deleted"}
