import {
  Entity,
  EvidenceRecord,
  DataSourceItem,
  TimelineEvent,
  AIInsight,
  EntityMatchItem,
  GraphNode,
  GraphEdge,
  PatternItem,
} from '../types';

export const CASE_METADATA = {
  name: 'Operation Nexus: Hawala & Financial Structuring',
  caseId: 'CASE-NX-2026-001',
  status: 'ACTIVE',
  priority: 'CRITICAL',
  leadInvestigator: 'Insp. V. Kulkarni (Special Task Force - Central Command)',
  caseOfficer: 'Insp. V. Kulkarni',
  openedDate: '12 May 2026',
  jurisdiction: 'Cyber & Financial Crimes Investigation Wing',
  classification: 'RESTRICTED // LAW ENFORCEMENT SENSITIVE // OFFICIAL SUBMISSION',
  description:
    'A coordinated cross-network probe into illicit cash extortion, structured hawala transfers, rapid money mule dispersal, and encrypted burner communications operating across inter-state corridors.',
};

export const INITIAL_ENTITIES: Entity[] = [
  {
    id: 'ent-rahul',
    name: 'Rahul Sharma',
    type: 'person',
    role: 'Primary Field Target & Ground Coordinator',
    identifier: 'SUBJ-NX-01',
    risk: 'high',
    connectionsCount: 6,
    connectedEntityIds: ['ent-ajay', 'ent-phone-rahul', 'ent-veh-creta', 'ent-loc-bus', 'ent-loc-wh', 'ent-ev-call'],
    relatedEvidenceIds: ['EV-001', 'EV-002', 'EV-007'],
    metadata: {
      'Identity Tag': 'SUBJ-NX-01',
      'PAN (Verified)': 'ABCPS8819K',
      'Primary Handset': '+91-98765-43210',
      'Transit Vehicle': 'MH-12-DE-4419 (Hyundai Creta)',
      'Network Degree': 6,
      'Betweenness Centrality': '0.82',
    },
    notes: 'Drove Hyundai Creta to Central Bus Terminal on 12 May 2026 at 08:35, met Ajay Patil on Platform 3, handed over sealed envelope, then made 241s encrypted call.',
  },
  {
    id: 'ent-ajay',
    name: 'Ajay Patil',
    type: 'person',
    role: 'Financial Conduit & Cash Broker',
    identifier: 'ENT-NX-02',
    risk: 'high',
    connectionsCount: 7,
    connectedEntityIds: ['ent-rahul', 'ent-apatil', 'ent-phone-ajay', 'ent-acc-889922', 'ent-loc-bus', 'ent-loc-wh', 'ent-ev-call'],
    relatedEvidenceIds: ['EV-001', 'EV-002', 'EV-003', 'EV-005'],
    metadata: {
      'Identity Tag': 'ENT-NX-02',
      'Primary Handset': '+91-98234-11876',
      'Banking Alias': 'A. Patil (SBI A/C 889922)',
      'Network Degree': 7,
      'Betweenness Centrality': '0.91 (#1 in Network)',
      'Resolution Status': '94% Probabilistic Match with A. Patil',
    },
    notes: 'Key bridge node between field operatives and banking channels. Received cash from Rahul, proceeded to Sector 4 Depot, initiated wire transfer.',
  },
  {
    id: 'ent-apatil',
    name: 'A. Patil (Candidate Alias)',
    type: 'person',
    role: 'Bank Record Identity extracted from SBI Wire Logs',
    identifier: 'BANK-ALIAS-01',
    risk: 'high',
    connectionsCount: 3,
    connectedEntityIds: ['ent-ajay', 'ent-acc-889922', 'ent-phone-ajay'],
    relatedEvidenceIds: ['EV-003'],
    metadata: {
      'Identifier': 'BANK-ALIAS-01',
      'Registered Account': 'SBI A/C 889922',
      'KYC Mobile': '+91-98234-11876 (Exact Match)',
      'KYC Address': 'Flat 302, Green Park Enclave',
      'Resolution Confidence': '94% (Pending Investigator Sign-off)',
    },
    notes: 'Debit account holder in SBI SFMS wire transfer records. Exact phone match with Ajay Patil; resolved via multi-attribute AI scoring.',
    isResolvedDuplicate: true,
  },
  {
    id: 'ent-neha',
    name: 'Neha Verma',
    type: 'person',
    role: 'Authorized Corporate Signatory & Director',
    identifier: 'ENT-NX-03',
    risk: 'medium',
    connectionsCount: 4,
    connectedEntityIds: ['ent-acc-482701', 'ent-acc-772145', 'ent-xyz', 'ent-vikram'],
    relatedEvidenceIds: ['EV-004', 'EV-006', 'EV-008'],
    metadata: {
      'DIN': 'DIN-0941294',
      'Authorized Accounts': 'ICICI A/C 772145 & HDFC 482701',
      'Equity Share': '40% in XYZ Traders Pvt Ltd',
      'Betweenness Centrality': '0.62',
    },
    notes: 'Authorized signatory for XYZ Traders accounts. Received ₹48,200 smurfing transfer from intermediate mule ledger within 22 minutes.',
  },
  {
    id: 'ent-xyz',
    name: 'XYZ Traders Pvt Ltd',
    type: 'organisation',
    role: 'Commercial Shell Conduit Company',
    identifier: 'ORG-NX-01',
    risk: 'high',
    connectionsCount: 4,
    connectedEntityIds: ['ent-neha', 'ent-acc-772145', 'ent-loc-wh', 'ent-vikram'],
    relatedEvidenceIds: ['EV-004', 'EV-006', 'EV-009'],
    metadata: {
      'CIN': 'U51909MH2021PTC369123',
      'GSTIN': '27AABCT8891Q1ZZ (Suspended for non-filing)',
      'Registered Office': 'Gala 14, Sector 4 Industrial Complex',
      'Pooled Inflows': '₹45,00,000+ structured under ₹50k',
    },
    notes: 'Suspected commercial shell company. Zero authentic commercial turnover. Controlled indirectly by offshore syndicate head Vikram Singhania.',
  },
  {
    id: 'ent-vikram',
    name: 'Vikram "Bhai" Singhania',
    type: 'person',
    role: 'Cartel Kingpin & Shadow Beneficiary',
    identifier: 'SUBJ-NX-00',
    risk: 'high',
    connectionsCount: 3,
    connectedEntityIds: ['ent-xyz', 'ent-phone-burner', 'ent-neha'],
    relatedEvidenceIds: ['EV-006', 'EV-009'],
    metadata: {
      'Intelligence Tag': 'Target Alpha (Offshore Controller)',
      'Current Location': 'Dubai Transit Hub (UAE)',
      'Communication Channel': 'Disposable Satellite VoIP Burst',
      'Provenance Mode': 'AI-Synthesized (78% Confidence)',
    },
    notes: 'Offshore controller commanding hawala transfers and shell company creation through encrypted disposable communication links.',
  },
  {
    id: 'ent-phone-rahul',
    name: '+91-98765-43210',
    type: 'phone',
    role: 'Rahul Mobile Handset',
    identifier: 'IMEI-864192040182910',
    risk: 'high',
    connectionsCount: 2,
    connectedEntityIds: ['ent-rahul', 'ent-ev-call'],
    relatedEvidenceIds: ['EV-002'],
    metadata: {
      'Carrier': 'Airtel Cellular',
      'Cell Tower Sector': 'MUM-C4-89 (Central Terminal)',
      'SIM Status': 'Active Postpaid',
    },
  },
  {
    id: 'ent-phone-ajay',
    name: '+91-98234-11876',
    type: 'phone',
    role: 'Ajay Facilitator Line',
    identifier: 'IMEI-869201948201928',
    risk: 'high',
    connectionsCount: 3,
    connectedEntityIds: ['ent-ajay', 'ent-apatil', 'ent-ev-call'],
    relatedEvidenceIds: ['EV-002', 'EV-003'],
    metadata: {
      'Carrier': 'Jio Telecom Intercept',
      'Cell Tower Sector': 'MUM-C4-89 & TWR-SEC4-02',
      'KYC Binding': 'Matched with SBI A/C 889922',
    },
  },
  {
    id: 'ent-phone-burner',
    name: '+91-91230-00991',
    type: 'phone',
    role: 'Offshore Burner SIM (<48h Churn)',
    identifier: 'IMEI-358921094820194',
    risk: 'high',
    connectionsCount: 2,
    connectedEntityIds: ['ent-vikram', 'ent-xyz'],
    relatedEvidenceIds: ['EV-009'],
    metadata: {
      'Carrier': 'Prepaid International Roaming',
      'Lifespan': 'Active 48 hours only',
      'Hardware Match': 'Recurring IMEI flagged in Operation Falcon',
    },
  },
  {
    id: 'ent-acc-889922',
    name: 'A/C 889922 (SBI)',
    type: 'account',
    role: 'Ajay Originating Commercial Debit Account',
    identifier: 'SBI-SFMS-889922',
    risk: 'high',
    connectionsCount: 2,
    connectedEntityIds: ['ent-ajay', 'ent-acc-482701'],
    relatedEvidenceIds: ['EV-003'],
    metadata: {
      'Bank': 'State Bank of India (Commercial Wing)',
      'Account Holder': 'A. PATIL',
      'Outflow': '₹50,000 (11:48 AM IST via SFMS)',
    },
  },
  {
    id: 'ent-acc-482701',
    name: 'A/C 482701 (HDFC)',
    type: 'account',
    role: 'Rapid Intermediary Mule Ledger',
    identifier: 'HDFC-MULE-482701',
    risk: 'high',
    connectionsCount: 3,
    connectedEntityIds: ['ent-acc-889922', 'ent-neha', 'ent-acc-772145'],
    relatedEvidenceIds: ['EV-003', 'EV-004', 'EV-008'],
    metadata: {
      'Bank': 'HDFC Retail Banking',
      'Account Holder': 'Dinesh Kumar (Mule Nominee)',
      'Turnaround': '22 minutes (₹50k in -> ₹48.2k out)',
      'Cross-Case Hit': 'Flagged in Syndicate Pegasus (CASE-PG-2026-109)',
    },
  },
  {
    id: 'ent-acc-772145',
    name: 'A/C 772145 (ICICI)',
    type: 'account',
    role: 'XYZ Corporate Destination Pool',
    identifier: 'ICICI-XYZ-772145',
    risk: 'high',
    connectionsCount: 2,
    connectedEntityIds: ['ent-neha', 'ent-xyz'],
    relatedEvidenceIds: ['EV-004', 'EV-006'],
    metadata: {
      'Bank': 'ICICI Corporate Banking',
      'Account Holder': 'XYZ Traders Pvt Ltd',
      'Authorized Signatory': 'Neha Verma',
      'Structured Inflow': '₹48,200 (12:10 PM IST)',
    },
  },
  {
    id: 'ent-loc-bus',
    name: 'Central Bus Terminal',
    type: 'location',
    role: 'CCTV Rendezvous Site (Platform 3)',
    identifier: 'LOC-CBT-01',
    risk: 'medium',
    connectionsCount: 2,
    connectedEntityIds: ['ent-rahul', 'ent-ajay'],
    relatedEvidenceIds: ['EV-001', 'EV-002'],
    metadata: {
      'Coordinates': '18.5204° N, 73.8567° E',
      'Surveillance Feed': 'Camera CAM-04 & CAM-12',
      'Incident Time': '08:45 AM IST',
    },
  },
  {
    id: 'ent-loc-wh',
    name: 'Sector 4 Depot',
    type: 'location',
    role: 'Covert Warehouse & Corporate Storage',
    identifier: 'LOC-SEC4-WH',
    risk: 'high',
    connectionsCount: 2,
    connectedEntityIds: ['ent-ajay', 'ent-xyz'],
    relatedEvidenceIds: ['EV-001', 'EV-005', 'EV-006'],
    metadata: {
      'Coordinates': '18.5912° N, 73.9104° E',
      'Premises': 'Gala 14, Industrial Phase 2',
      'SIGINT Ping': 'Mobile +91-98234-11876 attached at 11:15 AM',
    },
  },
  {
    id: 'ent-veh-creta',
    name: 'MH-12-DE-4419',
    type: 'vehicle',
    role: 'Creta Transit Car',
    identifier: 'VEH-CRETA-4419',
    risk: 'medium',
    connectionsCount: 1,
    connectedEntityIds: ['ent-rahul'],
    relatedEvidenceIds: ['EV-001', 'EV-007'],
    metadata: {
      'Make & Model': 'Hyundai Creta (Phantom Black)',
      'Registered Owner': 'Rahul Sharma',
      'ANPR Checkpoint': 'Sector 12 ➔ Central Hub corridor at 08:35 AM',
    },
  },
];

