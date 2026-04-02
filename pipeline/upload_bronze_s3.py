import os
import boto3

# 👇 Get absolute path to pipeline folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 👇 Correct bronze directory
BRONZE_DIR = os.path.join(BASE_DIR, "../data/bronze")

# 👇 Get latest bronze file automatically
files = os.listdir(BRONZE_DIR)
latest_file = sorted(files)[-1]
BRONZE_FILE = os.path.join(BRONZE_DIR, latest_file)

BUCKET_NAME = "hope-data-ecommerce-pipeline-us-east-2-project"
S3_KEY = f"bronze/{latest_file}"

s3 = boto3.client("s3", region_name="us-east-2")

print(f"Uploading: {BRONZE_FILE}")

s3.upload_file(BRONZE_FILE, BUCKET_NAME, S3_KEY)

print(f"Uploaded to s3://{BUCKET_NAME}/{S3_KEY}")