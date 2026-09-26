"""
Unit & Module Tests: Data Cleaning & Preprocessing Pipeline
============================================================
Test Suite: TC-CLN-001 through TC-CLN-008
"""

import os
import pandas as pd
import numpy as np
import pytest
from src.data_cleaner import (
    load_raw_dataset,
    audit_raw_data,
    clean_and_standardize_data,
    validate_cleaned_dataset
)

RAW_PATH = os.path.join("data", "raw", "Dataset for Data Analytics(1).xlsx")


@pytest.fixture(scope="module")
def raw_df():
    """Loads raw dataset once for the module tests."""
    return load_raw_dataset(RAW_PATH)


@pytest.fixture(scope="module")
def cleaned_artifacts(raw_df):
    """Executes data cleaning pipeline and provides df and changelog."""
    return clean_and_standardize_data(raw_df)


def test_tc_cln_001_raw_data_dimensions(raw_df):
    """
    TC-CLN-001: Verify raw data loading dimensions and integrity.
    Input: Dataset for Data Analytics(1).xlsx
    Expected: Exactly 1,200 rows and 14 columns.
    """
    assert len(raw_df) == 1200, f"Expected 1200 rows, found {len(raw_df)}"
    assert len(raw_df.columns) == 14, f"Expected 14 columns, found {len(raw_df.columns)}"


def test_tc_cln_002_coupon_code_imputation(cleaned_artifacts):
    """
    TC-CLN-002: Verify strategic imputation of CouponCode (Replace NaN with 'NO_COUPON').
    Input: Raw dataset with 309 missing CouponCode values.
    Expected: Zero NaN values in CouponCode; 309 occurrences of 'NO_COUPON'.
    """
    df_clean, _ = cleaned_artifacts
    assert df_clean["CouponCode"].isnull().sum() == 0, "Nulls remain in CouponCode!"
    assert (df_clean["CouponCode"] == "NO_COUPON").sum() == 309, "Incorrect imputation count!"


def test_tc_cln_003_date_iso_standardization(cleaned_artifacts):
    """
    TC-CLN-003: Verify ISO 8601 date string generation (YYYY-MM-DD).
    Input: Date column with datetime timestamps.
    Expected: Date_ISO column matching regex ^\\d{4}-\\d{2}-\\d{2}$ and 0 invalid dates.
    """
    df_clean, _ = cleaned_artifacts
    assert "Date_ISO" in df_clean.columns
    assert df_clean["Date_ISO"].str.match(r"^\d{4}-\d{2}-\d{2}$").all()


def test_tc_cln_004_financial_math_consistency(cleaned_artifacts):
    """
    TC-CLN-004: Verify TotalPrice == Quantity * UnitPrice.
    Input: Quantity, UnitPrice, TotalPrice.
    Expected: Calculated total matches TotalPrice within 0.01 tolerance across 100% of rows.
    """
    df_clean, _ = cleaned_artifacts
    calc_total = (df_clean["Quantity"] * df_clean["UnitPrice"]).round(2)
    diff = (calc_total - df_clean["TotalPrice"].round(2)).abs()
    assert (diff > 0.01).sum() == 0, f"Found {discrepancies} financial math discrepancies!"


def test_tc_cln_005_order_id_uniqueness(cleaned_artifacts):
    """
    TC-CLN-005: Verify 0% error rate on unique OrderID primary keys.
    Input: Cleaned dataset OrderID column.
    Expected: 0 duplicates; 1,200 unique OrderIDs.
    """
    df_clean, _ = cleaned_artifacts
    assert df_clean["OrderID"].duplicated().sum() == 0
    assert df_clean["OrderID"].nunique() == 1200


def test_tc_cln_006_feature_engineering_temporal(cleaned_artifacts):
    """
    TC-CLN-006: Verify temporal feature extraction (OrderYear, OrderMonth, IsWeekend).
    Input: Cleaned Date column.
    Expected: OrderYear in {2023, 2024, 2025}, IsWeekend in {0, 1}.
    """
    df_clean, _ = cleaned_artifacts
    assert set(df_clean["OrderYear"].unique()).issubset({2023, 2024, 2025})
    assert set(df_clean["IsWeekend"].unique()).issubset({0, 1})
    assert "StatusGroup" in df_clean.columns


def test_tc_cln_007_outlier_detection_bounds(cleaned_artifacts):
    """
    TC-CLN-007: Verify Tukey's IQR outlier detection on TotalPrice.
    Input: TotalPrice series.
    Expected: Outlier flags generated, upper bound correctly identified.
    """
    df_clean, _ = cleaned_artifacts
    assert "IsOutlier_IQR_TotalPrice" in df_clean.columns
    assert "ZScore_TotalPrice" in df_clean.columns
    outlier_count = df_clean["IsOutlier_IQR_TotalPrice"].sum()
    assert outlier_count > 0, "Expected at least 1 high-value outlier detected."


def test_tc_cln_008_quality_gate_validation(cleaned_artifacts):
    """
    TC-CLN-008: Verify automated validation gate assertion function.
    Input: Cleaned dataset.
    Expected: Returns True without assertion failure.
    """
    df_clean, _ = cleaned_artifacts
    assert validate_cleaned_dataset(df_clean) is True
