"""Feature 7: Alert Suppression Rules service."""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.suppression_rule import SuppressionRule


def list_rules(db: Session) -> list[SuppressionRule]:
    return db.query(SuppressionRule).order_by(SuppressionRule.created_at.desc()).all()


def create_rule(
    db: Session,
    rule_type: str,
    value: str,
    reason: Optional[str] = None,
    created_by: Optional[int] = None,
) -> SuppressionRule:
    rule = SuppressionRule(
        rule_type=rule_type,
        value=value,
        reason=reason,
        is_active=True,
        created_by=created_by,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def toggle_rule(db: Session, rule_id: int, active: bool) -> Optional[SuppressionRule]:
    rule = db.query(SuppressionRule).filter(SuppressionRule.id == rule_id).first()
    if not rule:
        return None
    rule.is_active = active
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: int) -> bool:
    rule = db.query(SuppressionRule).filter(SuppressionRule.id == rule_id).first()
    if not rule:
        return False
    db.delete(rule)
    db.commit()
    return True
