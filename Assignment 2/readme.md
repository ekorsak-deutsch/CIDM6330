# Assignment 2 Overview

## Purpose
For Assignment 2, I am developing an API that allows administrators to review email forwarding settings from cloud email servers like Gmail or Exchange Online for auditing and cybersecurity purposes. 

Why is this important? When a cybercriminal compromises an email account, they often aim to impersonate the account owner while maintaining covert control over the account. For instance, if an attacker gains access to an accountant's email account, they might send emails to business partners, instructing them to transfer payments to the attacker's bank account instead of the legitimate one. During this process, the attacker would want to prevent the accountant from discovering the breach by hiding the attacker's emails and the partners' responses. To achieve this, the attacker could set up email forwarding rules, ensuring that interactions between the attacker and the victims are not visible to the account owner but are instead forwarded to an external mailbox controlled by the attacker. While some organizations completely block email forwarding rules to prevent such compromises, this is not always feasible. Therefore, a system to review email forwarding rules is a valuable component of a Cloud ADR system.

## Implementation
This API uses sample data about email forwarding rules, imported into a SQLite database via the `sample_data_import.py` script.

## Core Functionality
The main focus of this assignment is developing an API that allows administrators to:

1. Access forwarding rule data from the database
2. Review forwarding rules and add investigation notes, for example:
   - **Not malicious** - When forwarding serves a necessary business purpose
   - **Under investigation** - During the period when administrators are investigating the rule
   - **Delete entries** - When a user has confirmed the forwarding rule has been removed

# Email Forwarding Rules Audit API

This application provides a REST API for auditing email forwarding rules.

## Prerequisites
1. Python 3.13
2. Rust (required for Pydantic 2.x)
   - Download and install from https://rustup.rs/

## Installation Steps
1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
2. Populate the sample data by running the sample_data_import.py


3. Run the application:
   ```
   python -m uvicorn main:app --reload
   ```

## Entity Relationship Diagram (ERD)
**Entity Relationship Diagram**
![ERD](https://github.com/ekorsak-deutsch/CIDM6330/blob/f91eb8b4f61a908084c714aa763b0c03a464bfdb/Assignment%202/EmailForwardingRuleReviewERD.png)



Entity: AutoForwarding
Description: Stores information about email forwarding rules for users

Attributes:
- id: Integer, Primary Key, Auto-increment
  Description: Unique identifier for each forwarding rule

- email: Text, Unique, Not Null
  Description: Email address of the user who owns the forwarding rule
  
- name: Text
  Description: Name of the user

- forwarding_email: Text
  Description: Destination email address where messages are forwarded
  Note: Null if forwarding is disabled

- disposition: Text
  Description: What happens to the original email after forwarding
  Values: "keep", "archive", "trash"
  Note: Null if forwarding is disabled

- has_forwarding_filters: Boolean
  Description: Indicates whether the forwarding rule has filters
  Values: true (has filters), false (no filters)

- error: Text
  Description: Error message if there was a problem with the forwarding rule
  Note: Null if no errors

- investigation_note: Text
  Description: Notes from the investigation/audit of this forwarding rule
  Note: Used for tracking the review process

Entity: ForwardingFilters
Description: Stores filter details for email forwarding rules

Attributes:
- id: Integer, Primary Key, Auto-increment
  Description: Unique identifier for each filter

- forwarding_id: Integer, Foreign Key, Not Null
  Description: References the AutoForwarding rule this filter belongs to
  
- email_address: Text, Not Null
  Description: Email address that the filter applies to
  
- created_at: Text
  Description: Date when the filter was created
  Format: YYYY-MM-DD

Relationships:
- AutoForwarding (1) to ForwardingFilters (0..n): One forwarding rule can have multiple filters
  Relationship Type: One-to-Many
  Foreign Key: ForwardingFilters.forwarding_id references AutoForwarding.id


## Project Files

- **main.py**: Contains the FastAPI application and all API endpoint definitions. Handles HTTP requests, database interactions, and response formatting.

- **models.py**: Defines Pydantic models for data validation and SQLite database models. Includes functions for database initialization and connection management.

- **requirements.txt**: Lists all Python package dependencies required to run the application, including FastAPI, Uvicorn, Pydantic, and other supporting libraries.

- **sample_data_import.py**: Utility script that populates the SQLite database with sample email forwarding rules for testing and demonstration purposes.

- **email_forwarding.db**: SQLite database file that stores all email forwarding rules and their associated metadata. Created automatically when the sample_data_import.py runs.

- **Assignment2_readme.md**: This documentation file providing an overview of the project, installation instructions, and usage guidelines.

## API Documentation
Once the application is running, you can access:
- Interactive API documentation: http://127.0.0.1:8000/docs
- Alternative API documentation: http://127.0.0.1:8000/redoc

## Available Endpoints
- GET /rules/ - Get all forwarding rules
- GET /rules/{rule_id} - Get a specific rule
- PUT /rules/{rule_id}/investigation - Update investigation notes
- DELETE /rules/{rule_id} - Delete a rule
- GET /rules/search/ - Search rules with filters
- GET /stats/ - Get statistics about forwarding rules
- GET /rules/{rule_id}/filters - Get filters for a specific rule

## Sample PowerShell Commands for CRUD API Operations

Below are PowerShell commands to interact with each endpoint in the Email Forwarding Rules Audit API.

### Get All Forwarding Rules
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rules/" -Method Get
```

### Get a Specific Rule by ID
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rules/1" -Method Get
```

### Update Investigation Note for a Rule
```powershell
$updateData = @{
    investigation_note = "Suspicious forwarding to external domain - needs further review"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/rules/1/investigation" -Method Put -Body $updateData -ContentType "application/json"
```

### Delete a Rule
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rules/4" -Method Delete
```

### Search for Rules by Email
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rules/search/?email=example.com" -Method Get
```

### Search for Rules with Filters
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rules/search/?has_filters=true" -Method Get
```

### Get Statistics About Forwarding Rules
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/stats/" -Method Get
```

### Get Filters for a Specific Rule
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rules/1/filters" -Method Get
```

## Project Structure
- main.py: FastAPI application and endpoints
- models.py: Database models and Pydantic schemas
- requirements.txt: Project dependencies
- email_forwarding.db: SQLite database (created automatically)