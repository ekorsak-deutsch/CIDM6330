# Assignment 5: Django Ninja with Celery/Redis for Email Forwarding Rules Audit

## Overview

This application has been enhanced with Celery and Redis to provide asynchronous task processing capabilities. It builds upon the Django and Django Ninja implementation from Assignment 4, adding the ability to generate comprehensive PDF reports of email forwarding rules.

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
- Each AutoForwarding rule can have exactly one ForwardingFilter (one-to-one relationship) - different forwarding filter for the same user can be reflected in a different AutoForwarding rule
- The previous implementation that allowed multiple filter email addresses has been replaced with the more flexible JSON-based criteria and action fields to more realistically reflect gmail forwarding filters

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

- GET /api/rules/ - Get all forwarding rules
- GET /api/rules/{rule_id} - Get a specific rule
- PUT /api/rules/{rule_id}/investigation - Update investigation notes
- DELETE /api/rules/{rule_id} - Delete a rule
- GET /api/rules/search/ - Search rules with filters
- GET /api/stats/ - Get statistics about forwarding rules
- GET /api/rules/{rule_id}/filter - Get the filter for a specific rule
- POST /api/reports/generate - Generate a PDF report of all forwarding rules (async)

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

### Report Generation Endpoint

#### POST /api/reports/generate
Initiates an asynchronous task to generate a PDF report of all forwarding rules in the database. The report includes detailed information about each rule and its filter configuration.

Request parameters:
- `report_name` (optional): Custom name for the generated report file

Example response:
```json
{
  "message": "Report generation started",
  "task_id": "8f1b3c2a-5d6e-4f7g-8h9i-0j1k2l3m4n5o",
  "status": "The report will be saved to the reports directory."
}
```

The generated PDF report includes:
- Title and generation timestamp
- Summary statistics
- Detailed listing of all forwarding rules
- Filter configuration details for rules with filters

## Additional Django Admin Features

This implementation includes a Django admin interface for managing forwarding rules:

- Access the admin at `/admin/` (requires creating a superuser)
- Create, read, update, and delete forwarding rules and filters
- Filter and search capabilities
- Manage related data

## Prerequisites

1. Python 3.10 or higher
2. Django 4.2+ and Django Ninja 1.0+
3. Redis server (for Celery message broker)
4. Celery 5.3+ (for asynchronous task processing)
5. ReportLab 4.0+ (for PDF generation)

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

## Installation Steps

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   cp .env.template .env
   ```
   
   Then generate a SECRET_KEY and add it to your .env file:
   ```
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
   ```

3. Start Redis using Docker:
   ```
   docker-compose up -d redis
   ```
   
   This will start a Redis container in the background using the configuration in docker-compose.yml.
   
   Alternatively, if you don't want to use Docker, you can install Redis directly:
   - **Windows**: Download and install from https://github.com/tporadowski/redis/releases
   - **Linux**: `sudo apt install redis-server`
   - **macOS**: `brew install redis`
   And then start it with: `redis-server`

4. Apply database migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser for the admin interface (optional):
   ```
   python manage.py createsuperuser
   ```

6. Populate the sample data:
   ```
   python sample_data_import.py
   ```

7. Start Celery worker in a separate terminal:
   ```
  python -m celery -A forwarding_audit worker --loglevel=info
   ```

8. Run the Django application:
   ```
   python manage.py runserver
   ```

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
  
- **manage.py**: Django management script
- **requirements.txt**: Project dependencies
- **sample_data_import.py**: Script to populate the database with sample data
- **reports/**: Directory for storing generated PDF reports

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
$reportParams = @{
    report_name = "quarterly_audit_report.pdf"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/reports/generate" -Method Post -Body $reportParams -ContentType "application/json"
```

### Tips for Better Output
For better readability, format the JSON output:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/rules/1" -Method Get | ConvertTo-Json -Depth 5
```

## Key Differences from Previous Version
1. **Asynchronous Processing**: Added Celery for background task processing
2. **Message Broker**: Integrated Redis as a message broker for Celery
3. **PDF Generation**: Added ReportLab for creating detailed PDF reports
4. **New API Endpoint**: Added report generation endpoint for asynchronous report creation

## Running in Production

For a production deployment, consider the following:

1. Use a process manager like Supervisor to manage Celery workers
2. Configure Redis with password protection and proper security
3. Set up monitoring for Celery tasks
4. Configure Nginx or Apache as a reverse proxy for Django
5. Set up periodic tasks for automatic report generation

## Troubleshooting

### Redis Connection Issues
If you encounter Redis connection issues:

#### When using Docker:
- Check if the Redis container is running: `docker ps` should show the redis container
- Check Redis container logs: `docker logs assignment5-redis-1`
- Ensure the REDIS_HOST in your .env file is set to 'redis' when using Docker

#### When using a locally installed Redis:
- Verify Redis is running: `redis-cli ping` should return "PONG"
- Check Redis connection settings in .env file (REDIS_HOST should be 'localhost')
- Ensure Redis port (default 6379) is not blocked by a firewall

### Celery Worker Issues
If Celery workers are not processing tasks:
- Ensure the Celery worker is running
- Check Celery logs for errors
- Verify Redis connection is working
- Try restarting the Celery worker

### Environment Variables Issues
- If you get a "SECRET_KEY not set" error, ensure you've:
  1. Created a proper .env file (you can use .env.template as a starting point)
  2. Generated and added a SECRET_KEY to your .env file
  3. Confirmed that python-dotenv is installed

### Docker Issues
- If Docker containers won't start, ensure Docker Desktop (Windows/Mac) or Docker Engine (Linux) is running
- For permission issues: on Linux, you might need to run commands with sudo or add your user to the docker group

## Redis Configuration with Docker

When running Redis in Docker and connecting to it from your local machine (outside Docker), there are two important configurations to understand:

### Connection Address

- **For applications running directly on your machine** (Django and Celery in this case):
  ```
  REDIS_HOST=localhost
  ```
  This is because Docker maps the container's port to your localhost.

- **For applications running inside Docker** connecting to the Redis container:
  ```
  REDIS_HOST=redis  
  ```
  This would use the Docker service name instead.

The default configuration in `.env.template` is set for Docker, but when you copy it to `.env`, you'll need to adjust it based on where your application is running relative to Redis.

### Troubleshooting Redis Connection

If you see this error with Celery:
```
Cannot connect to redis://redis:6379/0: Error 11001 connecting to redis:6379. getaddrinfo failed
```

It means Celery is trying to connect to "redis" hostname which doesn't exist from your computer. Change the REDIS_HOST in your .env file to "localhost" since your Django and Celery are running directly on your computer, not in Docker.

## Running the Application with Docker

To avoid Python version compatibility issues with Celery, you can run the entire application stack using Docker:

### Prerequisites for Docker Approach

1. Docker and Docker Compose installed on your system
2. Basic familiarity with Docker commands

### Docker Setup Steps

1. Set up environment variables in `.env` (make sure REDIS_HOST is set to `redis`):
   ```
   # Redis Configuration
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_DB=0
   
   # Django Configuration
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Add your SECRET_KEY here
   SECRET_KEY=your_generated_key
   ```

2. Start all services with Docker Compose:
   ```
   docker-compose up
   ```
   
   Or to run in the background:
   ```
   docker-compose up -d
   ```

3. To run only specific services (e.g., just Redis and Celery):
   ```
   docker-compose up redis celery
   ```

4. Apply database migrations (first time only):
   ```
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser (optional):
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

6. Import sample data (first time only):
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

This Docker-based approach ensures all services are running with compatible versions and properly networked together.