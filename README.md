# AI Calendar Scheduling Bot (Pickaxe + GitHub + Make.com + TidyCal)

## **Overview**
This repository contains a **GitHub Actions workflow** and a **Python script** that automate calendar scheduling by:

1. Accepting a **preferred date** and **user timezone** as input from Pickaxe.
2. Sending the request to **Make.com**, which triggers GitHub Actions.
3. Converting the date to **Australia/Melbourne time**.
4. Fetching **available slots from TidyCal**.
5. Saving the results in a uniquely named `output_{request_id}.json` file.
6. Make.com waits for 10 seconds, then retrieves the correct file from GitHub.
7. Make.com returns the response back to Pickaxe.

This system allows a chatbot to **seamlessly schedule meetings** while ensuring that each request gets the correct response.

---

## **Files Required in GitHub**

### **1️⃣ `.github/workflows/schedule_bot.yml` (GitHub Actions Workflow)**
This workflow listens for `repository_dispatch` events triggered by Make.com and runs the `fetch_availability.py` script.

```yaml
name: Fetch Available Slots
on:
  repository_dispatch:
    types: [fetch-availability]

jobs:
  run-script:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: pip install -r requirements.txt

      - name: Run Availability Script
        run: python fetch_availability.py "${{ github.event.client_payload.request_id }}" "${{ github.event.client_payload.preferred_day }}" "${{ github.event.client_payload.user_timezone }}"
```

---

### **2️⃣ `fetch_availability.py` (Fetch Available Slots and Save to GitHub)**
This script:
- Extracts `request_id`, `preferred_day`, and `user_timezone` from GitHub Actions.
- Converts the date to **Australia/Melbourne time**.
- Fetches available slots from **TidyCal**.
- Saves the results in `output_{request_id}.json` in GitHub.

```python
import requests
import json
import sys
import base64
import pytz
from datetime import datetime

# GitHub Configuration
GITHUB_REPO = "your_username/schedule-meeting"
GITHUB_TOKEN = "your_github_token"

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
        "Authorization": f"token {GITHUB_TOKEN}",
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
```

---

### **3️⃣ `requirements.txt` (Dependencies for Python Script)**
```txt
pytz
requests
```

---

## **Next Steps**
✅ **Set up Make.com to trigger this workflow and wait 10 seconds before fetching results.**  
✅ **Modify Make.com to retrieve `output_{request_id}.json` after the delay.**  
✅ **Ensure Make.com forwards the retrieved data back to Pickaxe via webhook response.**

For improvements or questions, feel free to **submit an issue** or **pull request**! 🚀

