import csv
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


SAMPLE_SIZE = 100


def normalize_confidence(value):
    mapping = {
        "HIGH": "High",
        "MEDIUM": "Medium",
        "LOW": "Low",
    }

    if not value:
        return ""

    return mapping.get(value.strip().upper(), value.strip())


def compare_file(filename, primary_id):
    source_path = SOURCE_DIR / filename
    prepared_path = PREPARED_DIR / filename

    with source_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as source_file, prepared_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as prepared_file:

        source_reader = csv.DictReader(source_file)
        prepared_reader = csv.DictReader(prepared_file)

        checked = 0

        for source_row, prepared_row in zip(
            source_reader,
            prepared_reader,
        ):
            source_id = (
                source_row.get(primary_id) or ""
            ).strip()

            prepared_id = (
                prepared_row.get(primary_id) or ""
            ).strip()

            if source_id != prepared_id:
                raise ValueError(
                    f"Primary ID mismatch in {filename}: "
                    f"{source_id} != {prepared_id}"
                )

            if (
                source_row.get("synthetic_flag", "")
                != prepared_row.get("Synthetic_Flag", "")
            ):
                raise ValueError(
                    f"Synthetic_Flag mismatch in {filename}"
                )

            if (
                source_row.get("source_dataset", "")
                != prepared_row.get("Source_Dataset", "")
            ):
                raise ValueError(
                    f"Source_Dataset mismatch in {filename}"
                )

            if (
                source_row.get("source_record_reference", "")
                != prepared_row.get("source_record_reference", "")
            ):
                raise ValueError(
                    f"source_record_reference mismatch in {filename}"
                )

            source_confidence = normalize_confidence(
                source_row.get("confidence", "")
            )

            if (
                source_confidence
                != prepared_row.get("Confidence_Level", "")
            ):
                raise ValueError(
                    f"Confidence_Level mismatch in {filename}"
                )

            if (
                source_row.get("scenario_id", "")
                != prepared_row.get("Generation_Batch_ID", "")
            ):
                raise ValueError(
                    f"Generation_Batch_ID mismatch in {filename}"
                )

            checked += 1

            if checked >= SAMPLE_SIZE:
                break

    return checked


def main():
    print("=== SOURCE vs PREPARED VALIDATION ===")

    total_checked = 0

    for filename, primary_id in PRIMARY_KEYS.items():
        checked = compare_file(
            filename,
            primary_id,
        )

        total_checked += checked

        print(
            f"{filename}: PASS | "
            f"sample rows compared={checked}"
        )

    print()
    print(f"Total rows compared: {total_checked}")
    print("OVERALL: PASS")


if __name__ == "__main__":
    main()