"""
Extract 20-case subset using relationship-based graph traversal.
Persons/phones etc have no scenario_id — we must trace through relationships.
"""
import csv
import os
import sys
import shutil
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("D:/TraceX/TRACEX_DATA")
OUTPUT_DIR = Path("D:/TraceX/Backend/scratch/demo_a_20cases")

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184", "CASE-00529",
    "CASE-00959", "CASE-01084", "CASE-01664", "CASE-00564", "CASE-01209",
    "CASE-01334", "CASE-01594", "CASE-00349", "CASE-01269", "CASE-01994",
    "CASE-00139", "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]
case_set = set(CASES)

print("=== STEP 1: Trace all entity IDs reachable from the 20 cases via relationships.csv ===")

# Load all relationships, build adjacency maps
rel_rows = []
all_scenario_ids = set()
entities_by_type = defaultdict(set)  # type -> set of ids

# First pass: load ALL relationships (3M file but manageable)
with open(DATA_DIR / "relationships.csv", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        src_type = row["source_entity_type"]
        src_id = row["source_entity_id"]
        tgt_type = row["target_entity_type"]
        tgt_id = row["target_entity_id"]
        rel_type = row["relationship_type"]
        if src_id in case_set or tgt_id in case_set:
            rel_rows.append(row)
            entities_by_type[src_type].add(src_id)
            entities_by_type[tgt_type].add(tgt_id)

print(f"  Relationships touching our 20 cases: {len(rel_rows)}")
print(f"  Entity types found: {dict({k: len(v) for k, v in entities_by_type.items()})}")

# Collect all entity IDs by type
person_ids = entities_by_type.get("Person", set())
incident_ids = entities_by_type.get("Incident", set())
document_ids = entities_by_type.get("Document", set())

print(f"  Persons: {len(person_ids)}")
print(f"  Incidents: {len(incident_ids)}")
print(f"  Documents: {len(document_ids)}")

# Now trace second hop: what do persons connect to?
print("\n=== STEP 2: Two-hop traversal for person-linked entities ===")
person_linked_entities = defaultdict(set)
with open(DATA_DIR / "relationships.csv", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        src_id = row["source_entity_id"]
        tgt_id = row["target_entity_id"]
        src_type = row["source_entity_type"]
        tgt_type = row["target_entity_type"]
        if src_id in person_ids or tgt_id in person_ids:
            person_linked_entities[src_type].add(src_id)
            person_linked_entities[tgt_type].add(tgt_id)

for t, ids in person_linked_entities.items():
    print(f"  {t}: {len(ids)}")

# Collect ALL IDs we need per entity type
needed = defaultdict(set)
needed["Case"] = case_set
needed["Person"] = person_ids | person_linked_entities.get("Person", set())
needed["Incident"] = incident_ids | person_linked_entities.get("Incident", set())
needed["Document"] = document_ids | person_linked_entities.get("Document", set())
needed["Account"] = person_linked_entities.get("Account", set())
needed["Phone"] = person_linked_entities.get("Phone", set())
needed["Device"] = person_linked_entities.get("Device", set())
needed["Location"] = person_linked_entities.get("Location", set())
needed["Organisation"] = person_linked_entities.get("Organisation", set())
needed["Vehicle"] = person_linked_entities.get("Vehicle", set())
# For events — use scenario_id based on cases
scenario_set = set()
with open(DATA_DIR / "cases.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["case_id"] in case_set:
            scenario_set.add(row["scenario_id"])

print(f"\n=== STEP 3: Writing filtered subset to {OUTPUT_DIR} ===")

if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True)

def write_filtered(fname, id_field, id_set, label=""):
    src = DATA_DIR / fname
    dst = OUTPUT_DIR / fname
    if not src.exists():
        print(f"  SKIP {fname}")
        return 0
    count = 0
    with open(src, encoding="utf-8", newline="") as fin, \
         open(dst, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row[id_field] in id_set:
                writer.writerow(row)
                count += 1
    print(f"  {fname}: {count} rows")
    return count

def write_scenario_filtered(fname, scenario_col="scenario_id"):
    src = DATA_DIR / fname
    dst = OUTPUT_DIR / fname
    if not src.exists():
        print(f"  SKIP {fname}")
        return 0
    count = 0
    with open(src, encoding="utf-8", newline="") as fin, \
         open(dst, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row.get(scenario_col, "") in scenario_set:
                writer.writerow(row)
                count += 1
    print(f"  {fname}: {count} rows")
    return count

# Entity files
write_filtered("cases.csv", "case_id", case_set)
write_filtered("persons.csv", "person_id", needed["Person"])
write_filtered("accounts.csv", "account_id", needed["Account"])
write_filtered("phones.csv", "phone_id", needed["Phone"])
write_filtered("devices.csv", "device_id", needed["Device"])
write_filtered("locations.csv", "location_id", needed["Location"])
write_filtered("organizations.csv", "organization_id", needed["Organisation"])
write_filtered("vehicles.csv", "vehicle_id", needed["Vehicle"])
write_filtered("documents.csv", "document_id", needed["Document"])

# Incidents — filter by incident_id
write_filtered("incidents.csv", "incident_id", needed["Incident"])

# Events — filter by scenario_id (they're tagged per scenario)
write_scenario_filtered("transactions.csv")
write_scenario_filtered("communication_events.csv")
write_scenario_filtered("physical_access_events.csv")
write_scenario_filtered("network_events.csv")

# Relationships — write only those already in rel_rows (case-touching + person-hop)
rel_dst = OUTPUT_DIR / "relationships.csv"
with open(DATA_DIR / "relationships.csv", encoding="utf-8", newline="") as fin, \
     open(rel_dst, "w", encoding="utf-8", newline="") as fout:
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
    writer.writeheader()
    count = 0
    all_needed = set()
    for ids in needed.values():
        all_needed |= ids
    for row in reader:
        if row["source_entity_id"] in all_needed or row["target_entity_id"] in all_needed:
            writer.writerow(row)
            count += 1
print(f"  relationships.csv: {count} rows")

# crime_context is reference — copy as-is
shutil.copy(DATA_DIR / "crime_context.csv", OUTPUT_DIR / "crime_context.csv")
print(f"  crime_context.csv: copied as reference data")

print(f"\n=== COMPLETE — Subset written to {OUTPUT_DIR} ===")
print(f"Full TRACEX_DATA: NOT modified. NOT fully ingested.")
