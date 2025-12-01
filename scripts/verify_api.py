import urllib.request
import urllib.error
import json
import sys

TOKEN = "149852281d416bad38f2119065758f6e0e1f865b"
BASE_URL = "http://localhost:8000/api"

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
            print(f"--- {method} {endpoint} ---")
            print(f"Status: {response.status}")
            body = response.read().decode('utf-8')
            print(f"Response: {body[:500]}...") # Truncate for readability
            return True
    except urllib.error.HTTPError as e:
        print(f"--- {method} {endpoint} Failed ---")
        print(f"Status: {e.code}")
        print(f"Reason: {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def verify():
    print("Verifying API Endpoints...")
    
    # Test GET Tracks
    if not make_request("/tracks/", "GET"):
        sys.exit(1)
        
    # Test POST User
    user_data = {
        "name": "API Test User",
        "email": "apitest@example.com",
        "password": "password123",
        "role": 1 # Assuming Admin role ID is 1
    }
    if not make_request("/users/", "POST", user_data):
        sys.exit(1)

    print("\nVerification Successful!")

if __name__ == "__main__":
    verify()