export const INITIAL_EVIDENCE_RECORDS: EvidenceRecord[] = [
  {
    id: 'EV-001',
    title: 'Surveillance Report: Central Bus Terminal Rendezvous',
    type: 'police_report',
    typeLabel: 'Physical Surveillance',
    source: 'Special Surveillance Unit (Alpha Team)',
    date: '12 May 2026',
    timestamp: '08:45 AM IST',
    status: 'Verified',
    summary:
      'At 08:35, Rahul Sharma arrived in Hyundai Creta MH-12-DE-4419. At 08:45, Ajay Patil met him near tea stall on Platform 3, conversed for 7 mins, and Sharma handed Patil a sealed brown envelope.',
    rawContent: `OFFICIAL PHYSICAL SURVEILLANCE REPORT
Classification: RESTRICTED // LAW ENFORCEMENT SENSITIVE
Reporting Unit: Special Surveillance Unit (Alpha Team)
Operation: Operation Nexus (CASE-NX-2026-001)

SITREP NARRATIVE:
At 08:35, Subject Rahul Sharma arrived in black Hyundai Creta MH-12-DE-4419 at Central Bus Terminal parking area.
At 08:45, Ajay Patil arrived on foot from the metro subway exit. Both subjects met near tea stall on Platform 3, conversed for 7 mins in low whispers.
At 08:51, Sharma handed Patil a thick sealed brown envelope (suspected currency courier handover). Patil concealed envelope inside dark jacket and walked toward SBI ATM booth. Sharma returned to vehicle.`,
    extractedEntities: [
      { text: 'Rahul Sharma', type: 'person', entityId: 'ent-rahul' },
      { text: 'Ajay Patil', type: 'person', entityId: 'ent-ajay' },
      { text: 'MH-12-DE-4419', type: 'vehicle', entityId: 'ent-veh-creta' },
      { text: 'Central Bus Terminal', type: 'location', entityId: 'ent-loc-bus' },
    ],
    supportedRelationships: [
      'Physical meeting between Rahul Sharma and Ajay Patil',
      'Handover of illicit currency envelope',
    ],
    relatedInsightIds: ['INS-001', 'INS-003'],
    custodyChain: 'Captured by Insp. S. Joshi -> Digitized by Cyber Cell -> SHA-256 Verified',
    hashChecksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
  },
  {
    id: 'EV-002',
    title: 'CDR Intercept: Rahul Sharma to Ajay Patil Encrypted Voice Burst',
    type: 'communication',
    typeLabel: 'Lawful Telecom Intercept',
    source: 'Airtel & Jio Lawful Interception Wing',
    date: '12 May 2026',
    timestamp: '08:55 AM IST',
    status: 'Verified',
    summary:
      'Calling Party 9876543210 (Rahul Sharma) to Called Party 9823411876 (Ajay Patil). Call duration 241 seconds, routed through identical cell tower sector MUM-C4-89.',
    rawContent: `TELECOM CDR EXTRACT
Source: Airtel & Jio Regulatory Lawful Interception Feed
Target File Reference: AIRTEL_CDR_D12

Call ID: TEL-20260512-0855-4481
Calling Party (A): +91-98765-43210 (Rahul Sharma)
Originating IMEI: 864192040182910 (Sector MUM-C4-89)
Called Party (B): +91-98234-11876 (Ajay Patil)
Terminating IMEI: 869201948201928 (Sector MUM-C4-89)

Timestamp: 12 May 2026, 08:55:12 IST
Duration: 241 seconds (4 minutes 01 second)
Tower Colocation: Identical sector azimuth confirmed. Both handsets active within 200m radius of Central Terminal.`,
    extractedEntities: [
      { text: '+91-98765-43210', type: 'phone', entityId: 'ent-phone-rahul' },
      { text: '+91-98234-11876', type: 'phone', entityId: 'ent-phone-ajay' },
      { text: 'Rahul Sharma', type: 'person', entityId: 'ent-rahul' },
      { text: 'Ajay Patil', type: 'person', entityId: 'ent-ajay' },
    ],
    supportedRelationships: [
      'Encrypted telephony communication post-handover',
      'Cell tower sector colocation at Central Terminal',
    ],
    relatedInsightIds: ['INS-001', 'INS-002'],
    custodyChain: 'Telecom Regulatory Gateway -> Cyber Intelligence Desk -> SHA-256 Verified',
    hashChecksum: 'a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8',
  },
  {
    id: 'EV-003',
    title: 'Core Banking Wire: ₹50,000 Transferred from SBI A/C 889922',
    type: 'financial',
    typeLabel: 'Core Banking SFMS Wire',
    source: 'SBI Financial Intelligence Unit',
    date: '12 May 2026',
    timestamp: '11:48 AM IST',
    status: 'Verified',
    summary:
      'Debit A/C 889922 (A. PATIL) pushed ₹50,000.00 via NetBanking Mobile (IP: 103.42.19.82) to Credit A/C 482701 (HDFC, Dinesh Kumar).',
    rawContent: `CORE BANKING WIRE LEDGER (SFMS)
Source: State Bank of India Financial Intelligence Unit (FIU-IND Feed)
UTR Reference: SBIN2026051288992201

Debit Account: 889922
Account Holder Name: A. PATIL
Credit Account: 482701 (HDFC Retail Banking, Dinesh Kumar)
Amount: INR 50,000.00
Transaction Timestamp: 12 May 2026 • 11:48:32 IST
Channel: NetBanking Mobile App
IP Address: 103.42.19.82 (Attached to Sector 4 Industrial Gateway)`,
    extractedEntities: [
      { text: 'A. Patil', type: 'person', entityId: 'ent-apatil' },
      { text: 'A/C 889922', type: 'account', entityId: 'ent-acc-889922' },
      { text: 'A/C 482701', type: 'account', entityId: 'ent-acc-482701' },
    ],
    supportedRelationships: [
      'Originating wire transfer connecting Ajay Patil alias to intermediary mule',
    ],
    relatedInsightIds: ['INS-001', 'INS-002'],
    custodyChain: 'SBI FIU Gateway -> Core Banking Clearing -> SHA-256 Verified',
    hashChecksum: '1c8d5a2f3b9e4a7c6d1e0f8a2b5c7d9e4a6f8b1c3d5e7a9b0c2d4e6f8a1b3c5',
  },
  {
    id: 'EV-004',
    title: 'Financial Smurfing Dispersal Alert: ₹48,200 Routed to A/C 772145',
    type: 'financial',
    typeLabel: 'Suspicious Activity Report',
    source: 'HDFC Suspicious Activity Monitor',
    date: '12 May 2026',
    timestamp: '12:10 PM IST',
    status: 'Verified',
    summary:
      'Rapid smurfing layering detected. Inflow ₹50,000 received at 11:48; within 22 minutes, account pushed ₹48,200 to XYZ Traders account 772145, withholding ₹1,800 mule cut.',
    rawContent: `HDFC SUSPICIOUS ACTIVITY ALERT (AML-LAYER-77)
Alert Reference: SAR-HDFC-20260512-482

Account Under Surveillance: 482701 (Dinesh Kumar - Dormant Mule Account)
Inflow: INR 50,000.00 received at 11:48 IST from SBI A/C 889922
Outflow: INR 48,200.00 pushed via IMPS at 12:10 IST to ICICI A/C 772145 (XYZ Traders Pvt Ltd)
Retained Balance: INR 1,800.00 (suspected 3.6% courier commission)
Layering Velocity: 22 minutes total transit time. High anomaly smurfing pattern under ₹50,000 threshold.`,
    extractedEntities: [
      { text: 'A/C 482701', type: 'account', entityId: 'ent-acc-482701' },
      { text: 'A/C 772145', type: 'account', entityId: 'ent-acc-772145' },
      { text: 'XYZ Traders Pvt Ltd', type: 'organisation', entityId: 'ent-xyz' },
    ],
    supportedRelationships: [
      'Layered fund dispersal into corporate shell entity',
      'Smurfing below mandatory reporting limits',
    ],
    relatedInsightIds: ['INS-001'],
    custodyChain: 'HDFC AML Server -> Special Task Force Economic Wing -> SHA-256 Verified',
    hashChecksum: '9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8',
  },
  {
    id: 'EV-005',
    title: 'Field SIGINT Telemetry: Sector 4 Depot Convergence',
    type: 'surveillance',
    typeLabel: 'SIGINT & Cell Tower Telemetry',
    source: 'Joint Field Intelligence Center (JIC)',
    date: '12 May 2026',
    timestamp: '11:15 AM IST',
    status: 'Verified',
    summary:
      'Cell tower telemetry attaches Ajay Patil mobile +91-98234-11876 to tower TWR-SEC4-02 directly overlooking Sector 4 Depot Gala 14 at 11:15 AM.',
    rawContent: `SIGINT TOWER PING DOSSIER
Source: State Police Special Task Force SIGINT Unit
Location: Sector 4 Warehouse Industrial Depot (18.5912° N, 73.9104° E)

Telemetry log confirms target mobile MSISDN +91-98234-11876 attached to Sector 4 tower sector from 11:15 to 13:40 IST. Visual patrol confirms subject walked into Gala 14 loading bay carrying courier satchel.`,
    extractedEntities: [
      { text: 'Ajay Patil', type: 'person', entityId: 'ent-ajay' },
      { text: 'Sector 4 Depot', type: 'location', entityId: 'ent-loc-wh' },
    ],
    supportedRelationships: [
      'Physical presence of cash courier at suspected warehouse facility',
    ],
    relatedInsightIds: ['INS-003'],
    custodyChain: 'JIC Ground Intercept -> STF Archive -> SHA-256 Verified',
    hashChecksum: 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3',
  },
  {
    id: 'EV-006',
    title: 'Corporate Registry Filing (MCA RoC): XYZ Traders Pvt Ltd',
    type: 'organisation_activity',
    typeLabel: 'MCA RoC Corporate Search',
    source: 'Ministry of Corporate Affairs (MCA21)',
    date: '12 May 2026',
    timestamp: '12:30 PM IST',
    status: 'Verified',
    summary:
      'CIN U51909MH2021PTC369123. Neha Verma registered as Director with 40% equity share. Registered address: Gala 14, Sector 4 Industrial Complex. GST status suspended.',
    rawContent: `MCA21 REGISTRATION MASTER DATA
Company Name: XYZ Traders Private Limited
CIN: U51909MH2021PTC369123
Date of Incorporation: 14 October 2021
Registered Office: Gala 14, Sector 4 Industrial Complex

Key Directors:
1. Neha Verma (DIN: 0941294) - Authorized Bank Signatory (40% equity)
2. Dummy Director nominee (60% equity)

Tax Profile: GSTIN 27AABCT8891Q1ZZ suspended for persistent failure to submit annual turnover filings.`,
    extractedEntities: [
      { text: 'XYZ Traders Pvt Ltd', type: 'organisation', entityId: 'ent-xyz' },
      { text: 'Neha Verma', type: 'person', entityId: 'ent-neha' },
    ],
    supportedRelationships: [
      'Beneficial ownership and corporate signatory control of conduit company',
    ],
    relatedInsightIds: ['INS-001'],
    custodyChain: 'MCA21 Regulatory Extract -> STF Economic Wing -> SHA-256 Verified',
    hashChecksum: '3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d',
  },
  {
    id: 'EV-007',
    title: 'Smart City ANPR Intercept: Vehicle MH-12-DE-4419 Route Corroboration',
    type: 'surveillance',
    typeLabel: 'Smart City ANPR Camera',
    source: 'Municipal Traffic Control ANPR Network',
    date: '12 May 2026',
    timestamp: '08:35 AM IST',
    status: 'Verified',
    summary:
      'Automated Number Plate Recognition hit for black Hyundai Creta MH-12-DE-4419 registered to Rahul Sharma passing Sector 12 Junction en route to Central Terminal.',
    rawContent: `ANPR TOLL CAMERA HIT
Camera ID: ANPR-SEC12-NORTH-04
Vehicle Registered: MH-12-DE-4419
Owner Name: Rahul Sharma
Speed: 44 km/h
Optical Confidence: 99.4%
Timestamp: 12 May 2026 • 08:35:10 IST`,
    extractedEntities: [
      { text: 'MH-12-DE-4419', type: 'vehicle', entityId: 'ent-veh-creta' },
      { text: 'Rahul Sharma', type: 'person', entityId: 'ent-rahul' },
    ],
    supportedRelationships: [
      'Corroborates vehicle movement and departure timeline from suspect residence',
    ],
    relatedInsightIds: ['INS-001'],
    custodyChain: 'Traffic Police Server -> Cyber Crime Coordination Wing -> SHA-256 Verified',
    hashChecksum: '4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e',
  },
  {
    id: 'EV-008',
    title: 'Core Banking Layering Analysis: HDFC Mule A/C 482701 Velocity Dossier',
    type: 'financial',
    typeLabel: 'AML Velocity Forensics',
    source: 'Financial Intelligence Unit (FIU-IND)',
    date: '12 May 2026',
    timestamp: '13:00 PM IST',
    status: 'Verified',
    summary:
      'Account 482701 exhibits zero organic transaction balance for 6 months, followed by rapid pass-through structuring under ₹50,000 threshold within 22 minutes.',
    rawContent: `FIU-IND FORENSIC PASS-THROUGH REPORT
Account: 482701 (HDFC)
Profile: Individual Savings Account opened with forged electricity utility receipt.
Turnaround Velocity: 22 minutes average retention.
Funds in: ₹50,000.00 | Funds out: ₹48,200.00.
Classification: High-Risk Smurfing Mule Ledger.`,
    extractedEntities: [
      { text: 'A/C 482701', type: 'account', entityId: 'ent-acc-482701' },
      { text: 'Neha Verma', type: 'person', entityId: 'ent-neha' },
    ],
    supportedRelationships: [
      'Mule account facilitation for hawala money laundering',
    ],
    relatedInsightIds: ['INS-001'],
    custodyChain: 'FIU-IND Gateway -> STF Analysis Ledger -> SHA-256 Verified',
    hashChecksum: '5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f',
  },
  {
    id: 'EV-009',
    title: 'Offshore Satellite Encrypted Telemetry Burst: Dubai Controller Link',
    type: 'communication',
    typeLabel: 'SIGINT Satellite Intercept',
    source: 'National Technical Research Agency (NTRO)',
    date: '12 May 2026',
    timestamp: '14:30 PM IST',
    status: 'Verified',
    summary:
      'Encrypted satellite burst logged between XYZ Traders industrial router and offshore VoIP terminal in Dubai linked to cartel head Vikram Singhania.',
    rawContent: `NTRO SATELLITE SIGINT INTERCEPT
Source: Secure Gateway Intercept
Origin IP: 103.42.19.82 (Gala 14, XYZ Traders router)
Destination: Dubai Internet City (UAE) Satellite Terminal
Target Associated: Vikram "Bhai" Singhania (Target Alpha)
Payload: Encrypted 512-bit burst transmission immediately following banking fund absorption.`,
    extractedEntities: [
      { text: 'Vikram Singhania', type: 'person', entityId: 'ent-vikram' },
      { text: '+91-91230-00991', type: 'phone', entityId: 'ent-phone-burner' },
      { text: 'XYZ Traders Pvt Ltd', type: 'organisation', entityId: 'ent-xyz' },
    ],
    supportedRelationships: [
      'Offshore command-and-control connection to commercial shell entity',
    ],
    relatedInsightIds: ['INS-001'],
    custodyChain: 'NTRO Satellite Desk -> Special Task Force High Command -> SHA-256 Verified',
    hashChecksum: '6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a',
  },
];

