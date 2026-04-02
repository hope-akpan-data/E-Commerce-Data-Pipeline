import os
import boto3

# 1️⃣ Get absolute path to this script (pipeline/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2️⃣ Point to Silver directory
SILVER_DIR = os.path.join(BASE_DIR, "../data/silver")

# 3️⃣ Get latest Silver file automatically
files = os.listdir(SILVER_DIR)
latest_file = sorted(files)[-1]
SILVER_FILE = os.path.join(SILVER_DIR, latest_file)

# 4️⃣ S3 configuration
BUCKET_NAME = "hope-data-ecommerce-pipeline-us-east-2-project"
S3_KEY = f"silver/{latest_file}"

# 5️⃣ Initialize S3 client
s3 = boto3.client("s3", region_name="us-east-2")

print(f"Uploading: {SILVER_FILE}")

# 6️⃣ Upload file
s3.upload_file(SILVER_FILE, BUCKET_NAME, S3_KEY)

print(f"Uploaded to s3://{BUCKET_NAME}/{S3_KEY}")