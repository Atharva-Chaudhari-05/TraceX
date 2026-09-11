import os
import sys
import subprocess
import requests
import time
import hashlib
import json
import uuid
import shutil
import csv
from pathlib import Path

WORKSPACE = Path(os.environ.get("WORKSPACE", r"C:\Users\pawar\OneDrive\Desktop\SIH\CODEBASE"))
TRACEX_PREPARED = WORKSPACE.parent / "TRACEX_PREPARED"
SMOKE_DATASET = WORKSPACE / "scratch" / "smoke_dataset"
SMOKE_MODELS = WORKSPACE / "scratch" / "smoke_models"

PYTHON_EXE = WORKSPACE / ".venv" / "Scripts" / "python.exe"
UVICORN_EXE = WORKSPACE / ".venv" / "Scripts" / "uvicorn.exe"

os.environ["PATH"] = r"C:\Users\pawar\.local\bin;" + os.environ.get("PATH", "")
os.environ["POSTGRES_DB"] = "tracex_test"
os.environ["NEO4J_URI"] = "bolt://localhost:7688"
os.environ["BOOTSTRAP_ADMIN_EMAIL"] = "admin@tracex.local"
os.environ["BOOTSTRAP_ADMIN_PASSWORD"] = "admin_password"
os.environ["EXTRACTION_DOCUMENTS_PATH"] = str(SMOKE_DATASET / "documents.csv")
os.environ["TRACEX_MODEL_DIR"] = str(SMOKE_MODELS)
os.environ["PYTHONPATH"] = str(WORKSPACE)

def hash_directory(directory: Path) -> str:
    hasher = hashlib.sha256()
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            filepath = Path(root) / name
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
    return hasher.hexdigest()

