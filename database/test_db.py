#!/usr/bin/env python3
"""Test SQLite database connection (canonical DB file)."""

import os
import sqlite3
import sys
from pathlib import Path

from db_paths import get_sqlite_db_path

try:
    db_path = Path(get_sqlite_db_path())

    if not db_path.exists():
        print(f"Database file '{db_path}' not found")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT sqlite_version()")
    version = cursor.fetchone()[0]
    conn.close()

    print(f"SQLite version: {version}")
    print(f"SQLite DB path: {db_path}")
    print(f"SQLITE_DB env: {os.getenv('SQLITE_DB') or '(not set)'}")
    sys.exit(0)

except sqlite3.Error as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
