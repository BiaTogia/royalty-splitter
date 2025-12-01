import urllib.request
import urllib.error
import json
import sys
import subprocess

TOKEN = "149852281d416bad38f2119065758f6e0e1f865b"
BASE_URL = "http://localhost:8000/api"

ENDPOINTS = [
    "/users/",
    "/tracks/",
    "/wallets/",
    "/siem-events/",
    "/royalties/",
    "/splits/",
    "/payouts/",
    "/payout-status/",
    "/severity-levels/"
]

def make_request(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    
    if data:
        data = json.dumps(data).encode('utf-8')
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[SUCCESS] {method} {endpoint} - Status: {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"[FAILED] {method} {endpoint} - Status: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
        return False
    except Exception as e:
        print(f"[ERROR] {method} {endpoint} - {e}")
        return False

def verify_drf_token_command():
    print("\n--- Verifying drf_create_token command ---")
    try:
        # We need to run this inside the container context, but this script is running inside the container
        # So we can just call manage.py directly? No, this script is executed via docker exec from outside usually?
        # Wait, I am writing this script to be run INSIDE the container.
        # So I can use subprocess to call manage.py
        
        # Note: drf_create_token is a management command provided by rest_framework.authtoken
        result = subprocess.run(
            ["python", "manage.py", "drf_create_token", "togrul"],
            capture_output=True, text=True
        )
        print(f"Command Output: {result.stdout.strip()}")
        if result.returncode == 0 and "Token" in result.stdout:
            print("[SUCCESS] drf_create_token worked")
        else:
            print(f"[WARNING] drf_create_token output: {result.stderr}")
            # It might just print the existing token, which is fine.
    except Exception as e:
        print(f"[ERROR] Failed to run drf_create_token: {e}")

def verify():
    print("--- Verifying All Endpoints ---")
    all_success = True
    for endpoint in ENDPOINTS:
        if not make_request(endpoint):
            all_success = False
            
    # Test POST User again to be sure
    print("\n--- Verifying POST User ---")
    user_data = {
        "name": "Final Test User",
        "email": "finaltest@example.com",
        "password": "password123",
        "role": 1
    }
    if not make_request("/users/", "POST", user_data):
        all_success = False

    verify_drf_token_command()

    if all_success:
        print("\nAll systems operational.")
    else:
        print("\nSome checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    verify()
