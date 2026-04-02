# E-Commerce Data Pipeline
### End-to-End ETL Pipeline | Python · AWS S3 · Parquet · Streamlit

---

## What This Project Does

This pipeline pulls product data from an external API, processes it through a 3-hop architecture (Bronze → Silver → Gold), stores each stage in AWS S3, and surfaces the final output in a live Streamlit dashboard.

The end result: clean, aggregated product metrics, queryable, visualized, and cloud-hosted, with no manual steps after the initial run.

---

## The Problem It Solves

E-commerce data arrives messy. Nested structures, inconsistent categories, missing fields, no standard format. Analysts can't build reports from raw API responses. They need clean, structured data with consistent types and clear aggregations.

---

## Architecture

```
API (dummyjson.com)
        │
        ▼
  Bronze Layer ──────────────► S3: /bronze/
  (Raw JSON, timestamped)
        │
        ▼
  Silver Layer ──────────────► S3: /silver/
  (Cleaned Parquet: nulls removed,
   types standardized, columns renamed)
        │
        ▼
  Gold Layer ─────────────────► S3: /gold/
  (Aggregated metrics:
   total products + avg price per category)
        │
        ▼
  Streamlit Dashboard
  (Reads directly from S3 Gold layer)
```

**Why 3-hop architecture:**
Each layer has a single responsibility. Bronze preserves the raw source. Silver applies cleaning logic. Gold applies business logic. If something breaks at any stage, you know exactly where to look — and the upstream data is always intact.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Pipeline orchestration and transformation logic |
| Pandas | Data cleaning, type handling, aggregation |
| boto3 | AWS S3 upload and interaction |
| s3fs + pyarrow | Reading Parquet files directly from S3 |
| Streamlit | Interactive dashboard layer |
| AWS S3 | Cloud storage for all three pipeline layers |

---

## Project Structure

```
ecommerce-pipeline/
│
├── data/
│   ├── bronze/          # Raw JSON files (timestamped)
│   ├── silver/          # Cleaned Parquet files
│   └── gold/            # Aggregated Parquet files
│
├── pipeline/
│   ├── ingest.py        # Bronze: API pull and raw storage
│   ├── transform.py     # Silver: cleaning and Parquet conversion
│   ├── aggregate.py     # Gold: category-level aggregation
│   ├── upload_bronze_s3.py
│   ├── upload_silver_s3.py
│   ├── upload_gold_s3.py
│   ├── read_from_s3.py  # Validates S3 read before dashboard
│   └── dashboard.py     # Streamlit dashboard
│
└── README.md
```

---

## Pipeline Walkthrough

### Bronze — Ingestion

`ingest.py` calls the dummyjson products API, extracts the `products` array from the response, and writes the raw JSON to `/data/bronze/` with a timestamp in the filename.

```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = os.path.join(BRONZE_DIR, f"products_raw_{timestamp}.json")
```

Timestamping serves two purposes: it creates a natural audit trail, and it makes the latest-file selection in downstream scripts straightforward.

All file paths use `os.path.abspath(__file__)` to resolve from the script's location rather than the execution directory. This prevents the common path bug where scripts run successfully but write files nowhere you can find them.

---

### Silver — Cleaning

`transform.py` reads the latest Bronze file, applies cleaning logic, and writes Parquet to `/data/silver/`.

Cleaning steps:
- Drop rows missing `title`, `category`, or `price` — these are non-negotiable fields for any downstream analysis
- Fill missing descriptions with a placeholder rather than dropping records
- Strip and lowercase category strings to prevent grouping failures from whitespace or casing inconsistencies
- Cast price to float explicitly
- Rename columns to match a consistent internal schema (`id` → `product_id`, `title` → `product_name`)

Why Parquet over CSV at this stage: columnar storage reads faster when downstream queries only touch a subset of columns. Parquet also enforces schema types on write, which catches type mismatches before they hit the Gold layer.

---

### Gold — Aggregation

`aggregate.py` reads the Silver Parquet file and produces two aggregations joined on category:

- `total_products`: count of distinct products per category
- `avg_price`: mean price per category

Output is a single Parquet file written to `/data/gold/products_aggregated.parquet`.

This is the layer the dashboard reads from. The separation means the dashboard logic stays simple — it doesn't need to know anything about cleaning or transformation, only how to read a clean aggregated file.

---

### S3 Upload

Three separate upload scripts handle Bronze, Silver, and Gold independently. Each reads the latest file from its local directory and uploads to the corresponding S3 prefix.

```
s3://hope-data-ecommerce-pipeline-us-east-2-project/bronze/
s3://hope-data-ecommerce-pipeline-us-east-2-project/silver/
s3://hope-data-ecommerce-pipeline-us-east-2-project/gold/
```

Keeping upload logic separate from transformation logic means you can re-run uploads without re-running transformations, and vice versa.

---

### Dashboard

`dashboard.py` reads the Gold Parquet file directly from S3 using `pandas.read_parquet()` with `s3fs` as the filesystem backend. No local copy needed.

The dashboard shows:
- Full aggregated data table
- Bar chart: total products per category
- Line chart: average price per category
- Category filter: drill into a single category's metrics

```python
@st.cache_data
def load_data():
    df = pd.read_parquet(S3_PATH, engine="pyarrow")
    return df
```

`@st.cache_data` prevents repeated S3 reads on every interaction — the data loads once per session.

---

## Errors I Hit and How I Fixed Them

Real debugging log. These aren't edge cases — they're the kind of issues that show up in any pipeline build.

**Path resolution errors**
Scripts were running without errors but files weren't appearing where expected. Root cause: relative paths like `../data/bronze` resolve from the execution directory, not the script location. Fixed by switching to `os.path.abspath(__file__)` throughout.

**Column name mismatch between Silver and Gold**
Silver renamed `id` to `product_id`. Gold aggregation was still referencing `id`. The script ran but produced incorrect output silently. Fixed by aligning column references after the rename step.

**NoSuchBucket on S3 upload**
Tried to upload before the bucket existed. S3 buckets don't get created on first write — they need to exist first. Created the bucket manually in the AWS console before running upload scripts.

**Response checksums mismatch on S3 read**
Pandas couldn't read Parquet from S3 without `s3fs` installed. The error message points at checksums but the actual fix is the missing filesystem library. Resolved with `pip install s3fs`.

---

## How to Run It

**Prerequisites**
- Python 3.8+
- AWS credentials configured (`aws configure` or environment variables)
- S3 bucket created in your target region

**Install dependencies**
```bash
pip install requests pandas pyarrow boto3 s3fs streamlit
```

**Run the pipeline in order**
```bash
python pipeline/ingest.py
python pipeline/transform.py
python pipeline/aggregate.py
python pipeline/upload_bronze_s3.py
python pipeline/upload_silver_s3.py
python pipeline/upload_gold_s3.py
```

**Launch the dashboard**
```bash
streamlit run pipeline/dashboard.py
```


## Related Project

[YouTube Data Engineering Pipeline (AWS)](https://github.com/hope-akpan-data/youtube-data-engineering-pipeline) — Serverless pipeline using S3, Lambda, Glue, and Athena to transform raw YouTube trending data into queryable Parquet datasets. Covers IAM setup, event-driven Lambda triggers, Glue crawlers, and Athena SQL querying.
