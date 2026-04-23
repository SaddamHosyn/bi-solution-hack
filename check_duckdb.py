import duckdb
from pathlib import Path

project_root = Path(__file__).resolve().parent
con = duckdb.connect(str(project_root / "warehouse" / "warehouse.duckdb"))

print("Tables in warehouse.duckdb:")
tables = con.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
).fetchall()
for t in tables:
    count = con.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"   {t[0]}: {count:,} rows")

print("\nSample Population Data:")
print(con.execute("SELECT * FROM bronze_population LIMIT 5").df())

print("\nMunicipalities:")
print(con.execute("SELECT DISTINCT municipality_name FROM bronze_population").df())
