import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[4]
SPEC_PATH = Path(__file__).resolve().parent / "remediation_spec.json"

def load_spec():
    with SPEC_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_confidence(value):
    if not value:
        return ""

    value = value.strip().upper()

    mapping = {
        "HIGH": "High",
        "MEDIUM": "Medium",
        "LOW": "Low",
    }

    return mapping.get(value, value)


def build_audit_reference(filename, record_id):
    stem = Path(filename).stem
    return f"AUDIT-{stem}-{record_id}"


def transform_row(row, filename, primary_id):
    output = dict(row)

    output["Synthetic_Flag"] = output.pop(
        "synthetic_flag",
        "",
    )

    output["Source_Dataset"] = output.get(
        "source_dataset",
        "",
    )

    output["source_record_reference"] = output.get(
        "source_record_reference",
        "",
    )

    output["Generation_Batch_ID"] = output.pop(
        "scenario_id",
        "",
    )

    output["Confidence_Level"] = normalize_confidence(
        output.pop("confidence", "")
    )

    if filename == "relationships.csv":
        output["Provenance_Mode"] = "synthetic-design"
        output["relationship_type_tag"] = "design_synthetic"
    else:
        output["Provenance_Mode"] = "synthetic-design"

    output["Audit_Reference"] = build_audit_reference(
        filename,
        row.get(primary_id, ""),
    )

    return output


def validate_source_file(path, primary_id):
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(f"No header found: {path.name}")

        if primary_id not in reader.fieldnames:
            raise ValueError(
                f"Missing primary ID '{primary_id}' in {path.name}"
            )


def dry_run_file(path, primary_id, sample_size=10):
    validate_source_file(path, primary_id)

    rows_checked = 0

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            transformed = transform_row(
                row,
                path.name,
                primary_id,
            )

            if not transformed.get("Audit_Reference"):
                raise ValueError(
                    f"Missing Audit_Reference in {path.name}"
                )

            rows_checked += 1

            if rows_checked >= sample_size:
                break

    return rows_checked


def main():
    spec = load_spec()

    print("TraceX remediation module loaded")
    print(f"Source: {spec['source_directory']}")
    print(f"Output: {spec['output_directory']}")
    print(
        "Overwrite source:",
        spec["execution_policy"]["overwrite_source"],
    )

    print("\nDry-run sample validation:")

    entity_mappings = spec["field_mappings"]

    for filename in [
        "persons.csv",
        "accounts.csv",
        "documents.csv",
        "communication_events.csv",
        "relationships.csv",
    ]:
        mapping = None

        if filename in entity_mappings:
            mapping = entity_mappings[filename]

        if filename == "relationships.csv":
            primary_id = "relationship_id"
        elif filename == "communication_events.csv":
            primary_id = "communication_id"
        elif filename == "persons.csv":
            primary_id = "person_id"
        elif filename == "accounts.csv":
            primary_id = "account_id"
        elif filename == "documents.csv":
            primary_id = "document_id"
        else:
            continue

        source_path = BASE_DIR / "TRACEX_DATA" / filename

        checked = dry_run_file(
            source_path,
            primary_id,
        )

        print(
            f"  {filename}: PASS | "
            f"sample rows checked={checked}"
        )


if __name__ == "__main__":
    main()