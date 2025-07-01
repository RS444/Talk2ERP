# erp_api.py
import requests
import json
from datetime import date

ERP_BASE_URL = "https://7f6b-2401-4900-2316-7c23-71a1-1133-bd11-a771.ngrok-free.app"

# ----------------------------- CREATE MATERIAL REQUEST -----------------------------
def create_material_request(item, qty, api_key, api_secret):
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
        "items": [{
            "item_code": item,
            "qty": qty,
            "schedule_date": str(date.today()),
            "warehouse": "Main Stores - CPP"
        }]
    }

    try:
        url = f"{ERP_BASE_URL}/api/resource/Material Request"
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ----------------------------- APPROVE MATERIAL REQUEST -----------------------------
def approve_material_request(request_name, api_key, api_secret):
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    url = f"{ERP_BASE_URL}/api/resource/Material Request/{request_name}"

    try:
        response = requests.put(url, json={"docstatus": 1}, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ----------------------------- GET DRAFT REQUESTS -----------------------------
def get_draft_requests(api_key, api_secret, user_email=None):
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    filters = [["docstatus", "=", 0]]
    if user_email:
        filters.append(["owner", "=", user_email])

    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(["name", "owner", "transaction_date", "status"]),
        "limit": 20
    }

    try:
        url = f"{ERP_BASE_URL}/api/resource/Material Request"
        response = requests.get(url, headers=headers, params=params)
        return response.json().get("data", [])
    except Exception as e:
        return []
