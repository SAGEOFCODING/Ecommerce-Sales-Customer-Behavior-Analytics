"""
System, Black-Box & Acceptance Tests: Flask Web Application & REST APIs
=======================================================================
Test Suite: TC-SYS-001 through TC-SYS-008
"""

import pytest
from app.app import app


@pytest.fixture
def client():
    """Configures Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_tc_sys_001_dashboard_home_rendering(client):
    """
    TC-SYS-001: Acceptance Test for main dashboard user interface.
    Input: HTTP GET /
    Expected: HTTP 200, contains title and key dashboard DOM containers.
    """
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "E-Commerce Sales & Customer Behavior Analytics" in html
    assert "DECODELABS" in html
    assert "kpi-gross-revenue" in html
    assert "plot-monthly-trend" in html
    assert "sql-input" in html


def test_tc_sys_002_api_kpis_endpoint(client):
    """
    TC-SYS-002: Black-Box Test for /api/kpis REST endpoint.
    Input: HTTP GET /api/kpis
    Expected: JSON payload with status='success' and numerical business KPIs.
    """
    res = client.get("/api/kpis")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    data = json_data["data"]
    assert data["total_orders"] == 1200
    assert data["total_revenue"] > 1000000.0


def test_tc_sys_003_api_product_performance(client):
    """
    TC-SYS-003: Black-Box Test for /api/product-performance.
    Input: HTTP GET /api/product-performance
    Expected: List of 7 product categories with revenue and unit metrics.
    """
    res = client.get("/api/product-performance")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert len(json_data["data"]) == 7


def test_tc_sys_004_api_monthly_trends(client):
    """
    TC-SYS-004: Black-Box Test for /api/monthly-trends.
    Input: HTTP GET /api/monthly-trends
    Expected: Time-series monthly revenue array across 2023-2025.
    """
    res = client.get("/api/monthly-trends")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert len(json_data["data"]) >= 24


def test_tc_sys_005_api_filter_data(client):
    """
    TC-SYS-005: Integration & Functional Test for multi-dimensional filter.
    Input: POST /api/filter-data with product='Desk'.
    Expected: JSON response with filtered record count and sample table records.
    """
    res = client.post("/api/filter-data", json={"product": "Desk"})
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["record_count"] == 170
    assert len(json_data["records"]) <= 25


def test_tc_sys_006_api_query_sql_success(client):
    """
    TC-SYS-006: System Test for live interactive SQL query runner.
    Input: POST /api/query-sql with valid analytical query.
    Expected: Status success, columns array, rows array with matching keys.
    """
    query = "SELECT Product, SUM(Quantity) AS total_qty FROM ecommerce_flat GROUP BY Product;"
    res = client.post("/api/query-sql", json={"query": query})
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert "Product" in json_data["columns"]
    assert "total_qty" in json_data["columns"]
    assert len(json_data["rows"]) == 7


def test_tc_sys_007_api_query_sql_security_block(client):
    """
    TC-SYS-007: White-Box Security Test verifying block on non-SELECT statements.
    Input: POST /api/query-sql with 'DELETE FROM ecommerce_flat;'
    Expected: HTTP 400 with security rejection message.
    """
    query = "DELETE FROM ecommerce_flat WHERE OrderID = 'ORD200000';"
    res = client.post("/api/query-sql", json={"query": query})
    assert res.status_code == 400
    json_data = res.get_json()
    assert json_data["status"] == "error"
    assert "Security Alert" in json_data["message"]


def test_tc_sys_008_api_export_csv(client):
    """
    TC-SYS-008: Functional & Integration Test for CSV export endpoint.
    Input:
      1) GET /api/export-csv (unfiltered full export)
      2) POST /api/export-csv with {"product": "Laptop"}
    Expected:
      - HTTP 200 with mimetype text/csv
      - Content-Disposition header with filename
      - Unfiltered CSV contains 1,201 lines (header + 1,200 records)
      - Filtered CSV contains 174 lines (header + 173 Laptop records)
    """
    # Test 1: Full unfiltered export
    res_all = client.get("/api/export-csv")
    assert res_all.status_code == 200
    assert "text/csv" in res_all.content_type
    assert "attachment; filename=filtered_ecommerce_data_1200_records.csv" in res_all.headers.get("Content-Disposition", "")
    lines_all = res_all.data.decode("utf-8").strip().splitlines()
    assert len(lines_all) == 1201
    assert "OrderID" in lines_all[0]
    assert "Date_ISO" in lines_all[0]
    assert "Product" in lines_all[0]

    # Test 2: Filtered export for Laptop
    res_filtered = client.post("/api/export-csv", json={"product": "Laptop"})
    assert res_filtered.status_code == 200
    assert "text/csv" in res_filtered.content_type
    assert "attachment; filename=filtered_ecommerce_data_173_records.csv" in res_filtered.headers.get("Content-Disposition", "")
    lines_filtered = res_filtered.data.decode("utf-8").strip().splitlines()
    assert len(lines_filtered) == 174
    # Ensure all data lines have Laptop
    for line in lines_filtered[1:]:
        assert "Laptop" in line

