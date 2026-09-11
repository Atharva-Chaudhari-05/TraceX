# M4 Prototype Cases Analysis Report

- Analyzed 20 cases.
- Total unique entities across these cases (including 1-hop): 2262

## Entity Counts by Label
- **Event (PhysicalAccessEvent)**: 1368
- **Event (Transaction)**: 240
- **Device**: 110
- **Account**: 108
- **Phone**: 104
- **Organisation**: 79
- **Location**: 79
- **Vehicle**: 74
- **Person**: 40
- **Event (Incident)**: 20
- **Case**: 20
- **Document**: 20

## Relationship Counts
- **HAS_EVENT**: 1608
- **PARTICIPATED_IN**: 1368
- **USES**: 214
- **OWNS**: 183
- **WORKS_FOR**: 79
- **LOCATED_AT**: 79
- **ASSOCIATED_WITH**: 60
- **INVOLVED_IN**: 40
- **HAS_DOCUMENT**: 20

## Entity Property Fields for M4 Synthetic Evidence
### Account
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, account_id, id
- Human-Readable (Names/Identifiers): None detected

### Case
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, case_id, description, id
- Human-Readable (Names/Identifiers): description

### Device
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, device_id, id
- Human-Readable (Names/Identifiers): None detected

### Document
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, document_id, id, title
- Human-Readable (Names/Identifiers): title

### Event (Incident)
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, incident_id, timestamp
- Human-Readable (Names/Identifiers): None detected

### Event (PhysicalAccessEvent)
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, id, physical_event_id, timestamp
- Human-Readable (Names/Identifiers): None detected

### Event (Transaction)
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, amount, id, timestamp, transaction_id
- Human-Readable (Names/Identifiers): None detected

### Location
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, latitude, location_id, longitude
- Human-Readable (Names/Identifiers): None detected

### Organisation
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, name, organization_id
- Human-Readable (Names/Identifiers): name

### Person
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, name, person_id
- Human-Readable (Names/Identifiers): name

### Phone
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, phone_id, phone_number
- Human-Readable (Names/Identifiers): phone_number

### Vehicle
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, vehicle_id
- Human-Readable (Names/Identifiers): None detected

## Case Breakdown (Direct Connections via INVOLVED_IN)
### CASE-00139
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-002304, PER-002324)

### CASE-00184
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-003235, PER-003233)

### CASE-00349
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-006463, PER-006443)

### CASE-00394
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-007236, PER-007245)

### CASE-00529
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-009651, PER-009628)

### CASE-00564
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-010131, PER-010137)

### CASE-00959
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-017223, PER-017239)

### CASE-01059
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-018958, PER-018950)

### CASE-01084
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-019375, PER-019374)

### CASE-01124
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-020096, PER-020106)

### CASE-01209
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-021845, PER-021869)

### CASE-01269
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-022857, PER-022852)

### CASE-01334
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-023945, PER-023957)

### CASE-01519
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-027182, PER-027179)

### CASE-01584
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-028278, PER-028283)

### CASE-01591
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-028447, PER-028450)

### CASE-01594
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-028494, PER-028498)

### CASE-01664
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-029525, PER-029521)

### CASE-01744
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-031219, PER-031212)

### CASE-01994
- Directly connected entities: 2
  - **Person**: 2 (e.g. PER-035465, PER-035454)

- Analyzed 20 cases.
- Total unique entities across these cases (including 1-hop): 2262

## Entity Counts by Label
- **Event (PhysicalAccessEvent)**: 1368
- **Event (Transaction)**: 240
- **Device**: 110
- **Account**: 108
- **Phone**: 104
- **Organisation**: 79
- **Location**: 79
- **Vehicle**: 74
- **Person**: 40
- **Event (Incident)**: 20
- **Case**: 20
- **Document**: 20

## Relationship Counts
- **HAS_EVENT**: 1608
- **PARTICIPATED_IN**: 1368
- **USES**: 214
- **OWNS**: 183
- **WORKS_FOR**: 79
- **LOCATED_AT**: 79
- **ASSOCIATED_WITH**: 60
- **INVOLVED_IN**: 40
- **HAS_DOCUMENT**: 20

## Entity Property Fields for M4 Synthetic Evidence
### Account
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, account_id, id
- Human-Readable (Names/Identifiers): None detected

### Case
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, case_id, description, id
- Human-Readable (Names/Identifiers): description

### Device
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, device_id, id
- Human-Readable (Names/Identifiers): None detected

### Document
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, document_id, id, title
- Human-Readable (Names/Identifiers): title

### Event (Incident)
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, incident_id, timestamp
- Human-Readable (Names/Identifiers): None detected

### Event (PhysicalAccessEvent)
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, id, physical_event_id, timestamp
- Human-Readable (Names/Identifiers): None detected

### Event (Transaction)
- All populated fields: Audit_Reference, Generation_Batch_ID, Provenance_Mode, Synthetic_Flag, amount, id, timestamp, transaction_id
- Human-Readable (Names/Identifiers): None detected

### Location
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, latitude, location_id, longitude
- Human-Readable (Names/Identifiers): None detected

### Organisation
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, name, organization_id
- Human-Readable (Names/Identifiers): name

### Person
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, name, person_id
- Human-Readable (Names/Identifiers): name

### Phone
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, phone_id, phone_number
- Human-Readable (Names/Identifiers): phone_number

### Vehicle
- All populated fields: Audit_Reference, Provenance_Mode, Synthetic_Flag, id, vehicle_id
- Human-Readable (Names/Identifiers): None detected

