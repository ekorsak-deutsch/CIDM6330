from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
from models import SessionLocal

app = FastAPI(title="Email Forwarding Rules Audit API")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/rules/", response_model=List[models.ForwardingRule])
def get_all_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all forwarding rules with pagination"""
    rules = db.query(models.AutoForwarding).offset(skip).limit(limit).all()
    return rules

@app.get("/rules/{rule_id}", response_model=models.ForwardingRule)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific forwarding rule by ID"""
    rule = db.query(models.AutoForwarding).filter(models.AutoForwarding.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@app.put("/rules/{rule_id}/review", response_model=models.ForwardingRule)
def update_review_note(rule_id: int, update: models.ForwardingRuleUpdate, db: Session = Depends(get_db)):
    """Update the review note for a forwarding rule"""
    rule = db.query(models.AutoForwarding).filter(models.AutoForwarding.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    if update.review_note is not None:
        rule.review_note = update.review_note
    if update.investigation_note is not None:
        rule.investigation_note = update.investigation_note
    
    db.commit()
    db.refresh(rule)
    return rule

@app.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a forwarding rule"""
    rule = db.query(models.AutoForwarding).filter(models.AutoForwarding.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return None

# Additional endpoints for filtering and statistics
@app.get("/rules/search/", response_model=List[models.ForwardingRule])
def search_rules(email: str = None, has_filters: bool = None, db: Session = Depends(get_db)):
    """Search rules with filters"""
    query = db.query(models.AutoForwarding)
    
    if email:
        query = query.filter(models.AutoForwarding.email.contains(email))
    if has_filters is not None:
        query = query.filter(models.AutoForwarding.has_forwarding_filters == has_filters)
    
    return query.all()

@app.get("/stats/")
def get_statistics(db: Session = Depends(get_db)):
    """Get statistics about forwarding rules"""
    total_rules = db.query(models.AutoForwarding).count()
    active_forwarding = db.query(models.AutoForwarding).filter(
        models.AutoForwarding.forwarding_email.isnot(None)
    ).count()
    with_filters = db.query(models.AutoForwarding).filter(
        models.AutoForwarding.has_forwarding_filters == True
    ).count()
    with_errors = db.query(models.AutoForwarding).filter(
        models.AutoForwarding.error.isnot(None)
    ).count()
    
    return {
        "total_rules": total_rules,
        "active_forwarding": active_forwarding,
        "rules_with_filters": with_filters,
        "rules_with_errors": with_errors
    } 