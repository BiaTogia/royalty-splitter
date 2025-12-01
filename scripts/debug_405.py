import urllib.request
import urllib.error
import json

TOKEN = "149852281d416bad38f2119065758f6e0e1f865b"
BASE_URL = "http://localhost:8000/api"

def test_post(endpoint):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"test": "data"}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    print(f"POST {url}")
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Success: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Failed: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Error: {e}")

print("--- Testing Scenarios ---")
test_post("/users/")      # Should be 201 or 400 (Bad Request)
test_post("/users")       # Should be 301
test_post("/users/1/")    # Should be 405 (Method Not Allowed)
test_post("/tracks/")     # Should be 201 or 400
test_post("/tracks/1/")   # Should be 405
