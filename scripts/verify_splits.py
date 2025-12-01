import urllib.request
import urllib.error
import json
import sys

TOKEN = "149852281d416bad38f2119065758f6e0e1f865b"
BASE_URL = "http://localhost:8000/api"

def verify_nested_splits():
    print("--- Verifying Nested Split Creation ---")
    
    # Create a new track with splits
    track_data = {
        "title": "Nested Split Track",
        "duration": 200,
        "splits": [
            {"user": 9, "percentage": 50.0}, # Superuser ID 9 (from previous logs)
            {"user": 10, "percentage": 50.0} # Artist ID 10 (from previous logs)
        ]
    }
    
    url = f"{BASE_URL}/tracks/"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps(track_data).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            body = json.loads(response.read().decode('utf-8'))
            print(f"Status: {response.status}")
            print(f"Created Track: {json.dumps(body, indent=2)}")
            
            if len(body["splits"]) == 2:
                print(f"[SUCCESS] Created 2 splits correctly.")
            else:
                print(f"[FAILED] Expected 2 splits, got {len(body['splits'])}")
                sys.exit(1)

    except urllib.error.HTTPError as e:
        print(f"[FAILED] HTTP Error: {e.code}")
        print(e.read().decode('utf-8'))
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_nested_splits()
