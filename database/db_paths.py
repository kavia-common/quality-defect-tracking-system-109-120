"""Shared SQLite path utilities for the database tooling.

This module exists to ensure all database scripts (init, shell, tests, backup/restore)
refer to the same canonical SQLite file as the Django backend.
"""

from __future__ import annotations

import os
from pathlib import Path

# Canonical location of the SQLite database file (repo-local).
# This is used when SQLITE_DB is not set.
_CANONICAL_DB_PATH = (
    Path(__file__).resolve().parent / "myapp.db"
).resolve()


# PUBLIC_INTERFACE
def get_sqlite_db_path() -> str:
    """Return the canonical SQLite DB path.

    Resolution order:
    1) SQLITE_DB environment variable (absolute or relative)
    2) Canonical repo path: quality-defect-tracking-system-109-120/database/myapp.db

    Returns:
        Absolute filesystem path to the SQLite DB file.
    """
    env_val = os.getenv("SQLITE_DB")
    if env_val:
        return str(Path(env_val).expanduser().resolve())
    return str(_CANONICAL_DB_PATH)
