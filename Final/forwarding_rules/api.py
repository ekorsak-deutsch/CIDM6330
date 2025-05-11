from typing import List, Optional, Dict, Any
from ninja import NinjaAPI, Path
from ninja.responses import Response

from .schemas import (
    ForwardingRule,
    ForwardingRuleCreate,
    ForwardingRuleUpdate,
    ForwardingFilter,
    ForwardingFilterCreate,
    Error,
    Message
)
from .repository import create_repositories
from .models import AutoForwarding as DjangoAutoForwarding
from .models import ForwardingFilter as DjangoForwardingFilter
from .tasks import generate_rules_report, generate_stats_report, generate_rules_only_report

# Create API instance
api = NinjaAPI(title="Email Forwarding Rules Audit API")

# Create repositories
rule_repo, filter_repo = create_repositories()

# Helper function to convert database model to API schema
def db_to_api_rule(db_rule, filter_obj=None) -> ForwardingRule:
    """Convert database model to API schema"""
    data = {
        "id": db_rule.id,
        "email": db_rule.email,
        "name": db_rule.name,
        "forwarding_email": db_rule.forwarding_email,
        "disposition": db_rule.disposition,
        "has_forwarding_filters": db_rule.has_forwarding_filters,
        "error": db_rule.error,
        "investigation_note": db_rule.investigation_note,
    }
    
    if filter_obj is None:
        # Get filter for the rule
        filters_list = filter_repo.get_filters_for_rule(data["id"])
        if filters_list:
            # Should be only one filter per rule
            filter_obj = db_to_api_filter(filters_list[0])
        else:
            filter_obj = None
    
    data["filter"] = filter_obj
    return ForwardingRule.model_validate(data)


# Helper function to convert database filter model to API schema
def db_to_api_filter(db_filter) -> ForwardingFilter:
    """Convert database filter model to API schema"""
    data = {
        "id": db_filter.id,
        "forwarding_id": db_filter.forwarding_id,
        "criteria": db_filter.criteria,
        "action": db_filter.action,
        "created_at": db_filter.created_at,
    }
    
    return ForwardingFilter.model_validate(data)


@api.get("/rules/", response=List[ForwardingRule], tags=["rules"])
def get_all_rules(request, skip: int = 0, limit: int = 100):
    """Get all forwarding rules with pagination"""
    # Get rules from repository
    rules = rule_repo.get_all_rules(skip, limit)
    
    # Convert to API schemas
    return [db_to_api_rule(rule) for rule in rules]


@api.get("/rules/{rule_id}", response=ForwardingRule, tags=["rules"])
def get_rule(request, rule_id: int = Path(...)):
    """Get a specific forwarding rule by ID"""
    # Get rule from repository
    rule = rule_repo.get_rule_by_id(rule_id)
    if not rule:
        return Response({"detail": "Rule not found"}, status=404)
    
    # Get filter for the rule
    filters = filter_repo.get_filters_for_rule(rule_id)
    filter_obj = filters[0] if filters else None
    
    # Convert to API schema
    return db_to_api_rule(rule, db_to_api_filter(filter_obj) if filter_obj else None)


@api.put("/rules/{rule_id}/investigation", response=ForwardingRule, tags=["rules"])
def update_investigation_note(request, rule_id: int, update: ForwardingRuleUpdate):
    """Update the investigation note for a forwarding rule"""
    try:
        # Check if rule exists
        rule = rule_repo.get_rule_by_id(rule_id)
        if not rule:
            return Response({"detail": "Rule not found"}, status=404)
        
        # Prepare update data
        updates = {}
        if update.investigation_note is not None:
            updates["investigation_note"] = update.investigation_note
        
        # Update rule in repository
        if updates:
            updated_rule = rule_repo.update_rule(rule_id, updates)
            if not updated_rule:
                return Response({"detail": "Failed to update rule"}, status=500)
        
        # Return updated rule
        return db_to_api_rule(rule if not updates else updated_rule)
    
    except Exception as e:
        # Handle errors
        return Response({"detail": f"Error updating rule: {str(e)}"}, status=500)


@api.delete("/rules/{rule_id}", response={204: None}, tags=["rules"])
def delete_rule(request, rule_id: int):
    """Delete a forwarding rule"""
    # Check if rule exists
    rule = rule_repo.get_rule_by_id(rule_id)
    if not rule:
        return Response({"detail": "Rule not found"}, status=404)
    
    # Delete filter for the rule
    filter_repo.delete_filters_for_rule(rule_id)
    
    # Delete the rule
    success = rule_repo.delete_rule(rule_id)
    if not success:
        return Response({"detail": "Failed to delete rule"}, status=500)
    
    return 204, None


@api.get("/rules/search/", response=List[ForwardingRule], tags=["rules"])
def search_rules(request, email: Optional[str] = None, has_filters: Optional[bool] = None):
    """Search rules with filters"""
    # Search rules in repository
    rules = rule_repo.search_rules(email, has_filters)
    
    # Convert to API schemas
    return [db_to_api_rule(rule) for rule in rules]


@api.get("/stats/", response=Dict[str, int], tags=["statistics"])
def get_statistics(request):
    """Get statistics about forwarding rules"""
    # Get statistics from repository
    return rule_repo.get_statistics()


@api.get("/rules/{rule_id}/filter", response=ForwardingFilter, tags=["filters"])
def get_rule_filter(request, rule_id: int):
    """Get the filter for a specific forwarding rule"""
    # Check if rule exists
    rule = rule_repo.get_rule_by_id(rule_id)
    if not rule:
        return Response({"detail": "Rule not found"}, status=404)
    
    # Get filter for the rule
    filters = filter_repo.get_filters_for_rule(rule_id)
    if not filters:
        return Response({"detail": "Filter not found"}, status=404)
    
    # Convert to API schema
    return db_to_api_filter(filters[0])


@api.post("/reports/generate", response={200: Message}, tags=["reports"])
def generate_full_report_api(request, report_name: str = None):
    """
    Generate a PDF report of all forwarding rules
    
    This operation is asynchronous and will return immediately.
    The report will be generated in the background.
    """
    task = generate_rules_report.delay(report_name)
    return {"message": f"Report generation started (task id: {task.id})"}


@api.post("/reports/stats", response={200: Message}, tags=["reports"])
def generate_stats_report_api(request, report_name: str = None):
    """
    Generate a PDF report containing only statistics about forwarding rules
    
    This operation is asynchronous and will return immediately.
    The report will be generated in the background.
    """
    task = generate_stats_report.delay(report_name)
    return {"message": f"Statistics report generation started (task id: {task.id})"}


@api.post("/reports/rules-only", response={200: Message}, tags=["reports"])
def generate_rules_only_report_api(request, report_name: str = None):
    """
    Generate a PDF report of all forwarding rules without filter details
    
    This operation is asynchronous and will return immediately.
    The report will be generated in the background.
    """
    task = generate_rules_only_report.delay(report_name)
    return {"message": f"Rules-only report generation started (task id: {task.id})"} 