"""
Statistical Analytics and Business Intelligence Engine
======================================================
Project: E-Commerce Sales & Customer Behavior Analytics System
Organization: DecodeLabs Industrial Training (Batch 2026)
Program: BCA Major Project / Summer Training

This module computes descriptive statistics, five-number summaries,
Pearson correlation matrices, distribution geometries, and business KPIs
consumed by both the visualization notebooks and the Flask web dashboard.
"""

import os
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd


CLEANED_DATA_PATH = os.path.join("data", "processed", "cleaned_ecommerce_data.csv")


def load_cleaned_data(file_path: str = CLEANED_DATA_PATH) -> pd.DataFrame:
    """
    Loads the cleaned e-commerce dataset for analytical evaluation.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {file_path}")
    return pd.read_csv(file_path)


def compute_five_number_summary(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
    """
    Computes Tukey's Five-Number Summary plus Mean, Std, and Skewness
    satisfying DecodeLabs Project 2 (Pages 9-10).
    """
    if columns is None:
        columns = ["Quantity", "UnitPrice", "TotalPrice", "ItemsInCart"]

    summaries = {}
    for col in columns:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        q1 = float(series.quantile(0.25))
        median = float(series.median())
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        mean = float(series.mean())
        std = float(series.std())
        skew = float(series.skew())

        summaries[col] = {
            "count": int(len(series)),
            "mean": round(mean, 2),
            "std": round(std, 2),
            "min": round(float(series.min()), 2),
            "q1": round(q1, 2),
            "median": round(median, 2),
            "q3": round(q3, 2),
            "max": round(float(series.max()), 2),
            "iqr": round(iqr, 2),
            "skewness": round(skew, 3),
            "shape": "Right-Skewed" if skew > 0.5 else ("Left-Skewed" if skew < -0.5 else "Symmetrical")
        }
    return summaries


def compute_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes high-level business metrics for the dashboard banner.
    """
    total_revenue = float(df["TotalPrice"].sum())
    total_orders = len(df)
    total_customers = int(df["CustomerID"].nunique())
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
    
    delivered_orders = int((df["OrderStatus"] == "Delivered").sum())
    fulfillment_rate = (delivered_orders / total_orders * 100.0) if total_orders > 0 else 0.0

    returned_cancelled = int(df["OrderStatus"].isin(["Returned", "Cancelled"]).sum())
    reversal_rate = (returned_cancelled / total_orders * 100.0) if total_orders > 0 else 0.0

    coupon_orders = int(df["HasCoupon"].sum())
    coupon_penetration = (coupon_orders / total_orders * 100.0) if total_orders > 0 else 0.0

    median_order_value = float(df["TotalPrice"].median()) if total_orders > 0 else 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "avg_order_value": round(avg_order_value, 2),
        "median_order_value": round(median_order_value, 2),
        "delivered_orders": delivered_orders,
        "reversal_orders": returned_cancelled,
        "coupon_orders": coupon_orders,
        "total_units_sold": int(df["Quantity"].sum()),
        "fulfillment_rate": round(fulfillment_rate, 2),
        "reversal_rate": round(reversal_rate, 2),
        "coupon_penetration": round(coupon_penetration, 2)
    }


def compute_product_metrics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes revenue, volume, and share per product category.
    """
    if df.empty:
        return []

    total_rev = df["TotalPrice"].sum()
    grouped = df.groupby("Product").agg(
        total_revenue=("TotalPrice", "sum"),
        order_count=("OrderID", "count"),
        units_sold=("Quantity", "sum"),
        avg_unit_price=("UnitPrice", "mean")
    ).reset_index()

    grouped["revenue_share_pct"] = (grouped["total_revenue"] / total_rev * 100.0).round(2) if total_rev > 0 else 0.0
    grouped = grouped.sort_values(by="total_revenue", ascending=False)

    return [
        {
            "product": row["Product"],
            "total_revenue": round(float(row["total_revenue"]), 2),
            "order_count": int(row["order_count"]),
            "units_sold": int(row["units_sold"]),
            "avg_unit_price": round(float(row["avg_unit_price"]), 2),
            "revenue_share_pct": float(row["revenue_share_pct"])
        }
        for _, row in grouped.iterrows()
    ]


def compute_monthly_trends(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes monthly revenue and order volume trends.
    """
    if df.empty:
        return []

    monthly = df.groupby("OrderMonth").agg(
        revenue=("TotalPrice", "sum"),
        order_count=("OrderID", "count"),
        avg_order_value=("TotalPrice", "mean")
    ).reset_index().sort_values(by="OrderMonth")

    return [
        {
            "month": row["OrderMonth"],
            "revenue": round(float(row["revenue"]), 2),
            "order_count": int(row["order_count"]),
            "avg_order_value": round(float(row["avg_order_value"]), 2)
        }
        for _, row in monthly.iterrows()
    ]


