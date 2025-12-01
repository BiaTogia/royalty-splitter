import urllib.request
import urllib.error
import json
import sys

TOKEN = "149852281d416bad38f2119065758f6e0e1f865b"
BASE_URL = "http://localhost:8000/api"

def verify_release_date():
    print("--- Verifying Automatic Release Date ---")
    
    # Create a new track without release_date
    track_data = {
        "title": "Auto Date Track",
        "duration": 180,
        "owner_counts": 1,
        "splits": [{"user": 1, "percentage": 100.0}]
    }
    
    url = f"{BASE_URL}/tracks/"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps(track_data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            body = json.loads(response.read().decode('utf-8'))
            print(f"Status: {response.status}")
            print(f"Created Track: {body}")
            
            if "release_date" in body and body["release_date"]:
                print(f"[SUCCESS] Release Date: {body['release_date']}")
            else:
                print("[FAILED] Release Date missing or empty")
                sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_release_date()
