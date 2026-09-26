"""
Relational Database and SQL Analytics Engine
=============================================
Project: E-Commerce Sales & Customer Behavior Analytics System
Organization: DecodeLabs Industrial Training (Batch 2026)
Program: BCA Major Project / Summer Training

This module initializes an SQLite relational database, creates normalized (3NF)
and analytical flat tables, loads cleaned data, and exposes an executable suite
of SQL queries demonstrating Project 3 relational logic.
"""

import os
import sqlite3
from typing import Dict, List, Tuple, Any
import pandas as pd


DB_PATH = os.path.join("data", "ecommerce_analytics.db")
CLEANED_DATA_PATH = os.path.join("data", "processed", "cleaned_ecommerce_data.csv")


def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Establishes and returns a connection to the SQLite database.
    Enables foreign key constraints and returns rows as dictionaries.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_path: str = DB_PATH) -> None:
    """
    Creates normalized relational dimensions, fact tables, and flat analytics table.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Drop existing tables to allow clean recreation
    cursor.executescript("""
    DROP TABLE IF EXISTS fact_orders;
    DROP TABLE IF EXISTS dim_customers;
    DROP TABLE IF EXISTS dim_products;
    DROP TABLE IF EXISTS ecommerce_flat;

    -- Dimension 1: Customers
    CREATE TABLE dim_customers (
        customer_id TEXT PRIMARY KEY,
        shipping_address TEXT NOT NULL,
        first_order_date TEXT,
        total_orders INTEGER DEFAULT 0
    );

    -- Dimension 2: Products
    CREATE TABLE dim_products (
        product_name TEXT PRIMARY KEY,
        default_unit_price REAL NOT NULL
    );

    -- Fact Table: Orders (Normalized)
    CREATE TABLE fact_orders (
        order_id TEXT PRIMARY KEY,
        order_date TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_price REAL NOT NULL,
        payment_method TEXT NOT NULL,
        order_status TEXT NOT NULL,
        status_group TEXT NOT NULL,
        tracking_number TEXT NOT NULL,
        items_in_cart INTEGER NOT NULL,
        coupon_code TEXT NOT NULL,
        has_coupon INTEGER NOT NULL,
        referral_source TEXT NOT NULL,
        order_year INTEGER NOT NULL,
        order_month TEXT NOT NULL,
        order_day_of_week TEXT NOT NULL,
        is_weekend INTEGER NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES dim_customers (customer_id),
        FOREIGN KEY (product_name) REFERENCES dim_products (product_name)
    );

    -- Analytical Flat Table (Optimized for rapid analytical querying and dashboards)
    CREATE TABLE ecommerce_flat (
        OrderID TEXT PRIMARY KEY,
        Date TEXT NOT NULL,
        Date_ISO TEXT NOT NULL,
        CustomerID TEXT NOT NULL,
        Product TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        UnitPrice REAL NOT NULL,
        ShippingAddress TEXT NOT NULL,
        PaymentMethod TEXT NOT NULL,
        OrderStatus TEXT NOT NULL,
        StatusGroup TEXT NOT NULL,
        TrackingNumber TEXT NOT NULL,
        ItemsInCart INTEGER NOT NULL,
        CouponCode TEXT NOT NULL,
        HasCoupon INTEGER NOT NULL,
        ReferralSource TEXT NOT NULL,
        TotalPrice REAL NOT NULL,
        OrderYear INTEGER NOT NULL,
        OrderMonth TEXT NOT NULL,
        OrderMonthName TEXT NOT NULL,
        OrderDayOfWeek TEXT NOT NULL,
        IsWeekend INTEGER NOT NULL,
        IsOutlier_IQR_TotalPrice INTEGER NOT NULL,
        IsOutlier_Z_TotalPrice INTEGER NOT NULL
    );

    -- Indexes for high-speed querying
    CREATE INDEX idx_orders_date ON fact_orders(order_date);
    CREATE INDEX idx_orders_customer ON fact_orders(customer_id);
    CREATE INDEX idx_orders_product ON fact_orders(product_name);
    CREATE INDEX idx_orders_status ON fact_orders(order_status);
    CREATE INDEX idx_flat_date ON ecommerce_flat(Date_ISO);
    CREATE INDEX idx_flat_product ON ecommerce_flat(Product);
    CREATE INDEX idx_flat_status ON ecommerce_flat(OrderStatus);
    CREATE INDEX idx_flat_referral ON ecommerce_flat(ReferralSource);
    """)

    conn.commit()
    conn.close()


def seed_database(csv_path: str = CLEANED_DATA_PATH, db_path: str = DB_PATH) -> int:
    """
    Populates normalized dimension and fact tables as well as the flat table
    from the cleaned CSV dataset.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Populate dim_customers
    customer_agg = df.groupby("CustomerID").agg(
        shipping_address=("ShippingAddress", "first"),
        first_order_date=("Date_ISO", "min"),
        total_orders=("OrderID", "count")
    ).reset_index()

    for _, row in customer_agg.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO dim_customers (customer_id, shipping_address, first_order_date, total_orders)
            VALUES (?, ?, ?, ?)
        """, (row["CustomerID"], row["shipping_address"], row["first_order_date"], int(row["total_orders"])))

    # 2. Populate dim_products
    product_agg = df.groupby("Product").agg(
        default_unit_price=("UnitPrice", "median")
    ).reset_index()

    for _, row in product_agg.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO dim_products (product_name, default_unit_price)
            VALUES (?, ?)
        """, (row["Product"], float(row["default_unit_price"])))

    # 3. Populate fact_orders
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO fact_orders (
                order_id, order_date, customer_id, product_name, quantity, unit_price,
                total_price, payment_method, order_status, status_group, tracking_number,
                items_in_cart, coupon_code, has_coupon, referral_source, order_year,
                order_month, order_day_of_week, is_weekend
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(row["OrderID"]), str(row["Date_ISO"]), str(row["CustomerID"]),
            str(row["Product"]), int(row["Quantity"]), float(row["UnitPrice"]),
            float(row["TotalPrice"]), str(row["PaymentMethod"]), str(row["OrderStatus"]),
            str(row["StatusGroup"]), str(row["TrackingNumber"]), int(row["ItemsInCart"]),
            str(row["CouponCode"]), int(row["HasCoupon"]), str(row["ReferralSource"]),
            int(row["OrderYear"]), str(row["OrderMonth"]), str(row["OrderDayOfWeek"]),
            int(row["IsWeekend"])
        ))

    # 4. Populate ecommerce_flat
    df.to_sql("ecommerce_flat", conn, if_exists="replace", index=False)

    conn.commit()
    count = cursor.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0]
    conn.close()
    return count


