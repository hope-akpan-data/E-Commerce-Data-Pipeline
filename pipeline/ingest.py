import requests
import json
import os
from datetime import datetime

# 1. Define the API URL
API_URL = "https://dummyjson.com/products"

# 2. Get the absolute path to this script's folder (pipeline/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 3. Define Bronze directory inside your project
BRONZE_DIR = os.path.join(BASE_DIR, "../data/bronze")

# 4. Create the folder if it doesn't exist
os.makedirs(BRONZE_DIR, exist_ok=True)

# 5. Pull data from API
response = requests.get(API_URL)

if response.status_code == 200:
    raw = response.json()
    data = raw["products"]  # extract the actual list
else:
    raise Exception(f"API request failed with status {response.status_code}")

# 6. Create timestamp for unique file name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 7. Build full file path
file_path = os.path.join(BRONZE_DIR, f"products_raw_{timestamp}.json")

# 8. Save the data
with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

# 9. Print confirmation
print(f"Saved raw data to {file_path}")