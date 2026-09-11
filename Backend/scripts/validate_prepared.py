import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = BASE_DIR.parent / "TRACEX_DATA"
PREPARED_DIR = BASE_DIR.parent / "TRACEX_PREPARED"


PRIMARY_KEYS = {
    "accounts.csv": "account_id",
    "cases.csv": "case_id",
    "communication_events.csv": "communication_id",
    "crime_context.csv": "context_id",
    "devices.csv": "device_id",
    "documents.csv": "document_id",
    "incidents.csv": "incident_id",
    "locations.csv": "location_id",
    "network_events.csv": "network_event_id",
    "organizations.csv": "organization_id",
    "persons.csv": "person_id",
    "phones.csv": "phone_id",
    "physical_access_events.csv": "physical_event_id",
    "relationships.csv": "relationship_id",
    "transactions.csv": "transaction_id",
    "vehicles.csv": "vehicle_id",
}


CANONICAL_FIELDS = {
    "Synthetic_Flag",
    "Source_Dataset",
    "source_record_reference",
    "Generation_Batch_ID",
    "Confidence_Level",
    "Provenance_Mode",
    "Audit_Reference",
}


def count_rows(path):
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return sum(1 for _ in csv.DictReader(file))


def get_headers(path):
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return csv.DictReader(file).fieldnames or []


def main():
    print("=== PREPARED DATASET VALIDATION ===")

    if not SOURCE_DIR.is_dir():
        raise FileNotFoundError(
            f"Source directory missing: {SOURCE_DIR}"
        )

    if not PREPARED_DIR.is_dir():
        raise FileNotFoundError(
            f"Prepared directory missing: {PREPARED_DIR}"
        )

    total_source_rows = 0
    total_prepared_rows = 0

    for filename, primary_id in PRIMARY_KEYS.items():
        source_path = SOURCE_DIR / filename
        prepared_path = PREPARED_DIR / filename

        if not prepared_path.exists():
            raise FileNotFoundError(
                f"Prepared file missing: {filename}"
            )

        source_rows = count_rows(source_path)
        prepared_rows = count_rows(prepared_path)

        total_source_rows += source_rows
        total_prepared_rows += prepared_rows

        headers = set(get_headers(prepared_path))
        missing_fields = CANONICAL_FIELDS - headers

        if missing_fields:
            raise ValueError(
                f"{filename} missing canonical fields: "
                f"{sorted(missing_fields)}"
            )

        if prepared_rows != source_rows:
            raise ValueError(
                f"Row count mismatch in {filename}: "
                f"source={source_rows:,}, "
                f"prepared={prepared_rows:,}"
            )

        if primary_id not in headers:
            raise ValueError(
                f"Primary ID missing in prepared {filename}: "
                f"{primary_id}"
            )

        print(
            f"{filename}: PASS | "
            f"rows={prepared_rows:,} | "
            f"canonical fields=OK"
        )

    report_path = PREPARED_DIR / "remediation_report.json"

    if not report_path.exists():
        raise FileNotFoundError(
            "remediation_report.json missing"
        )

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    if report.get("status") != "SUCCESS":
        raise ValueError(
            "Remediation report does not show SUCCESS"
        )

    print()
    print("=== SUMMARY ===")
    print(f"Source rows:   {total_source_rows:,}")
    print(f"Prepared rows: {total_prepared_rows:,}")
    print("Remediation report: SUCCESS")
    print()
    print("OVERALL: PASS")


if __name__ == "__main__":
    main()