def compute_order_status_distribution(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculates order counts and revenue associated with each order status.
    """
    if df.empty:
        return []

    status_df = df.groupby("OrderStatus").agg(
        order_count=("OrderID", "count"),
        revenue=("TotalPrice", "sum")
    ).reset_index()

    total_orders = len(df)
    status_df["percentage"] = (status_df["order_count"] / total_orders * 100.0).round(2) if total_orders > 0 else 0.0
    status_df = status_df.sort_values(by="order_count", ascending=False)

    return [
        {
            "status": row["OrderStatus"],
            "order_count": int(row["order_count"]),
            "revenue": round(float(row["revenue"]), 2),
            "percentage": float(row["percentage"])
        }
        for _, row in status_df.iterrows()
    ]


def compute_referral_performance(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Aggregates performance across marketing acquisition channels.
    """
    if df.empty:
        return []

    ref_df = df.groupby("ReferralSource").agg(
        order_count=("OrderID", "count"),
        total_revenue=("TotalPrice", "sum"),
        avg_aov=("TotalPrice", "mean"),
        avg_cart_size=("ItemsInCart", "mean")
    ).reset_index().sort_values(by="total_revenue", ascending=False)


    return [
        {
            "channel": row["ReferralSource"],
            "order_count": int(row["order_count"]),
            "total_revenue": round(float(row["total_revenue"]), 2),
            "avg_aov": round(float(row["avg_aov"]), 2),
            "avg_cart_size": round(float(row["avg_cart_size"]), 2)
        }
        for _, row in ref_df.iterrows()
    ]


def compute_correlation_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes Pearson Correlation matrix for numeric variables.
    """
    numeric_cols = ["Quantity", "UnitPrice", "TotalPrice", "ItemsInCart"]
    corr = df[numeric_cols].corr(method="pearson").round(3)
    
    return {
        "columns": numeric_cols,
        "matrix": corr.values.tolist(),
        "dict": corr.to_dict()
    }


def filter_dataset(
    df: pd.DataFrame,
    product: Optional[str] = None,
    order_status: Optional[str] = None,
    payment_method: Optional[str] = None,
    referral_source: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Dynamically slices the dataset based on dashboard filter criteria.
    """
    filtered = df.copy()

    if product and product.lower() != "all":
        filtered = filtered[filtered["Product"].str.lower() == product.lower()]

    if order_status and order_status.lower() != "all":
        filtered = filtered[filtered["OrderStatus"].str.lower() == order_status.lower()]

    if payment_method and payment_method.lower() != "all":
        filtered = filtered[filtered["PaymentMethod"].str.lower() == payment_method.lower()]

    if referral_source and referral_source.lower() != "all":
        filtered = filtered[filtered["ReferralSource"].str.lower() == referral_source.lower()]

    if start_date:
        filtered = filtered[filtered["Date_ISO"] >= start_date]

    if end_date:
        filtered = filtered[filtered["Date_ISO"] <= end_date]

    return filtered


if __name__ == "__main__":
    df_sample = load_cleaned_data()
    print("=== Five-Number Summary ===")
    print(compute_five_number_summary(df_sample))
    print("\n=== Executive KPIs ===")
    print(compute_executive_kpis(df_sample))
    print("\n=== Pearson Correlation ===")
    print(compute_correlation_matrix(df_sample))
