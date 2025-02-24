import requests
import json
import sys
import base64
import pytz
from datetime import datetime

# GitHub Configuration
GITHUB_REPO = "your_username/schedule-meeting"
PICKAXE_TOKEN = "your_github_token"

# Extract parameters from GitHub Actions input
request_id = sys.argv[1]
preferred_day = sys.argv[2]
user_timezone = sys.argv[3]
output_filename = f"output_{request_id}.json"

# Convert to Australia/Melbourne time
def convert_to_australian_time(user_date, user_tz):
    user_tz = pytz.timezone(user_tz)
    aus_tz = pytz.timezone("Australia/Melbourne")
    user_dt = user_tz.localize(datetime.strptime(user_date, "%Y-%m-%d"))
    aus_dt = user_dt.astimezone(aus_tz)
    return aus_dt.strftime("%Y-%m-%d")

aus_date = convert_to_australian_time(preferred_day, user_timezone)

# Fetch available slots from TidyCal
def get_tidycal_availability(aus_date):
    TIDYCAL_API_KEY = "your_tidycal_api_key"
    TIDYCAL_URL = f"https://api.tidycal.com/v1/availability?date={aus_date}"
    headers = {"Authorization": f"Bearer {TIDYCAL_API_KEY}"}
    response = requests.get(TIDYCAL_URL, headers=headers)
    return response.json().get("available_times", []) if response.status_code == 200 else []

available_slots = get_tidycal_availability(aus_date)

def save_to_github(data):
    """Save available slots to a uniquely named output file"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{output_filename}"
    headers = {
        "Authorization": f"token {PICKAXE_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Check if file already exists
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha", None) if response.status_code == 200 else None

    # Encode JSON data
    encoded_content = base64.b64encode(json.dumps(data).encode()).decode()

    # Prepare request payload
    payload = {"message": f"Updated availability slots for {request_id}", "content": encoded_content}
    if sha:
        payload["sha"] = sha  # Required for updating an existing file

    return requests.put(url, headers=headers, json=payload)

# Save output to GitHub
status, response = save_to_github({"request_id": request_id, "available_times": available_slots})
print(f"GitHub Save Response: {status}, {response.json()}")
