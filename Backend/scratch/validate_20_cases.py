import psycopg2
import httpx
import os
import json

db_url = os.environ.get("DATABASE_URL", "postgresql://tracex:tracex_dev_password@localhost:5432/tracex")
base_url = "http://localhost:8000/api/v1"

def run_checks():
    report = {
        "pg_cases_count": 0,
        "case_ids": [],
        "verified_count": 0,
        "neo4j_verification": "FAILED (No case nodes found)",
        "graph_result": "FAILED",
        "analytics_result": "FAILED",
        "ml_result": "FAILED",
        "resolution_result": "FAILED",
        "failures": []
    }
    
    # 1 & 2. PG Check
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT canonical_label, COUNT(*) FROM canonical_node_records GROUP BY canonical_label;")
        labels = cur.fetchall()
        
        # Check if 'Case' exists in labels
        has_cases = False
        for label, count in labels:
            if label.lower() == 'case':
                has_cases = True
                report["pg_cases_count"] = count
        
        if not has_cases:
            report["failures"].append("No case records found in PostgreSQL (canonical_node_records).")
    except Exception as e:
        report["failures"].append(f"PG Error: {e}")
        
    # Test APIs with Admin Token
    try:
        res = httpx.post(f"{base_url}/auth/login", json={"email": "admin@tracex.local", "password": "adminpassword"})
        if res.status_code == 200:
            token = res.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Graph
            r_graph = httpx.get(f"{base_url}/graph/neighborhood/UNKNOWN_PERSON", headers=headers)
            report["graph_result"] = f"{r_graph.status_code} - {len(r_graph.json().get('nodes', []))} nodes returned"
            
            # Analytics
            r_ana = httpx.get(f"{base_url}/analytics/network", headers=headers)
            report["analytics_result"] = str(r_ana.status_code)
            
            # ML
            r_ml = httpx.get(f"{base_url}/ml/case/CASE-NX-2026-001/signals", headers=headers)
            report["ml_result"] = str(r_ml.status_code)
            
            # Resolution
            r_res = httpx.post(f"{base_url}/match/match-1/decision", json={"decision": "approved"}, headers=headers)
            report["resolution_result"] = str(r_res.status_code)
            
    except Exception as e:
        report["failures"].append(f"API Error: {e}")
        
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_checks()
