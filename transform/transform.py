import duckdb
import time

DB_PATH = "warehouse/warehouse.duckdb"

def get_db_connection():
    return duckdb.connect(DB_PATH)

def create_silver_grocery(con):
    print("🥈 Creating Silver Grocery Sales (Joining Products & Stores)...")
    start = time.time()
    
    con.execute("""
        CREATE OR REPLACE TABLE silver_grocery_sales AS
        SELECT 
            s.date,
            s.store_id,
            st.store_name,
            st.municipality_code,
            s.product_id,
            p.product_name,
            p.product_category,  -- Updated from 'category' to 'product_category'
            s.sales_amount AS revenue
        FROM bronze_grocery_sales s
        LEFT JOIN bronze_products p ON s.product_id = p.product_id
        LEFT JOIN bronze_stores st ON s.store_id = st.store_id
    """)
    
    end = time.time()
    print(f"✅ Silver Grocery created in {end - start:.2f} seconds.")


def create_silver_population(con):
    print("🥈 Creating Silver Population (Joining Municipality Names)...")
    
    # Join population with municipality names to make it readable
    # We also filter out any potential aggregate rows if they exist (though we did some filtering in ingest)
    con.execute("""
        CREATE OR REPLACE TABLE silver_population AS
        SELECT 
            p.year,
            p.municipality_code,
            m.municipality_name,
            p.population
        FROM bronze_population p
        LEFT JOIN dim_municipality m ON p.municipality_code = m.municipality_code
    """)
    print("✅ Silver Population created.")

def data_quality_checks(con):
    print("🕵️ Running Data Quality Checks...")
    
    # Check 1: Do we have any null municipality names in population?
    null_muns = con.execute("SELECT COUNT(*) FROM silver_population WHERE municipality_name IS NULL").fetchone()[0]
    if null_muns > 0:
        print(f"⚠️ WARNING: Found {null_muns} rows in Population with unknown Municipality Codes!")
    else:
        print("   - Population municipalities look good.")

    # Check 2: Do we have any sales with unknown products?
    null_prods = con.execute("SELECT COUNT(*) FROM silver_grocery_sales WHERE product_name IS NULL").fetchone()[0]
    if null_prods > 0:
        print(f"⚠️ WARNING: Found {null_prods} sales with unknown Product IDs!")
    else:
        print("   - Grocery joins look good.")

def main():
    con = get_db_connection()
    create_silver_grocery(con)
    create_silver_population(con)
    data_quality_checks(con)
    con.close()
    print("🚀 Silver Transformation Complete!")

if __name__ == "__main__":
    main()
