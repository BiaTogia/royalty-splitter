#!/usr/bin/env python
"""
Script to recreate a user account via the API
"""
import requests
import json
import sys

API_BASE = "http://localhost:8000"

def recreate_user(email, password, name):
    """Register a user via the API"""
    print(f"Registering user: {email}")
    
    url = f"{API_BASE}/api/register/"
    payload = {
        "email": email,
        "password": password,
        "name": name
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201]:
            print(f"\n✓ User {email} created successfully!")
            return True
        else:
            print(f"\n✗ Failed to create user")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Recreate the xpert user
    success = recreate_user(
        email="xpert@xpert.com",
        password="YourSecurePassword123",
        name="Expert User"
    )
    
    sys.exit(0 if success else 1)
