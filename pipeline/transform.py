import pandas as pd
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRONZE_DIR = os.path.join(BASE_DIR, "../data/bronze")
SILVER_DIR = os.path.join(BASE_DIR, "../data/silver")
os.makedirs(SILVER_DIR, exist_ok=True)

# Load latest raw file
files = os.listdir(BRONZE_DIR)
latest_file = sorted(files)[-1]
file_path = os.path.join(BRONZE_DIR, latest_file)
logging.info(f"Reading file: {file_path}")

with open(file_path, "r") as f:
    raw = json.load(f)

# Check if data is list or dict
data = raw.get("products") if isinstance(raw, dict) else raw

# Convert to DataFrame
df = pd.DataFrame(data)

# Cleaning
df = df.dropna(subset=["title", "category", "price"])
df["description"] = df.get("description", "").fillna("No description available")
df["category"] = df["category"].str.strip().str.lower()
df["price"] = df["price"].astype(float)

# Rename columns
df = df.rename(columns={
    "id": "product_id",
    "title": "product_name",
    "description": "product_description"
})

# Save cleaned data
output_path = os.path.join(SILVER_DIR, "products_clean.parquet")
df.to_parquet(output_path, index=False)
logging.info(f"Saved cleaned data to {output_path}")