# -*- coding: utf-8 -*-
"""
Small idempotent migrations for the SQLite-first local deployment.
"""
import os
import sqlite3


def _sqlite_path(database_uri):
    prefix = 'sqlite:///'
    if not database_uri.startswith(prefix):
        return None
    return database_uri[len(prefix):]


def run_sqlite_migrations(database_uri):
    """Apply lightweight schema updates that db.create_all() cannot handle."""
    db_path = _sqlite_path(database_uri)
    if not db_path or not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    try:
        existing_tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if 'custom_module' not in existing_tables:
            return

        columns = {
            row[1] for row in conn.execute('PRAGMA table_info(custom_module)').fetchall()
        }
        migrations = [
            ('is_locked', 'ALTER TABLE custom_module ADD COLUMN is_locked BOOLEAN DEFAULT 1'),
            ('locked_at', 'ALTER TABLE custom_module ADD COLUMN locked_at DATETIME'),
            ('version', 'ALTER TABLE custom_module ADD COLUMN version INTEGER DEFAULT 1'),
            ('source_module_id', 'ALTER TABLE custom_module ADD COLUMN source_module_id INTEGER'),
        ]
        for column_name, statement in migrations:
            if column_name not in columns:
                conn.execute(statement)

        conn.execute('UPDATE custom_module SET is_locked = 1 WHERE is_locked IS NULL')
        conn.execute('UPDATE custom_module SET version = 1 WHERE version IS NULL')
        conn.commit()
    finally:
        conn.close()
