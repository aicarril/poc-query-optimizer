"""Sample Python file with intentional issues for CI Review Agent demo."""

import json
import os
import boto3
import requests
from datetime import datetime

# Missing type hints, missing docstring, bare except, print statements
def get_user_data(user_id):
    try:
        client = boto3.client('dynamodb')
        response = client.get_item(
            TableName='users',
            Key={'userId': {'S': user_id}}
        )
        print("Got user data: " + str(response))
        return response['Item']
    except:
        print("Something went wrong")
        return None


def process_orders(orders, status):
    results = []
    for order in orders:
        if order['status'] == status:
            results.append(order)
    return results


# Hardcoded credentials (security issue)
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "supersecretpassword123"

def call_external_api(endpoint):
    headers = {"Authorization": "Bearer " + API_KEY}
    resp = requests.get(endpoint, headers=headers)
    data = resp.json()
    return data


# Using os.path instead of pathlib
def read_config():
    config_path = os.path.join(os.getcwd(), "config", "settings.json")
    with open(config_path) as f:
        return json.load(f)
