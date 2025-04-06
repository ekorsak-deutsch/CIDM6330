#!/usr/bin/env python
"""
Sample data import script for Email Forwarding Rules Audit API.

This script imports sample data into the Django database.

Usage:
    python sample_data_import.py  # Imports sample data into Django database
"""

import argparse
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forwarding_audit.settings')
django.setup()

from forwarding_rules.repository import create_repositories

# Sample data representing forwarding rules
SAMPLE_DATA = [
    {
        "email": "user1@example.com",
        "name": "John Doe",
        "forwarding_email": "forwarding@example.com",
        "disposition": "keep",
        "has_forwarding_filters": True,
        "error": None,
        "investigation_note": "Legitimate forwarding to",
        "filter": {
            "criteria": {
                "from": "newsletter@company.com"
            },
            "action": {
                "forward": "john.archive@example.com"
            },
            "created_at": "2024-01-15"
        }
    },
    {
        "email": "user3@example.com", 
        "name": "Mary Johnson",
        "forwarding_email": "mary.personal@example.com",
        "disposition": "archive",
        "has_forwarding_filters": True, 
        "error": None,
        "investigation_note": "Approved by manager on 2024-03-05",
        "filter": {
            "criteria": {
                "subject": "timesheet"
            },
            "action": {
                "addLabels": "IMPORTANT",
                "forward": "mary.work@example.com"
            },
            "created_at": "2024-02-10"
        }
    },
    {
        "email": "user4@example.com",
        "name": "Bob Wilson",
        "forwarding_email": "bob.backup@example.com",
        "disposition": "trash",
        "has_forwarding_filters": True,
        "error": None,
        "investigation_note": "Needs further investigation - external domain",
        "filter": {
            "criteria": {
                "from": "hacky@hackyhackers.com",
                "subject": "invoice"
            },
            "action": {
                "addLabels": "TRASH",
                "forward": "security@example.com"
            },
            "created_at": "2024-02-02"
        }
    },
    {
        "email": "user2@example.com",
        "name": "Jane Smith",
        "forwarding_email": None,
        "disposition": None,
        "has_forwarding_filters": False,
        "error": "Permission denied",
        "investigation_note": "Error occurred during audit"
    }
]

def store_autoforwarding_data(rule_repo, filter_repo, user_data):
    """
    Import data into repositories
    
    Args:
        rule_repo: Repository for auto-forwarding rules
        filter_repo: Repository for forwarding filters
        user_data: List of user data dictionaries
    """
    for user in user_data:
        email = user["email"]
        name = user["name"]
        forwarding_email = user.get("forwarding_email")
        disposition = user.get("disposition")
        has_filters = user.get("has_forwarding_filters", False)
        error = user.get("error")
        investigation_note = user.get("investigation_note")

        # Create a rule
        rule_data = {
            "email": email,
            "name": name,
            "forwarding_email": forwarding_email,
            "disposition": disposition,
            "has_forwarding_filters": has_filters,
            "error": error,
            "investigation_note": investigation_note
        }
        
        # Check if rule already exists by searching for email
        existing_rules = rule_repo.search_rules(email=email)
        existing_rule = next(iter(existing_rules), None)
        
        if existing_rule:
            # Update existing rule
            rule_id = existing_rule.id
            rule = rule_repo.update_rule(rule_id, rule_data)
        else:
            # Create new rule
            rule = rule_repo.create_rule(rule_data)
            rule_id = rule.id
            
        # Delete existing filter
        filter_repo.delete_filters_for_rule(rule_id)
        
        # Create filter if it exists
        filter_data = user.get("filter")
        if filter_data:
            criteria = filter_data.get("criteria", {})
            action = filter_data.get("action", {})
            created_at = filter_data.get("created_at")
            
            filter_data = {
                "forwarding_id": rule_id,
                "criteria": criteria,
                "action": action,
                "created_at": created_at
            }
            
            filter_repo.create_filter(filter_data)
            
            # Ensure rule is marked as having filters
            if not rule.has_forwarding_filters:
                rule_repo.update_rule(rule_id, {"has_forwarding_filters": True})

def print_repository_results(rule_repo, filter_repo):
    """
    Print results from repositories
    
    Args:
        rule_repo: Repository for auto-forwarding rules
        filter_repo: Repository for forwarding filters
    """
    print("\nAuto-Forwarding Rules:")
    rules = rule_repo.get_all_rules()
    for rule in rules:
        print(f"ID: {rule.id}, Email: {rule.email}, Name: {rule.name}")
        
        # Print filter for this rule
        filters = filter_repo.get_filters_for_rule(rule.id)
        if filters:
            print("  Filter:")
            for f in filters:
                criteria_str = ", ".join([f"{k}: {v}" for k, v in f.criteria.items()])
                action_str = ", ".join([f"{k}: {v}" for k, v in f.action.items()])
                print(f"    ID: {f.id}, Criteria: {criteria_str}, Action: {action_str}, Created At: {f.created_at}")
        else:
            print("  No filter")
        print()

    # Print statistics
    stats = rule_repo.get_statistics()
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")

def import_data():
    """
    Import data into the Django database
    """
    # Create repositories
    rule_repo, filter_repo = create_repositories()
    
    # Store data in repository
    store_autoforwarding_data(rule_repo, filter_repo, SAMPLE_DATA)
    
    # Print results
    print_repository_results(rule_repo, filter_repo)

def main():
    """Main entry point"""
    print("Importing sample data into Django database...")
    import_data()
    print("\nSample data import complete.")

if __name__ == "__main__":
    main()
