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




## CODE: sample_data_import.py

```python
import sqlite3

# Database Connection
conn = sqlite3.connect("email_forwarding.db")
cursor = conn.cursor()

# Create Table for Storing Autoforwarding Data
cursor.execute('''
CREATE TABLE IF NOT EXISTS AutoForwarding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    forwarding_email TEXT,
    disposition TEXT,
    has_forwarding_filters BOOLEAN,
    error TEXT,
    investigation_note TEXT
)
''')
conn.commit()

# Create Table for Storing Forwarding Filters
cursor.execute('''
CREATE TABLE IF NOT EXISTS ForwardingFilters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forwarding_id INTEGER NOT NULL,
    email_address TEXT NOT NULL,
    created_at TEXT,
    FOREIGN KEY (forwarding_id) REFERENCES AutoForwarding(id)
)
''')
conn.commit()

# Function to Insert Data into the Database
def store_autoforwarding_data(userForwardingData):
    for user in userForwardingData:
        email = user["email"]
        name = user["name"]
        forwarding_email = user["autoForwarding"].get("emailAddress", None) if user["autoForwarding"].get("enabled") else None
        disposition = user["autoForwarding"].get("disposition", None)
        has_filters = bool(user["forwardingFilters"])  # True if filters exist
        error = user.get("error", None)
        investigation_note = user.get("investigation_note", None)

        # Insert or update the AutoForwarding record
        cursor.execute('''
            INSERT INTO AutoForwarding (email, name, forwarding_email, disposition, has_forwarding_filters, error, investigation_note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name=excluded.name,
                forwarding_email=excluded.forwarding_email,
                disposition=excluded.disposition,
                has_forwarding_filters=excluded.has_forwarding_filters,
                error=excluded.error,
                investigation_note=excluded.investigation_note
        ''', (email, name, forwarding_email, disposition, has_filters, error, investigation_note))
        
        # Get the ID of the inserted/updated AutoForwarding record
        cursor.execute("SELECT id FROM AutoForwarding WHERE email = ?", (email,))
        forwarding_id = cursor.fetchone()[0]
        
        # Delete existing filters for this forwarding rule (to handle updates)
        cursor.execute("DELETE FROM ForwardingFilters WHERE forwarding_id = ?", (forwarding_id,))
        
        # Insert filter details if they exist
        if user["forwardingFilters"]:
            for filter_item in user["forwardingFilters"]:
                email_address = filter_item["emailAddress"]
                created_at = filter_item.get("createdAt", None)
                
                cursor.execute('''
                    INSERT INTO ForwardingFilters (forwarding_id, email_address, created_at)
                    VALUES (?, ?, ?)
                ''', (forwarding_id, email_address, created_at))

    conn.commit()

# Example Data (Replace with actual script output)
userForwardingData = [
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

# Store Data in Database
store_autoforwarding_data(userForwardingData)

# Verify Data Stored
cursor.execute("SELECT * FROM AutoForwarding")
print("AutoForwarding Records:")
for row in cursor.fetchall():
    print(row)

# Verify Filters Stored
cursor.execute("SELECT * FROM ForwardingFilters")
print("\nForwardingFilters Records:")
for row in cursor.fetchall():
    print(row)

# Close Connection
conn.close()
```

## CODE: models.py (Pydantic Models)

```python
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import sqlite3

# Pydantic Models for API
class ForwardingFilter(BaseModel):
    id: Optional[int] = None
    forwarding_id: int
    email_address: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingFilterCreate(BaseModel):
    email_address: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingRuleBase(BaseModel):
    email: str
    name: str
    forwarding_email: Optional[str] = None
    disposition: Optional[str] = None
    has_forwarding_filters: bool
    error: Optional[str] = None
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingRuleCreate(ForwardingRuleBase):
    pass

class ForwardingRule(ForwardingRuleBase):
    id: int
    filters: Optional[List[ForwardingFilter]] = None

class ForwardingRuleUpdate(BaseModel):
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Database initialization function
def init_db():
    """Initialize the SQLite database with the required tables"""
    conn = sqlite3.connect("email_forwarding.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AutoForwarding (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT,
        forwarding_email TEXT,
        disposition TEXT,
        has_forwarding_filters BOOLEAN,
        error TEXT,
        investigation_note TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ForwardingFilters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forwarding_id INTEGER NOT NULL,
        email_address TEXT NOT NULL,
        created_at TEXT,
        FOREIGN KEY (forwarding_id) REFERENCES AutoForwarding(id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Database connection function
def get_db():
    """Get a database connection with row factory set to return dictionaries"""
    conn = None
    try:
        conn = sqlite3.connect("email_forwarding.db")
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn is not None:
            conn.close()

# Initialize the database when this module is imported
init_db() 
```

##CODE: main.py

```python
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import sqlite3

# Pydantic Models for API
class ForwardingFilter(BaseModel):
    id: Optional[int] = None
    forwarding_id: int
    email_address: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingFilterCreate(BaseModel):
    email_address: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingRuleBase(BaseModel):
    email: str
    name: str
    forwarding_email: Optional[str] = None
    disposition: Optional[str] = None
    has_forwarding_filters: bool
    error: Optional[str] = None
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingRuleCreate(ForwardingRuleBase):
    pass

class ForwardingRule(ForwardingRuleBase):
    id: int
    filters: Optional[List[ForwardingFilter]] = None

class ForwardingRuleUpdate(BaseModel):
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Database initialization function
def init_db():
    """Initialize the SQLite database with the required tables"""
    conn = sqlite3.connect("email_forwarding.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AutoForwarding (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT,
        forwarding_email TEXT,
        disposition TEXT,
        has_forwarding_filters BOOLEAN,
        error TEXT,
        investigation_note TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ForwardingFilters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forwarding_id INTEGER NOT NULL,
        email_address TEXT NOT NULL,
        created_at TEXT,
        FOREIGN KEY (forwarding_id) REFERENCES AutoForwarding(id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Database connection function
def get_db():
    """Get a database connection with row factory set to return dictionaries"""
    conn = None
    try:
        conn = sqlite3.connect("email_forwarding.db")
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn is not None:
            conn.close()

# Initialize the database when this module is imported
init_db() 
```