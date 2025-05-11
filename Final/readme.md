# Email Forwarding Rules Audit System

## Application Overview

The Email Forwarding Rules Audit System is a security-focused application designed to help organizations detect, monitor, and investigate potentially risky email forwarding rules. In many organizations, employees can configure automatic forwarding of emails to external addresses, which creates security risks if not properly monitored.

### Problems This Application Solves:

1. **Data Exfiltration Detection**: Identifies email forwarding rules that could be used to exfiltrate sensitive company information to external email addresses.

2. **Security Audit Compliance**: Provides comprehensive documentation and reporting to demonstrate email security compliance during audits.

3. **Suspicious Activity Investigation**: Allows security teams to investigate potentially malicious forwarding rules by adding investigation notes and tracking dispositions.

4. **Risk Assessment**: Offers statistical analysis to understand the scope of email forwarding within an organization and identify patterns.

5. **Asynchronous Reporting**: Generates detailed PDF reports without blocking the application, enabling efficient use by security teams.

6. **Centralized Monitoring**: Creates a single view of all email forwarding rules across the organization, including complex forwarding filters.

This application serves as a critical security tool for IT administrators, security analysts, and compliance teams who need to ensure that confidential information isn't being inappropriately forwarded outside the organization.

## UML Diagrams

The application architecture is documented through several UML diagrams available in the `UML` folder:

### Class Diagram
This diagram shows the class structure of the application, including models, repositories, and their relationships.

![UML Class Diagram](UML/UML%20Class%20Diagram.jpeg)

### Component Diagram
This diagram illustrates the high-level components of the system and their dependencies.

![UML Component Diagram](UML/UML%20Component%20Diagram.jpeg)

### Sequence Diagram
This diagram shows the interactions between objects during the report generation process.

![UML Report Generation Sequence Diagram](UML/UML%20Report%20Generation%20Sequence%20Diagram.jpeg)

### State Machine Diagram
This diagram illustrates the different states a forwarding rule can go through during investigation.

![UML State Diagram - Rule investigation](UML/UML%20State%20Diagram%20-%20Rule%20investigation.jpeg)

### Use Case Diagram
This diagram depicts the interactions between users and the system.

![Use Case Diagram](UML/Use%20Case%20Diagram.jpeg)

### Activity Diagram
This diagram shows the workflow of the report generation process.

![Activity diagram - Report Generation](UML/Activity%20diagram%20-%20Report%20Generation.jpeg)

## Overview

This application has been enhanced with Celery and Redis to provide asynchronous task processing capabilities for generating PDF reports. It builds upon the Django and Django Ninja implementation from Assignment 4, adding the ability to generate comprehensive PDF reports of email forwarding rules. 

## Key Enhancements
1. **Asynchronous Processing**: Added Celery for background task processing
2. **Message Broker**: Integrated Redis as a message broker for Celery
3. **PDF Generation**: Added ReportLab for creating detailed PDF reports
4. **Report API Endpoints**: Added multiple report generation endpoints for asynchronous report creation
5. **Unit Tests**: Added comprehensive unit tests in the `tests.py` file
6. **BDD and DDD**: Added a glossary for Domain-Driven Design in the `domain_glossary.md` file and Gherkin notation for tests in the `tests_description.md` file
7. **Containerization**: Complete Docker setup for reliable and consistent deployment

### Asynchronous Processing with Celery

The application uses Celery to handle time-consuming tasks asynchronously, such as:
- Generating PDF reports of all forwarding rules
- Background processing that doesn't block API responses
- Task scheduling and monitoring

### Redis as Message Broker

Redis serves as the message broker for Celery, providing:
- Reliable message passing between Django application and Celery workers
- Task queue management
- Result storage and retrieval

### Containerization

To avoid compatibility issues, the application is fully containerized with Docker. This includes:
- Django (web container)
- Redis (redis container)
- Celery (celery container)

A `docker-compose.yml` file is provided for easy container orchestration.

## Domain-Driven Design

This project follows Domain-Driven Design (DDD) principles to ensure a shared understanding between technical and business stakeholders. A comprehensive domain glossary has been created to establish a ubiquitous language.

### Domain Glossary

The `domain_glossary.md` file contains the official terminology used throughout the application. This glossary:

