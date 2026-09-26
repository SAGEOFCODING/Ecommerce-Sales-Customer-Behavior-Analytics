"""
Flask Web Application: E-Commerce Analytics Dashboard
======================================================
Project: E-Commerce Sales & Customer Behavior Analytics System
Organization: DecodeLabs Industrial Training (Batch 2026)
Program: Enterprise Data Analytics & Intelligence Platform

This web application serves an executive business dashboard, RESTful analytical
endpoints, live multidimensional filtering, and an interactive SQL query console.
"""

import os
import sys
from typing import Dict, Any
from flask import Flask, render_template, request, jsonify, Response

# Add parent directory to sys.path to allow importing from src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.analytics_engine import (
    load_cleaned_data,
    compute_executive_kpis,
    compute_product_metrics,
    compute_monthly_trends,
    compute_order_status_distribution,
    compute_referral_performance,
    compute_five_number_summary,
    compute_correlation_matrix,
    filter_dataset
)
from src.db_manager import (
    get_db_connection,
    execute_query,
    PREDEFINED_QUERIES,
    DB_PATH
)

app = Flask(
    __name__,
    template_folder=os.path.join(current_dir, "templates"),
    static_folder=os.path.join(current_dir, "static")
)

# In-memory cached dataframe for fast slicing
DATA_PATH = os.path.join(parent_dir, "data", "processed", "cleaned_ecommerce_data.csv")
DF_CLEAN = load_cleaned_data(DATA_PATH)


@app.route("/")
def index():
    """
    Renders the primary executive dashboard page.
    """
    products = sorted(DF_CLEAN["Product"].unique().tolist())
    statuses = sorted(DF_CLEAN["OrderStatus"].unique().tolist())
    payments = sorted(DF_CLEAN["PaymentMethod"].unique().tolist())
    referrals = sorted(DF_CLEAN["ReferralSource"].unique().tolist())
    
    return render_template(
        "index.html",
        products=products,
        statuses=statuses,
        payments=payments,
        referrals=referrals,
        predefined_queries=PREDEFINED_QUERIES
    )


@app.route("/api/kpis", methods=["GET"])
def api_kpis():
    """
    Returns executive KPI metrics for the header banner.
    """
    kpis = compute_executive_kpis(DF_CLEAN)
    return jsonify({"status": "success", "data": kpis})


@app.route("/api/product-performance", methods=["GET"])
def api_products():
    """
    Returns product revenue, units sold, and revenue share.
    """
    metrics = compute_product_metrics(DF_CLEAN)
    return jsonify({"status": "success", "data": metrics})


@app.route("/api/monthly-trends", methods=["GET"])
def api_monthly():
    """
    Returns time-series monthly revenue and order volume.
    """
    trends = compute_monthly_trends(DF_CLEAN)
    return jsonify({"status": "success", "data": trends})


@app.route("/api/order-status-distribution", methods=["GET"])
def api_status():
    """
    Returns order fulfillment status breakdown.
    """
    status_data = compute_order_status_distribution(DF_CLEAN)
    return jsonify({"status": "success", "data": status_data})


@app.route("/api/referral-performance", methods=["GET"])
def api_referrals():
    """
    Returns acquisition channel performance metrics.
    """
    ref_data = compute_referral_performance(DF_CLEAN)
    return jsonify({"status": "success", "data": ref_data})


@app.route("/api/five-number-summary", methods=["GET"])
def api_stats():
    """
    Returns Tukey's five-number summary and skewness.
    """
    stats = compute_five_number_summary(DF_CLEAN)
    return jsonify({"status": "success", "data": stats})


@app.route("/api/correlation", methods=["GET"])
def api_correlation():
    """
    Returns Pearson correlation matrix.
    """
    corr = compute_correlation_matrix(DF_CLEAN)
    return jsonify({"status": "success", "data": corr})


@app.route("/api/filter-data", methods=["POST"])
def api_filter():
    """
    Applies multi-dimensional criteria to slice data dynamically.
    """
    payload = request.get_json() or {}
    product = payload.get("product")
    order_status = payload.get("order_status")
    payment_method = payload.get("payment_method")
    referral_source = payload.get("referral_source")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")

    filtered_df = filter_dataset(
        DF_CLEAN,
        product=product,
        order_status=order_status,
        payment_method=payment_method,
        referral_source=referral_source,
        start_date=start_date,
        end_date=end_date
    )

    kpis = compute_executive_kpis(filtered_df)
    monthly = compute_monthly_trends(filtered_df)
    products = compute_product_metrics(filtered_df)
    statuses = compute_order_status_distribution(filtered_df)
    referrals = compute_referral_performance(filtered_df)
    
    # Return top 25 records for display
    sample_records = filtered_df.head(25)[
        ["OrderID", "Date_ISO", "CustomerID", "Product", "Quantity", "UnitPrice", "TotalPrice", "PaymentMethod", "OrderStatus", "ReferralSource"]
    ].to_dict(orient="records")

    return jsonify({
        "status": "success",
        "record_count": len(filtered_df),
        "kpis": kpis,
        "monthly": monthly,
        "products": products,
        "statuses": statuses,
        "referrals": referrals,
        "records": sample_records
    })


@app.route("/api/export-csv", methods=["GET", "POST"])
def api_export_csv():
    """
    Exports the filtered dataset matching active criteria as a downloadable CSV.
    """
    if request.method == "POST":
        payload = request.get_json() or {}
    else:
        payload = request.args.to_dict()

    product = payload.get("product")
    order_status = payload.get("order_status")
    payment_method = payload.get("payment_method")
    referral_source = payload.get("referral_source")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")

    filtered_df = filter_dataset(
        DF_CLEAN,
        product=product,
        order_status=order_status,
        payment_method=payment_method,
        referral_source=referral_source,
        start_date=start_date,
        end_date=end_date
    )

    csv_data = filtered_df.to_csv(index=False)
    filename = f"filtered_ecommerce_data_{len(filtered_df)}_records.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/api/query-sql", methods=["POST"])
def api_query_sql():
    """
    Executes a custom or predefined SQL SELECT query against the SQLite database.
    """
    payload = request.get_json() or {}
    query_str = payload.get("query", "").strip()

    if not query_str:
        return jsonify({"status": "error", "message": "SQL query string is required."}), 400

    try:
        abs_db_path = os.path.abspath(os.path.join(parent_dir, DB_PATH))
        columns, rows = execute_query(query_str, db_path=abs_db_path)
        return jsonify({
            "status": "success",
            "columns": columns,
            "rows": rows[:100],  # Cap output at 100 rows for display safety
            "row_count": len(rows),
            "execution_note": "Executed successfully against SQLite database."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route("/api/predefined-queries", methods=["GET"])
def api_predefined_queries():
    """
    Returns available Project 3 SQL analytical queries.
    """
    return jsonify({"status": "success", "queries": PREDEFINED_QUERIES})


if __name__ == "__main__":
    print("[*] Starting Flask Analytics Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