# Predefined Business SQL Queries strictly satisfying DecodeLabs Project 3
PREDEFINED_QUERIES = {
    "kpi_overview": {
        "title": "Executive KPI Summary",
        "description": "Measures total revenue, order count, unique customers, and average basket value.",
        "sql": """
            SELECT 
                COUNT(OrderID) AS total_orders,
                COUNT(DISTINCT CustomerID) AS total_customers,
                ROUND(SUM(TotalPrice), 2) AS gross_revenue,
                ROUND(AVG(TotalPrice), 2) AS average_order_value,
                ROUND(SUM(Quantity), 0) AS total_units_sold
            FROM ecommerce_flat;
        """
    },
    "product_performance": {
        "title": "Product Category Sales & Revenue Contribution",
        "description": "Uses GROUP BY and aggregations to rank products by total revenue and unit sales.",
        "sql": """
            SELECT 
                Product,
                COUNT(OrderID) AS orders_count,
                SUM(Quantity) AS units_sold,
                ROUND(AVG(UnitPrice), 2) AS avg_unit_price,
                ROUND(SUM(TotalPrice), 2) AS total_revenue,
                ROUND(100.0 * SUM(TotalPrice) / (SELECT SUM(TotalPrice) FROM ecommerce_flat), 2) AS revenue_share_pct
            FROM ecommerce_flat
            GROUP BY Product
            ORDER BY total_revenue DESC;
        """
    },
    "order_fulfillment_audit": {
        "title": "Order Fulfillment & Revenue at Risk",
        "description": "Isolates delivered revenue vs. revenue lost to cancellations and returns.",
        "sql": """
            SELECT 
                OrderStatus,
                COUNT(OrderID) AS order_count,
                ROUND(SUM(TotalPrice), 2) AS status_revenue,
                ROUND(100.0 * COUNT(OrderID) / (SELECT COUNT(*) FROM ecommerce_flat), 2) AS volume_pct
            FROM ecommerce_flat
            GROUP BY OrderStatus
            ORDER BY order_count DESC;
        """
    },
    "marketing_channel_roi": {
        "title": "Referral Marketing Channel Efficacy",
        "description": "Analyzes which acquisition channels drive the highest order volume and revenue.",
        "sql": """
            SELECT 
                ReferralSource,
                COUNT(OrderID) AS total_orders,
                ROUND(SUM(TotalPrice), 2) AS total_revenue,
                ROUND(AVG(TotalPrice), 2) AS avg_order_value,
                ROUND(AVG(ItemsInCart), 2) AS avg_cart_size
            FROM ecommerce_flat
            GROUP BY ReferralSource
            ORDER BY total_revenue DESC;
        """
    },
    "payment_method_breakdown": {
        "title": "Payment Method Distribution",
        "description": "Compares adoption rate and revenue flow across payment channels.",
        "sql": """
            SELECT 
                PaymentMethod,
                COUNT(OrderID) AS transaction_count,
                ROUND(SUM(TotalPrice), 2) AS total_revenue,
                ROUND(AVG(TotalPrice), 2) AS avg_ticket_size
            FROM ecommerce_flat
            GROUP BY PaymentMethod
            ORDER BY transaction_count DESC;
        """
    },
    "coupon_impact_analysis": {
        "title": "Coupon Code Utilization (Using HAVING Clause)",
        "description": "Demonstrates HAVING to filter promotional buckets with > 50 transactions.",
        "sql": """
            SELECT 
                CouponCode,
                COUNT(OrderID) AS usage_count,
                ROUND(SUM(TotalPrice), 2) AS total_spend,
                ROUND(AVG(TotalPrice), 2) AS avg_spend
            FROM ecommerce_flat
            GROUP BY CouponCode
            HAVING COUNT(OrderID) > 50
            ORDER BY usage_count DESC;
        """
    },
    "vip_high_value_orders": {
        "title": "High-Value Transaction Filter (WHERE TotalPrice >= 2500)",
        "description": "Applies strict row-level filtering to detect top-tier enterprise/VIP orders.",
        "sql": """
            SELECT 
                OrderID,
                Date_ISO,
                CustomerID,
                Product,
                Quantity,
                UnitPrice,
                TotalPrice,
                PaymentMethod,
                OrderStatus
            FROM ecommerce_flat
            WHERE TotalPrice >= 2500.00
            ORDER BY TotalPrice DESC
            LIMIT 20;
        """
    },
    "monthly_sales_trend": {
        "title": "Monthly Revenue & Volume Trend",
        "description": "Time-based aggregation across months to identify growth trajectory.",
        "sql": """
            SELECT 
                OrderMonth,
                COUNT(OrderID) AS monthly_orders,
                ROUND(SUM(TotalPrice), 2) AS monthly_revenue,
                ROUND(AVG(TotalPrice), 2) AS avg_monthly_aov
            FROM ecommerce_flat
            GROUP BY OrderMonth
            ORDER BY OrderMonth ASC;
        """
    }
}