export const INITIAL_DATA_SOURCES: DataSourceItem[] = [
  {
    id: 'ds-01',
    name: 'Police CCTNS & Case Diaries',
    category: 'Field Reports & FIRs',
    recordCount: 2,
    status: 'Processed',
    lastUpdated: '12 May 2026 • 08:50 IST',
    sourceSystem: 'State Law Enforcement CCTNS / Incident Records',
    fileFormat: 'PDF Narrative / Signed SITREP',
    integrityHash: 'SHA-256: e3b0c442...b855',
    records: ['EV-001', 'EV-007'],
    description: 'Physical surveillance reports, patrol dispatch notes, field officer visual observations, and ANPR camera logs.',
  },
  {
    id: 'ds-02',
    name: 'Telecom Lawful CDR Gateways',
    category: 'Telecom CDR & Tower Logs',
    recordCount: 2,
    status: 'Processed',
    lastUpdated: '12 May 2026 • 09:05 IST',
    sourceSystem: 'Airtel & Jio Lawful Interception Wing',
    fileFormat: 'Structured CSV / ASCII Telemetry',
    integrityHash: 'SHA-256: a7b8c9d0...a7b8',
    records: ['EV-002', 'EV-009'],
    description: 'Call detail records, IMEI-IMSI binding maps, cell tower azimuth data, and satellite burst transmissions.',
  },
  {
    id: 'ds-03',
    name: 'Core Banking SFMS & Wire Feeds',
    category: 'Core Banking & Wire Feeds',
    recordCount: 3,
    status: 'Processed',
    lastUpdated: '12 May 2026 • 13:10 IST',
    sourceSystem: 'SBI, HDFC, ICICI & FIU-IND Gateway (RTGS/IMPS)',
    fileFormat: 'ISO20022 Financial XML & Banking Ledger',
    integrityHash: 'SHA-256: 1c8d5a2f...3c5',
    records: ['EV-003', 'EV-004', 'EV-008'],
    description: 'Inter-bank transaction wires, KYC phone metadata records, structuring fund flows under ₹50,000.',
  },
  {
    id: 'ds-04',
    name: 'Corporate MCA & Smart City SIGINT',
    category: 'Geo-Spatial & Corporate MCA',
    recordCount: 2,
    status: 'Processed',
    lastUpdated: '12 May 2026 • 14:40 IST',
    sourceSystem: 'Ministry of Corporate Affairs & Smart City ANPR',
    fileFormat: 'GeoJSON / SIGINT / MCA21 Master Data',
    integrityHash: 'SHA-256: 3c4d5e6f...3c4d',
    records: ['EV-005', 'EV-006'],
    description: 'Corporate shell registration, director DIN credentials, cell tower perimeter pings, and warehouse surveillance.',
  },
  {
    id: 'ds-05',
    name: 'Social Media & Dark Web Intelligence (OSINT)',
    category: 'Social Media & Dark Web OSINT',
    recordCount: 3,
    status: 'Processed',
    lastUpdated: '12 May 2026 • 15:15 IST',
    sourceSystem: 'State Cyber Forensics / Telegram Intercepts & P2P Forum Crawlers',
    fileFormat: 'JSON Scrape / Encrypted Channel Logs',
    integrityHash: 'SHA-256: d5e6f7a8...9b0c',
    records: ['EV-002', 'EV-009'],
    description: 'Encrypted Telegram bot channel logs, burner social media handles, darknet escrow chatter, and P2P cryptocurrency wallet addresses.',
  },
  {
    id: 'ds-06',
    name: 'National Criminal Records & ICJS Warrants',
    category: 'Criminal Records & Warrant Registry',
    recordCount: 2,
    status: 'Processed',
    lastUpdated: '12 May 2026 • 16:00 IST',
    sourceSystem: 'Inter-Operable Criminal Justice System (ICJS) & NCRB Database',
    fileFormat: 'XML Offender Registry / Warrant Docket',
    integrityHash: 'SHA-256: 4e5f6a7b...8c9d',
    records: ['EV-001', 'EV-005'],
    description: 'Prior syndicate arrest records, chargesheet archives, active non-bailable warrants, and inter-state habitual offender profiling.',
  },
  {
    id: 'ds-07',
    name: 'FIU-IND Suspicious Transaction Reports (STR/SAR)',
    category: 'Financial Intelligence Unit Feeds',
    recordCount: 4,
    status: 'Processed',
    lastUpdated: '12 May 2026 • 16:30 IST',
    sourceSystem: 'Financial Intelligence Unit (FIU-IND) & Central Intelligence Agency',
    fileFormat: 'STR-v2 Secure XML / FINnet 2.0 Telemetry',
    integrityHash: 'SHA-256: 7f8a9b0c...1d2e',
    records: ['EV-003', 'EV-004', 'EV-008'],
    description: 'Automated Hawala structuring alerts, high-risk PEP flags, cross-border remittance patterns, and confidential intelligence agency briefings.',
  },
];

