import csv
from pathlib import Path
from collections import Counter


DATA_DIR = Path("../TRACEX_DATA")


ENTITY_FILES = {
    "PERSON": ("persons.csv", "person_id"),
    "PHONE": ("phones.csv", "phone_id"),
    "ACCOUNT": ("accounts.csv", "account_id"),
    "DEVICE": ("devices.csv", "device_id"),
    "LOCATION": ("locations.csv", "location_id"),
    "ORGANIZATION": ("organizations.csv", "organization_id"),
    "ORGANISATION": ("organizations.csv", "organization_id"),
    "VEHICLE": ("vehicles.csv", "vehicle_id"),
    "DOCUMENT": ("documents.csv", "document_id"),
    "CASE": ("cases.csv", "case_id"),
    "EVENT": None,
    "INCIDENT": ("incidents.csv", "incident_id"),
    "TRANSACTION": ("transactions.csv", "transaction_id"),
    "COMMUNICATIONEVENT": ("communication_events.csv", "communication_id"),
    "NETWORKEVENT": ("network_events.csv", "network_event_id"),
    "PHYSICALACCESSEVENT": (
        "physical_access_events.csv",
        "physical_event_id",
    ),
}


VALID_RELATIONSHIPS = {
    "ASSOCIATED_WITH",
    "COMMUNICATES_WITH",
    "CONNECTED_TO",
    "HAS_DOCUMENT",
    "HAS_EVENT",
    "INVOLVED_IN",
    "LOCATED_AT",
    "OWNS",
    "PARTICIPATED_IN",
    "TRANSFERRED_TO",
    "USES",
    "WORKS_FOR",
}


def normalize_type(value):
    return "".join(
        character
        for character in (value or "").strip().upper()
        if character.isalnum()
    )


def load_ids(filename, field):
    ids = set()

    with (DATA_DIR / filename).open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            value = (row.get(field) or "").strip()

            if value:
                ids.add(value)

    return ids


def main():
    print("=== LOADING ENTITY IDS ===")

    entity_ids = {}

    for entity_type, mapping in ENTITY_FILES.items():
        if mapping is None:
            continue

        filename, field = mapping
        entity_ids[entity_type] = load_ids(filename, field)

        print(
            f"{entity_type}: "
            f"{len(entity_ids[entity_type]):,} IDs loaded"
        )

    print("\n=== RELATIONSHIP INTEGRITY ===")

    relationship_counts = Counter()
    invalid_types = Counter()
    invalid_source_types = Counter()
    invalid_target_types = Counter()
    missing_sources = 0
    missing_targets = 0
    empty_source_fields = 0
    empty_target_fields = 0

    path = DATA_DIR / "relationships.csv"

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            source_type = normalize_type(row.get("source_entity_type"))
            target_type = normalize_type(row.get("target_entity_type"))
            relationship_type = (
                row.get("relationship_type") or ""
            ).strip().upper()

            source_id = (row.get("source_entity_id") or "").strip()
            target_id = (row.get("target_entity_id") or "").strip()

            relationship_counts[relationship_type] += 1

            if relationship_type not in VALID_RELATIONSHIPS:
                invalid_types[relationship_type] += 1

            if not source_type or not source_id:
                empty_source_fields += 1
            elif source_type not in entity_ids:
                invalid_source_types[source_type] += 1
            elif source_id not in entity_ids[source_type]:
                missing_sources += 1

            if not target_type or not target_id:
                empty_target_fields += 1
            elif target_type not in entity_ids:
                invalid_target_types[target_type] += 1
            elif target_id not in entity_ids[target_type]:
                missing_targets += 1

    print("\nRelationship types:")

    for relationship_type, count in relationship_counts.most_common():
        status = (
            "PASS"
            if relationship_type in VALID_RELATIONSHIPS
            else "CHECK"
        )

        print(
            f"  {relationship_type}: "
            f"{count:,} | {status}"
        )

    print("\nIntegrity summary:")

    print(
        f"  Invalid relationship types: "
        f"{sum(invalid_types.values()):,}"
    )

    print(
        f"  Invalid source entity types: "
        f"{sum(invalid_source_types.values()):,}"
    )

    print(
        f"  Invalid target entity types: "
        f"{sum(invalid_target_types.values()):,}"
    )

    print(
        f"  Missing source IDs: "
        f"{missing_sources:,}"
    )

    print(
        f"  Missing target IDs: "
        f"{missing_targets:,}"
    )

    print(
        f"  Empty source fields: "
        f"{empty_source_fields:,}"
    )

    print(
        f"  Empty target fields: "
        f"{empty_target_fields:,}"
    )

    total_errors = (
        sum(invalid_types.values())
        + sum(invalid_source_types.values())
        + sum(invalid_target_types.values())
        + missing_sources
        + missing_targets
        + empty_source_fields
        + empty_target_fields
    )

    print(
        "\nOVERALL:",
        "PASS" if total_errors == 0 else "CHECK",
    )


if __name__ == "__main__":
    main()