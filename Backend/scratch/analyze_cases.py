import sys
import os
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.ingestion.models import CanonicalNodeRecord, CanonicalRelationshipRecord

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184", "CASE-00529",
    "CASE-00959", "CASE-01084", "CASE-01664", "CASE-00564", "CASE-01209",
    "CASE-01334", "CASE-01594", "CASE-00349", "CASE-01269", "CASE-01994",
    "CASE-00139", "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

def analyze_cases():
    from scripts.run_demo_projection import build_case_subgraph, load_nodes
    with SessionLocal() as db:
        node_ids, relationships = build_case_subgraph(db, CASES)
        nodes = load_nodes(db, list(node_ids))
        
        all_unique_entities = set(node_ids)
        
        label_counts = defaultdict(int)
        fields_by_label = defaultdict(set)
        human_readable_hints = defaultdict(set)
        
        human_readable_keys = ["name", "title", "description", "address", "city", "state", "country", "phone_number", "account_number", "email", "type", "make", "model", "license_plate", "vin", "category", "number"]
        
        node_types = {}
        for node in nodes:
            label = node.canonical_label
            if label == "Event" and node.event_type:
                label = f"Event ({node.event_type})"
            label_counts[label] += 1
            node_types[node.canonical_id] = label
            
            payload = node.payload
            for k, v in payload.items():
                if v is not None and str(v).strip() != "":
                    fields_by_label[label].add(k)
                    if any(hk in k.lower() for hk in human_readable_keys):
                        human_readable_hints[label].add(k)
                        
        case_to_entities = defaultdict(set)
        
        involved = db.query(
            CanonicalRelationshipRecord.source_id,
            CanonicalRelationshipRecord.target_id
        ).filter(
            CanonicalRelationshipRecord.relationship_type == "INVOLVED_IN",
            CanonicalRelationshipRecord.target_id.in_(CASES)
        ).all()
        
        for source_id, target_id in involved:
            if target_id in CASES:
                case_to_entities[target_id].add(source_id)

        rel_counts = defaultdict(int)
        for rel in relationships:
            rel_counts[rel.relationship_type] += 1
            
        report_path = os.path.join(os.path.dirname(__file__), "m4_analysis_report.md")
        with open(report_path, "w") as f:
            f.write("# M4 Prototype Cases Analysis Report\n\n")
            f.write(f"- Analyzed {len(CASES)} cases.\n")
            f.write(f"- Total unique entities across these cases (including 1-hop): {len(all_unique_entities)}\n\n")
            
            f.write("## Entity Counts by Label\n")
            for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
                f.write(f"- **{label}**: {count}\n")
            f.write("\n")
            
            f.write("## Relationship Counts\n")
            for rel_type, count in sorted(rel_counts.items(), key=lambda x: -x[1]):
                f.write(f"- **{rel_type}**: {count}\n")
            f.write("\n")
            
            f.write("## Entity Property Fields for M4 Synthetic Evidence\n")
            for label in sorted(fields_by_label.keys()):
                fields = sorted(list(fields_by_label[label]))
                human_fields = sorted(list(human_readable_hints[label]))
                f.write(f"### {label}\n")
                f.write(f"- All populated fields: {', '.join(fields)}\n")
                f.write(f"- Human-Readable (Names/Identifiers): {', '.join(human_fields) if human_fields else 'None detected'}\n\n")
                
            f.write("## Case Breakdown (Direct Connections via INVOLVED_IN)\n")
            for case_id in sorted(CASES):
                entities = case_to_entities[case_id]
                f.write(f"### {case_id}\n")
                f.write(f"- Directly connected entities: {len(entities)}\n")
                ent_by_type = defaultdict(list)
                for eid in entities:
                    ent_by_type[node_types.get(eid, "Unknown")].append(eid)
                for t, eids in sorted(ent_by_type.items()):
                    f.write(f"  - **{t}**: {len(eids)} (e.g. {', '.join(eids[:3])}{'...' if len(eids) > 3 else ''})\n")
                f.write("\n")
            f.write(f"- Analyzed {len(CASES)} cases.\n")
            f.write(f"- Total unique entities across these cases (including 1-hop): {len(all_unique_entities)}\n\n")
            
            f.write("## Entity Counts by Label\n")
            for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
                f.write(f"- **{label}**: {count}\n")
            f.write("\n")
            
            f.write("## Relationship Counts\n")
            for rel_type, count in sorted(rel_counts.items(), key=lambda x: -x[1]):
                f.write(f"- **{rel_type}**: {count}\n")
            f.write("\n")
            
            f.write("## Entity Property Fields for M4 Synthetic Evidence\n")
            for label in sorted(fields_by_label.keys()):
                fields = sorted(list(fields_by_label[label]))
                human_fields = sorted(list(human_readable_hints[label]))
                f.write(f"### {label}\n")
                f.write(f"- All populated fields: {', '.join(fields)}\n")
                f.write(f"- Human-Readable (Names/Identifiers): {', '.join(human_fields) if human_fields else 'None detected'}\n\n")
                
        print(f"\n--- M4 Analysis Summary ---")
        print(f"Analyzed {len(CASES)} cases (matched DEFAULT_CASES from run_demo_projection.py).")
        print(f"Total unique connected entities (1-hop): {len(all_unique_entities)}")
        print("\nNode Counts:")
        for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
            print(f"  {label}: {count}")
        print("\nRelationship Counts:")
        for rel_type, count in sorted(rel_counts.items(), key=lambda x: -x[1]):
            print(f"  {rel_type}: {count}")
        print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    analyze_cases()
