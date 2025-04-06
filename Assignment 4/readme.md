# Assignment 4: Django Ninja Implementation of Email Forwarding Rules Audit

## Overview

This application has been rewritten to use Django and Django Ninja, replacing the original FastAPI implementation. The application continues to provide a robust API for auditing email forwarding rules with multiple storage options through the repository pattern.

## Why Django with Django Ninja?

This implementation migrates the FastAPI application to Django with Django Ninja for several key advantages:

1. **Django Ninja**: Provides FastAPI-like experience with type hints, automatic validation and API documentation
2. **ORM Advantage**: Django's ORM is more mature and feature-rich than SQLModel
3. **Admin Interface**: Built-in admin interface for managing data
4. **Django's Security**: Built-in protection against CSRF, XSS, SQL injection, etc.
5. **Deployment Flexibility**: More deployment options and better scaling capabilities

While maintaining the same API contract and repository pattern implementation as the original.

## Core Functionality

The main focus of this application is providing an API that allows administrators to:

1. Access forwarding rule data from different data sources
2. Review forwarding rules and add investigation notes, for example:
   - **Not malicious** - When forwarding serves a necessary business purpose
   - **Under investigation** - During the period when administrators are investigating the rule
   - **Delete entries** - When a user has confirmed the forwarding rule has been removed

## Repository Pattern Implementation

### Overview

This API implements the Repository Pattern, a design pattern that abstracts the data access layer from the rest of the application. This provides several benefits:

1. **Separation of concerns**: The business logic is separated from data access logic
2. **Testability**: Makes it easier to unit test the application by mocking repositories
3. **Flexibility**: Allows switching between different data storage mechanisms without changing the business logic

### Repository Types

The application supports three different repository implementations:

1. **Django Repository**: Uses Django's ORM to interact with the database (replacing SQLModel)
2. **CSV Repository**: Stores data in CSV files
3. **In-Memory Repository**: Keeps data in memory, useful for testing

### Repository Structure

The repository implementation consists of:

- **Base Interfaces**: Abstract base classes defining the operations repositories must implement
- **Django Repository**: Interacts with a SQLite database using Django's ORM
- **CSV Repository**: Reads and writes data to CSV files
- **In-Memory Repository**: Stores data in memory

## How to Use Different Repositories

You can choose the repository type by setting the `REPO_TYPE` environment variable:

```powershell
# Use Django repository (default)
python manage.py runserver

# Use CSV repository
$env:REPO_TYPE="csv"
python manage.py runserver

# Use in-memory repository (automatically loads sample data)
$env:REPO_TYPE="memory"
python manage.py runserver
```

## Important Notes

- **Django repository**: Default repository that uses Django's ORM
- **CSV repository**: Provides persistence without database requirements but with more limited querying capabilities
- **In-memory repository**: 
  - Automatically loads sample data when the API starts
  - All data will be lost when the application is restarted
  - Primarily useful for testing and demonstrations
  - The repository type is reflected in each rule's investigation note for verification

## Sample Data Import

The `sample_data_import.py` script allows you to populate any of the repository types with sample data:

```powershell
# Using default Django repository
python sample_data_import.py

# Import to a specific repository type
python sample_data_import.py --repo=django    # Django repository
python sample_data_import.py --repo=csv       # CSV repository  

# Import to all repository types at once
python sample_data_import.py --repo=all
```

This makes it easy to test and compare the different repository implementations.

## Data Model

The data model consists of two main entities:

**AutoForwarding**: Stores information about email forwarding rules for users
- Properties include: id, email, name, forwarding_email, disposition, has_forwarding_filters, error, investigation_note

**ForwardingFilters**: Stores filter details for email forwarding rules 
- Properties include: id, forwarding, email_address, created_at
- Relationship: Many filters can belong to one forwarding rule (one-to-many)

## API Endpoints

- GET /api/rules/ - Get all forwarding rules
- GET /api/rules/{rule_id} - Get a specific rule
- PUT /api/rules/{rule_id}/investigation - Update investigation notes
- DELETE /api/rules/{rule_id} - Delete a rule
- GET /api/rules/search/ - Search rules with filters
- GET /api/stats/ - Get statistics about forwarding rules
- GET /api/rules/{rule_id}/filters - Get filters for a specific rule

## Additional Django Admin Features

This implementation includes a Django admin interface for managing forwarding rules:

- Access the admin at `/admin/` (requires creating a superuser)
- Create, read, update, and delete forwarding rules and filters
- Filter and search capabilities
- Manage related data

## Prerequisites

1. Python 3.10 or higher
2. Django 4.2+ and Django Ninja 1.0+

## Installation Steps

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Apply database migrations:
   ```
   python manage.py migrate
   ```

3. Create a superuser for the admin interface (optional):
   ```
   python manage.py createsuperuser
   ```