export const INITIAL_TIMELINE_EVENTS: TimelineEvent[] = [
  {
    id: 'time-01',
    time: '08:30',
    date: '12 May 2026',
    datetime: '12 May 2026, 08:30 AM IST',
    title: 'Rahul Sharma departs residence in Hyundai Creta',
    description: 'Rahul Sharma departs Sector 12 residence driving black Hyundai Creta MH-12-DE-4419, captured by Smart City ANPR cameras.',
    source: 'ANPR / Physical Surveillance',
    sourceType: 'surveillance',
    evidenceId: 'EV-007',
    entities: ['Rahul Sharma', 'MH-12-DE-4419'],
    category: 'movement',
    location: 'Sector 12 Residence',
  },
  {
    id: 'time-02',
    time: '08:45',
    date: '12 May 2026',
    datetime: '12 May 2026, 08:45 AM IST',
    title: 'Physical Handover at Central Bus Terminal Platform 3',
    description: 'Physical rendezvous between Rahul Sharma and Ajay Patil on Platform 3. Rahul Sharma hands sealed currency envelope to Ajay Patil.',
    source: 'Police Surveillance SITREP',
    sourceType: 'police_report',
    evidenceId: 'EV-001',
    entities: ['Rahul Sharma', 'Ajay Patil', 'Central Terminal'],
    category: 'meeting',
    location: 'Central Bus Terminal',
    highlightInHiddenPath: true,
  },
  {
    id: 'time-03',
    time: '08:55',
    date: '12 May 2026',
    datetime: '12 May 2026, 08:55 AM IST',
    title: 'Encrypted Voice Call Intercept (241 seconds)',
    description: 'Lawful CDR voice intercept between Rahul Sharma (+91-98765-43210) and Ajay Patil (+91-98234-11876) routed on tower sector MUM-C4-89.',
    source: 'Telecom CDR Intercept',
    sourceType: 'communication',
    evidenceId: 'EV-002',
    entities: ['Rahul Sharma', 'Ajay Patil', '+91-98765-43210', '+91-98234-11876'],
    category: 'communication',
    duration: '241 seconds',
    location: 'Tower Sector MUM-C4-89',
    highlightInHiddenPath: true,
  },
  {
    id: 'time-04',
    time: '11:15',
    date: '12 May 2026',
    datetime: '12 May 2026, 11:15 AM IST',
    title: 'Ajay Patil enters Sector 4 Warehouse Depot',
    description: 'SIGINT telemetry logs Ajay Patil mobile attaching to Sector 4 tower overlooking Gala 14 loading bay.',
    source: 'SIGINT Telemetry',
    sourceType: 'surveillance',
    evidenceId: 'EV-005',
    entities: ['Ajay Patil', 'Sector 4 Depot'],
    category: 'movement',
    location: 'Sector 4 Depot',
  },
  {
    id: 'time-05',
    time: '11:48',
    date: '12 May 2026',
    datetime: '12 May 2026, 11:48 AM IST',
    title: 'Originating Wire: ₹50,000 Transferred from SBI A/C 889922',
    description: 'Core banking transfer of ₹50,000 originating from A/C 889922 (Holder: A. Patil) to intermediate HDFC mule ledger A/C 482701.',
    source: 'SBI Core Banking SFMS',
    sourceType: 'financial',
    evidenceId: 'EV-003',
    entities: ['A. Patil', 'A/C 889922', 'A/C 482701'],
    category: 'financial',
    amount: '₹50,000',
    highlightInHiddenPath: true,
  },
  {
    id: 'time-06',
    time: '12:10',
    date: '12 May 2026',
    datetime: '12 May 2026, 12:10 PM IST',
    title: 'Rapid Smurfing Dispersal: ₹48,200 Routed to A/C 772145',
    description: 'Rapid layering: within 22 minutes of inflow, account 482701 forwards ₹48,200 to XYZ Traders account 772145, withholding ₹1,800 mule cut.',
    source: 'HDFC AML Monitor',
    sourceType: 'financial',
    evidenceId: 'EV-004',
    entities: ['A/C 482701', 'A/C 772145', 'Neha Verma', 'XYZ Traders Ltd'],
    category: 'financial',
    amount: '₹48,200',
    highlightInHiddenPath: true,
  },
  {
    id: 'time-07',
    time: '14:30',
    date: '12 May 2026',
    datetime: '12 May 2026, 14:30 PM IST',
    title: 'Offshore Encrypted Satellite Telemetry Burst',
    description: 'Satellite transmission burst from XYZ Traders router to Dubai terminal linked to offshore syndicate head Vikram Singhania.',
    source: 'NTRO Satellite Intercept',
    sourceType: 'communication',
    evidenceId: 'EV-009',
    entities: ['XYZ Traders Ltd', 'Vikram Singhania'],
    category: 'communication',
  },
];

