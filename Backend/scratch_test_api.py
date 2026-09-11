import requests
import uvicorn
import threading
import time

from backend.app.main import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(2) # let it boot

base_url = "http://127.0.0.1:8002/api/v1/auth/login"

# 1. Valid credentials (from .env.example -> admin@tracex.local / tracex_dev_password)
print("Testing valid credentials...")
resp = requests.post(base_url, json={"email": "admin@tracex.local", "password": "change-this-local-password"})
print(resp.status_code)
if resp.status_code == 200:
    print(resp.json().keys())

# 2. Wrong password
print("Testing wrong password...")
resp = requests.post(base_url, json={"email": "admin@tracex.local", "password": "wrong"})
print(resp.status_code, resp.json())

# 3. Unknown user
print("Testing unknown user...")
resp = requests.post(base_url, json={"email": "nobody@tracex.local", "password": "wrong"})
print(resp.status_code, resp.json())

# 4. Malformed request
print("Testing malformed request...")
resp = requests.post(base_url, json={"email": "nobody"})
print(resp.status_code, resp.json())