- Defines all key domain concepts precisely
- Establishes relationships between concepts
- Provides examples to aid understanding
- Serves as the single source of truth for domain language

Refer to this glossary when discussing features, writing documentation, or implementing code to ensure consistent use of domain terminology across the entire project.

## Core Functionality

The main focus of this application is providing an API that allows administrators to:

1. Access forwarding rule data from the database
2. Review forwarding rules and add investigation notes, for example:
   - **Not malicious** - When forwarding serves a necessary business purpose
   - **Under investigation** - During the period when administrators are investigating the rule
   - **Delete entries** - When a user has confirmed the forwarding rule has been removed
3. **Generate comprehensive PDF reports** of all forwarding rules for documentation and compliance purposes

### Django Repository

The application uses Django's ORM to interact with the database, with repositories acting as an abstraction layer between the API and the database models.

### Filter Implementation Notes
- Each AutoForwarding rule can have exactly one ForwardingFilter (one-to-one relationship)
- Different forwarding filter for the same user can be reflected in a different AutoForwarding rule
- The previous implementation that allowed multiple filter email addresses has been replaced with more flexible JSON-based criteria and action fields to realistically reflect Gmail forwarding filters

## Data Model

The data model consists of two main entities:

**AutoForwarding**: Stores information about email forwarding rules for users
- Properties include: id, email, name, forwarding_email, disposition, has_forwarding_filters, error, investigation_note

**ForwardingFilter**: Stores advanced filter configuration for an email forwarding rule
- Properties include: 
  - **id**: Filter identifier
  - **criteria**: JSON object with filter conditions (e.g., `{"from": "example@example.com", "subject": "invoice"}`)
  - **action**: JSON object with actions to take (e.g., `{"forward": "backup@example.com", "addLabels": "TRASH"}`)
  - **created_at**: When the filter was created
- Relationship: **One-to-one** with AutoForwarding rule - each rule can have at most one filter configuration

## Filter Configuration

### Criteria Examples
- `{"from": "newsletter@company.com"}` - Match emails from a specific sender
- `{"subject": "invoice"}` - Match emails with specific text in the subject
- `{"from": "partner@example.com", "subject": "urgent"}` - Match emails from a sender with specific subject
- `{"to": "team@company.com"}` - Match emails sent to a specific recipient
- `{"hasAttachment": true}` - Match emails with attachments
- `{"size": ">5M"}` - Match emails larger than 5MB

### Action Examples
- `{"forward": "archive@example.com"}` - Forward matching emails to an archive address
- `{"forward": "security@example.com", "addLabels": "SPAM"}` - Multiple actions for matching emails
- `{"forward": "manager@company.com", "addLabels": ["URGENT", "NEEDS_REVIEW"]}` - Forward and add multiple labels

## API Endpoints

### Core Endpoints
- GET /api/rules/ - Get all forwarding rules
- GET /api/rules/{rule_id} - Get a specific rule
- PUT /api/rules/{rule_id}/investigation - Update investigation notes
- DELETE /api/rules/{rule_id} - Delete a rule
- GET /api/rules/search/ - Search rules with filters
- GET /api/stats/ - Get statistics about forwarding rules
- GET /api/rules/{rule_id}/filter - Get the filter for a specific rule

### Report Generation Endpoints
- POST /api/reports/generate - Generate a comprehensive PDF report of all forwarding rules (async)
- POST /api/reports/stats - Generate a statistics-only PDF report (async)
- POST /api/reports/rules-only - Generate a rules-only PDF report without filter details (async)

### Filter-Specific Endpoints

The filter endpoints reflect the one-to-one relationship between rules and filters:

#### GET /api/rules/{rule_id}/filter
Returns the filter configuration for a specific rule, including both criteria and action JSON objects.

Example response:
```json
{
  "id": 1,
  "criteria": {
    "from": "newsletter@example.com",
    "subject": "Weekly Update"
  },
  "action": {
    "forward": "archive@company.com",
    "addLabels": ["NEWSLETTER", "AUTOMATED"]
  },
  "created_at": "2023-04-15T10:30:00Z"
}
```

## PDF Report Generation

The API provides PDF report generation capabilities through asynchronous Celery tasks:

### Report Types

1. **Complete Report** - `POST /api/reports/generate`
   - Comprehensive report with statistics and detailed information about all forwarding rules including their filter configurations
   - Useful for audits and compliance documentation
   - Contains rich data about each rule and its associated filter

