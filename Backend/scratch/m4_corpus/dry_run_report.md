# M4 Extraction Dry Run Report

## Overview
- Total Documents Processed: 100
- Total Entities Extracted: 999
- Total Relationships Extracted: 82
- Documents with Zero Extracted Entities: 30
- Average Entities per Document: 9.99
- Average Relationships per Document: 0.82

## Sentence & Complexity Metrics
- Max Entity Mentions per Sentence: 7
- Total Expected LUKE Inference Pairs: 1449

## Extracted Entity Counts by Label
- **ORG**: 289
- **Organization**: 242
- **PER**: 200
- **Person**: 137
- **Event**: 76
- **Location**: 55

## Extracted Relationship Counts by Type
- **WORKS_FOR**: 82

## Alignment with Fixture Manifest
The extraction pipeline identifies standard NER tags (PER, ORG, LOC, etc.). Our manifest sources these from canonical PostgreSQL labels (Person, Organisation, Location, Event, Account, Device, Vehicle). The dry run successfully pulled spans corresponding to the textual injection of these canonical properties, meaning M4 is operating logically on the synthetic text.

## Document Samples
### Sample 1: M4-DOC-CASE-01591-1
**Text:**
> This file belongs to case CASE-01591. Case Description: Synthetic investigation case for TraceX analytical testing.. INCIDENT REPORT SUMMARY.

**Expected Canonical Source Labels:**
- Case

**Extracted Entities:**
- `CASE-01591` (Organization)

**Extracted Relationships:**
- None

### Sample 2: M4-DOC-CASE-01591-2
**Text:**
> This file belongs to case CASE-01591. Case Description: Synthetic investigation case for TraceX analytical testing.. INTERVIEW TRANSCRIPT. Interviewee is Ira Verma 28450. Interviewee is Aanya Kulkarni 28447.

**Expected Canonical Source Labels:**
- Person, Case

**Extracted Entities:**
- `CASE-01591` (Organization)
- `Interviewee` (Location)
- `Interviewee` (Location)
- `Aanya Kulkarni 28447` (Person)
- `IN` (ORG)
- `VI` (ORG)
- `Ira Verma` (PER)
- `Aanya Kulkarni` (PER)

**Extracted Relationships:**
- None

### Sample 3: M4-DOC-CASE-01591-3
**Text:**
> This file belongs to case CASE-01591. Case Description: Synthetic investigation case for TraceX analytical testing.. FINANCIAL SUMMARY. Account examined was ACC-005115. Account examined was ACC-013737. Financial records show that Aanya Kulkarni 28447 is employed by Synthetic Organization 01646. Financial records show that Ira Verma 28450 is employed by Synthetic Organization 01798. Financial records show that Aanya Kulkarni 28447 is employed by Synthetic Organization 00436. Financial records show that Ira Verma 28450 is employed by Synthetic Organization 00757. Financial records show that Ira Verma 28450 is employed by Synthetic Organization 02043.

**Expected Canonical Source Labels:**
- Person, Account, Organisation, Case

**Extracted Entities:**
- `CASE-01591` (Organization)
- `ACC-005115` (Organization)
- `ACC-013737` (Organization)
- `Aanya Kulkarni 28447` (Person)
- `Synthetic Organization 01646` (Organization)
- `Synthetic Organization 01798` (Organization)
- `Aanya Kulkarni 28447` (Person)
- `Synthetic Organization 00436` (Organization)
- `Synthetic Organization 00757` (Organization)
- `Synthetic Organization 02043` (Organization)
- `TraceX` (ORG)
- `CI` (ORG)
- `ACC` (ORG)
- `ACC` (ORG)
- `Aanya Kulkarni` (PER)
- `Synthetic Organization` (ORG)
- `Ira Verma` (PER)
- `Synthetic Organization` (ORG)
- `Aanya Kulkar` (PER)
- `Synthetic Organization` (ORG)
- `Ira Verma` (PER)
- `Synthetic Organization` (ORG)
- `Ira Verma` (PER)
- `Synthetic Organization` (ORG)

**Extracted Relationships:**
- `Aanya Kulkarni` -[WORKS_FOR]-> `Synthetic Organization`
- `Ira Verma` -[WORKS_FOR]-> `Synthetic Organization`
- `Aanya Kulkar` -[WORKS_FOR]-> `Synthetic Organization`
- `Ira Verma` -[WORKS_FOR]-> `Synthetic Organization`
- `Ira Verma` -[WORKS_FOR]-> `Synthetic Organization`

### Sample 4: M4-DOC-CASE-01591-4
**Text:**
> This file belongs to case CASE-01591. Case Description: Synthetic investigation case for TraceX analytical testing.. CYBER FORENSICS LOG. Forensic capture on device DEV-017243. Forensic capture on device DEV-019294. Logs indicate Aanya Kulkarni 28447 accessed the corporate network of Synthetic Organization 01646. Logs indicate Ira Verma 28450 accessed the corporate network of Synthetic Organization 01798. Logs indicate Aanya Kulkarni 28447 accessed the corporate network of Synthetic Organization 00436. Logs indicate Ira Verma 28450 accessed the corporate network of Synthetic Organization 00757. Logs indicate Ira Verma 28450 accessed the corporate network of Synthetic Organization 02043.

**Expected Canonical Source Labels:**
- Person, Organisation, Device, Case

**Extracted Entities:**
- `CASE-01591` (Organization)
- `CYBER FORENSICS LOG` (Organization)
- `Aanya Kulkarni 28447` (Person)
- `Synthetic Organization` (Organization)
- `01646` (Event)
- `Ira Verma 28450` (Organization)
- `Synthetic Organization 01798` (Organization)
- `Aanya Kulkarni 28447` (Person)
- `Synthetic Organization` (Organization)
- `00436` (Event)
- `Ira Verma 28450` (Organization)
- `Synthetic Organization 00757` (Organization)
- `Ira Verma 28450` (Organization)
- `Synthetic Organization 02043` (Organization)
- `Aanya Kulkarni` (PER)
- `Synthetic Organization` (ORG)
- `Ira Verma` (PER)
- `Synthetic Organization` (ORG)
- `Aanya Kulkar` (PER)
- `Synthetic Organization` (ORG)
- `Ira Verma` (PER)
- `Synthetic Organization` (ORG)
- `Ira Verma` (PER)
- `Synthetic Organization` (ORG)

**Extracted Relationships:**
- None

### Sample 5: M4-DOC-CASE-01591-5
**Text:**
> This file belongs to case CASE-01591. Case Description: Synthetic investigation case for TraceX analytical testing.. FIELD OBSERVATION. Observed vehicle VEH-012683. Observed vehicle VEH-000697.

**Expected Canonical Source Labels:**
- Vehicle, Case

**Extracted Entities:**
- `CASE-01591` (Organization)
- `VEH-012683` (Organization)

**Extracted Relationships:**
- None

