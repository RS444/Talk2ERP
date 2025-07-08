import requests
import json
from datetime import date
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
ERP_BASE_URL = os.getenv("ERP_BASE_URL")

# ----------------------------- CREATE MATERIAL REQUEST -----------------------------
def create_material_request(item, qty, api_key, api_secret):
    if not item or not qty:
        return {"error": "Item and quantity are required"}

    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    data = {
        "doctype": "Material Request",
        "material_request_type": "Purchase",
        "company": "COLLEGE PURCHASING PORTAL",
        "transaction_date": str(date.today()),
        "schedule_date": str(date.today()),
        "items": [
            {
                "item_code": item,
                "qty": qty,
                "schedule_date": str(date.today()),
                "warehouse": "Main Stores - CPP"
            }
        ]
    }

    try:
        url = f"{ERP_BASE_URL}/api/resource/Material Request"
        response = requests.post(url, json=data, headers=headers, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid JSON response from server"}

# ----------------------------- APPROVE MATERIAL REQUEST -----------------------------
def approve_material_request(request_name, api_key, api_secret):
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    url = f"{ERP_BASE_URL}/api/resource/Material Request/{request_name}"

    try:
        response = requests.put(url, json={"docstatus": 1}, headers=headers, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid JSON response from server"}

# ----------------------------- GET DRAFT REQUESTS -----------------------------
def get_draft_requests(api_key, api_secret, user_email=None, fields=None):
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    filters = [["docstatus", "=", 0]]
    if user_email:
        filters.append(["owner", "=", user_email])

    default_fields = ["name", "owner", "transaction_date", "status"]
    selected_fields = fields if fields else default_fields

    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(selected_fields),
        "limit": 20
    }

    try:
        url = f"{ERP_BASE_URL}/api/resource/Material Request"
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid JSON response from server"}
