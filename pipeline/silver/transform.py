import duckdb
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE_DIR = PROJECT_ROOT / "warehouse"
DB_PATH = WAREHOUSE_DIR / "warehouse.duckdb"


def get_db_connection():
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def create_silver_grocery(con):
    print("🥈 Creating Silver Grocery Sales (Joining Products & Stores)...")
    start = time.time()

    con.execute(
        """
        CREATE OR REPLACE TABLE silver_grocery_sales AS
        SELECT 
            s.store_id,
            st.store_name,
            st.municipality_name AS municipality,
            s.product_id,
            p.product_name,
            p.product_category AS category,
            p.unit_price,
            s.units_sold AS quantity,
            CAST(s.date AS DATE) AS transaction_date,
            YEAR(CAST(s.date AS DATE)) AS year,
            MONTH(CAST(s.date AS DATE)) AS month,
            s.sales_amount AS total_amount
        FROM bronze_grocery_sales s
        LEFT JOIN bronze_products p ON s.product_id = p.product_id
        LEFT JOIN bronze_stores st ON s.store_id = st.store_id
    """
    )

    count = con.execute("SELECT COUNT(*) FROM silver_grocery_sales").fetchone()[0]
    end = time.time()
    print(f"✅ Silver Grocery Sales: {count:,} rows (in {end - start:.2f}s)")


def create_silver_population(con):
    print("🥈 Creating Silver Population (from API data)...")
    start = time.time()

    # Filter to only 'Total' age (not individual age breakdowns)
    # Keep all sex categories for flexibility
    con.execute(
        """
        CREATE OR REPLACE TABLE silver_population AS
        SELECT 
            CAST(year AS INTEGER) AS year,
            municipality_name,
            sex,
            population
        FROM bronze_population
        WHERE age = 'Total'
    """
    )

    count = con.execute("SELECT COUNT(*) FROM silver_population").fetchone()[0]
    end = time.time()
    print(f"✅ Silver Population: {count:,} rows (in {end - start:.2f}s)")


def create_silver_population_total(con):
    print("🥈 Creating Silver Population Total (for Per-Capita calculations)...")
    start = time.time()

    # Only 'Both sexes' = total population per municipality per year
    con.execute(
        """
        CREATE OR REPLACE TABLE silver_population_total AS
        SELECT 
            year,
            municipality_name,
            population
        FROM silver_population
        WHERE sex = 'Both sexes'
    """
    )

    count = con.execute("SELECT COUNT(*) FROM silver_population_total").fetchone()[0]
    end = time.time()
    print(f"✅ Silver Population Total: {count:,} rows (in {end - start:.2f}s)")


def create_silver_tourism(con):
    print("🥈 Creating Silver Tourism...")
    start = time.time()

    con.execute(
        """
        CREATE OR REPLACE TABLE silver_tourism AS
        SELECT 
            year,
            month,
            date,
            municipality_code,
            municipality_name,
            accommodation_type,
            origin_country,
            visitor_count,
            revenue
        FROM bronze_tourism
        WHERE visitor_count IS NOT NULL
    """
    )

    count = con.execute("SELECT COUNT(*) FROM silver_tourism").fetchone()[0]
    end = time.time()
    print(f"✅ Silver Tourism: {count:,} rows (in {end - start:.2f}s)")


def data_quality_checks(con):
    print("🕵️ Running Data Quality Checks...")

    # Check 1: Null product names in sales
    null_prods = con.execute(
        "SELECT COUNT(*) FROM silver_grocery_sales WHERE product_name IS NULL"
    ).fetchone()[0]
    if null_prods > 0:
        raise Exception(
            f"Pipeline failed: {null_prods} sales have unknown Product IDs."
        )
    else:
        print("   ✓ Grocery product joins look good.")

    # Check 2: Null municipality in sales
    null_mun = con.execute(
        "SELECT COUNT(*) FROM silver_grocery_sales WHERE municipality IS NULL"
    ).fetchone()[0]
    if null_mun > 0:
        print(f"   ⚠️ WARNING: {null_mun} sales with unknown Municipality!")
    else:
        print("   ✓ Grocery municipality joins look good.")

    # Check 3: Population data coverage
    pop_years = con.execute(
        "SELECT MIN(year), MAX(year) FROM silver_population_total"
    ).fetchone()
    print(f"   ✓ Population data covers years: {pop_years[0]} - {pop_years[1]}")

    # Check 4: Municipalities in population vs sales
    pop_muns = con.execute(
        "SELECT COUNT(DISTINCT municipality_name) FROM silver_population_total"
    ).fetchone()[0]
    sales_muns = con.execute(
        "SELECT COUNT(DISTINCT municipality) FROM silver_grocery_sales"
    ).fetchone()[0]
    print(f"   ✓ Municipalities - Population: {pop_muns}, Sales: {sales_muns}")

    # Check 5: Tourism data coverage
    tourism_years = con.execute(
        "SELECT MIN(year), MAX(year) FROM silver_tourism"
    ).fetchone()
    print(f"   ✓ Tourism data covers years: {tourism_years[0]} - {tourism_years[1]}")


def main():
    con = get_db_connection()

    create_silver_grocery(con)
    create_silver_population(con)
    create_silver_population_total(con)
    create_silver_tourism(con)
    data_quality_checks(con)

    con.close()
    print("🚀 Silver Transformation Complete!")


if __name__ == "__main__":
    main()