export const INITIAL_AI_INSIGHTS: AIInsight[] = [
  {
    id: 'INS-001',
    priority: 'high',
    priorityLabel: 'HIGH SEVERITY',
    title: 'Suspect Linked to Commercial Shell Entity Through Layered Financial Conduit',
    category: 'Hidden Relationship',
    whatFound:
      'An indirect 5-hop relationship connects primary target Rahul Sharma to commercial shell XYZ Traders Ltd via cash broker Ajay Patil, SBI A/C 889922, HDFC mule A/C 482701, and corporate director Neha Verma.',
    whyFlagged:
      'Physical meeting at Central Terminal and 241s encrypted call between Rahul and Ajay was followed within 3 hours by structured financial dissipation into XYZ Traders, intentionally smurfing under ₹50,000.',
    whyItMatters:
      'Establishes provable judicial nexus between the street-level target and corporate beneficiaries despite zero direct contact, defeating single-point watchlist queries.',
    supportingEvidenceIds: ['EV-001', 'EV-002', 'EV-003', 'EV-004', 'EV-006'],
    relatedEntityIds: ['ent-rahul', 'ent-ajay', 'ent-apatil', 'ent-acc-889922', 'ent-acc-482701', 'ent-neha', 'ent-xyz'],
    status: 'AI-Generated',
    confidenceScore: 96,
    recommendedSteps: [
      'Subpoena bank wire transmission logs & KYC records for intermediate mule A/C 482701.',
      'Serve notice to Neha Verma regarding corporate ownership of ICICI A/C 772145.',
      'Seek freezing orders under Section 102 CrPC for all associated commercial accounts.',
    ],
    actionLabel: 'View Path on Graph',
    actionTargetView: 'path',
  },
  {
    id: 'INS-002',
    priority: 'medium',
    priorityLabel: 'MEDIUM SEVERITY',
    title: 'AI Entity Resolution: Ajay Patil (CCTNS) ↔ A. Patil (SBI SFMS)',
    category: 'Entity Resolution',
    whatFound:
      'A. Patil in Core Banking wire records (A/C 889922) matches field operative Ajay Patil identified in telecom CDR records with 94% probabilistic confidence.',
    whyFlagged:
      'Identical registered mobile (+91-98234-11876, 100% match), matching Green Park Enclave address (92%), and temporal transfer alignment 173 minutes post-meeting.',
    whyItMatters:
      'Approving this candidate match completes the unbroken evidentiary bridge from street-level cash collection to the banking ledger.',
    supportingEvidenceIds: ['EV-002', 'EV-003'],
    relatedEntityIds: ['ent-ajay', 'ent-apatil', 'ent-phone-ajay', 'ent-acc-889922'],
    status: 'Under Review',
    confidenceScore: 94,
    recommendedSteps: [
      'Cross-verify bank signature card for A/C 889922 with voter identification roll.',
      'Approve entity resolution match in queue to consolidate network graph.',
    ],
    actionLabel: 'Review Match',
    actionTargetView: 'resolution',
  },
  {
    id: 'INS-003',
    priority: 'low',
    priorityLabel: 'INFORMATIONAL',
    title: 'Spatial Convergence Detected at Sector 4 Depot Perimeter',
    category: 'Location Pattern',
    whatFound:
      'Multiple relevant subjects and registered corporate premises show spatial convergence at Sector 4 Depot during the active investigation window.',
    whyFlagged:
      'Ajay Patil mobile attached to Sector 4 tower at 11:15 AM; XYZ Traders registered corporate office located at adjacent Gala 14.',
    whyItMatters:
      'Identifies the physical operational coordination hub bridging field conspirators with the corporate storage entity.',
    supportingEvidenceIds: ['EV-001', 'EV-005', 'EV-006'],
    relatedEntityIds: ['ent-rahul', 'ent-ajay', 'ent-loc-wh', 'ent-xyz'],
    status: 'Verified by Investigator',
    confidenceScore: 91,
    recommendedSteps: [
      'Obtain search warrant under Section 93 CrPC for Gala 14, Sector 4 Industrial Complex.',
      'Subpoena commercial power consumption records for the warehouse.',
    ],
    actionLabel: 'View Location Timeline',
    actionTargetView: 'timeline',
  },
];

