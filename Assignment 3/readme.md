# Assignment 3 Overview

## Purpose
This API allows administrators to review email forwarding settings from cloud email servers like Gmail or Exchange Online for auditing and cybersecurity purposes. 

Why is this important? When a cybercriminal compromises an email account, they often aim to impersonate the account owner while maintaining covert control over the account. For instance, if an attacker gains access to an accountant's email account, they might send emails to business partners, instructing them to transfer payments to the attacker's bank account instead of the legitimate one. During this process, the attacker would want to prevent the accountant from discovering the breach by hiding the attacker's emails and the partners' responses. To achieve this, the attacker could set up email forwarding rules, ensuring that interactions between the attacker and the victims are not visible to the account owner but are instead forwarded to an external mailbox controlled by the attacker. While some organizations completely block email forwarding rules to prevent such compromises, this is not always feasible. Therefore, a system to review email forwarding rules is a valuable component of a Cloud ADR system.

## Core Functionality
The main focus of this application is providing an API that allows administrators to:

1. Access forwarding rule data from different data sources
2. Review forwarding rules and add investigation notes, for example:
   - **Not malicious** - When forwarding serves a necessary business purpose
   - **Under investigation** - During the period when administrators are investigating the rule
   - **Delete entries** - When a user has confirmed the forwarding rule has been removed

# Repository Pattern Implementation

## Overview

This API implements the Repository Pattern, a design pattern that abstracts the data access layer from the rest of the application. This provides several benefits:

1. **Separation of concerns**: The business logic is separated from data access logic
2. **Testability**: Makes it easier to unit test the application by mocking repositories
3. **Flexibility**: Allows switching between different data storage mechanisms without changing the business logic

## Repository Types

The application supports three different repository implementations:

1. **SQLModel Repository**: Uses SQLModel (an ORM built on SQLAlchemy and Pydantic) to interact with a SQLite database
2. **CSV Repository**: Stores data in CSV files
3. **In-Memory Repository**: Keeps data in memory, useful for testing

## Repository Structure

The repository implementation consists of:

- **Base Interfaces**: Abstract base classes defining the operations repositories must implement
- **SQLModel Repository**: Interacts with a SQLite database using SQLModel
- **CSV Repository**: Reads and writes data to CSV files
- **In-Memory Repository**: Stores data in memory

## How to Use Different Repositories

You can choose the repository type by setting the `REPO_TYPE` environment variable:

```powershell
# Use SQLModel repository (default)
python -m uvicorn main:app --reload

# Use CSV repository
$env:REPO_TYPE="csv"
python -m uvicorn main:app --reload

# Use in-memory repository (automatically loads sample data)
$env:REPO_TYPE="memory"
python -m uvicorn main:app --reload
```

## Important Notes

- **SQLModel repository**: Requires Python 3.11 or 3.12 for full compatibility. With Python 3.13, the application will automatically fall back to a memory repository if SQLModel is not available.
- **CSV repository**: Provides persistence without database requirements but with more limited querying capabilities.
- **In-memory repository**: 
  - Automatically loads sample data when the API starts
  - All data will be lost when the application is restarted
  - Primarily useful for testing and demonstrations
  - The repository type is reflected in each rule's investigation note for verification

## Sample Data Import

The `sample_data_import.py` script allows you to populate any of the repository types with sample data:

```powershell
# Using default SQLModel repository
python sample_data_import.py

# Import to a specific repository type
python sample_data_import.py --repo=sqlmodel    # SQLModel repository
python sample_data_import.py --repo=csv         # CSV repository  

# Import to all repository types at once
python sample_data_import.py --repo=all
```

This makes it easy to test and compare the different repository implementations.

# Email Forwarding Rules Audit API

This application provides a REST API for auditing email forwarding rules with flexible data storage options.

## Data Model

The data model consists of two main entities:

**AutoForwarding**: Stores information about email forwarding rules for users
- Properties include: id, email, name, forwarding_email, disposition, has_forwarding_filters, error, investigation_note

**ForwardingFilters**: Stores filter details for email forwarding rules 
- Properties include: id, forwarding_id, email_address, created_at
- Relationship: Many filters can belong to one forwarding rule (one-to-many)

## API Integration

The API endpoints use repositories to:

1. Retrieve data for HTTP GET requests
2. Persist data for HTTP POST, PUT, and DELETE requests
3. Query data for search operations
4. Gather statistics

This implementation provides a clean separation between API controllers and data access logic.

## Available Endpoints
- GET /rules/ - Get all forwarding rules
- GET /rules/{rule_id} - Get a specific rule
- PUT /rules/{rule_id}/investigation - Update investigation notes
- DELETE /rules/{rule_id} - Delete a rule
- GET /rules/search/ - Search rules with filters
- GET /stats/ - Get statistics about forwarding rules
- GET /rules/{rule_id}/filters - Get filters for a specific rule

## Prerequisites
1. Python 3.13
2. Rust (required for Pydantic 2.x)
   - Download and install from https://rustup.rs/

## Installation Steps
1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
2. Populate the sample data by running the sample_data_import.py script:
   ```
   # Using default SQLModel repository
   python sample_data_import.py
   
   # Using a specific repository type
   python sample_data_import.py --repo=sqlmodel    # SQLModel repository
   python sample_data_import.py --repo=csv         # CSV repository
   
   # Import into all repository types at once
   python sample_data_import.py --repo=all
   ```

3. Run the application:
   ```
   python -m uvicorn main:app --reload
   ```

## Project Files

- **main.py**: Contains the FastAPI application and API endpoint definitions that use the repository pattern.

- **models.py**: Defines Pydantic models for API data validation and serialization.

- **repository.py**: Implements the repository pattern with support for multiple data store types:
  - SQLModel for SQLite database
  - CSV file storage
  - In-memory storage

- **requirements.txt**: Lists all Python package dependencies required to run the application.

- **sample_data_import.py**: Utility script that populates the chosen data store with sample email forwarding rules.
  Features command-line options to use different repository types:
  ```
  python sample_data_import.py --repo=[sqlmodel|csv|memory|all]
  ```

## API Documentation
Once the application is running, you can access:
- Interactive API documentation: http://127.0.0.1:8000/docs
- Alternative API documentation: http://127.0.0.1:8000/redoc

## Sample PowerShell Commands for API Operations

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

### Tips for Better Output
For better readability, format the JSON output:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rules/1" -Method Get | ConvertTo-Json -Depth 5
```

### Working with Results
Save results to a variable for further processing:
```powershell
$rules = Invoke-RestMethod -Uri "http://localhost:8000/rules/" -Method Get
$rules | ForEach-Object { Write-Host "Rule ID: $($_.id), Email: $($_.email)" }
```