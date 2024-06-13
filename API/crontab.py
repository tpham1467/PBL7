
from datetime import datetime
import requests

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

api_url = "http://localhost:8123/files?type=crawl_data"

try:
    response = requests.get(api_url)
    response.raise_for_status()  # Check if the request was successful
    print(f"current time {current_time}")
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")