export const INITIAL_ENTITY_MATCH: EntityMatchItem = {
  matchId: 'MATCH-NX-001',
  confidence: 94,
  status: 'pending',
  leftEntity: {
    name: 'Ajay Patil',
    sourceType: 'Police CCTNS & Lawful Telecom CDR',
    phone: '+91-98234-11876',
    location: 'Central Terminal / Sector 4 Depot',
    evidenceId: 'EV-001 & EV-002',
    role: 'Ground Facilitator & Cash Courier',
  },
  rightEntity: {
    name: 'A. Patil',
    sourceType: 'SBI Core Banking SFMS Wire Records',
    phoneMetadata: '+91-98234-11876',
    linkedAccount: 'A/C 889922 (SBI)',
    evidenceId: 'EV-003',
    role: 'Originating Bank Account Holder',
  },
  supportingSignals: [
    {
      title: 'Exact Mobile Number Match (100% Match)',
      description: '+91-98234-11876 is identical in lawful CDR telecom log and SBI Core Banking KYC metadata.',
      verified: true,
    },
    {
      title: 'Fuzzy KYC Address Alignment (92% Match)',
      description: 'Flat 302, Green Park Enclave coordinates match field surveillance residency records.',
      verified: true,
    },
    {
      title: 'Phonetic Soundex & Metaphone Alignment (95% Match)',
      description: '"A. Patil" matches "Ajay Patil" via Double-Metaphone token alignment algorithm.',
      verified: true,
    },
    {
      title: 'Temporal Action Gap (96% Context Alignment)',
      description: 'Bank transfer occurred at 11:48 AM, exactly 173 minutes after intercepted physical cash handover.',
      verified: true,
    },
  ],
};

