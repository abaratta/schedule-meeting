import requests
import json
import datetime
import pytz
import os

# Configuration
TIDYCAL_API_KEY = os.getenv("TIDYCAL_API_KEY")  # Load from GitHub Secrets
BOOKING_TYPE_ID = os.getenv("TIDYCAL_BOOKING_TYPE_ID")  # Load from GitHub Secrets
TIDYCAL_URL = f"https://tidycal.com/api/booking-types/{BOOKING_TYPE_ID}/timeslots"

if not TIDYCAL_API_KEY:
    print("Error: TIDYCAL_API_KEY is not set or is empty.")
    exit(1)

print(f"API Key Loaded, Length: {len(TIDYCAL_API_KEY)}")

# Function to convert date
def convert_to_australian_time(user_date, user_tz):
    """Convert user-provided date to Australia/Melbourne time."""
    user_tz = pytz.timezone(user_tz)
    aus_tz = pytz.timezone("Australia/Melbourne")

    user_dt = user_tz.localize(datetime.datetime.strptime(user_date, "%Y-%m-%d"))
    aus_dt = user_dt.astimezone(aus_tz)
    return aus_dt.strftime("%Y-%m-%d")

# Function to fetch availability from TidyCal
def get_tidycal_availability(aus_date):
    """Fetch available timeslots from TidyCal"""
    # Convert the date to a full UTC range
    start_time = f"{aus_date}T00:00:00Z"
    end_time = f"{aus_date}T23:59:59Z"

    params = {
        "starts_at": start_time,
        "ends_at": end_time,
    }
    
    headers = {
    "Authorization": f"Bearer {TIDYCAL_API_KEY}",  # Ensure 'Bearer' is included
    "Accept": "application/json",
    "Content-Type": "application/json"
    }

    print(f"Using API Key (masked): Bearer {TIDYCAL_API_KEY[:4]}...{TIDYCAL_API_KEY[-4:]}")
    
    response = requests.get(TIDYCAL_URL, headers=headers, params=params)

    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")  # Debugging: Print the raw response

    if response.status_code == 200:
        try:
            return response.json().get("data", [])
        except json.JSONDecodeError:
            print("Error: Response is not valid JSON")
            return []
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

# Example usage (replace this with your actual script logic)
if __name__ == "__main__":
    aus_date = convert_to_australian_time("2025-02-24", "America/New_York")
    available_slots = get_tidycal_availability(aus_date)
    print("Available slots:", available_slots)

