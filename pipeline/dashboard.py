# pipeline/dashboard.py
import streamlit as st
import pandas as pd

# -----------------------------
# S3 settings
# -----------------------------
BUCKET = "hope-data-ecommerce-pipeline-us-east-2-project"
KEY = "gold/products_aggregated.parquet"

S3_PATH = f"s3://{BUCKET}/{KEY}"

# -----------------------------
# Load data
# -----------------------------
st.title("E-commerce Gold Data Dashboard")
st.write("Aggregated product metrics by category")

# Using s3fs with PyArrow engine
@st.cache_data
def load_data():
    df = pd.read_parquet(S3_PATH, engine="pyarrow")
    return df

df = load_data()
st.write("Preview of Gold data:")
st.dataframe(df)

# -----------------------------
# Metrics summary
# -----------------------------
st.subheader("Category Metrics")
st.write("Total products and average price per category")

# Bar chart: number of products per category
st.bar_chart(df.set_index("category")["total_products"])

# Line chart: average price per category
st.line_chart(df.set_index("category")["avg_price"])

# -----------------------------
# Optional: select a category
# -----------------------------
st.subheader("Explore by Category")
categories = df["category"].unique()
selected_cat = st.selectbox("Choose a category", categories)
filtered = df[df["category"] == selected_cat]
st.write(filtered)