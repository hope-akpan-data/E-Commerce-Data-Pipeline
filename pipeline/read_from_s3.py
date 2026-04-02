import pandas as pd

bucket = "hope-data-ecommerce-pipeline-us-east-2-project"
key = "gold/products_aggregated.parquet"

s3_path = f"s3://{bucket}/{key}"

df = pd.read_parquet(s3_path)

print(df.head())