// All 15 Graph Nodes matching Master Entity Directory Section 5.2
export const INITIAL_GRAPH_NODES: GraphNode[] = [
  { id: 'ent-rahul', label: 'Rahul Sharma', type: 'person', risk: 'high', x: 120, y: 220, connections: 6, role: 'Primary Target', partOfHiddenPath: true },
  { id: 'ent-ajay', label: 'Ajay Patil', type: 'person', risk: 'high', x: 300, y: 220, connections: 7, role: 'Cash Broker', partOfHiddenPath: true },
  { id: 'ent-apatil', label: 'A. Patil (SBI)', type: 'person', risk: 'high', x: 440, y: 85, connections: 3, role: 'Candidate Alias', isResolvedMerged: false, partOfHiddenPath: true },
  { id: 'ent-acc-889922', label: 'A/C 889922 (SBI)', type: 'account', risk: 'high', x: 570, y: 220, connections: 2, role: 'Origin Debit A/C', partOfHiddenPath: true },
  { id: 'ent-acc-482701', label: 'A/C 482701 (HDFC)', type: 'account', risk: 'high', x: 760, y: 220, connections: 3, role: 'Mule Ledger', partOfHiddenPath: true },
  { id: 'ent-neha', label: 'Neha Verma', type: 'person', risk: 'medium', x: 950, y: 220, connections: 4, role: 'Director (40%)', partOfHiddenPath: true },
  { id: 'ent-acc-772145', label: 'A/C 772145 (ICICI)', type: 'account', risk: 'high', x: 1055, y: 360, connections: 2, role: 'Corporate Pool', partOfHiddenPath: true },
  { id: 'ent-xyz', label: 'XYZ Traders Ltd', type: 'organisation', risk: 'high', x: 1160, y: 220, connections: 4, role: 'Commercial Shell', partOfHiddenPath: true },
  { id: 'ent-vikram', label: 'Vikram Singhania', type: 'person', risk: 'high', x: 1160, y: 75, connections: 3, role: 'Offshore Kingpin' },
  { id: 'ent-phone-rahul', label: '+91-98765-43210', type: 'phone', risk: 'high', x: 120, y: 375, connections: 2, role: 'Rahul Handset' },
  { id: 'ent-phone-ajay', label: '+91-98234-11876', type: 'phone', risk: 'high', x: 300, y: 375, connections: 3, role: 'Ajay Mobile' },
  { id: 'ent-phone-burner', label: '+91-91230-00991', type: 'phone', risk: 'high', x: 1300, y: 75, connections: 2, role: 'Burner SIM' },
  { id: 'ent-loc-bus', label: 'Central Terminal', type: 'location', risk: 'medium', x: 210, y: 75, connections: 2, role: 'Rendezvous Site' },
  { id: 'ent-loc-wh', label: 'Sector 4 Depot', type: 'location', risk: 'high', x: 550, y: 385, connections: 2, role: 'Storage Depot' },
  { id: 'ent-veh-creta', label: 'MH-12-DE-4419', type: 'vehicle', risk: 'medium', x: -70, y: 220, connections: 1, role: 'Transit Creta' },
  { id: 'ent-ev-call', label: 'CDR Call 08:55', type: 'event', risk: 'medium', x: 210, y: 305, connections: 3, role: '241s Encrypted' },
];

