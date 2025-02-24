# schedule-meeting

# AI Calendar Scheduling Bot (Pickaxe + GitHub + TidyCal)

## **Overview**
This repository contains a **GitHub Actions workflow** and a **Python script** that automate calendar scheduling by:
1. Accepting a **preferred date** and **user timezone** as input.
2. Converting the date to **Australia/Melbourne time**.
3. Fetching **available slots from TidyCal**.
4. Converting the available slots **back to the user's timezone**.
5. Storing the **available slots in `output.json`** for retrieval by a chatbot (Pickaxe).

This system allows a chatbot to **seamlessly schedule meetings** while handling **time zone conversions automatically**.

---

## **How It Works**
### **1️⃣ Triggering the Workflow**
- The workflow is triggered via a **GitHub repository dispatch event**.
- Pickaxe (or any external system) sends a **preferred date and user timezone** via GitHub API.
- GitHub Actions executes `fetch_availability.py`.

### **2️⃣ Fetching and Converting Available Slots**
- `fetch_availability.py`:
  - Converts the preferred date to **Australia/Melbourne time**.
  - Calls **TidyCal API** to retrieve available slots.
  - Converts slots **back to the user's time zone**.
  - Saves the available slots in `output.json`.

### **3️⃣ Retrieving Available Slots**
- Pickaxe or an external system fetches `output.json` from GitHub to display available times to the user.
- Once the user selects a time, a separate **meeting booking function** is triggered.

---

## **Setup Instructions**

### **1️⃣ Create a GitHub Repository**
1. Clone this repository or create a new one.
2. Ensure the following structure exists:
   ```
   .github/workflows/schedule_bot.yml
   fetch_availability.py
   requirements.txt
   output.json (auto-generated after execution)
   ```

### **2️⃣ Set Up GitHub Secrets**
- Go to **Settings → Secrets and variables → Actions → New Repository Secret**.
- Add the following secrets:
  - `TIDYCAL_API_KEY` → Your **TidyCal API Key**.
  - `GITHUB_TOKEN` → Personal Access Token (if triggering via API).

### **3️⃣ Configure GitHub Actions Workflow**
- The **workflow file (`.github/workflows/schedule_bot.yml`)** automatically runs when triggered via API.

### **4️⃣ Install Dependencies**
- The Python script requires **pytz** and **requests**.
- Install dependencies locally with:
  ```sh
  pip install -r requirements.txt
  ```

---

## **Usage**
### **1️⃣ Trigger the Workflow via API**
Use the following Python snippet to trigger GitHub Actions:
```python
import requests

GITHUB_TOKEN = "your_github_token"
GITHUB_REPO = "your_username/your_repo"

def trigger_github_workflow(preferred_day, user_timezone):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "event_type": "fetch-availability",
        "client_payload": {
            "preferred_day": preferred_day,
            "user_timezone": user_timezone
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.status_code, response.text
```

### **2️⃣ Retrieve Available Slots**
Fetch the `output.json` file from GitHub to display available times:
```python
import requests
import json
import base64

GITHUB_REPO = "your_username/your_repo"
GITHUB_TOKEN = "your_github_token"

def get_available_slots():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/output.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = json.loads(response.text)["content"]
        decoded_content = base64.b64decode(content).decode("utf-8")
        return json.loads(decoded_content)
    
    return {"error": "No availability found"}
```

---

## **Next Steps**
✅ **Test API triggers** to fetch availability.
✅ **Integrate Pickaxe chatbot** to interact with this system.
✅ **Develop a function to book meetings** once a slot is selected.

For improvements or questions, feel free to **submit an issue** or **pull request**! 🚀

