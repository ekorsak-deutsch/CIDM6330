from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
import sqlite3
import json
from models import ForwardingRule, ForwardingRuleBase, ForwardingRuleUpdate, ForwardingFilter, ForwardingFilterCreate, get_db, init_db

app = FastAPI(title="Email Forwarding Rules Audit API")

# Initialize database
init_db()

# Helper function to get filters for a rule
def get_filters_for_rule(rule_id: int, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ForwardingFilters WHERE forwarding_id = ?", (rule_id,))
    filters = [dict(row) for row in cursor.fetchall()]
    return filters

# Helper function to convert a rule row to a ForwardingRule with filters
def rule_with_filters(rule_dict: dict, db: sqlite3.Connection):
    rule_id = rule_dict["id"]
    filters = get_filters_for_rule(rule_id, db)
    rule_dict["filters"] = filters
    return rule_dict

@app.get("/rules/", response_model=List[ForwardingRule])
def get_all_rules(skip: int = 0, limit: int = 100, db: sqlite3.Connection = Depends(get_db)):
    """Get all forwarding rules with pagination"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding LIMIT ? OFFSET ?", (limit, skip))
    rules = [dict(row) for row in cursor.fetchall()]
    
    # Add filters to each rule
    for rule in rules:
        rule["filters"] = get_filters_for_rule(rule["id"], db)
    
    return rules

@app.get("/rules/{rule_id}", response_model=ForwardingRule)
def get_rule(rule_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get a specific forwarding rule by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    rule = cursor.fetchone()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule_dict = dict(rule)
    rule_dict["filters"] = get_filters_for_rule(rule_id, db)
    
    return rule_dict

@app.put("/rules/{rule_id}/investigation", response_model=ForwardingRule)
def update_investigation_note(rule_id: int, update: ForwardingRuleUpdate, db: sqlite3.Connection = Depends(get_db)):
    """Update the investigation note for a forwarding rule"""
    try:
        cursor = db.cursor()
        
        # First check if the rule exists
        cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
        rule = cursor.fetchone()
        if rule is None:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Prepare update data
        updates = {}
        if update.investigation_note is not None:
            updates["investigation_note"] = update.investigation_note
        
        # Only perform update if there are fields to update
        if updates:
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values())
            values.append(rule_id)
            
            # Execute update
            cursor.execute(f"UPDATE AutoForwarding SET {set_clause} WHERE id = ?", values)
            db.commit()
        
        # Get the updated rule
        cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
        updated_rule = cursor.fetchone()
        if updated_rule is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated rule")
            
        # Convert to dictionary and add filters
        rule_dict = dict(updated_rule)
        rule_dict["filters"] = get_filters_for_rule(rule_id, db)
        
        return rule_dict
    
    except sqlite3.Error as e:
        # Handle database errors
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle other errors
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating rule: {str(e)}")

@app.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Delete a forwarding rule"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    rule = cursor.fetchone()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Delete associated filters first (due to foreign key constraint)
    cursor.execute("DELETE FROM ForwardingFilters WHERE forwarding_id = ?", (rule_id,))
    
    # Then delete the rule
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
    
    # Add filters to each rule
    for rule in rules:
        rule["filters"] = get_filters_for_rule(rule["id"], db)
    
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
    
    cursor.execute("SELECT COUNT(*) FROM ForwardingFilters")
    total_filters = cursor.fetchone()[0]
    
    return {
        "total_rules": total_rules,
        "active_forwarding": active_forwarding,
        "rules_with_filters": with_filters,
        "rules_with_errors": with_errors,
        "total_filters": total_filters
    }

# Only keep the GET endpoint for filters
@app.get("/rules/{rule_id}/filters", response_model=List[ForwardingFilter])
def get_rule_filters(rule_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get all filters for a specific forwarding rule"""
    # Check if rule exists
    cursor = db.cursor()
    cursor.execute("SELECT * FROM AutoForwarding WHERE id = ?", (rule_id,))
    rule = cursor.fetchone()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get filters
    filters = get_filters_for_rule(rule_id, db)
    return filters