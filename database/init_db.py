#!/usr/bin/env python3
"""Initialize SQLite database for database.

Aligns all tooling on a canonical SQLite file path and inserts minimal seed data
for local usability.
"""

import os
import sqlite3
from pathlib import Path

from db_paths import get_sqlite_db_path

print("Starting SQLite setup...")

DB_PATH = Path(get_sqlite_db_path())
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Check if database already exists
db_exists = DB_PATH.exists()
if db_exists:
    print(f"SQLite database already exists at {DB_PATH}")
    # Verify it's accessible
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("SELECT 1")
        conn.close()
        print("Database is accessible and working.")
    except Exception as e:
        print(f"Warning: Database exists but may be corrupted: {e}")
else:
    print(f"Creating new SQLite database at {DB_PATH}...")

# Create/open database
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Create initial schema (tooling-local tables; Django tables are managed by migrations)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS app_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

# Minimal seed data for local usability
seed_app_info = {
    "project_name": "quality-defect-tracking-system",
    "version": "0.1.0",
    "environment": "local",
    "description": "Local seed data for development",
}
for k, v in seed_app_info.items():
    cursor.execute(
        "INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
        (k, v),
    )

# Seed a couple of local users if table is empty
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
if user_count == 0:
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (?, ?)",
        ("admin", "admin@example.com"),
    )
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (?, ?)",
        ("inspector", "inspector@example.com"),
    )

conn.commit()

# Get database statistics
cursor.execute(
    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
)
table_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM app_info")
record_count = cursor.fetchone()[0]

conn.close()

# Save connection information to a file (keep it deterministic and canonical)
try:
    with open("db_connection.txt", "w", encoding="utf-8") as f:
        f.write("# SQLite connection methods:\n")
        f.write("# Canonical DB file (used by Django + tooling):\n")
        f.write(f"#   {DB_PATH}\n")
        f.write("#\n")
        f.write("# Python:\n")
        f.write(f"#   sqlite3.connect('{DB_PATH}')\n")
        f.write("#\n")
        f.write("# Connection string:\n")
        f.write(f"#   sqlite:///{DB_PATH}\n")
        f.write("#\n")
        f.write("# File path:\n")
        f.write(f"#   {DB_PATH}\n")
    print("Connection information saved to db_connection.txt")
except Exception as e:
    print(f"Warning: Could not save connection info: {e}")

# Create environment variables file for Node.js viewer (always points to canonical DB)
try:
    with open("db_visualizer/sqlite.env", "w", encoding="utf-8") as f:
        f.write(f'export SQLITE_DB="{DB_PATH}"\n')
    print("Environment variables saved to db_visualizer/sqlite.env")
except Exception as e:
    print(f"Warning: Could not save environment variables: {e}")

print("\nSQLite setup complete!")
print(f"Database: {DB_PATH.name}")
print(f"Location: {DB_PATH}")
print("")
print("To use with Node.js viewer, run: source db_visualizer/sqlite.env")
print("")
print("Database statistics:")
print(f"  Tables: {table_count}")
print(f"  App info records: {record_count}")
print("\nScript completed successfully.")