2. **Statistics-Only Report** - `POST /api/reports/stats`
   - Concise report containing only statistical information about forwarding rules
   - Provides aggregate data such as total rules, rules with filters, etc.
   - Ideal for management overviews and trend analysis

3. **Rules-Only Report** - `POST /api/reports/rules-only`
   - Detailed listing of all forwarding rules without filter information
   - Offers a middle ground between the comprehensive and statistics-only reports
   - Useful when filter details aren't relevant to the audience

All report generation endpoints accept an optional `report_name` parameter to customize the filename.

Reports are generated asynchronously using Celery tasks and are saved to the `reports` directory.

### Sample Reports

For reference, sample reports of each type have been included in the `sample_reports` folder:

- **Complete Report**: Full audit report with all forwarding rules and their filter details
- **Statistics-Only Report**: Report focused solely on the statistics of forwarding rules
- **Rules-Only Report**: Report showing forwarding rules without filter configurations

These sample reports demonstrate the format and content of each report type, making it easier to understand the differences between them without having to generate them yourself. They were generated using the Celery tasks and can be used as examples for customizing or extending the reporting functionality.

## Testing

Unit tests have been implemented to verify the functionality of all API endpoints. The tests use Django's testing framework and unittest.mock to isolate the components being tested.

### Testing Documentation

The test documentation in `tests_description.md` includes:
- Detailed descriptions of each test
- **Gherkin notation** for BDD-style test scenarios
- Clear specification of expected behaviors and edge cases
- Information about the testing approach

Gherkin notation (Given-When-Then format) helps communicate the test scenarios in a human-readable way that bridges the gap between technical and non-technical stakeholders.

### Running Tests

To run the tests in your Docker environment:

```bash
docker-compose exec web python manage.py test forwarding_rules
```

### Test Coverage

The tests cover:
- All API endpoints (CRUD operations for rules and filters)
- Report generation endpoints with mocked Celery tasks
- Error cases and edge conditions
- Parameter validation

See `tests_description.md` for detailed information about each test.

## Additional Django Admin Features

This implementation includes a Django admin interface for managing forwarding rules:

- Access the admin at `/admin/` (requires creating a superuser)
- Create, read, update, and delete forwarding rules and filters
- Filter and search capabilities
- Manage related data

## Installation and Running the Application

This application uses Docker and Docker Compose to create a containerized environment with all the necessary components:
- Django web application
- Celery worker for asynchronous tasks
- Redis for message broker
- Reports volume for PDF storage

### Prerequisites

1. Docker and Docker Compose installed on your system
2. No need to install Python, Django, Redis, Celery, or ReportLab separately - all dependencies are managed through Docker containers
3. Basic familiarity with Docker commands
4. Sufficient disk space for Docker images and containers
5. Ports 8000 (web server) and 6379 (Redis) available on your host machine

### Setup Steps

1. Set up environment variables:
   ```
   cp .env.template .env
   ```
   
   Then generate a SECRET_KEY and add it to your .env file:
   ```
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
   ```

2. Start all services with Docker Compose:
   ```
   docker-compose up
   ```
   
   Or to run in the background:
   ```
   docker-compose up -d
   ```

3. Apply database migrations (first time only):
   ```
   docker-compose exec web python manage.py migrate
   ```

4. Create a superuser for the admin interface (optional):
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

5. Populate the sample data:
   ```
   docker-compose exec web python sample_data_import.py
   ```

### Managing Docker Services

- **View logs**:
  ```
  docker-compose logs -f celery
  ```

- **Restart a service**:
  ```
  docker-compose restart celery
  ```

- **Stop all services**:
  ```
  docker-compose down
  ```

- **Rebuild after changes**:
  ```
  docker-compose build
  docker-compose up
  ```

### Accessing Generated PDF Reports

When running in Docker, the PDF reports are generated inside the container's filesystem. To access these reports from your local machine, you have several options:

#### View Available Reports

To see a list of all generated reports:
```
docker-compose exec web ls -la /app/reports
```

#### Copy a Specific Report to Your Local Machine

To copy a specific report (replace the filename with your actual report name):
```
docker cp assignment5-web-1:/app/reports/forwarding_rules_report_20250413_150231.pdf ./
```

