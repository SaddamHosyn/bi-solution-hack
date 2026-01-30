# ============================================
# 🥦 Åland Grocery BI - Medallion Pipeline
# ============================================

.PHONY: install bronze silver gold pipeline dashboard clean help

# Variables
PYTHON = python
STREAMLIT = streamlit
WAREHOUSE = warehouse/warehouse.duckdb

# --------------------------------------------
# 1. BRONZE LAYER (Ingest Raw Data)
# --------------------------------------------
bronze:
	@echo "🥉 Running BRONZE Layer (Ingest)..."
	$(PYTHON) pipeline/bronze/ingest.py
	@echo "✅ Bronze Complete."

# --------------------------------------------
# 2. SILVER LAYER (Clean & Transform)
# --------------------------------------------
silver: bronze
	@echo "🥈 Running SILVER Layer (Transform)..."
	$(PYTHON) pipeline/silver/transform.py
	@echo "✅ Silver Complete."

# --------------------------------------------
# 3. GOLD LAYER (Business Aggregates)
# --------------------------------------------
gold: silver
	@echo "🥇 Running GOLD Layer (Analytics)..."
	$(PYTHON) pipeline/gold/analytics.py
	@echo "✅ Gold Complete."

# --------------------------------------------
# FULL PIPELINE
# --------------------------------------------
pipeline: gold
	@echo "🎉 ETL Pipeline Finished Successfully!"

# --------------------------------------------
# DASHBOARD
# --------------------------------------------
dashboard:
	@echo "🚀 Launching App..."
	$(STREAMLIT) run app/dashboard.py

# --------------------------------------------
# UTILS
# --------------------------------------------
clean:
	rm -f $(WAREHOUSE)
	@echo "🧹 Warehouse cleaned."

help:
	@echo "Commands: make bronze, make silver, make gold, make pipeline, make dashboard"