4. Populate the sample data:
   ```
   python sample_data_import.py
   ```

5. Run the application:
   ```
   python manage.py runserver
   ```

## Project Structure

- **forwarding_audit/**: Django project settings package
  - **settings.py**: Django settings including repository configuration
  - **urls.py**: Main URL configuration
  
- **forwarding_rules/**: Django app containing the application logic
  - **models.py**: Django models for database tables
  - **admin.py**: Admin interface configuration
  - **api.py**: Django Ninja API endpoints
  - **schemas.py**: Pydantic schemas for request/response validation
  - **repository.py**: Repository pattern implementation
  - **urls.py**: URL configuration for the app
  
- **manage.py**: Django management script
- **requirements.txt**: Project dependencies
- **sample_data_import.py**: Script to populate repositories with sample data

## API Documentation

Once the application is running, you can access:
- Interactive API documentation: http://127.0.0.1:8000/api/docs
- Django Admin interface: http://127.0.0.1:8000/admin/

## Sample PowerShell Commands for API Operations

Below are PowerShell commands to interact with each endpoint:

### Get All Forwarding Rules
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/" -Method Get
```

### Get a Specific Rule by ID
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/1" -Method Get
```

### Update Investigation Note for a Rule
```powershell
$updateData = @{
    investigation_note = "Suspicious forwarding to external domain - needs further review"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/rules/1/investigation" -Method Put -Body $updateData -ContentType "application/json"
```

### Delete a Rule
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/4" -Method Delete
```

### Search for Rules by Email
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/search/?email=example.com" -Method Get
```

### Search for Rules with Filters
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/search/?has_filters=true" -Method Get
```

### Get Statistics About Forwarding Rules
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats/" -Method Get
```

### Get Filters for a Specific Rule
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/1/filters" -Method Get
```

### Tips for Better Output
For better readability, format the JSON output:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/1" -Method Get | ConvertTo-Json -Depth 5
```

## Key Differences from FastAPI Version

1. **Routing**: Django's URL routing system vs. FastAPI's router
2. **ORM**: Django ORM vs. SQLModel
3. **Request Handling**: Django request/response cycle vs. FastAPI's dependency injection
4. **Authentication**: Django's auth system vs. FastAPI's security utilities
5. **Admin Interface**: Django's admin vs. no built-in admin in FastAPI
6. **Migration System**: Django's migration system vs. SQLModel's alembic-based system

## Benefits of This Implementation

1. **Complete Ecosystem**: Django provides a complete web framework ecosystem
2. **Mature ORM**: Django's ORM is more mature and feature-rich
3. **Admin Interface**: Built-in admin interface for data management
4. **Community Support**: Larger community and more resources
5. **Deployment Options**: More deployment options and better scaling
6. **Security Features**: More built-in security features

While maintaining the API-first approach and strong typing of the original FastAPI implementation through Django Ninja.

## Files Added, Changed, and Removed

### Added Files

#### Django Project Structure
- **manage.py**: Django's command-line utility for administrative tasks like running the server, creating migrations, etc.
- **forwarding_audit/** directory: Core Django project package
  - **settings.py**: Project settings including database configuration, installed apps, and middleware
  - **urls.py**: Main URL configuration that routes to the application URLs
  - **wsgi.py**: WSGI application configuration for deployment
  - **__init__.py**: Package marker

#### Django Application
- **forwarding_rules/** directory: Django application package
  - **models.py**: Django ORM models (replacing SQLModel models)
  - **admin.py**: Configuration for Django's admin interface
  - **api.py**: Django Ninja API endpoints implementation
  - **schemas.py**: Pydantic schemas for request/response validation
  - **urls.py**: URL routing specific to the API endpoints
  - **apps.py**: Django app configuration
  - **__init__.py**: Package marker
  
#### Other Files
- **.gitignore**: Git ignore file for Django-specific and Python files

### Changed Files

- **sample_data_import.py**: Updated to work with Django's ORM models and repository structure
- **requirements.txt**: Changed dependencies from FastAPI to Django and Django Ninja
- **models.py** (root): Simplified to serve as compatibility layer, importing from new location

### Removed Files

- **main.py**: The FastAPI application entry point, replaced by Django's structure
- **Original models**: FastAPI/SQLModel-based models replaced by Django ORM models
- **FastAPI router files**: Removed in favor of Django Ninja API endpoints

### Migration Details

This migration represents a full rewrite of the application from FastAPI to Django with Django Ninja, while maintaining:
- The same API contract and endpoints
- The repository pattern implementation
- Similar data models and validation
- The ability to use different storage mechanisms (Django ORM, CSV, in-memory)

The Django implementation adds the powerful Django admin interface and leverages Django's mature ecosystem while keeping the API-first approach through Django Ninja.