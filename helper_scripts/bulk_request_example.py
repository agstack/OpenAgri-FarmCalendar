#!/usr/bin/env python
import os
from datetime import datetime, timedelta
import json
import requests
from typing import List, Dict, Any


GATEKEEPER_BASE_URL = 'http://localhost:8001'
LOGIN_URL = url = f"{GATEKEEPER_BASE_URL}/api/login/"
SERVICE_BASE_URL = f'{GATEKEEPER_BASE_URL}/api/proxy/farmcalendar'
API_ENDPOINT = '/api/v1/bulk/animal-lactating-activities/'
API_URL = f'{SERVICE_BASE_URL}{API_ENDPOINT}'


def get_auth_token(username, passsword):

    data = {
        "username": username,
        "password": passsword
    }
    response = requests.post(url, data=data)

    if response.status_code == 200:
        # Extract tokens from the JSON response
        tokens = response.json()
        token = tokens.get("access")

    return token


def send_bulk_request(bulk_data: List[Dict[str, Any]], auth_token):
    """Send bulk request to API."""
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    response = requests.post(API_URL, json=bulk_data, headers=headers)
    return response


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py <username> <password> <json_file_path>")
        print("Example: python script.py admin admin farm_calendar_animals_bulk.json")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    json_file_path = sys.argv[3]

    with open(json_file_path, 'r') as f:
        bulk_data = json.load(f)

    # Generate token
    auth_token = get_auth_token(username, password)

    # Send request
    response = send_bulk_request(bulk_data, auth_token)

    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Error: {response.text}")
