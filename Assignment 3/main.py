from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
import os
from models import ForwardingRule, ForwardingRuleBase, ForwardingRuleUpdate, ForwardingFilter
from repository import (
    create_repositories,
    AutoForwardingBase,
    AutoForwarding,
    ForwardingFilterBase,
    ForwardingFilter as SQLModelForwardingFilter
)

# Set repository type from environment variable or use sqlmodel as default
REPO_TYPE = os.environ.get("REPO_TYPE", "sqlmodel").lower()
print(f"Using repository type: {REPO_TYPE}")

app = FastAPI(title="Email Forwarding Rules Audit API")

# Create repositories
rule_repo, filter_repo = create_repositories(REPO_TYPE)

# If using memory repository, import sample data directly
# This ensures data is available in the same process
if REPO_TYPE == "memory":
    try:
        print("Loading sample data into memory repository...")
        from sample_data_import import SAMPLE_DATA, store_autoforwarding_data
        store_autoforwarding_data(rule_repo, filter_repo, SAMPLE_DATA, REPO_TYPE)
        print("Sample data loaded successfully!")
    except Exception as e:
        print(f"Error loading sample data: {e}")

# Helper function to convert database model to API model
def db_to_api_rule(db_rule, filters=None):
    """Convert database model to API model"""
    rule_dict = db_rule.dict() if hasattr(db_rule, "dict") else dict(db_rule)
    
    if filters is None:
        # Get filters for the rule
        filters_list = filter_repo.get_filters_for_rule(rule_dict["id"])
        filters = [db_to_api_filter(f) for f in filters_list]
    
    rule_dict["filters"] = filters
    return ForwardingRule(**rule_dict)

# Helper function to convert database filter model to API model
def db_to_api_filter(db_filter):
    """Convert database filter model to API model"""
    filter_dict = db_filter.dict() if hasattr(db_filter, "dict") else dict(db_filter)
    return ForwardingFilter(**filter_dict)

@app.get("/rules/", response_model=List[ForwardingRule])
def get_all_rules(skip: int = 0, limit: int = 100):
    """Get all forwarding rules with pagination"""
    # Get rules from repository
    rules = rule_repo.get_all_rules(skip, limit)
    
    # Convert to API models
    return [db_to_api_rule(rule) for rule in rules]

@app.get("/rules/{rule_id}", response_model=ForwardingRule)
def get_rule(rule_id: int):
    """Get a specific forwarding rule by ID"""
    # Get rule from repository
    rule = rule_repo.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get filters for the rule
    filters = filter_repo.get_filters_for_rule(rule_id)
    
    # Convert to API model
    return db_to_api_rule(rule, [db_to_api_filter(f) for f in filters])

@app.put("/rules/{rule_id}/investigation", response_model=ForwardingRule)
def update_investigation_note(rule_id: int, update: ForwardingRuleUpdate):
    """Update the investigation note for a forwarding rule"""
    try:
        # Check if rule exists
        rule = rule_repo.get_rule_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Prepare update data
        updates = {}
        if update.investigation_note is not None:
            updates["investigation_note"] = update.investigation_note
        
        # Update rule in repository
        if updates:
            updated_rule = rule_repo.update_rule(rule_id, updates)
            if not updated_rule:
                raise HTTPException(status_code=500, detail="Failed to update rule")
            
            # Get filters for the rule
            filters = filter_repo.get_filters_for_rule(rule_id)
            
            # Convert to API model
            return db_to_api_rule(updated_rule, [db_to_api_filter(f) for f in filters])
        
        # If no updates were provided, return the rule as is
        return db_to_api_rule(rule)
    
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=f"Error updating rule: {str(e)}")

@app.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int):
    """Delete a forwarding rule"""
    # Check if rule exists
    rule = rule_repo.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Delete filters for the rule
    filter_repo.delete_filters_for_rule(rule_id)
    
    # Delete the rule
    success = rule_repo.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete rule")
    
    return None

# Additional endpoints for filtering and statistics
@app.get("/rules/search/", response_model=List[ForwardingRule])
def search_rules(email: str = None, has_filters: bool = None):
    """Search rules with filters"""
    # Search rules in repository
    rules = rule_repo.search_rules(email, has_filters)
    
    # Convert to API models
    return [db_to_api_rule(rule) for rule in rules]

@app.get("/stats/")
def get_statistics():
    """Get statistics about forwarding rules"""
    # Get statistics from repository
    return rule_repo.get_statistics()

# Get filters for a specific rule
@app.get("/rules/{rule_id}/filters", response_model=List[ForwardingFilter])
def get_rule_filters(rule_id: int):
    """Get all filters for a specific forwarding rule"""
    # Check if rule exists
    rule = rule_repo.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get filters for the rule
    filters = filter_repo.get_filters_for_rule(rule_id)
    
    # Convert to API models
    return [db_to_api_filter(f) for f in filters]