import os
import csv

def create_dataset():
    import time
    run_id = str(int(time.time()))
    dataset_dir = "scratch/smoke_dataset"
    os.makedirs(dataset_dir, exist_ok=True)
    
    # cases.csv
    with open(f"{dataset_dir}/cases.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "title", "description", "status", "priority", "created_date", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["CASE-SMOKE-POS", "Test Fin Case", "Fin desc", "OPEN", "HIGH", "2024-01-01", "True", "smoke", "smoke_c1", "SCN-FIN-001", f"smoke_audit1_{run_id}", "direct"])
        writer.writerow(["CASE-SMOKE-NEG", "Test Com Case", "Com desc", "OPEN", "LOW", "2024-01-02", "True", "smoke", "smoke_c2", "OTHER-001", f"smoke_audit2_{run_id}", "direct"])

    # persons.csv
    with open(f"{dataset_dir}/persons.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["person_id", "first_name", "last_name", "dob", "nationality", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["PERSON-POS-1", "John", "Doe", "1990-01-01", "US", "True", "smoke", "smoke_p1", "SCN-FIN-001", f"smoke_audit3_{run_id}", "direct"])
        writer.writerow(["PERSON-NEG-1", "Jane", "Smith", "1985-05-05", "UK", "True", "smoke", "smoke_p2", "OTHER-001", f"smoke_audit4_{run_id}", "direct"])

    # documents.csv
    with open(f"{dataset_dir}/documents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document_id", "description", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        writer.writerow(["DOC-POS-1", "John Doe was seen near the bank.", "True", "smoke", "smoke_d1", "SCN-FIN-001", f"smoke_audit5_{run_id}", "direct"])
        writer.writerow(["DOC-NEG-1", "Jane Smith attended the conference.", "True", "smoke", "smoke_d2", "OTHER-001", f"smoke_audit6_{run_id}", "direct"])

    # relationships.csv
    with open(f"{dataset_dir}/relationships.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "target_id", "relationship_type", "weight", "start_date", "end_date", "description", "Synthetic_Flag", "Source_Dataset", "source_record_reference", "scenario_id", "Audit_Reference", "Provenance_Mode"])
        # Link cases to persons
        writer.writerow(["PERSON-POS-1", "CASE-SMOKE-POS", "INVOLVED_IN", "1.0", "2024-01-01", "", "Case targets John", "True", "smoke", "smoke_r1", "SCN-FIN-001", f"smoke_audit7_{run_id}", "direct"])
        writer.writerow(["PERSON-NEG-1", "CASE-SMOKE-NEG", "INVOLVED_IN", "1.0", "2024-01-02", "", "Case targets Jane", "True", "smoke", "smoke_r2", "OTHER-001", f"smoke_audit8_{run_id}", "direct"])

    print(f"Created synthetic dataset with run_id {run_id}.")

if __name__ == "__main__":
    create_dataset()
