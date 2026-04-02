import boto3
import os

GOLD_FILE = "../data/gold/products_aggregated.parquet"

BUCKET_NAME = "hope-data-ecommerce-pipeline-us-east-2-project"

# 👇 This is the key change
S3_KEY = "gold/products_aggregated.parquet"

s3 = boto3.client("s3", region_name="us-east-2")

s3.upload_file(GOLD_FILE, BUCKET_NAME, S3_KEY)

print(f"Uploaded to s3://{BUCKET_NAME}/{S3_KEY}")