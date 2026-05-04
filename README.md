# 🥦 Åland Grocery BI Solution

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![DuckDB](https://img.shields.io/badge/DuckDB-Warehouse-yellow?style=for-the-badge&logo=duckdb)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![dbt](https://img.shields.io/badge/dbt-Transforms-orange?style=for-the-badge&logo=dbt)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

> **A full-stack BI solution processing 5+ million sales records to uncover per-capita consumption trends across all 12 municipalities of Åland, Finland.**

---

## 🎯 The Challenge

A local grocery retail chain in Åland needed to understand their market penetration across the archipelago. They faced a classic data silo problem:

| Data Source | Format | Problem |
|---|---|---|
| Sales Transactions | Daily JSON logs | Unstructured, high-volume |
| Demographics | ÅSUB Government API | External, inconsistent schema |
| Tourism Data | CSV files | Messy, no join keys |

**The Goal:** Build a unified ELT pipeline to answer: *"Which municipalities spend the most on groceries per capita, and how does tourism affect seasonal sales patterns?"*

---

## 📊 Live Dashboard Preview

The finished dashboard delivers interactive BI across three views: KPI overview, revenue trends, and product & seasonal analysis — all filterable by year and municipality.

**Key metrics surfaced (2025):**
- 💶 **€101M+** total revenue across 12 municipalities
- 🧾 **204,579** transactions processed
- 👥 **28,938** residents tracked across population data
- 🏆 **Kökar** identified as top per-capita spender

---

## 🏗️ Architecture: Medallion ELT Pattern

```
Raw Data Sources
      │
      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌──────────────────┐
│  🥉 BRONZE  │ ───▶ │  🥈 SILVER  │ ───▶ │  🥇 GOLD   │ ───▶ │  📊 STREAMLIT    │
│   Ingest    │      │  Clean &    │      │  Business   │      │   Dashboard      │
│  Raw Files  │      │  Transform  │      │  Aggregates │      │  app/dashboard   │
└─────────────┘      └─────────────┘      └─────────────┘      └──────────────────┘
        │                   │                    │
   JSON / CSV           DuckDB SQL           Gold Tables
   ÅSUB API           dbt Models           per-capita KPIs
```

All layers persist inside a single **DuckDB warehouse** at `warehouse/warehouse.duckdb`.

---

## 📁 Project Structure

```
.
├── app/
│   ├── dashboard.py          # Streamlit entry point
│   └── pages/                # Multi-page views (Municipality Deep Dive, etc.)
├── pipeline/
│   ├── bronze/
│   │   └── ingest.py         # Raw data ingestion
│   ├── silver/
│   │   └── transform.py      # Cleaning & joins
│   └── gold/
│       └── analytics.py      # Business aggregations
├── dbt_project/
│   └── my_pipeline/          # dbt models for advanced transforms
├── data/
│   ├── grocery/              # Raw sales JSON logs
│   └── tourism/              # Raw tourism CSVs
├── warehouse/
│   └── warehouse.duckdb      # Central DuckDB warehouse
├── requirements.txt
├── makefile
└── README.md
```

---

## ⚙️ Pipeline Layers

### 🥉 Bronze — Raw Ingestion
Reads all raw sources (JSON sales logs, tourism CSVs, ÅSUB API) and loads them as-is into DuckDB bronze tables. No transformations — full fidelity of source data preserved.

```bash
make bronze
```

### 🥈 Silver — Clean & Transform
Applies schema normalization, null handling, type casting, and cross-source joins (sales ↔ demographics ↔ tourism). Produces clean, analytics-ready tables.

```bash
make silver
```

### 🥇 Gold — Business Aggregates
Computes final business metrics: revenue by municipality, per-capita spend, monthly seasonality, product category breakdowns, and YoY growth rates.

```bash
make gold
```

---

## 🚀 Quickstart

### 1. Clone & Set Up Environment

```bash
git clone <repo-url>
cd bi-solution-Course-Project

# Create a fresh virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS / Linux)
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Full Pipeline

```bash
# Run all three layers end-to-end
make pipeline
```

Or run each layer individually:

```bash
make bronze   # Ingest raw data
make silver   # Clean & transform
make gold     # Build aggregates
```

### 4. Launch the Dashboard

```bash
make dashboard
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🛠️ Makefile Commands

| Command | Description |
|---|---|
| `make bronze` | Ingest raw data into the Bronze layer |
| `make silver` | Clean and transform into the Silver layer (depends on bronze) |
| `make gold` | Build business aggregates into the Gold layer (depends on silver) |
| `make pipeline` | Run the full end-to-end pipeline (bronze → silver → gold) |
| `make dashboard` | Launch the Streamlit dashboard |
| `make clean` | Delete the DuckDB warehouse file |
| `make help` | List all available commands |

---

## 📈 Dashboard Features

### 🏠 Main Dashboard
- **KPI Cards** — Total Revenue, Transactions, Population, Top Spender (with YoY % change)
- **Revenue Growth Trajectory** — Line chart from 2000–2025 with linear forecast overlay
- **Revenue vs Population Scatter** — Bubble chart correlating municipality size with spend

### 🔍 Municipality Deep Dive
- Multi-select region filter (all 12 Åland municipalities)
- Year selector for historical comparisons
- Per-capita revenue rankings

### 🍊 Product & Seasonal Analysis
- **Donut chart** — Sales breakdown by category (produce, dairy, beverages, bakery, meat, canned, frozen)
- **Monthly Seasonality Bar Chart** — Revenue heatmap across Jan–Dec

---

## 🗃️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Warehouse | DuckDB | Embedded OLAP engine, all layers |
| Transforms | Python + SQL | Bronze → Silver → Gold ELT |
| Advanced Models | dbt | Modular, testable SQL transforms |
| Visualization | Streamlit | Interactive BI dashboard |
| Orchestration | GNU Make | Dependency-ordered pipeline runner |
| Data Sources | JSON, CSV, REST API | Sales, tourism, ÅSUB demographics |

---

## 🧹 Maintenance

Reset the warehouse and re-run the full pipeline from scratch:

```bash
make clean
make pipeline
```

> ⚠️ `make clean` permanently deletes `warehouse/warehouse.duckdb`. All data is re-derived from the raw sources in `data/`.

---

## 📋 Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt` (DuckDB, Streamlit, Pandas, dbt-duckdb)
- GNU Make (Windows: install via [Chocolatey](https://chocolatey.org/) — `choco install make`)

---

## 🎓 Context

Built as a capstone project for the **BI Solutions DE Crash Course 2026**, demonstrating end-to-end data engineering competency: from raw source ingestion through warehouse modelling to interactive business intelligence delivery.

---

*Åland Fresh Market BI — Grocery Sales & Demographics Insights*
