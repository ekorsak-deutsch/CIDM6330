# Assignment 4: Django Ninja Implementation of Email Forwarding Rules Audit

## Overview

This application has been rewritten to use Django and Django Ninja, replacing the original FastAPI implementation. The application provides a robust API for auditing email forwarding rules with a Django ORM repository implementation.

## Core Functionality

The main focus of this application is providing an API that allows administrators to:

1. Access forwarding rule data from the database
2. Review forwarding rules and add investigation notes, for example:
   - **Not malicious** - When forwarding serves a necessary business purpose
   - **Under investigation** - During the period when administrators are investigating the rule
   - **Delete entries** - When a user has confirmed the forwarding rule has been removed

### Django Repository

The application uses Django's ORM to interact with the database, with repositories acting as an abstraction layer between the API and the database models.

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
  - **settings.py**: Django settings 
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
- **sample_data_import.py**: Script to populate the database with sample data

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

The Django implementation adds the powerful Django admin interface and leverages Django's mature ecosystem while keeping the API-first approach through Django Ninja.