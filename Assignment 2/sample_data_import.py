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
