import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.ingestion.remediation import (
    transform_row,
    validate_source_file,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR.parent / "TRACEX_DATA"


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


SAMPLE_SIZE = 25


def validate_file(filename, primary_id):
    path = DATA_DIR / filename

    validate_source_file(path, primary_id)

    checked = 0

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            original_id = (row.get(primary_id) or "").strip()

            transformed = transform_row(
                row,
                filename,
                primary_id,
            )

            if not original_id:
                raise ValueError(
                    f"Empty primary ID in {filename}"
                )

            if transformed.get(primary_id) != original_id:
                raise ValueError(
                    f"Primary ID changed in {filename}"
                )

            if not transformed.get("Audit_Reference"):
                raise ValueError(
                    f"Missing Audit_Reference in {filename}"
                )

            if transformed.get("Synthetic_Flag") == "":
                raise ValueError(
                    f"Missing Synthetic_Flag in {filename}"
                )

            if transformed.get("Confidence_Level") not in {
                "High",
                "Medium",
                "Low",
            }:
                raise ValueError(
                    f"Invalid Confidence_Level in {filename}: "
                    f"{transformed.get('Confidence_Level')}"
                )

            if transformed.get("Provenance_Mode") not in {
                "direct",
                "validated-join",
                "synthetic-design",
            }:
                raise ValueError(
                    f"Invalid Provenance_Mode in {filename}"
                )

            checked += 1

            if checked >= SAMPLE_SIZE:
                break

    return checked


def main():
    print("=== ALL-FILE REMEDIATION VALIDATION ===")

    total_checked = 0

    for filename, primary_id in PRIMARY_KEYS.items():
        checked = validate_file(
            filename,
            primary_id,
        )

        total_checked += checked

        print(
            f"{filename}: PASS | "
            f"sample rows checked={checked}"
        )

    print("\nOVERALL: PASS")
    print(f"Total sample rows checked: {total_checked}")


if __name__ == "__main__":
    main()