def run_command(cmd, env=None):
    print(f"\n> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=WORKSPACE, env=env or os.environ)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result

def create_dataset():
    import time
    run_id = str(int(time.time()))
    SMOKE_DATASET.mkdir(exist_ok=True, parents=True)
    
    # cases.csv
    with open(SMOKE_DATASET / "cases.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "title", "description", "status", "priority", "created_date", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["CASE-SMOKE-POS", "Test Fin Case", "Fin desc", "OPEN", "HIGH", "2024-01-01", "True", "smoke", "smoke_c1", "SCN-FIN-001", f"smoke_audit1_{run_id}", "direct"])
        writer.writerow(["CASE-SMOKE-NEG", "Test Com Case", "Com desc", "OPEN", "LOW", "2024-01-02", "True", "smoke", "smoke_c2", "OTHER-001", f"smoke_audit2_{run_id}", "direct"])

    # persons.csv
    with open(SMOKE_DATASET / "persons.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["person_id", "first_name", "last_name", "dob", "nationality", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["PERSON-POS-1", "John", "Doe", "1990-01-01", "US", "True", "smoke", "smoke_p1", "SCN-FIN-001", f"smoke_audit3_{run_id}", "direct"])
        writer.writerow(["PERSON-NEG-1", "Jane", "Smith", "1985-05-05", "UK", "True", "smoke", "smoke_p2", "OTHER-001", f"smoke_audit4_{run_id}", "direct"])

    # documents.csv
    with open(SMOKE_DATASET / "documents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document_id", "description", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["DOC-POS-1", "John Doe was seen near the bank.", "True", "smoke", "smoke_d1", "SCN-FIN-001", f"smoke_audit5_{run_id}", "direct"])
        writer.writerow(["DOC-NEG-1", "Jane Smith attended the conference.", "True", "smoke", "smoke_d2", "OTHER-001", f"smoke_audit6_{run_id}", "direct"])

    # relationships.csv
    with open(SMOKE_DATASET / "relationships.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "target_id", "relationship_type", "weight", "start_date", "end_date", "description", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["PERSON-POS-1", "CASE-SMOKE-POS", "INVOLVED_IN", "1.0", "2024-01-01", "", "Case targets John", "True", "smoke", "smoke_r1", "SCN-FIN-001", f"smoke_audit7_{run_id}", "direct"])
        writer.writerow(["PERSON-NEG-1", "CASE-SMOKE-NEG", "INVOLVED_IN", "1.0", "2024-01-02", "", "Case targets Jane", "True", "smoke", "smoke_r2", "OTHER-001", f"smoke_audit8_{run_id}", "direct"])
    print(f"Created synthetic dataset directly with run_id {run_id}.")

def main():
    print("=== TraceX PRE-M11 SMOKE TEST ===")
    
    print("\n[Stage 1] Hashing Baseline Dataset")
    baseline_hash_before = hash_directory(TRACEX_PREPARED)
    print(f"Baseline Hash Before: {baseline_hash_before}")
    
    print("\n[Stage 2] Starting Isolated Infrastructure")
    run_command("docker rm -f tracex-neo4j-smoke")
    run_command("docker run -d --name tracex-neo4j-smoke -p 7688:7687 -e NEO4J_AUTH=none neo4j:5-community")
    
    if SMOKE_MODELS.exists():
        shutil.rmtree(SMOKE_MODELS)
    SMOKE_MODELS.mkdir(exist_ok=True, parents=True)
    
    print("Waiting for Neo4j to initialize (15s)...")
    time.sleep(15)
    
    create_dataset()
    
    print("\nStarting Uvicorn Server in background...")
    with open(WORKSPACE / "scratch" / "uvicorn.log", "w") as f_out:
        uvicorn_proc = subprocess.Popen(
            f"{UVICORN_EXE} backend.app.main:app --port 8001",
            shell=True,
            cwd=WORKSPACE,
            env=os.environ,
            stdout=f_out,
            stderr=subprocess.STDOUT
        )
    time.sleep(15) # Wait for startup
    
    try:
        print("\n[Stage 3] Authentication")
        resp = requests.post("http://127.0.0.1:8001/api/v1/auth/login", json={"email": "admin@tracex.local", "password": "admin_password"})
        if resp.status_code != 200:
            print("Failed to authenticate.")
            print(resp.text)
            
            print("\n--- Uvicorn Logs ---")
            with open(WORKSPACE / "scratch" / "uvicorn.log", "r") as f:
                print(f.read())
            print("--------------------\n")
            
        resp.raise_for_status()
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Successfully authenticated.")

        print("\n[Stage 4] Ingestion CLI")
        run_command(f"{PYTHON_EXE} scripts/run_ingestion.py --source {SMOKE_DATASET}")

        print("\n[Stage 5] Extraction API")
        ext_resp = requests.post("http://127.0.0.1:8001/api/v1/extraction/trigger", json={}, headers=headers)
        ext_resp.raise_for_status()
        batch_id = ext_resp.json()["batch_id"]
        print(f"Extraction Batch ID: {batch_id}")
        
        print("Polling extraction status...")
        for _ in range(1800):
            stat_resp = requests.get(f"http://127.0.0.1:8001/api/v1/extraction/status/{batch_id}", headers=headers)
            stat_resp.raise_for_status()
            status = stat_resp.json()["status"]
            print(f"Status: {status}")
            if status == "COMPLETED":
                break
            elif status == "FAILED":
                raise Exception("Extraction FAILED")
            time.sleep(2)
        
        if status != "COMPLETED":
            raise Exception("Extraction timed out!")

        print("\n[Stage 6] Resolution API")
        res_resp = requests.post(f"http://127.0.0.1:8001/api/v1/resolution/batch/{batch_id}/run", json={}, headers=headers)
        res_resp.raise_for_status()
        print("Resolution batch run successfully.")
        
        print("\n[Stage 6b] Review Matches CLI (Isolated Auto-Confirm for test only)")
        run_command(f"{PYTHON_EXE} scripts/review_matches.py {batch_id} --auto-confirm 0.0 --auto-mint --admin-email admin@tracex.local")

        print("\n[Stage 7] Graph Projection API")
        graph_resp = requests.get("http://127.0.0.1:8001/api/v1/graph/neighborhood/CASE-SMOKE-POS?depth=1&limit=10", headers=headers)
        graph_resp.raise_for_status()
        graph_data = graph_resp.json()
        print(f"Graph nodes: {len(graph_data.get('nodes', []))} edges: {len(graph_data.get('edges', []))}")

        print("\n[Stage 8] Network Analytics API")
        ana_resp = requests.get("http://127.0.0.1:8001/api/v1/analytics/network?case_id=CASE-SMOKE-POS", headers=headers)
        ana_resp.raise_for_status()
        print("Analytics Output:", json.dumps(ana_resp.json(), indent=2))

        print("\n[Stage 9] ML Training API")
        ml_train_resp = requests.post("http://127.0.0.1:8001/api/v1/ml/train", json={
            "case_ids": ["CASE-SMOKE-POS", "CASE-SMOKE-NEG"],
            "target_definition": "synthetic_dev_target_v1"
        }, headers=headers)
        ml_train_resp.raise_for_status()
        print("ML Training Output:", json.dumps(ml_train_resp.json(), indent=2))

        print("\n[Stage 9b] ML Inference API")
        ml_infer_resp = requests.get("http://127.0.0.1:8001/api/v1/ml/case/CASE-SMOKE-POS/signals", headers=headers)
        ml_infer_resp.raise_for_status()
        print("ML Inference Output:", json.dumps(ml_infer_resp.json(), indent=2))

        print("\n[Stage 10] Audit API")
        audit_resp = requests.get("http://127.0.0.1:8001/api/v1/audit/logs?limit=5", headers=headers)
        audit_resp.raise_for_status()
        print(f"Retrieved {audit_resp.json()['total']} total audit logs. Sample:")
        print(json.dumps(audit_resp.json()["data"][:2], indent=2))
        
        print("\n[Stage 11] Verification")
        if SMOKE_MODELS.exists() and len(list(SMOKE_MODELS.iterdir())) > 0:
            print("Model isolation successful (artifacts written to TRACEX_MODEL_DIR)")
        else:
            print("Model isolation failed (no artifacts written)")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        try:
            with open(WORKSPACE / "scratch" / "uvicorn.log", "r") as f:
                print("\n--- Uvicorn Logs on Error ---")
                print(f.read())
        except Exception:
            pass
    finally:
        print("\n[Stage 12] Cleanup & Final Verification")
        uvicorn_proc.kill()
        run_command("docker rm -f tracex-neo4j-smoke")
        
        baseline_hash_after = hash_directory(TRACEX_PREPARED)
        print(f"\nBaseline Hash Before: {baseline_hash_before}")
        print(f"Baseline Hash After:  {baseline_hash_after}")
        if baseline_hash_before == baseline_hash_after:
            print("DATASET INTEGRITY: PASSED (Immutable)")
        else:
            print("DATASET INTEGRITY: FAILED (Mutated!)")
            
        print("\nSMOKE TEST FINISHED.")

if __name__ == "__main__":
    main()
