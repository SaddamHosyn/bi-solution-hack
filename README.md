
# 🛒 Åland Grocery BI Solution (End-to-End Data Engineering Project)

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![DuckDB](https://img.shields.io/badge/DuckDB-Warehouse-yellow?style=for-the-badge&logo=duckdb)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)

A full-stack data engineering pipeline that ingests, transforms, and visualizes 5+ million sales records for a grocery retail chain in Åland, Finland. The solution integrates disparate data sources (JSON sales logs, CSV tourism data, and Population statistics API) to calculate advanced business metrics like **Sales Per Capita**.

---

## 🏗️ Architecture

The project follows a **Medallion Architecture** (Bronze → Silver → Gold) using a modern ELT approach:

| Layer | Description | Tech Stack |
| :--- | :--- | :--- |
| **Ingest (Bronze)** | Raw data loading from CSV, JSON, and JSON-stat (API). | `Python`, `Pandas` |
| **Warehouse** | Embedded OLAP database for high-performance analytics. | `DuckDB` |
| **Transform (Silver)** | Cleaning, Joining (Star Schema), and Quality Checks. | `DuckDB SQL` |
| **Analytics (Gold)** | Aggregating metrics (Revenue per Capita, Monthly Trends). | `DuckDB SQL` |
| **Visualize** | Interactive BI Dashboard for business stakeholders. | `Streamlit`, `Plotly` |

---

## 🚀 Key Features

*   **Multi-Format Ingestion**: Handles messy real-world data including nested JSON, CSVs, and statistical API formats (PX-Web).
*   **Data Modeling**: Builds a **Star Schema** linking Fact Tables (Sales) to Dimensions (Products, Stores, Municipalities).
*   **Smart Matching**: Implements fuzzy joining logic to bridge internal store codes (e.g., `MH`) with official government municipality names (e.g., `Mariehamn`).
*   **Performance**: Processes **5.3 Million rows** of sales data in seconds using DuckDB's vectorized engine.
*   **Quality Assurance**: Automated data quality checks verify foreign key integrity and missing values during transformation.

---

## 📂 Project Structure

```text
.
├── ingest/             # Extract & Load scripts (Bronze Layer)
│   └── ingest.py       # Loads raw JSON/CSV into DuckDB
├── transform/          # Transformation scripts (Silver Layer)
│   └── transform.py    # Joins tables & performs cleaning
├── gold/               # Aggregation scripts (Gold Layer)
│   └── gold.py         # Calculates business KPIs (Revenue per Capita)
├── app/                # Frontend application
│   └── dashboard.py    # Streamlit dashboard code
├── warehouse/          # Local DuckDB database storage
└── data/               # Raw data files (Git ignored)
```

## 💻 How to Run

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Pipeline (ETL)**
    Execute the layers sequentially to build the warehouse:
    ```bash
    python ingest/ingest.py       # Load Raw Data
    python transform/transform.py # Clean & Join
    python gold/gold.py           # Aggregate KPIs
    ```

3.  **Launch the Dashboard**
    ```bash
    streamlit run app/dashboard.py
    ```

---

## 📊 Dashboard Preview

The dashboard provides interactive insights into:
*   **Total Revenue & Population Metrics**
*   **Geographic Performance:** A bubble chart correlating population size with revenue.
*   **Top Municipalities:** Ranking regions by "Sales Per Capita" to identify high-performance zones (e.g., Kökar).
*   **Seasonal Trends:** Line charts showing product category performance over time.

---

## 🛠️ Technology Stack
*   **Language:** Python
*   **Database:** DuckDB (OLAP)
*   **Visualization:** Streamlit, Plotly Express
*   **Data Processing:** Pandas, NumPy

