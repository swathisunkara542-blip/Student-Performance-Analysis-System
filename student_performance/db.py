"""Small MySQL helper. All SQL uses parameterized queries (%s placeholders)."""
from decimal import Decimal

import mysql.connector
from flask import current_app


def get_connection():
    cfg = current_app.config
    return mysql.connector.connect(
        host=cfg["DB_HOST"], port=cfg["DB_PORT"], user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"], database=cfg["DB_NAME"],
    )


def _clean(row):
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}


def query(sql, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return [_clean(r) for r in cur.fetchall()]
    finally:
        conn.close()


def query_one(sql, params=None):
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    """Run INSERT/UPDATE/DELETE. Returns (last_insert_id, rows_affected)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid, cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
