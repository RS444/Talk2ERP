import requests
from datetime import date

def create_material_request(item, qty, api_key, api_secret):
    """
    Create a Material Request in ERPNext using user's API credentials.
    Args:
        item (str): Item code or name from ERPNext.
        qty (int): Quantity to request.
        api_key (str): User's ERPNext API Key.
        api_secret (str): User's ERPNext API Secret.

    Returns:
        dict: ERPNext API response.
    """

    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    data = {
        "doctype": "Material Request",
        "material_request_type": "Purchase",
        "company": "COLLEGE PURCHASING PORTAL",  # Replace with your actual company name
        "transaction_date": str(date.today()),
        "schedule_date": str(date.today()),
        "items": [{
            "item_code": item,
            "qty": qty,
            "schedule_date": str(date.today()),
            "warehouse": "Main Stores - CPP"  # Replace with your actual warehouse
        }]
    }

    try:
        url = "http://localhost:8000/api/resource/Material Request"
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
