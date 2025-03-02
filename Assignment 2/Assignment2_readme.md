# Email Forwarding Rules Audit API

This application provides a REST API for managing and auditing email forwarding rules.

## Prerequisites
1. Python 3.13
2. Rust (required for Pydantic 2.x)
   - Download and install from https://rustup.rs/

## Installation Steps
1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python -m uvicorn main:app --reload
   ```

## API Documentation
Once the application is running, you can access:
- Interactive API documentation: http://127.0.0.1:8000/docs
- Alternative API documentation: http://127.0.0.1:8000/redoc

## Available Endpoints
- GET /rules/ - Get all forwarding rules
- GET /rules/{rule_id} - Get a specific rule
- PUT /rules/{rule_id}/review - Update review/investigation notes
- DELETE /rules/{rule_id} - Delete a rule
- GET /rules/search/ - Search rules with filters
- GET /stats/ - Get statistics about forwarding rules

## Project Structure
- main.py: FastAPI application and endpoints
- models.py: Database models and Pydantic schemas
- requirements.txt: Project dependencies
- email_forwarding.db: SQLite database (created automatically)