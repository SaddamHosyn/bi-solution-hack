import duckdb
import time

# Use the same path as transform.py
DB_PATH = "warehouse/warehouse.duckdb"

def get_db_connection():
    return duckdb.connect(DB_PATH)

def create_gold_sales_by_municipality(con):
    print("🥇 Creating Gold Table: Sales per Municipality per Year...")
    
    # 1. Aggregating sales by Year and Store's Municipality NAME (from Silver Stores)
    # 2. Joining with Population using Municipality NAME (from Dim Municipality)
    con.execute("""
        CREATE OR REPLACE TABLE gold_sales_by_municipality AS
        WITH sales_agg AS (
            SELECT 
                year(date::DATE) AS year,
                municipality_code, -- This is the 'MH', 'JO' code
                SUM(revenue) AS total_revenue
            FROM silver_grocery_sales
            GROUP BY 1, 2
        ),
        -- We need a distinct map of Code -> Name from the Stores table
        store_map AS (
            SELECT DISTINCT 
                municipality_code, 
                municipality_name 
            FROM bronze_stores
        )
        SELECT 
            s.year,
            map.municipality_name,
            s.total_revenue,
            p.population,
            ROUND(s.total_revenue / p.population, 2) AS revenue_per_capita
        FROM sales_agg s
        -- Join Sales Code (MH) to Name (Mariehamn) using Stores data
        JOIN store_map map 
            ON s.municipality_code = map.municipality_code
        -- Join Name (Mariehamn) to Population data
        JOIN silver_population p 
            ON map.municipality_name = p.municipality_name 
            AND s.year = p.year
        ORDER BY s.year DESC, revenue_per_capita DESC
    """)
    print("✅ Gold Sales/Municipality created.")


def create_gold_monthly_trends(con):
    print("🥇 Creating Gold Table: Monthly Sales Trends...")
    
    con.execute("""
        CREATE OR REPLACE TABLE gold_monthly_sales AS
        SELECT 
            strftime(date::DATE, '%Y-%m') AS month_year,
            product_category,
            SUM(revenue) AS total_revenue
        FROM silver_grocery_sales
        GROUP BY 1, 2
        ORDER BY 1 DESC
    """)
    print("✅ Gold Monthly Trends created.")

def main():
    con = get_db_connection()
    create_gold_sales_by_municipality(con)
    create_gold_monthly_trends(con)
    
    # Preview the data
    print("\n--- PREVIEW: Top Municipalities by Sales per Capita (2024) ---")
    print(con.execute("SELECT * FROM gold_sales_by_municipality WHERE year=2024 LIMIT 5").fetchdf())
    
    con.close()
    print("\n🚀 Gold Layer Complete! Ready for Dashboard.")

if __name__ == "__main__":
    main()
