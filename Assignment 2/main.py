from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
import sqlite3
import json
from models import ForwardingRule, ForwardingRuleBase, ForwardingRuleUpdate, get_db, init_db

app = FastAPI(title="Email Forwarding Rules Audit API")

# Initialize database
init_db()

@app.get("/rules/", response_model=List[ForwardingRule])
def get_all_rules(skip: int = 0, limit: int = 100, db: sqlite3.Connection = Depends(get_db)):
    """Get all forwarding rules with pagination"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding LIMIT ? OFFSET ?", (limit, skip))
    rules = [dict(row) for row in cursor.fetchall()]
    return rules

@app.get("/rules/{rule_id}", response_model=ForwardingRule)
def get_rule(rule_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get a specific forwarding rule by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    rule = cursor.fetchone()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return dict(rule)

@app.put("/rules/{rule_id}/review", response_model=ForwardingRule)
def update_review_note(rule_id: int, update: ForwardingRuleUpdate, db: sqlite3.Connection = Depends(get_db)):
    """Update the review note for a forwarding rule"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    rule = cursor.fetchone()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update fields
    updates = {}
    if update.review_note is not None:
        updates["review_note"] = update.review_note
    if update.investigation_note is not None:
        updates["investigation_note"] = update.investigation_note
    
    if updates:
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(rule_id)
        cursor.execute(f"UPDATE AutoForwarding SET {set_clause} WHERE id = ?", values)
        db.commit()
    
    # Get updated rule
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    updated_rule = cursor.fetchone()
    return dict(updated_rule)

@app.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Delete a forwarding rule"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    rule = cursor.fetchone()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    cursor.execute("DELETE FROM AutoForwarding WHERE id = ?", (rule_id,))
    db.commit()
    return None

# Additional endpoints for filtering and statistics
@app.get("/rules/search/", response_model=List[ForwardingRule])
def search_rules(email: str = None, has_filters: bool = None, db: sqlite3.Connection = Depends(get_db)):
    """Search rules with filters"""
    cursor = db.cursor()
    query = "SELECT * FROM AutoForwarding WHERE 1=1"
    params = []
    
    if email:
        query += " AND email LIKE ?"
        params.append(f"%{email}%")
    if has_filters is not None:
        query += " AND has_forwarding_filters = ?"
        params.append(has_filters)
    
    cursor.execute(query, params)
    rules = [dict(row) for row in cursor.fetchall()]
    return rules

@app.get("/stats/")
def get_statistics(db: sqlite3.Connection = Depends(get_db)):
    """Get statistics about forwarding rules"""
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM AutoForwarding")
    total_rules = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM AutoForwarding WHERE forwarding_email IS NOT NULL")
    active_forwarding = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM AutoForwarding WHERE has_forwarding_filters = 1")
    with_filters = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM AutoForwarding WHERE error IS NOT NULL")
    with_errors = cursor.fetchone()[0]
    
    return {
        "total_rules": total_rules,
        "active_forwarding": active_forwarding,
        "rules_with_filters": with_filters,
        "rules_with_errors": with_errors
    }

# Add a new endpoint to create rules
@app.post("/rules/", response_model=ForwardingRule, status_code=status.HTTP_201_CREATED)
def create_rule(rule: ForwardingRuleBase, db: sqlite3.Connection = Depends(get_db)):
    """Create a new forwarding rule"""
    cursor = db.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT id FROM AutoForwarding WHERE email = ?", (rule.email,))
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Insert new rule
    columns = ["email", "name", "forwarding_email", "disposition", 
               "has_forwarding_filters", "error", "review_note", "investigation_note"]
    values = [
        rule.email, 
        rule.name, 
        rule.forwarding_email, 
        rule.disposition, 
        rule.has_forwarding_filters, 
        rule.error, 
        rule.review_note, 
        rule.investigation_note
    ]
    
    placeholders = ", ".join(["?"] * len(columns))
    columns_str = ", ".join(columns)
    
    cursor.execute(
        f"INSERT INTO AutoForwarding ({columns_str}) VALUES ({placeholders})",
        values
    )
    db.commit()
    
    # Get the created rule
    rule_id = cursor.lastrowid
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    created_rule = cursor.fetchone()
    
    return dict(created_rule)