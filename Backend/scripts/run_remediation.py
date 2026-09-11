import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.ingestion.remediation import (
    build_audit_reference,
    normalize_confidence,
)

BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = BASE_DIR.parent / "TRACEX_DATA"
OUTPUT_DIR = BASE_DIR.parent / "TRACEX_PREPARED"
SPEC_PATH = BASE_DIR / "backend" / "app" / "ingestion" / "remediation_spec.json"

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


def load_spec():
    with SPEC_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


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

    output["Generation_Batch_ID"] = output.pop(
        "scenario_id",
        "",
    )

    output["Confidence_Level"] = normalize_confidence(
        output.pop("confidence", "")
    )

    output["Provenance_Mode"] = "synthetic-design"

    if filename == "relationships.csv":
        output["relationship_type_tag"] = "design_synthetic"

    output["Audit_Reference"] = build_audit_reference(
        filename,
        row.get(primary_id, ""),
    )

    return output


def process_file(filename, primary_id):
    source_path = SOURCE_DIR / filename
    output_path = OUTPUT_DIR / filename

    rows_read = 0
    rows_written = 0

    with source_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as source_file:

        reader = csv.DictReader(source_file)

        if not reader.fieldnames:
            raise ValueError(
                f"No header found: {filename}"
            )

        if primary_id not in reader.fieldnames:
            raise ValueError(
                f"Missing primary ID '{primary_id}' "
                f"in {filename}"
            )

        first_row = next(reader, None)

        if first_row is None:
            raise ValueError(
                f"Empty data file: {filename}"
            )

        first_transformed = transform_row(
            first_row,
            filename,
            primary_id,
        )

        output_fields = list(first_transformed.keys())

        with output_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as output_file:

            writer = csv.DictWriter(
                output_file,
                fieldnames=output_fields,
                extrasaction="ignore",
            )

            writer.writeheader()

            writer.writerow(first_transformed)

            rows_read += 1
            rows_written += 1

            for row in reader:
                transformed = transform_row(
                    row,
                    filename,
                    primary_id,
                )

                if (
                    transformed.get(primary_id)
                    != row.get(primary_id)
                ):
                    raise ValueError(
                        f"Primary ID changed in {filename}"
                    )

                writer.writerow(transformed)

                rows_read += 1
                rows_written += 1

    if rows_read != rows_written:
        raise ValueError(
            f"Row count mismatch in {filename}"
        )

    return rows_read, rows_written


def main():
    spec = load_spec()

    if not SOURCE_DIR.exists():
        raise FileNotFoundError(
            f"Source directory not found: {SOURCE_DIR}"
        )

    if spec["execution_policy"]["overwrite_source"]:
        raise RuntimeError(
            "Safety check failed: overwrite_source must be false."
        )

    if OUTPUT_DIR.exists():
        raise RuntimeError(
            f"Output directory already exists: {OUTPUT_DIR}\n"
            "Delete or rename it manually before running again."
        )

    OUTPUT_DIR.mkdir(parents=True)

    report = {
        "status": "SUCCESS",
        "source_directory": str(SOURCE_DIR),
        "output_directory": str(OUTPUT_DIR),
        "source_unchanged": True,
        "files": {},
    }

    try:
        print("=== TRACEX FULL REMEDIATION ===")
        print(f"Source: {SOURCE_DIR}")
        print(f"Output: {OUTPUT_DIR}")
        print()

        for filename, primary_id in PRIMARY_KEYS.items():
            print(f"Processing {filename}...")

            rows_read, rows_written = process_file(
                filename,
                primary_id,
            )

            report["files"][filename] = {
                "rows_read": rows_read,
                "rows_written": rows_written,
                "primary_key": primary_id,
            }

            print(
                f"  PASS | "
                f"rows={rows_written:,}"
            )

        report_path = (
            OUTPUT_DIR / "remediation_report.json"
        )

        with report_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=2,
            )

        print()
        print("=== REMEDIATION COMPLETE ===")
        print("OVERALL: PASS")
        print(f"Output: {OUTPUT_DIR}")

    except Exception:
        report["status"] = "FAILED"

        with (
            OUTPUT_DIR / "remediation_report.json"
        ).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=2,
            )

        print()
        print("REMEDIATION FAILED")
        print("The source dataset was not modified.")

        raise


if __name__ == "__main__":
    main()