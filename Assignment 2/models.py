from pydantic import BaseModel, ConfigDict
from typing import Optional
import sqlite3

# Pydantic Models for API
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

class ForwardingRuleUpdate(BaseModel):
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Database initialization function
def init_db():
    """Initialize the SQLite database with the required table"""
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