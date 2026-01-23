import duckdb
import pandas as pd
import json
import glob
import os
import numpy as np

# CONFIG: Path to your DuckDB warehouse
DB_PATH = "warehouse/warehouse.duckdb"

# CONFIG: Paths to raw data
TOURISM_CSV = "data/tourism/tourism_data.csv"
GROCERY_DIR = "data/grocery"
POPULATION_JSON = "data/population/BE001.json"

def get_db_connection():
    """Connects to the local DuckDB warehouse."""
    return duckdb.connect(DB_PATH)

def load_tourism(con):
    """Loads the Tourism CSV into a Bronze table."""
    print("Loading Tourism Data...")
    try:
        query = f"""
            CREATE OR REPLACE TABLE bronze_tourism AS 
            SELECT * FROM read_csv_auto('{TOURISM_CSV}', header=True);
        """
        con.execute(query)
        print("✅ Bronze Tourism loaded.")
    except Exception as e:
        print(f"❌ Error loading Tourism: {e}")

def load_grocery_reference(con):
    """Loads Stores and Products JSONs."""
    print("Loading Grocery Reference Data...")
    try:
        # Stores
        with open(f"{GROCERY_DIR}/stores.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        df_stores = pd.json_normalize(data)
        con.execute("CREATE OR REPLACE TABLE bronze_stores AS SELECT * FROM df_stores")
        print("✅ Bronze Stores loaded.")
        
        # Products
        with open(f"{GROCERY_DIR}/products.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        df_products = pd.json_normalize(data)
        con.execute("CREATE OR REPLACE TABLE bronze_products AS SELECT * FROM df_products")
        print("✅ Bronze Products loaded.")
    except Exception as e:
        print(f"❌ Error loading Reference Data: {e}")

def load_grocery_sales(con):
    """Loops through all yearly sales JSON files and combines them."""
    print("Loading Grocery Sales...")
    files = glob.glob(f"{GROCERY_DIR}/grocery_sales_*.json")
    if not files:
        print("⚠️ No grocery sales files found!")
        return

    all_dfs = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_dfs.append(pd.json_normalize(data))
    
    if all_dfs:
        full_df = pd.concat(all_dfs, ignore_index=True)
        con.execute("CREATE OR REPLACE TABLE bronze_grocery_sales AS SELECT * FROM full_df")
        print(f"✅ Bronze Grocery Sales loaded ({len(full_df)} rows).")

def load_population_from_be001_json(con):
    """Parses the complex PX-Web JSON-stat format."""
    print("Loading Population Data (JSON)...")
    try:
        if not os.path.exists(POPULATION_JSON):
            print(f"⚠️ Population file not found at {POPULATION_JSON}")
            return

        with open(POPULATION_JSON, "r", encoding="utf-8") as f:
            j = json.load(f)

        ds = j["dataset"]
        dim = ds["dimension"]

        # 1. Extract indices for dimensions
        year_idx = dim["år"]["category"]["index"]
        age_idx = dim["ålder"]["category"]["index"]
        mun_idx = dim["kommun"]["category"]["index"]
        sex_idx = dim["kön"]["category"]["index"]

        # 2. Build ordered lists of codes
        years = [k for k, _ in sorted(year_idx.items(), key=lambda kv: kv[1])]
        muns  = [k for k, _ in sorted(mun_idx.items(),  key=lambda kv: kv[1])]

        # 3. Reshape the flat value list into a 4D array
        sizes = dim["size"]  # [year, age, municipality, sex]
        arr = np.array(ds["value"], dtype="float64").reshape(sizes)

        # 4. Filter: Age='SSS' (Total), Sex='0' (Both sexes)
        # Note: We access by the integer index we found in step 1
        arr_tot = arr[:, age_idx["SSS"], :, sex_idx["0"]]  # shape: (years, municipalities)

        # 5. Convert to DataFrame (Year x Municipality)
        df = (
            pd.DataFrame(arr_tot, index=years, columns=muns)
              .reset_index(names="year")
              .melt(id_vars=["year"], var_name="municipality_code", value_name="population")
        )
        df["year"] = df["year"].astype(int)

        # 6. Create Dimension Table (Code -> Name)
        mun_label = dim["kommun"]["category"]["label"]
        dim_mun = pd.DataFrame(
            [{"municipality_code": code, "municipality_name": mun_label[code]} for code in muns]
        )

        # 7. Save to DuckDB
        con.register("pop_df", df)
        con.execute("CREATE OR REPLACE TABLE bronze_population AS SELECT * FROM pop_df")
        
        con.register("mun_df", dim_mun)
        con.execute("CREATE OR REPLACE TABLE dim_municipality AS SELECT * FROM mun_df")
        
        print("✅ Bronze Population & Municipality Dim loaded.")

    except Exception as e:
        print(f"❌ Error loading Population JSON: {e}")

def main():
    con = get_db_connection()
    
    load_tourism(con)
    load_grocery_reference(con)
    load_grocery_sales(con)
    load_population_from_be001_json(con)  # <--- Now calling the correct function
    
    con.close()
    print("🚀 Ingestion Complete! Data is in warehouse.duckdb")

if __name__ == "__main__":
    main()