export const INITIAL_GRAPH_EDGES: GraphEdge[] = [
  { id: 'e1', source: 'ent-rahul', target: 'ent-ajay', label: 'Physical Handover', type: 'meeting', evidenceId: 'EV-001', time: '08:45', partOfHiddenPath: true },
  { id: 'e2', source: 'ent-rahul', target: 'ent-ev-call', label: 'Outgoing Call', type: 'communication', evidenceId: 'EV-002', time: '08:55', labelRatio: 0.38, labelOffsetY: -6 },
  { id: 'e3', source: 'ent-ev-call', target: 'ent-ajay', label: 'Incoming Call', type: 'communication', evidenceId: 'EV-002', time: '08:55', labelRatio: 0.62, labelOffsetY: -6 },
  { id: 'e4', source: 'ent-ajay', target: 'ent-apatil', label: 'AI Deduplication (94%)', type: 'entity_match', evidenceId: 'EV-003', partOfHiddenPath: true, labelRatio: 0.42, labelOffsetX: -24, labelOffsetY: 12 },
  { id: 'e5', source: 'ent-apatil', target: 'ent-acc-889922', label: 'KYC Account Holder', type: 'ownership', evidenceId: 'EV-003', partOfHiddenPath: true, labelRatio: 0.58, labelOffsetX: 24, labelOffsetY: 12 },
  { id: 'e6', source: 'ent-acc-889922', target: 'ent-acc-482701', label: '₹50,000 Transfer', type: 'financial', evidenceId: 'EV-003', amount: '₹50,000', time: '11:48', partOfHiddenPath: true },
  { id: 'e7', source: 'ent-acc-482701', target: 'ent-neha', label: '₹48,200 Smurfing Wire', type: 'financial', evidenceId: 'EV-004', amount: '₹48,200', time: '12:10', partOfHiddenPath: true },
  { id: 'e8', source: 'ent-neha', target: 'ent-xyz', label: 'Director / Signatory', type: 'ownership', evidenceId: 'EV-006', partOfHiddenPath: true },
  { id: 'e9', source: 'ent-neha', target: 'ent-acc-772145', label: 'Signatory Authority', type: 'ownership', evidenceId: 'EV-004', labelRatio: 0.36, labelOffsetX: -32, labelOffsetY: 4 },
  { id: 'e10', source: 'ent-acc-772145', target: 'ent-xyz', label: 'Corporate Pool', type: 'financial', evidenceId: 'EV-006', labelRatio: 0.64, labelOffsetX: 32, labelOffsetY: 4 },
  { id: 'e11', source: 'ent-vikram', target: 'ent-xyz', label: 'Shadow Control', type: 'ownership', evidenceId: 'EV-009' },
  { id: 'e12', source: 'ent-vikram', target: 'ent-phone-burner', label: 'VoIP Terminal', type: 'communication', evidenceId: 'EV-009' },
  { id: 'e13', source: 'ent-rahul', target: 'ent-phone-rahul', label: 'Device Owner', type: 'ownership', evidenceId: 'EV-002' },
  { id: 'e14', source: 'ent-ajay', target: 'ent-phone-ajay', label: 'Device Owner', type: 'ownership', evidenceId: 'EV-002' },
  { id: 'e15', source: 'ent-rahul', target: 'ent-veh-creta', label: 'Registered Vehicle', type: 'ownership', evidenceId: 'EV-001' },
  { id: 'e16', source: 'ent-rahul', target: 'ent-loc-bus', label: 'Surveillance Site', type: 'location', evidenceId: 'EV-001', time: '08:45', labelRatio: 0.38, labelOffsetX: -14 },
  { id: 'e17', source: 'ent-ajay', target: 'ent-loc-bus', label: 'Surveillance Site', type: 'location', evidenceId: 'EV-001', time: '08:45', labelRatio: 0.38, labelOffsetX: 14 },
  { id: 'e18', source: 'ent-ajay', target: 'ent-loc-wh', label: 'SIGINT Tower Ping', type: 'location', evidenceId: 'EV-005', time: '11:15' },
  { id: 'e19', source: 'ent-xyz', target: 'ent-loc-wh', label: 'Gala 14 Premises', type: 'location', evidenceId: 'EV-006', labelRatio: 0.62, labelOffsetY: 12 },
];

export const PATTERNS_SUMMARY: PatternItem[] = [
  {
    id: 'pat-01',
    type: 'centrality',
    title: 'Network Centrality Broker: Ajay Patil (#1 Betweenness)',
    observation:
      'Ajay Patil exhibits the highest betweenness centrality (0.91) and degree (7) in the network, acting as the singular bridge between street operational actors and downstream banking conduit accounts.',
    supportingRecords: ['EV-001', 'EV-002', 'EV-003', 'EV-005'],
    entitiesInvolved: ['Ajay Patil', 'Rahul Sharma', 'Neha Verma'],
    severity: 'high',
  },
  {
    id: 'pat-02',
    type: 'path',
    title: 'Threshold Avoidance & Smurfing Layering (< ₹50,000)',
    observation:
      'Transactions were calibrated specifically under the ₹50,000 statutory PAN reporting threshold: ₹50,000 debited from A/C 889922 was forwarded within 22 minutes as ₹48,200 to XYZ Traders, withholding ₹1,800 mule cut.',
    supportingRecords: ['EV-003', 'EV-004', 'EV-008'],
    entitiesInvolved: ['A/C 889922', 'A/C 482701', 'A/C 772145', 'XYZ Traders Ltd'],
    severity: 'high',
  },
  {
    id: 'pat-03',
    type: 'cluster',
    title: 'Functional Community Clustering: Cell Alpha, Beta & Gamma',
    observation:
      'Graph community detection identifies Cell Alpha (Field Operations: Rahul, Vehicle, Central Terminal), Cell Beta (Financial Conduits: Ajay, SBI 889922, HDFC 482701), and Cell Gamma (Corporate Shells & Offshore: Neha, XYZ Traders, Vikram Singhania).',
    supportingRecords: ['EV-001', 'EV-003', 'EV-006', 'EV-009'],
    entitiesInvolved: ['Rahul Sharma', 'Ajay Patil', 'Neha Verma', 'Vikram Singhania'],
    severity: 'medium',
  },
  {
    id: 'pat-04',
    type: 'temporal',
    title: 'Co-Location Convergence & Disposable Burner Lifespan (<48h)',
    observation:
      'Two handsets attached to the identical cell tower sector MUM-C4-89 within 30 seconds despite zero previous interaction in 90 days. Burner phone +91-91230-00991 active for under 48 hours for tactical command.',
    supportingRecords: ['EV-002', 'EV-009'],
    entitiesInvolved: ['Rahul Sharma', 'Ajay Patil', '+91-91230-00991'],
    severity: 'high',
  },
];

export const INITIAL_AUDIT_LOGS = [
  {
    id: 'aud-001',
    timestamp: '12 May 2026 • 08:50:10 IST',
    action: 'INGEST_CCTNS_FEED',
    performedBy: 'System Ingestion Daemon',
    details: 'Ingested and cryptographically sealed Physical Surveillance Report EV-001 with SHA-256 integrity checksum.',
    signature: 'SHA256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
  },
  {
    id: 'aud-002',
    timestamp: '12 May 2026 • 09:05:22 IST',
    action: 'INGEST_CDR_GATEWAY',
    performedBy: 'Airtel/Jio Regulatory Bridge',
    details: 'Extracted 241s voice call intercept EV-002; matched calling and called IMEIs on cell sector MUM-C4-89.',
    signature: 'SHA256:a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8',
  },
  {
    id: 'aud-003',
    timestamp: '12 May 2026 • 11:55:05 IST',
    action: 'AI_ENTITY_RESOLUTION_MATCH',
    performedBy: 'TraceX Deduplication Service',
    details: 'Generated 94% probabilistic match candidate: Ajay Patil (CCTNS) ↔ A. Patil (SBI SFMS A/C 889922).',
    signature: 'SHA256:1c8d5a2f3b9e4a7c6d1e0f8a2b5c7d9e4a6f8b1c3d5e7a9b0c2d4e6f8a1b3c5',
  },
  {
    id: 'aud-004',
    timestamp: '12 May 2026 • 12:40:50 IST',
    action: 'QUERY_PATH',
    performedBy: 'Insp. V. Kulkarni (STF Central)',
    details: 'Executed multi-hop path traversal query between Rahul Sharma and XYZ Traders Ltd. 5-hop conduit uncovered.',
    signature: 'SHA256:9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8',
  },
];
