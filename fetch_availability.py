import sys
import requests
import json
from datetime import datetime
import pytz

# Load input variables
preferred_day = sys.argv[1]  # Format: "YYYY-MM-DD"
user_timezone = sys.argv[2]  # Example: "America/New_York"

# API Keys (Store these as GitHub Secrets in production)
TIDYCAL_API_KEY = "your_tidycal_api_key"

# Convert user time to Australia/Melbourne time
def convert_to_australian_time(user_date, user_tz):
    user_tz = pytz.timezone(user_tz)
    aus_tz = pytz.timezone("Australia/Melbourne")

    user_dt = user_tz.localize(datetime.strptime(user_date, "%Y-%m-%d"))
    aus_dt = user_dt.astimezone(aus_tz)
    
    return aus_dt.strftime("%Y-%m-%d")

# Fetch available slots from TidyCal
def get_tidycal_availability(aus_date):
    TIDYCAL_URL = f"https://api.tidycal.com/v1/availability?date={aus_date}"
    headers = {"Authorization": f"Bearer {TIDYCAL_API_KEY}"}
    
    response = requests.get(TIDYCAL_URL, headers=headers)
    if response.status_code == 200:
        return response.json().get("available_times", [])
    else:
        return []

# Convert Australian time slots back to user's time zone
def convert_slots_to_user_timezone(available_slots, user_tz):
    aus_tz = pytz.timezone("Australia/Melbourne")
    user_tz = pytz.timezone(user_tz)

    converted_slots = []
    for slot in available_slots:
        aus_dt = aus_tz.localize(datetime.strptime(slot, "%H:%M"))
        user_dt = aus_dt.astimezone(user_tz)
        converted_slots.append(user_dt.strftime("%I:%M %p"))  # 12-hour format

    return converted_slots

# Main execution
aus_date = convert_to_australian_time(preferred_day, user_timezone)
available_slots = get_tidycal_availability(aus_date)
converted_slots = convert_slots_to_user_timezone(available_slots, user_timezone)

# Save output to JSON file
output_data = {"available_slots": converted_slots}
with open("output.json", "w") as f:
    json.dump(output_data, f, indent=4)

print(json.dumps(output_data))  # Print output for debugging