def execute_query(query_str: str, params: Tuple = (), db_path: str = DB_PATH) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Safely executes an analytical SQL SELECT query against the SQLite database.
    Prevents destructive operations (DROP, DELETE, UPDATE, INSERT) in analytical mode.
    
    Parameters:
        query_str (str): The SQL SELECT query.
        params (tuple): Parameterized arguments.
        db_path (str): Path to SQLite database.
        
    Returns:
        Tuple[List[str], List[Dict[str, Any]]]: Column headers and list of row dicts.
    """
    import re
    clean_query = query_str.strip()
    if not clean_query:
        raise ValueError("Query string is empty.")

    # Split by semicolon to ensure no destructive statements are chained
    statements = [s.strip() for s in clean_query.split(";") if s.strip()]
    for s in statements:
        # Strip comments (-- and /* */)
        unc = re.sub(r'--.*?\n', '\n', s)
        unc = re.sub(r'/\*.*?\*/', '', unc, flags=re.DOTALL).strip()
        if not unc:
            continue
        first_word = unc.split()[0].upper()
        if first_word not in ("SELECT", "WITH", "EXPLAIN"):
            raise ValueError(f"Security Alert: Only SELECT/WITH queries are permitted. Forbidden command: {first_word}")


    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(clean_query, params)
    
    columns = [col[0] for col in cursor.description] if cursor.description else []
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return columns, rows


def setup_and_seed_pipeline() -> None:
    """
    Orchestrates the entire database setup and seeding workflow.
    """
    print(f"[*] Step 1: Initializing SQLite database schema at: {DB_PATH}")
    initialize_database()
    print("    Created dim_customers, dim_products, fact_orders, and ecommerce_flat tables with indexes.")

    print(f"[*] Step 2: Seeding database from cleaned CSV: {CLEANED_DATA_PATH}")
    rows_inserted = seed_database()
    print(f"    Successfully seeded {rows_inserted} order records into relational tables.")

    print("[*] Step 3: Verifying predefined analytical SQL queries...")
    for key, q in PREDEFINED_QUERIES.items():
        cols, results = execute_query(q["sql"])
        print(f"    - {q['title']} -> Returned {len(results)} rows, {len(cols)} columns.")
    print("    [PASSED] All SQL analytical queries verified successfully.")


if __name__ == "__main__":
    setup_and_seed_pipeline()
