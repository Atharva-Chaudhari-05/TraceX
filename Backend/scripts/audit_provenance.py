import csv
from pathlib import Path
from collections import Counter


DATA_DIR = Path("../TRACEX_DATA")

FIELDS = [
    "synthetic_flag",
    "data_origin",
    "source_dataset",
    "source_record_reference",
    "confidence",
    "scenario_id",
    "relationship_origin",
]


def audit_file(path):
    counters = {field: Counter() for field in FIELDS}

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            for field in FIELDS:
                if field in row:
                    value = row[field].strip() if row[field] else "<NULL>"
                    counters[field][value] += 1

    print(f"\n===== {path.name} =====")

    for field, counter in counters.items():
        if counter:
            total = sum(counter.values())
            nulls = counter.get("<NULL>", 0)

            print(f"\n{field}")
            print(f"  Total: {total:,}")
            print(f"  NULL:  {nulls:,}")

            for value, count in counter.most_common(10):
                print(f"  {value}: {count:,}")


def main():
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    for path in csv_files:
        audit_file(path)


if __name__ == "__main__":
    main()