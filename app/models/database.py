"""
SQLite database helper for the Hospital Token System.
Creates hospital.db and initializes tables automatically.
"""

import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / 'hospital.db'


def get_db_connection():
    """Get a SQLite database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Create SQLite tables and seed departments if needed."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mobile_number TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT NOT NULL,
            dept_code TEXT NOT NULL UNIQUE,
            description TEXT,
            icon TEXT,
            queue_count INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dept_id INTEGER NOT NULL,
            token_number TEXT NOT NULL UNIQUE,
            dept_code TEXT NOT NULL,
            dept_name TEXT NOT NULL,
            token_type TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            status TEXT NOT NULL DEFAULT 'waiting',
            queue_position INTEGER NOT NULL DEFAULT 1,
            estimated_wait_time INTEGER NOT NULL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(dept_id) REFERENCES departments(id)
        )
    """)

    cursor.execute("PRAGMA table_info(tokens)")
    columns = [row['name'] for row in cursor.fetchall()]
    if 'status' not in columns:
        cursor.execute("ALTER TABLE tokens ADD COLUMN status TEXT NOT NULL DEFAULT 'waiting'")
    else:
        cursor.execute("UPDATE tokens SET status = 'waiting' WHERE status = 'active'")

    cursor.execute("SELECT COUNT(1) FROM departments")
    row = cursor.fetchone()
    if row is None or row[0] == 0:
        departments = [
            ('General OPD', 'GEN', 'General healthcare and consultation services', '🏥'),
            ('Cardiology', 'CARD', 'Heart and cardiovascular disease specialists', '❤️'),
            ('Orthopedics', 'ORTH', 'Bone, joint and orthopedic care', '🦴'),
            ('ENT', 'ENT', 'Ear, nose and throat specialists', '👂'),
            ('Neurology', 'NEUR', 'Nervous system and neurological disorders', '🧠'),
            ('Pediatrics', 'PED', 'Child health and pediatric care', '👶')
        ]
        cursor.executemany(
            "INSERT INTO departments (dept_name, dept_code, description, icon) VALUES (?, ?, ?, ?)",
            departments
        )

    conn.commit()
    conn.close()


def db_init():
    """Alias for init_database, called during app startup."""
    init_database()

