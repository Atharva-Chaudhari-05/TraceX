import httpx
import json

base_url = "http://localhost:8000/api/v1"

try:
    # 1. Login
    res = httpx.post(f"{base_url}/auth/login", json={"email": "admin@tracex.local", "password": "adminpassword"})
    token = res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Graph
    res = httpx.get(f"{base_url}/graph/neighborhood/UNKNOWN_PERSON", headers=headers)
    print("Graph:", res.status_code)
    if res.status_code == 200:
        print(json.dumps(res.json())[:500])
        
    # 3. Analytics
    res = httpx.get(f"{base_url}/analytics/network", headers=headers)
    print("Analytics:", res.status_code)
    if res.status_code == 200:
        print(json.dumps(res.json())[:500])
        
    # 4. ML
    res = httpx.get(f"{base_url}/ml/case/CASE-NX-2026-001/signals", headers=headers)
    print("ML:", res.status_code)
    if res.status_code == 200:
        print(json.dumps(res.json())[:500])
        
    # 5. Audit
    res = httpx.get(f"{base_url}/logs", headers=headers)
    print("Audit:", res.status_code)
    if res.status_code == 200:
        print(json.dumps(res.json())[:500])
except Exception as e:
    print("Error:", e)
