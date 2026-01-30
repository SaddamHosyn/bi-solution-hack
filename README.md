# 🥦 Åland Grocery BI Solution (End-to-End Data Engineering)

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![DuckDB](https://img.shields.io/badge/DuckDB-Warehouse-yellow?style=for-the-badge&logo=duckdb)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

> **A full-stack BI solution processing 5+ million sales records to uncover per-capita consumption trends in Åland, Finland.**

---

## 🎯 The Challenge
A local grocery retail chain in Åland wanted to understand their market penetration. However, they faced a data silo problem:
- **Sales Data** was locked in daily JSON logs.
- **Demographics** were in an external government API (ÅSUB).
- **Tourism Data** was in messy CSV files.

**The Goal:** Build a unified data pipeline to answer the question: *"Which municipalities spend the most on groceries per capita, and how does tourism impact sales?"*

---

## 🏗️ Architecture: The Medallion Pattern

This project implements a robust **ELT (Extract, Load, Transform)** pipeline using DuckDB as the central warehouse.

```mermaid
graph LR
    A[Raw Data Sources] -->|Ingest| B[(Bronze Layer)]
    B -->|Clean & Join| C[(Silver Layer)]
    C -->|Aggregate| D[(Gold Layer)]
    D -->|Visualize| E[Streamlit Dashboard]
