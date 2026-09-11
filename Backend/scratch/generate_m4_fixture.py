import sys
import os
import json
import csv
from collections import defaultdict
import uuid
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.ingestion.models import CanonicalNodeRecord, CanonicalRelationshipRecord

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184", "CASE-00529",
    "CASE-00959", "CASE-01084", "CASE-01664", "CASE-00564", "CASE-01209",
    "CASE-01334", "CASE-01594", "CASE-00349", "CASE-01269", "CASE-01994",
    "CASE-00139", "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

DOC_TYPES = [
    "Incident Report",
    "Interview Transcript",
    "Financial Summary",
    "Cyber Forensics Log",
    "Field Observation"
]

def generate_fixture():
    out_dir = os.path.join(os.path.dirname(__file__), "m4_corpus")
    os.makedirs(out_dir, exist_ok=True)
    jsonl_path = os.path.join(out_dir, "documents.jsonl")
    manifest_path = os.path.join(out_dir, "manifest.csv")
    report_path = os.path.join(out_dir, "generation_report.md")
    
    with SessionLocal() as db:
        # Pre-fetch all nodes and relationships for the 20 cases to avoid N+1 queries
        print("Fetching graph for cases...")
        
        # 1. Core entities (INVOLVED_IN case)
        involved = db.query(CanonicalRelationshipRecord).filter(
            CanonicalRelationshipRecord.relationship_type == "INVOLVED_IN",
            CanonicalRelationshipRecord.target_id.in_(CASES)
        ).all()
        
        core_ids_by_case = defaultdict(set)
        all_core_ids = set()
        
        rel_tracker = {}
        for r in involved:
            if r.target_id in CASES:
                core_ids_by_case[r.target_id].add(r.source_id)
                all_core_ids.add(r.source_id)
                rel_tracker[r.id] = r
                
        # 2. 1-hop relationships from core entities
        relationships = db.query(CanonicalRelationshipRecord).filter(
            CanonicalRelationshipRecord.source_id.in_(all_core_ids) |
            CanonicalRelationshipRecord.target_id.in_(all_core_ids)
        ).all()
        
        all_node_ids = set(all_core_ids) | set(CASES)
        rels_by_case = defaultdict(list)
        
        for r in relationships:
            rel_tracker[r.id] = r
            all_node_ids.add(r.source_id)
            all_node_ids.add(r.target_id)
            # Assign relationship to case if it touches a core entity of that case
            for case_id, core_ids in core_ids_by_case.items():
                if r.source_id in core_ids or r.target_id in core_ids:
                    rels_by_case[case_id].append(r)
                    
        # 3. Load all canonical nodes
        node_records = db.query(CanonicalNodeRecord).filter(
            CanonicalNodeRecord.canonical_id.in_(all_node_ids)
        ).all()
        
        node_tracker = {n.canonical_id: n for n in node_records}
        
        print(f"Loaded {len(node_tracker)} nodes and {len(rel_tracker)} relationships.")
        
        docs = []
        manifest_rows = []
        
        # Stats
        stats_by_case = defaultdict(int)
        stats_by_doctype = defaultdict(int)
        stats_entity_types = defaultdict(int)
        stats_rel_types = defaultdict(int)
        
        # 4. Generate documents per case
        for case_id in CASES:
            # Gather case subgraph
            case_node_ids = set([case_id]) | core_ids_by_case[case_id]
            for r in rels_by_case[case_id]:
                case_node_ids.add(r.source_id)
                case_node_ids.add(r.target_id)
                
            case_nodes = [node_tracker[nid] for nid in case_node_ids if nid in node_tracker]
            case_rels = rels_by_case[case_id]
            
            # Group by canonical label for easy templating
            nodes_by_label = defaultdict(list)
            for n in case_nodes:
                nodes_by_label[n.canonical_label].append(n)
                
            for dt_idx, doc_type in enumerate(DOC_TYPES):
                doc_id = f"M4-DOC-{case_id}-{dt_idx+1}"
                used_nodes = set([case_id])
                used_rels = set()
                
                lines = []
                
                # Context line
                case_node = node_tracker.get(case_id)
                case_desc = case_node.payload.get("description", "Unknown case description") if case_node else "Unknown"
                lines.append(f"This file belongs to case {case_id}.")
                lines.append(f"Case Description: {case_desc}.")
                
                # Template Logic
                persons = nodes_by_label.get("Person", [])
                orgs = nodes_by_label.get("Organisation", [])
                locs = nodes_by_label.get("Location", [])
                
                if doc_type == "Incident Report":
                    lines.append("INCIDENT REPORT SUMMARY.")
                    incidents = nodes_by_label.get("Event", [])
                    incident_events = [e for e in incidents if e.event_type == "Incident"]
                    for inc in incident_events[:2]:
                        ts = inc.payload.get("timestamp", "unknown time")
                        lines.append(f"An incident occurred on {ts}.")
                        used_nodes.add(inc.canonical_id)
                    # Try to find a LOCATED_AT relation from Org to Loc
                    for r in case_rels:
                        if r.relationship_type == "LOCATED_AT":
                            src = node_tracker.get(r.source_id)
                            tgt = node_tracker.get(r.target_id)
                            if src and tgt and src.canonical_label == "Organisation" and tgt.canonical_label == "Location":
                                src_name = src.payload.get("name", "Unknown Org")
                                tgt_city = tgt.payload.get("city") or tgt.payload.get("latitude")
                                lines.append(f"The organization {src_name} operates facilities in {tgt_city}.")
                                used_nodes.add(src.canonical_id)
                                used_nodes.add(tgt.canonical_id)
                                used_rels.add(r.id)

                elif doc_type == "Interview Transcript":
                    lines.append("INTERVIEW TRANSCRIPT.")
                    for p in persons[:2]:
                        pname = p.payload.get("name", "Unknown Person")
                        lines.append(f"Interviewee is {pname}.")
                        used_nodes.add(p.canonical_id)
                        
                        # Find ASSOCIATED_WITH (Person to Person)
                        for r in case_rels:
                            if r.relationship_type == "ASSOCIATED_WITH" and r.source_id == p.canonical_id:
                                tgt = node_tracker.get(r.target_id)
                                if tgt and tgt.canonical_label == "Person":
                                    tgt_name = tgt.payload.get("name", "Unknown Person")
                                    lines.append(f"During the interview, {pname} admitted to being associated with {tgt_name}.")
                                    used_nodes.add(tgt.canonical_id)
                                    used_rels.add(r.id)

                elif doc_type == "Financial Summary":
                    lines.append("FINANCIAL SUMMARY.")
                    accounts = nodes_by_label.get("Account", [])
                    for acc in accounts[:2]:
                        acc_id = acc.payload.get("account_id", "Unknown Account")
                        lines.append(f"Account examined was {acc_id}.")
                        used_nodes.add(acc.canonical_id)
                        
                    # Find WORKS_FOR (Person to Organisation)
                    for r in case_rels:
                        if r.relationship_type == "WORKS_FOR":
                            src = node_tracker.get(r.source_id)
                            tgt = node_tracker.get(r.target_id)
                            if src and tgt and src.canonical_label == "Person" and tgt.canonical_label == "Organisation":
                                src_name = src.payload.get("name", "Unknown Person")
                                tgt_name = tgt.payload.get("name", "Unknown Org")
                                lines.append(f"Financial records show that {src_name} is employed by {tgt_name}.")
                                used_nodes.add(src.canonical_id)
                                used_nodes.add(tgt.canonical_id)
                                used_rels.add(r.id)

                elif doc_type == "Cyber Forensics Log":
                    lines.append("CYBER FORENSICS LOG.")
                    devices = nodes_by_label.get("Device", [])
                    for dev in devices[:2]:
                        lines.append(f"Forensic capture on device {dev.payload.get('device_id')}.")
                        used_nodes.add(dev.canonical_id)
                        
                    # Reuse WORKS_FOR but different phrasing
                    for r in case_rels:
                        if r.relationship_type == "WORKS_FOR":
                            src = node_tracker.get(r.source_id)
                            tgt = node_tracker.get(r.target_id)
                            if src and tgt and src.canonical_label == "Person" and tgt.canonical_label == "Organisation":
                                src_name = src.payload.get("name", "Unknown Person")
                                tgt_name = tgt.payload.get("name", "Unknown Org")
                                lines.append(f"Logs indicate {src_name} accessed the corporate network of {tgt_name}.")
                                used_nodes.add(src.canonical_id)
                                used_nodes.add(tgt.canonical_id)
                                used_rels.add(r.id)

                elif doc_type == "Field Observation":
                    lines.append("FIELD OBSERVATION.")
                    vehicles = nodes_by_label.get("Vehicle", [])
                    for veh in vehicles[:2]:
                        lines.append(f"Observed vehicle {veh.payload.get('vehicle_id')}.")
                        used_nodes.add(veh.canonical_id)
                    
                    # LOCATED_AT relation (Organisation to Location)
                    for r in case_rels:
                        if r.relationship_type == "LOCATED_AT":
                            src = node_tracker.get(r.source_id)
                            tgt = node_tracker.get(r.target_id)
                            if src and tgt and src.canonical_label == "Organisation" and tgt.canonical_label == "Location":
                                src_name = src.payload.get("name", "Unknown Org")
                                tgt_city = tgt.payload.get("city") or tgt.payload.get("latitude")
                                lines.append(f"Field agents surveilled {src_name} at their headquarters in {tgt_city}.")
                                used_nodes.add(src.canonical_id)
                                used_nodes.add(tgt.canonical_id)
                                used_rels.add(r.id)

                if len(lines) <= 2: # Just the case description
                    lines.append("No specific entities of this type were found for this case.")
                    lines.append("General observation concluded.")

                text_content = " ".join(lines)
                
                doc_record = {
                    "document_id": doc_id,
                    "case_id": case_id,
                    "document_type": doc_type,
                    "Generation_Batch_ID": "M4_FIXTURE_GEN",
                    "Source_Dataset": "M4_FIXTURE",
                    "Provenance_Mode": "synthetic-design",
                    "source_record_reference": None,
                    "Synthetic_Flag": True,
                    "Audit_Reference": f"AUDIT-m4-fixture-{doc_id}",
                    "text": text_content
                }
                
                docs.append(doc_record)
                
                # Update Stats
                stats_by_case[case_id] += 1
                stats_by_doctype[doc_type] += 1
                for nid in used_nodes:
                    stats_entity_types[node_tracker[nid].canonical_label] += 1
                for rid in used_rels:
                    stats_rel_types[rel_tracker[rid].relationship_type] += 1
                
                manifest_rows.append({
                    "document_id": doc_id,
                    "case_id": case_id,
                    "source_entity_ids": ";".join(sorted(list(used_nodes))),
                    "source_relationship_ids": ";".join(sorted([str(rid) for rid in used_rels])),
                    "text_preview": text_content[:50] + "..."
                })

        # Write outputs
        with open(jsonl_path, "w") as f:
            for d in docs:
                f.write(json.dumps(d) + "\n")
                
        with open(manifest_path, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["document_id", "case_id", "source_entity_ids", "source_relationship_ids", "text_preview"])
            writer.writeheader()
            writer.writerows(manifest_rows)
            
        with open(report_path, "w") as f:
            f.write("# M4 Generation Report\n\n")
            f.write(f"- Total Cases: {len(CASES)}\n")
            f.write(f"- Total Documents Generated: {len(docs)}\n\n")
            
            f.write("## Documents by Case\n")
            for c, cnt in sorted(stats_by_case.items()):
                f.write(f"- {c}: {cnt}\n")
            f.write("\n")
            
            f.write("## Documents by Type\n")
            for dt, cnt in sorted(stats_by_doctype.items()):
                f.write(f"- {dt}: {cnt}\n")
            f.write("\n")
            
            f.write("## Unique Entities Referenced (Frequency)\n")
            for et, cnt in sorted(stats_entity_types.items(), key=lambda x: -x[1]):
                f.write(f"- {et}: {cnt}\n")
            f.write("\n")
            
            f.write("## Unique Relationships Referenced (Frequency)\n")
            for rt, cnt in sorted(stats_rel_types.items(), key=lambda x: -x[1]):
                f.write(f"- {rt}: {cnt}\n")

        print(f"Generated {len(docs)} documents to {jsonl_path}.")
        print(f"Manifest saved to {manifest_path}.")
        print(f"Report saved to {report_path}.")

if __name__ == "__main__":
    generate_fixture()
