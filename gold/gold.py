import duckdb


def run_gold_layer():
    con = duckdb.connect('warehouse/warehouse.duckdb')

    # ========================================
    # GOLD: Monthly Sales Summary
    # ========================================
    print("🏆 Creating Gold Monthly Sales...")
    con.execute("""
        CREATE OR REPLACE TABLE gold_monthly_sales AS
        SELECT 
            year,
            month,
            municipality,
            category,
            COUNT(*) AS total_transactions,
            SUM(quantity) AS total_quantity,
            SUM(total_amount) AS total_revenue
        FROM silver_grocery_sales
        GROUP BY year, month, municipality, category
        ORDER BY year, month, municipality, category
    """)
    count = con.execute("SELECT COUNT(*) FROM gold_monthly_sales").fetchone()[0]
    print(f"✅ Gold Monthly Sales: {count:,} rows")

    # ========================================
    # GOLD: Yearly Sales by Municipality (with Per Capita)
    # ========================================
    print("🏆 Creating Gold Sales by Municipality (with Per Capita)...")
    con.execute("""
        CREATE OR REPLACE TABLE gold_sales_by_municipality AS
        SELECT 
            s.year,
            s.municipality,
            s.total_transactions,
            s.total_quantity,
            s.total_revenue,
            p.population,
            ROUND(s.total_revenue / NULLIF(p.population, 0), 2) AS revenue_per_capita,
            ROUND(CAST(s.total_transactions AS DOUBLE) / NULLIF(p.population, 0), 4) AS transactions_per_capita
        FROM (
            SELECT 
                year,
                municipality,
                COUNT(*) AS total_transactions,
                SUM(quantity) AS total_quantity,
                SUM(total_amount) AS total_revenue
            FROM silver_grocery_sales
            GROUP BY year, municipality
        ) s
        LEFT JOIN silver_population_total p 
            ON s.year = p.year 
            AND s.municipality = p.municipality_name
        ORDER BY s.year, s.municipality
    """)
    count = con.execute("SELECT COUNT(*) FROM gold_sales_by_municipality").fetchone()[0]
    print(f"✅ Gold Sales by Municipality: {count:,} rows")

    # ========================================
    # GOLD: Yearly Category Performance
    # ========================================
    print("🏆 Creating Gold Category Performance...")
    con.execute("""
        CREATE OR REPLACE TABLE gold_category_performance AS
        SELECT 
            year,
            category,
            SUM(total_amount) AS total_revenue,
            SUM(quantity) AS total_quantity,
            COUNT(*) AS total_transactions,
            ROUND(AVG(total_amount), 2) AS avg_transaction_value
        FROM silver_grocery_sales
        GROUP BY year, category
        ORDER BY year, total_revenue DESC
    """)
    count = con.execute("SELECT COUNT(*) FROM gold_category_performance").fetchone()[0]
    print(f"✅ Gold Category Performance: {count:,} rows")

    # ========================================
    # GOLD: Tourism + Sales Correlation Data
    # ========================================
    print("🏆 Creating Gold Tourism Sales Correlation...")
    con.execute("""
        CREATE OR REPLACE TABLE gold_tourism_sales AS
        SELECT 
            s.year,
            s.month,
            s.total_revenue,
            s.total_transactions,
            t.total_visitors,
            t.total_tourism_revenue,
            ROUND(s.total_revenue / NULLIF(t.total_visitors, 0), 2) AS grocery_revenue_per_tourist
        FROM (
            SELECT 
                year, 
                month, 
                SUM(total_amount) AS total_revenue,
                COUNT(*) AS total_transactions
            FROM silver_grocery_sales
            GROUP BY year, month
        ) s
        LEFT JOIN (
            SELECT 
                year, 
                month, 
                SUM(visitor_count) AS total_visitors,
                SUM(revenue) AS total_tourism_revenue
            FROM silver_tourism
            GROUP BY year, month
        ) t ON s.year = t.year AND s.month = t.month
        ORDER BY s.year, s.month
    """)
    count = con.execute("SELECT COUNT(*) FROM gold_tourism_sales").fetchone()[0]
    print(f"✅ Gold Tourism Sales: {count:,} rows")

    con.close()
    print("🚀 Gold Layer Complete!")


if __name__ == "__main__":
    run_gold_layer()
