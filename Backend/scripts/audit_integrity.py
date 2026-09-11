import csv
from pathlib import Path


DATA_DIR = Path("../TRACEX_DATA")


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


REFERENCES = {
    "accounts.csv": {
        "owner_person_id": ("persons.csv", "person_id"),
        "organization_id": ("organizations.csv", "organization_id"),
    },
    "cases.csv": {},
    "communication_events.csv": {
        "source_person_id": ("persons.csv", "person_id"),
        "target_person_id": ("persons.csv", "person_id"),
        "source_phone_id": ("phones.csv", "phone_id"),
        "target_phone_id": ("phones.csv", "phone_id"),
        "source_device_id": ("devices.csv", "device_id"),
        "target_device_id": ("devices.csv", "device_id"),
        "location_id": ("locations.csv", "location_id"),
    },
    "documents.csv": {
        "case_id": ("cases.csv", "case_id"),
    },
    "incidents.csv": {
        "location_id": ("locations.csv", "location_id"),
    },
    "locations.csv": {},
    "network_events.csv": {
        "source_device_id": ("devices.csv", "device_id"),
        "destination_device_id": ("devices.csv", "device_id"),
        "location_id": ("locations.csv", "location_id"),
    },
    "organizations.csv": {
        "location_id": ("locations.csv", "location_id"),
    },
    "persons.csv": {
        "organization_id": ("organizations.csv", "organization_id"),
        "primary_location_id": ("locations.csv", "location_id"),
    },
    "phones.csv": {},
    "physical_access_events.csv": {
        "person_id": ("persons.csv", "person_id"),
        "location_id": ("locations.csv", "location_id"),
    },
    "relationships.csv": {},
    "transactions.csv": {
        "sender_account_id": ("accounts.csv", "account_id"),
        "receiver_account_id": ("accounts.csv", "account_id"),
    },
    "vehicles.csv": {},
    "crime_context.csv": {},
}


def load_ids(filename, field):
    ids = set()
    duplicates = 0

    path = DATA_DIR / filename

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            value = (row.get(field) or "").strip()

            if not value:
                continue

            if value in ids:
                duplicates += 1
            else:
                ids.add(value)

    return ids, duplicates


def main():
    print("=== PRIMARY KEY UNIQUENESS ===")

    id_sets = {}

    for filename, field in PRIMARY_KEYS.items():
        ids, duplicates = load_ids(filename, field)
        id_sets[filename] = ids

        status = "PASS" if duplicates == 0 else "FAIL"

        print(
            f"{filename}: {status} | "
            f"unique={len(ids):,} | duplicates={duplicates:,}"
        )

    print("\n=== REFERENTIAL INTEGRITY ===")

    for source_file, references in REFERENCES.items():
        for source_field, (target_file, target_field) in references.items():

            target_ids = id_sets[target_file]
            missing = 0

            path = DATA_DIR / source_file

            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    value = (row.get(source_field) or "").strip()

                    if value and value not in target_ids:
                        missing += 1

            status = "PASS" if missing == 0 else "CHECK"

            print(
                f"{source_file}.{source_field} -> "
                f"{target_file}.{target_field}: "
                f"{status} | missing={missing:,}"
            )


if __name__ == "__main__":
    main()