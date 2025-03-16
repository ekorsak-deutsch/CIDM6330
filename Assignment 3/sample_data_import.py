#!/usr/bin/env python
"""
Sample data import script for Email Forwarding Rules Audit API.

This script imports sample data into different repository types.

Usage:
    python sample_data_import.py                    # Uses default repository (sqlmodel)
    python sample_data_import.py --repo=sqlmodel    # Uses SQLModel repository
    python sample_data_import.py --repo=csv         # Uses CSV repository
    python sample_data_import.py --repo=memory      # Uses in-memory repository
    python sample_data_import.py --repo=all         # Uses all repository types
"""

import argparse
import os
from repository import (
    create_repositories,
    AutoForwardingBase,
    AutoForwarding,
    ForwardingFilterBase,
    ForwardingFilter
)

# Sample data representing forwarding rules
SAMPLE_DATA = [
    {
        "email": "user1@example.com",
        "name": "John Doe",
        "autoForwarding": {"enabled": True, "emailAddress": "forwarding@example.com", "disposition": "keep"},
        "forwardingFilters": [{"emailAddress": "specific@example.com", "createdAt": "2024-02-28"}],
        "error": None,
        "investigation_note": "Legitimate forwarding to"
    },
    {
        "email": "user3@example.com", 
        "name": "Mary Johnson",
        "autoForwarding": {"enabled": True, "emailAddress": "mary.personal@example.com", "disposition": "archive"},
        "forwardingFilters": [{"emailAddress": "work@example.com", "createdAt": "2024-03-01"}],
        "error": None,
        "investigation_note": "Approved by manager on 2024-03-05"
    },
    {
        "email": "user4@example.com",
        "name": "Bob Wilson",
        "autoForwarding": {"enabled": True, "emailAddress": "bob.backup@example.com", "disposition": "trash"},
        "forwardingFilters": [],
        "error": None,
        "investigation_note": "Needs further investigation - external domain"
    },
    {
        "email": "user2@example.com",
        "name": "Jane Smith",
        "autoForwarding": {"enabled": False},
        "forwardingFilters": [],
        "error": "Permission denied",
        "investigation_note": "Error occurred during audit"
    }
]

def store_autoforwarding_data(rule_repo, filter_repo, user_data, repo_type="sqlmodel"):
    """
    Import data into repositories
    
    Args:
        rule_repo: Repository for auto-forwarding rules
        filter_repo: Repository for forwarding filters
        user_data: List of user data dictionaries
        repo_type: Type of repository being used
    """
    for user in user_data:
        email = user["email"]
        name = user["name"]
        forwarding_email = user["autoForwarding"].get("emailAddress", None) if user["autoForwarding"].get("enabled") else None
        disposition = user["autoForwarding"].get("disposition", None)
        has_filters = bool(user["forwardingFilters"])  # True if filters exist
        error = user.get("error", None)
        investigation_note = user.get("investigation_note", None)
        
        # TEMPORARY CODE - ADD REPOSITORY TYPE TO INVESTIGATION NOTE
        # This can be removed once repository verification is complete
        if investigation_note:
            investigation_note = f"{investigation_note} [Repository: {repo_type}]"
        else:
            investigation_note = f"[Repository: {repo_type}]"
        # END TEMPORARY CODE

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
        
        # Check if rule already exists
        existing_rules = rule_repo.search_rules(email=email)
        existing_rule = next(iter(existing_rules), None)
        
        if existing_rule:
            # Update existing rule
            rule_id = existing_rule.id
            rule_repo.update_rule(rule_id, rule_data)
        else:
            # Create new rule
            rule = AutoForwardingBase(**rule_data)
            created_rule = rule_repo.create_rule(rule)
            rule_id = created_rule.id
            
        # Delete existing filters
        filter_repo.delete_filters_for_rule(rule_id)
        
        # Create filters if they exist
        if user["forwardingFilters"]:
            for filter_item in user["forwardingFilters"]:
                email_address = filter_item["emailAddress"]
                created_at = filter_item.get("createdAt", None)
                
                filter_data = {
                    "forwarding_id": rule_id,
                    "email_address": email_address,
                    "created_at": created_at
                }
                
                filter = ForwardingFilterBase(**filter_data)
                filter_repo.create_filter(filter)

def print_repository_results(repo_type, rule_repo, filter_repo):
    """
    Print results from repositories
    
    Args:
        repo_type: Repository type (sqlmodel, csv, memory)
        rule_repo: Repository for auto-forwarding rules
        filter_repo: Repository for forwarding filters
    """
    print(f"\n{'=' * 20} Repository Type: {repo_type} {'=' * 20}")
    print("\nAuto-Forwarding Rules:")
    rules = rule_repo.get_all_rules()
    for rule in rules:
        print(f"ID: {rule.id}, Email: {rule.email}, Name: {rule.name}")
        
        # Print filters for this rule
        filters = filter_repo.get_filters_for_rule(rule.id)
        if filters:
            print("  Filters:")
            for f in filters:
                print(f"    ID: {f.id}, Email Address: {f.email_address}, Created At: {f.created_at}")
        else:
            print("  No filters")
        print()

    # Print statistics
    stats = rule_repo.get_statistics()
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    print(f"{'=' * 60}")

def import_data(repo_type="sqlmodel"):
    """
    Import data into the specified repository type
    
    Args:
        repo_type: Repository type (sqlmodel, csv, memory)
    """
    # Create repositories
    rule_repo, filter_repo = create_repositories(repo_type)
    
    # Store data in repository
    store_autoforwarding_data(rule_repo, filter_repo, SAMPLE_DATA, repo_type)
    
    # Print results
    print_repository_results(repo_type, rule_repo, filter_repo)

def main():
    """Main entry point"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Import sample data into repositories")
    parser.add_argument("--repo", choices=["sqlmodel", "csv", "memory", "all"], 
                        default=os.environ.get("REPO_TYPE", "sqlmodel"),
                        help="Repository type to use (default: sqlmodel)")
    args = parser.parse_args()
    
    if args.repo == "all":
        # Import data into all repository types
        import_data("sqlmodel")
        import_data("csv")
        import_data("memory")
    else:
        # Import data into the specified repository type
        import_data(args.repo)

if __name__ == "__main__":
    main()
