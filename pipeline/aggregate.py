# pipeline/aggregate.py

import pandas as pd
import os

# 1️⃣ Define Silver and Gold directories
SILVER_DIR = "../data/silver"
GOLD_DIR = "../data/gold"
os.makedirs(GOLD_DIR, exist_ok=True)  # create Gold folder if it doesn't exist

# 2️⃣ Find the Silver file (latest cleaned data)
files = os.listdir(SILVER_DIR)
latest_file = sorted(files)[-1]  # pick newest file based on timestamp
silver_path = os.path.join(SILVER_DIR, latest_file)

print(f"Reading file: {silver_path}")

# 3️⃣ Load Silver data
df = pd.read_parquet(silver_path)

# 4️⃣ Inspect columns (always good to check)
print("Columns in Silver data:", df.columns)

# 5️⃣ Aggregate metrics (Gold layer)
# Example 1: Count of products per category
category_counts = df.groupby("category")["id"].count().reset_index()
category_counts = category_counts.rename(columns={"id": "total_products"})

# Example 2: Average price per category
avg_price = df.groupby("category")["price"].mean().reset_index()
avg_price = avg_price.rename(columns={"price": "avg_price"})

# 6️⃣ Merge aggregated metrics
gold_df = pd.merge(category_counts, avg_price, on="category")

# 7️⃣ Save Gold data
gold_path = os.path.join(GOLD_DIR, "products_aggregated.parquet")
gold_df.to_parquet(gold_path, index=False)

print(f"Saved aggregated data to {gold_path}")
print("Preview of Gold data:")
print(gold_df.head())