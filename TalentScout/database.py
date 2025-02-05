import sqlite3
import json

# Create a global database connection
connection = sqlite3.connect("TalentScout.db", check_same_thread=False)

def initialize_database():
    """Initialize the database with required tables."""
    with connection:
        cursor = connection.cursor()
        # Table for candidates
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                years_of_experience INTEGER,
                desired_position TEXT,
                current_location TEXT,
                tech_stack TEXT
            );
            """
        )
        # Table for conversations
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                role TEXT,
                content TEXT,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            );
            """
        )

def insert_candidate(full_name, email, phone, years_of_experience, desired_position, current_location, tech_stack):
    """Insert a new candidate into the database."""
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO candidates (full_name, email, phone, years_of_experience, desired_position, current_location, tech_stack)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (full_name, email, phone, years_of_experience, desired_position, current_location, tech_stack),
        )
        return cursor.lastrowid

def insert_conversation(candidate_id, role, content):
    """Insert a conversation message into the database."""
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (candidate_id, role, content)
            VALUES (?, ?, ?)
            """,
            (candidate_id, role, content),
        )

def get_candidate_by_email(email):
    """Retrieve a candidate by email."""
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM candidates WHERE email = ?", (email,))
        return cursor.fetchone()

def get_conversations_by_candidate_id(candidate_id):
    """Retrieve all conversations for a candidate."""
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM conversations WHERE candidate_id = ? ORDER BY date ASC", (candidate_id,))
        return cursor.fetchall()