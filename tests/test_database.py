"""
Unit & Integration Tests: Relational Database & SQL Analytics Engine
=====================================================================
Test Suite: TC-DB-001 through TC-DB-008
"""

import os
import sqlite3
import pytest
from src.db_manager import (
    get_db_connection,
    initialize_database,
    seed_database,
    execute_query,
    PREDEFINED_QUERIES,
    DB_PATH
)


@pytest.fixture(scope="module")
def setup_db():
    """Initializes and seeds database once for test module."""
    initialize_database()
    rows = seed_database()
    return rows


def test_tc_db_001_database_connectivity(setup_db):
    """
    TC-DB-001: Verify SQLite connection and PRAGMA settings.
    Input: Path to data/ecommerce_analytics.db.
    Expected: Successful connection with foreign keys enabled.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    fk_status = cursor.execute("PRAGMA foreign_keys;").fetchone()[0]
    conn.close()
    assert fk_status == 1, "Foreign keys are not enabled!"


def test_tc_db_002_table_creation(setup_db):
    """
    TC-DB-002: Verify all 4 required tables exist in database.
    Input: Database sqlite_master schema.
    Expected: fact_orders, dim_customers, dim_products, ecommerce_flat exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    conn.close()
    expected = {"fact_orders", "dim_customers", "dim_products", "ecommerce_flat"}
    assert expected.issubset(set(tables)), f"Missing tables: {expected - set(tables)}"


def test_tc_db_003_record_counts(setup_db):
    """
    TC-DB-003: Verify row count integrity post-seeding.
    Input: Cleaned CSV seeded into tables.
    Expected: Exactly 1,200 rows in fact_orders and ecommerce_flat.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    fact_count = cursor.execute("SELECT COUNT(*) FROM fact_orders;").fetchone()[0]
    flat_count = cursor.execute("SELECT COUNT(*) FROM ecommerce_flat;").fetchone()[0]
    cust_count = cursor.execute("SELECT COUNT(*) FROM dim_customers;").fetchone()[0]
    prod_count = cursor.execute("SELECT COUNT(*) FROM dim_products;").fetchone()[0]
    conn.close()

    assert fact_count == 1200, f"Expected 1200 rows in fact_orders, found {fact_count}"
    assert flat_count == 1200, f"Expected 1200 rows in ecommerce_flat, found {flat_count}"
    assert cust_count == 1189, f"Expected 1189 unique customers, found {cust_count}"
    assert prod_count == 7, f"Expected 7 product lines, found {prod_count}"


def test_tc_db_004_kpi_query_execution(setup_db):
    """
    TC-DB-004: Execute Predefined Query 1 (Executive KPI Summary).
    Input: Aggregate query across ecommerce_flat.
    Expected: Returns 1 row, 5 columns, total_orders = 1200.
    """
    cols, rows = execute_query(PREDEFINED_QUERIES["kpi_overview"]["sql"])
    assert len(rows) == 1
    assert rows[0]["total_orders"] == 1200
    assert rows[0]["gross_revenue"] > 1200000.0


def test_tc_db_005_having_clause_query(setup_db):
    """
    TC-DB-005: Execute Predefined Query 6 (Coupon Utilization with HAVING).
    Input: GROUP BY CouponCode HAVING COUNT(OrderID) > 50.
    Expected: All returned coupon groups have usage_count > 50.
    """
    cols, rows = execute_query(PREDEFINED_QUERIES["coupon_impact_analysis"]["sql"])
    assert len(rows) > 0
    for row in rows:
        assert row["usage_count"] > 50, "HAVING condition violated!"


def test_tc_db_006_where_clause_vip_filter(setup_db):
    """
    TC-DB-006: Execute Predefined Query 7 (WHERE TotalPrice >= 2500).
    Input: Row filter WHERE TotalPrice >= 2500.00.
    Expected: Every returned record has TotalPrice >= 2500.00.
    """
    cols, rows = execute_query(PREDEFINED_QUERIES["vip_high_value_orders"]["sql"])
    assert len(rows) > 0
    for row in rows:
        assert row["TotalPrice"] >= 2500.00, "WHERE condition violated!"


def test_tc_db_007_forbidden_sql_protection(setup_db):
    """
    TC-DB-007: Test security gate preventing destructive SQL (DROP / DELETE).
    Input: 'DROP TABLE fact_orders;'
    Expected: Raises ValueError with Security Alert message.
    """
    with pytest.raises(ValueError) as excinfo:
        execute_query("DROP TABLE fact_orders;")
    assert "Security Alert" in str(excinfo.value)


def test_tc_db_008_sql_comments_and_chained_injection_protection(setup_db):
    """
    TC-DB-008: Verify support for SQL comments and blocking chained destructive statements.
    Input:
      1) Query starting with comments
      2) Query attempting chained DROP via semicolon
    Expected:
      1) Executes successfully and returns correct count.
      2) Blocked with Security Alert ValueError.
    """
    # 1. Valid query with comments
    comment_query = "-- Find total volume\n/* Multi-line header */\nSELECT COUNT(*) AS total FROM ecommerce_flat;"
    cols, rows = execute_query(comment_query)
    assert cols == ["total"]
    assert rows[0]["total"] == 1200

    # 2. Block chained DROP statement
    chained_query = "SELECT * FROM ecommerce_flat; DROP TABLE fact_orders;"
    with pytest.raises(ValueError) as excinfo:
        execute_query(chained_query)
    assert "Security Alert" in str(excinfo.value)