#### Copy All Reports to a Local Directory

To copy all reports to a local 'reports' directory:
```
# Create a local reports directory if it doesn't exist
mkdir -p reports

# Copy all reports from the container
docker cp assignment5-web-1:/app/reports/. ./reports/
```

#### Find the Container Name

If you're not sure about the container name (e.g., if it's not 'assignment5-web-1'), you can find it with:
```
docker-compose ps
```

Or with the docker command:
```
docker ps | grep web
```

## Security Setup

This application uses environment variables for configuration, particularly for sensitive information like the Django SECRET_KEY. The `.env` file containing these variables is excluded from version control for security reasons.

### Setting Up Environment Variables

1. Create a `.env` file in the project root (Assignment 5 directory) with the following variables:

```
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Django Configuration
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

2. Generate and add a secure SECRET_KEY to your `.env` file:

```
SECRET_KEY=your_generated_secret_key_here
```

### How to Generate a Secure SECRET_KEY

You can generate a secure SECRET_KEY using Python:

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
```

Copy the output and add it to your `.env` file.

IMPORTANT: Never commit your actual SECRET_KEY to version control. The `.env` file is included in `.gitignore` to prevent this, but be careful when sharing your code.

## Project Structure

- **forwarding_audit/**: Django project settings package
  - **settings.py**: Django settings 
  - **urls.py**: Main URL configuration
  - **celery.py**: Celery configuration
  
- **forwarding_rules/**: Django app containing the application logic
  - **models.py**: Django models for database tables
  - **admin.py**: Admin interface configuration
  - **api.py**: Django Ninja API endpoints
  - **schemas.py**: Pydantic schemas for request/response validation
  - **repository.py**: Repository pattern implementation
  - **urls.py**: URL configuration for the app
  - **tasks.py**: Celery tasks for asynchronous processing
  - **migrations/**: Database migration files
  - **tests.py**: Unit tests for the API endpoints
  
- **manage.py**: Django management script
- **requirements.txt**: Project dependencies
- **sample_data_import.py**: Script to populate the database with sample data
- **reports/**: Directory for storing generated PDF reports
- **sample_reports/**: Examples of generated reports for reference
- **tests_description.md**: Detailed descriptions of the unit tests
- **domain_glossary.md**: Ubiquitous language definitions for domain-driven design
- **UML/**: Directory containing UML diagrams for the application architecture

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

### Get Filter for a Specific Rule
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/1/filter" -Method Get
```

### Generate a PDF Report
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/reports/generate" -Method Post
```

### Generate a PDF Report with Custom Name
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/reports/generate?report_name=quarterly_audit_report.pdf" -Method Post
```

### Generate a Statistics-Only PDF Report
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/reports/stats" -Method Post
```

### Generate a Rules-Only PDF Report
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/reports/rules-only" -Method Post
```

### Tips for Better Output
For better readability, format the JSON output:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/1" -Method Get | ConvertTo-Json -Depth 5
```

## Running in Production

For a production deployment, consider the following:

1. Use a process manager like Supervisor to manage Celery workers
2. Configure Redis with password protection and proper security
3. Set up monitoring for Celery tasks
4. Configure Nginx or Apache as a reverse proxy for Django
5. Set up periodic tasks for automatic report generation

## Troubleshooting

### Docker Issues
- If Docker containers won't start, ensure Docker Desktop (Windows/Mac) or Docker Engine (Linux) is running
- For permission issues: on Linux, you might need to run commands with sudo or add your user to the docker group

### Redis Connection Issues
If you encounter Redis connection issues:
- Check if the Redis container is running: `docker ps` should show the redis container
- Check Redis container logs: `docker logs assignment5-redis-1`
- Ensure the REDIS_HOST in your .env file is set to 'redis'

### Celery Worker Issues
If Celery workers are not processing tasks:
- Check Celery container logs: `docker-compose logs celery`
- Verify Redis container is healthy: `docker-compose ps`
- Try restarting the Celery service: `docker-compose restart celery`

### Environment Variables Issues
- If you get a "SECRET_KEY not set" error, ensure you've:
  1. Created a proper .env file (you can use .env.template as a starting point)
  2. Generated and added a SECRET_KEY to your .env file
  3. Confirmed that python-dotenv is installed