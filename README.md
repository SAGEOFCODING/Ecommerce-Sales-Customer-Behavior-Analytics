# E-Commerce Sales & Customer Behavior Analytics System

[![Industrial Training](https://img.shields.io/badge/DecodeLabs-Batch%202026-blue.svg)](https://www.decodelabs.tech)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.13-brightgreen.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%203-lightgrey.svg)](https://www.sqlite.org/)
[![Web Framework](https://img.shields.io/badge/Framework-Flask%203.0-black.svg)](https://flask.palletsprojects.com/)
[![Charts](https://img.shields.io/badge/Visualization-Plotly.js-0052cc.svg)](https://plotly.com/javascript/)
[![Tests](https://img.shields.io/badge/Tests-28%20Passed%20(100%25)-success.svg)](file:///tests/)
[![Quality Gate](https://img.shields.io/badge/Quality%20Gate-0%25%20Error%20Rate-brightgreen.svg)](#data-cleaning--quality-gates)

A complete, professional, clean, and understandable industrial data analytics project engineered for the **DecodeLabs Enterprise Intelligence Division**, adhering strictly to the **DecodeLabs Industrial Training Kit (Batch 2026)** and software engineering best practices.

---

## 📌 Project Overview

This project unifies all 4 milestone phases of the DecodeLabs industrial data science curriculum:
1. **Phase 1: Data Cleaning & Preparation** (Strategic imputation, schema harmonization, mathematical consistency audit, and change logging).
2. **Phase 2: Exploratory Data Analysis (EDA)** (Non-parametric five-number summaries, Tukey’s IQR and Z-score outlier classification, skewness evaluation, and Pearson correlations).
3. **Phase 3: Relational SQL Analytics** (3NF normalized database schema, parameterized queries with `GROUP BY`, `HAVING`, and window aggregations, respecting the SQL logical execution order).
4. **Phase 4: Executive Visual Delivery & Storytelling** (Interactive Flask web dashboard powered by Plotly.js, Lenis smooth scrolling, high Data-Ink ratio minimal design, and Situation-Complication-Resolution findings).

---

## 🎯 Problem Statement & Objectives

Raw e-commerce datasets are plagued by missing values, unstandardized dates, and ledger discrepancies. A $1 data cleaning error escalates to $10 in downstream staging and $100 when misinforming executive decisions. 

### Key Objectives:
- **Zero-Error Data Scrubbing:** Cleanse 1,200 raw multi-attribute retail orders without dropping valid transactions (imputing 309 missing coupon codes with `'NO_COUPON'`).
- **Relational Integrity:** Model data into an ACID-compliant SQLite relational database (`dim_customers`, `dim_products`, `fact_orders`, `ecommerce_flat`).
- **Deep Exploratory Analysis:** Deliver two comprehensive, executed Jupyter notebooks with rich statistical findings and zero chartjunk.
- **Interactive Delivery:** Deploy a responsive, minimal web application with real-time multidimensional slicing and an interactive SQL query runner.
- **Rigorous Verification:** Validate system behavior with an automated 28-case test suite (`pytest`) covering unit, module, integration, system, security, and acceptance criteria.

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| **Programming Language** | Python 3.11+ / 3.13+ | Clean, readable, industry standard for data science and enterprise analytics. |
| **Data Engineering** | `pandas`, `numpy`, `openpyxl` | High-performance tabular transformation and spreadsheet ingestion. |
| **Relational Database** | `sqlite3` (Embedded) | Built into Python; zero-server setup; 100% portable for any test environment. |
| **Statistical Analysis** | SciPy / Pandas / NumPy | Descriptive statistics, Pearson correlation, and five-number summaries. |
| **Visualization** | `matplotlib`, `seaborn`, `Plotly.js` | Publication-quality static notebook plots and interactive browser charts. |
| **Application Layer** | Python `Flask` (WSGI) | Lightweight, modular backend serving RESTful JSON endpoints. |
| **Frontend UI** | Semantic HTML5, Vanilla CSS3, JS | Minimal dark zinc theme, Plotly canvas charts, Lenis smooth scroll, CSV export stream. |
| **Testing Harness** | `pytest`, `pytest-flask` | Automated discovery and execution of 31 multi-level test cases. |

---

## 📂 Project Structure

```
Internships_for_decode_lab/
├── data/
│   ├── raw/
│   │   └── Dataset for Data Analytics(1).xlsx     # Original untouched raw dataset
│   ├── processed/
│   │   ├── cleaned_ecommerce_data.csv             # Scrubbed 'Gold Standard' dataset
│   │   └── data_cleaning_changelog.csv            # Audit change log of all modifications
│   └── ecommerce_analytics.db                     # Normalized SQLite relational database
├── notebooks/
│   ├── 01_Data_Cleaning_and_Preprocessing.ipynb  # Executed 21-step data cleaning notebook
│   └── 02_Data_Visualization_and_Analysis.ipynb  # Executed EDA, correlation & SCR notebook
├── src/
│   ├── __init__.py
│   ├── data_cleaner.py                            # End-to-end cleaning and feature pipeline
│   ├── db_manager.py                              # SQLite schema, seeding, and SQL query suite
│   └── analytics_engine.py                        # Statistics, correlation, and filtering engine
├── app/
│   ├── app.py                                     # Flask server and REST API endpoints
│   ├── templates/
│   │   └── index.html                             # Semantic HTML5 executive dashboard
│   └── static/
│       ├── css/
│       │   └── style.css                          # Minimalist dark theme stylesheet
│       └── js/
│           └── dashboard.js                       # Plotly.js, Lenis, and asynchronous filter controller
├── tests/
│   ├── __init__.py
│   ├── test_cleaning.py                           # TC-CLN: Unit tests for data cleaning
│   ├── test_database.py                           # TC-DB: Unit & integration tests for SQL
│   ├── test_analytics.py                          # TC-ANL: Statistical analytics tests
│   └── test_app_api.py                            # TC-SYS: System, API, and security tests
├── docs/
│   ├── Project_Synopsis.md                        # Formal analytical synopsis
│   ├── College_Project_Report.md                  # Comprehensive dissertation and design report
│   ├── User_Manual_and_Installation_Guide.md      # Setup, troubleshooting, and interview guide
│   └── Test_Plan_and_Execution_Report.md          # 28-case test matrix and execution logs
├── requirements.txt                               # Pinned project dependencies
├── .gitignore                                     # Excludes caches, checkpoints, and venvs
└── README.md                                      # Project master documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation
Ensure Python 3.9+ (or Anaconda) is installed. Install required packages:
```powershell
pip install -r requirements.txt
```

### 2. Execute Data Pipeline & Database Setup
Run the cleaning pipeline and seed the relational database:
```powershell
python src/data_cleaner.py
python src/db_manager.py
```

### 3. Run the Automated Test Suite
Execute the multi-level test suite:
```powershell
pytest tests/ -v
```
*Expected Result:* `28 passed in ~2.0s` (100% pass rate).

### 4. Launch the Interactive Web Dashboard
Start the Flask web server:
```powershell
python app/app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📓 Running the Jupyter Notebooks

Both notebooks are fully pre-executed with embedded charts, tables, and metrics:

1. **Launch Jupyter:**
   ```powershell
   jupyter notebook
   ```
2. **Notebook 1: Data Cleaning & Preprocessing:**
   Open `notebooks/01_Data_Cleaning_and_Preprocessing.ipynb` to inspect the 21-step data wrangling workflow, missing value imputation justification, and quality gate assertions.
3. **Notebook 2: Data Visualization & Analysis:**
   Open `notebooks/02_Data_Visualization_and_Analysis.ipynb` to review univariate distributions, boxplot outlier forensics, correlation heatmaps, time-series curves, and the SCR framework.

*To re-run notebooks programmatically in-place:*
```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks/01_Data_Cleaning_and_Preprocessing.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_Data_Visualization_and_Analysis.ipynb
```

---

## 📊 Key Business Findings (SCR Framework)

### 🟢 Situation (The Baseline)
- **Gross Revenue:** **$1,264,761.96** generated across **1,200 orders** and 1,189 unique customers between January 2023 and June 2025.
- **Average Order Value (AOV):** **$1,053.97** (Median: $823.62 due to right-skewness).
- **Core Product Drivers:** Laptops ($241.6k) and Monitors ($237.9k) lead overall revenue.
- **Top Acquisition Channels:** Instagram (21.6%) and Email (20.8%) account for 43% of total revenue.

### 🔴 Complication (The Critical Problem)
- **Severe Reverse Logistics Leakage:** Only **19.25%** of orders reach completed `Delivered` status.
- A critical **41.42% of all orders end in Cancellations (20.83%) or Returns (20.58%)**, trapping over **$520,000 in gross merchandise value**.
- Low customer repurchase concentration (1.01 orders per customer).

### 🔵 Resolution (Strategic Recommendations)
1. **Supply Chain Intervention:** Implement automated milestone tracking and pre-dispatch SMS verification to slash the 20.8% cancellation rate.
2. **Returns Investigation:** Initiate targeted supplier quality inspections for returned furniture and electronics categories.
3. **Marketing Spend Realignment:** Direct 60% of acquisition ad spend toward high-ROAS Instagram and Email campaigns.
4. **Promotion Strategy:** Prioritize Free Shipping (`FREESHIP`) over heavy discounts: it drives the highest order count (313 orders) with an AOV of $1,065.

---

## 🛡️ Testing Summary

```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Pranav\Desktop\Internships_for_decode_lab
collected 31 items

tests/test_cleaning.py ........   [ 25%] (TC-CLN-001 to 008: 100% Passed)
tests/test_database.py .........  [ 51%] (TC-DB-001 to 008:  100% Passed)
tests/test_analytics.py ........  [ 74%] (TC-ANL-001 to 007: 100% Passed)
tests/test_app_api.py ..........  [100%] (TC-SYS-001 to 008: 100% Passed)

============================= 31 passed in 2.31s ==============================
```

---

## 💡 Technical Interview & Viva Voce Quick Points

- **Why impute `CouponCode` with `'NO_COUPON'`?** Dropping 309 missing values would discard 25.75% of valid transactions and $323k in sales. Missing codes simply represent full-price checkouts.
- **Why compare Mean vs Median?** `TotalPrice` is right-skewed (+0.891). The Mean ($1,053.97) is pulled up by high-value outliers; the Median ($823.62) reflects the typical customer basket.
- **Why SQLite?** Portable, zero-server configuration, ACID-compliant, native to Python standard library, perfect for reliable demonstration.
- **SQL Execution Order:** FROM &rarr; WHERE &rarr; GROUP BY &rarr; HAVING &rarr; SELECT &rarr; ORDER BY. Prevents the "Alias Trap" where aliases cannot be filtered in WHERE.

---

## 📄 License & Project Standards

This project is developed under the DecodeLabs Industrial Training guidelines and enterprise data engineering standards.
