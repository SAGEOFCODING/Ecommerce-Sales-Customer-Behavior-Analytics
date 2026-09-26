"""
Unit & Module Tests: Statistical Analytics & Insights Engine
=============================================================
Test Suite: TC-ANL-001 through TC-ANL-007
"""

import os
import pytest
import pandas as pd
from src.analytics_engine import (
    load_cleaned_data,
    compute_five_number_summary,
    compute_executive_kpis,
    compute_product_metrics,
    compute_correlation_matrix,
    filter_dataset
)

DATA_PATH = os.path.join("data", "processed", "cleaned_ecommerce_data.csv")


@pytest.fixture(scope="module")
def df_clean():
    """Provides cleaned DataFrame."""
    return load_cleaned_data(DATA_PATH)


def test_tc_anl_001_five_number_summary(df_clean):
    """
    TC-ANL-001: Verify five-number summary calculations (Min, Q1, Median, Q3, Max).
    Input: TotalPrice series.
    Expected: Values follow strict inequality Min <= Q1 <= Median <= Q3 <= Max.
    """
    summary = compute_five_number_summary(df_clean)
    assert "TotalPrice" in summary
    stats = summary["TotalPrice"]
    assert stats["min"] <= stats["q1"] <= stats["median"] <= stats["q3"] <= stats["max"]
    assert stats["shape"] == "Right-Skewed"


def test_tc_anl_002_kpi_calculations(df_clean):
    """
    TC-ANL-002: Verify executive KPI metrics calculations.
    Input: 1,200 orders DataFrame.
    Expected: Total revenue equals sum of TotalPrice, AOV = TotalRevenue / TotalOrders.
    """
    kpis = compute_executive_kpis(df_clean)
    assert kpis["total_orders"] == 1200
    assert kpis["total_revenue"] == round(df_clean["TotalPrice"].sum(), 2)
    expected_aov = round(df_clean["TotalPrice"].sum() / 1200, 2)
    assert kpis["avg_order_value"] == expected_aov
    assert 0 <= kpis["fulfillment_rate"] <= 100
    assert 0 <= kpis["reversal_rate"] <= 100


def test_tc_anl_003_product_metrics(df_clean):
    """
    TC-ANL-003: Verify product performance aggregation and revenue share.
    Input: DataFrame grouped by Product.
    Expected: Sum of product revenue shares equals 100% (+/- 0.1% rounding).
    """
    products = compute_product_metrics(df_clean)
    assert len(products) == 7
    total_share = sum(p["revenue_share_pct"] for p in products)
    assert abs(total_share - 100.0) < 0.2


def test_tc_anl_004_correlation_matrix(df_clean):
    """
    TC-ANL-004: Verify Pearson correlation matrix properties.
    Input: Quantity, UnitPrice, TotalPrice, ItemsInCart.
    Expected: Diagonal values are 1.0; matrix is symmetric.
    """
    corr_data = compute_correlation_matrix(df_clean)
    matrix = corr_data["matrix"]
    assert len(matrix) == 4
    for i in range(4):
        assert abs(matrix[i][i] - 1.0) < 0.001
        for j in range(4):
            assert abs(matrix[i][j] - matrix[j][i]) < 0.001


def test_tc_anl_005_filtering_by_product(df_clean):
    """
    TC-ANL-005: Verify dynamic dataset filtering by Product.
    Input: filter_dataset(product='Laptop').
    Expected: All rows in result have Product == 'Laptop'.
    """
    filtered = filter_dataset(df_clean, product="Laptop")
    assert len(filtered) > 0
    assert (filtered["Product"] == "Laptop").all()


def test_tc_anl_006_filtering_by_status_and_date(df_clean):
    """
    TC-ANL-006: Verify composite filtering by OrderStatus and Date range.
    Input: order_status='Delivered', start_date='2024-01-01', end_date='2024-12-31'.
    Expected: All rows delivered in 2024.
    """
    filtered = filter_dataset(
        df_clean,
        order_status="Delivered",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    assert len(filtered) > 0
    assert (filtered["OrderStatus"] == "Delivered").all()
    assert (filtered["Date_ISO"] >= "2024-01-01").all()
    assert (filtered["Date_ISO"] <= "2024-12-31").all()


def test_tc_anl_007_empty_dataframe_handling(df_clean):
    """
    TC-ANL-007: Edge-case test verifying graceful handling of empty DataFrame slices.
    Input: Empty DataFrame slice.
    Expected: compute_executive_kpis returns 0s without crashing; metrics return [].
    """
    empty_df = df_clean[df_clean["Product"] == "NON_EXISTENT_PRODUCT"]
    assert len(empty_df) == 0
    kpis = compute_executive_kpis(empty_df)
    assert kpis["total_orders"] == 0
    assert kpis["total_revenue"] == 0.0
    assert kpis["avg_order_value"] == 0.0
    assert compute_product_metrics(empty_df) == []

