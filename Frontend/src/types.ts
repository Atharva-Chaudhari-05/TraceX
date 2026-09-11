export type UserRole =
  | 'Investigator'
  | 'Intelligence Analyst'
  | 'System Administrator';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  badgeNumber: string;
  department: string;
  avatar?: string;
  photo?: string;
  rank?: string;
  jurisdiction?: string;
  clearance?: string;
  station?: string;
  contact?: string;
  casesAssigned?: string[];
  status: 'Active' | 'On Leave' | 'Suspended';
  lastLogin?: string;
}

export type EntityType = 'person' | 'organisation' | 'phone' | 'account' | 'location' | 'event' | 'vehicle';
export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type RiskLevel = 'high' | 'medium' | 'low' | 'neutral';
export type ProvenanceMode = 'source-backed' | 'synthetic';

export interface ProvenanceInfo {
  sourceDataset: string;
  mode: ProvenanceMode;
}

export interface Entity {
  id: string;
  name: string;
  type: EntityType;
  role?: string;
  identifier?: string;
  risk: RiskLevel;
  confidenceLevel?: ConfidenceLevel;
  provenance?: ProvenanceInfo;
  caseIds?: string[];
  attributes?: Record<string, string | number>;
  connectionsCount?: number;
  connectedEntityIds?: string[];
  relatedEvidenceIds?: string[];
  metadata?: Record<string, any>;
  notes?: string;
  isResolvedDuplicate?: boolean;
  isConfirmed?: boolean;
}

export interface Relationship {
  id: string;
  source: string;
  target: string;
  label: string;
  type: 'communication' | 'financial' | 'association' | 'location' | 'ownership' | 'event_link';
  confidenceLevel: ConfidenceLevel;
  provenance: ProvenanceInfo;
  caseId: string;
  isConfirmed: boolean;
  details?: Record<string, any>;
}

export interface CaseSummaryMetrics {
  suspectedAmount?: string;
  interceptsAnalyzed?: number;
  bankAccountsFrozen?: number;
  nodesAtHighRisk?: number;
}

export interface CaseItem {
  id: string;
  title: string;
  status: 'Active' | 'Under Review' | 'Closed';
  priority: 'Critical' | 'High' | 'Medium';
  leadInvestigator: string;
  department: string;
  primaryEntityId: string;
  primaryEntityName: string;
  entityCount: number;
  relationshipCount: number;
  unresolvedMatchesCount: number;
  createdAt: string;
  lastUpdated: string;
  description: string;
  tags: string[];
  summaryMetrics?: CaseSummaryMetrics;
}

export interface InvestigationEvent {
  id: string;
  caseId: string;
  datetime: string;
  date: string;
  time: string;
  title: string;
  description: string;
  category: 'financial' | 'communication' | 'movement' | 'meeting' | 'surveillance' | 'system';
  confidenceLevel: ConfidenceLevel;
  provenance: ProvenanceInfo;
  evidenceId: string;
  entityIds: string[];
}

export interface MatchingSignal {
  field: string;
  leftValue: string;
  rightValue: string;
  weight: string;
  isExact: boolean;
}

export interface ResolutionQueueItem {
  id: string;
  caseId: string;
  confidence: number;
  confidenceLevel: ConfidenceLevel;
  status: 'pending' | 'confirmed' | 'rejected';
  createdAt: string;
  primaryEntity: {
    id: string;
    name: string;
    type: EntityType;
    role: string;
    sourceDataset: string;
    provenanceMode: ProvenanceMode;
    identifier: string;
    keyAttributes: Record<string, string>;
  };
  candidateEntity: {
    id: string;
    name: string;
    type: EntityType;
    role: string;
    sourceDataset: string;
    provenanceMode: ProvenanceMode;
    identifier: string;
    keyAttributes: Record<string, string>;
  };
  matchingSignals: MatchingSignal[];
  aiRationale: string;
  rejectionReason?: string;
  resolvedAt?: string;
  resolvedBy?: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  user?: string;
  role?: UserRole | string;
  actionType?: string;
  affectedCaseId?: string;
  affectedEntityId?: string;
  details: string;
  ipAddress?: string;
  signature: string;
  action?: string;
  performedBy?: string;
}

export interface KeyIndividual {
  id: string;
  name: string;
  role: string;
  centralityScore: number;
  crossCaseCount: number;
  connectedCases: string[];
  confidenceLevel: ConfidenceLevel;
  risk: 'high' | 'medium' | 'low';
  provenance: ProvenanceInfo;
  summary: string;
}

export interface ClusterItem {
  id: string;
  name: string;
  primaryCase: string;
  memberCount: number;
  cohesionScore: number;
  algorithm: string;
  confidenceLevel: ConfidenceLevel;
  provenance: ProvenanceInfo;
  leadEntities: string[];
  description: string;
}

export interface UnusualPattern {
  id: string;
  title: string;
  category: string;
  severity: 'high' | 'medium' | 'low';
  confidenceLevel: ConfidenceLevel;
  provenance: ProvenanceInfo;
  involvedEntities: string[];
  anomalyMetrics: Record<string, string | number>;
  description: string;
}

export interface AnalyticsData {
  keyIndividuals: KeyIndividual[];
  clusters: ClusterItem[];
  unusualPatterns: UnusualPattern[];
}

export interface PathHop {
  from: Entity;
  to: Entity;
  relationship: Relationship;
}

export interface PathResult {
  found: boolean;
  sourceEntity: Entity | null;
  targetEntity: Entity | null;
  hops: PathHop[];
  totalHops: number;
  overallConfidence: ConfidenceLevel;
  sourceBackedCount: number;
  syntheticCount: number;
  message?: string;
}

export interface GraphFilterState {
  entityTypes: Record<EntityType, boolean>;
  confidenceLevels: Record<ConfidenceLevel, boolean>;
  provenanceModes: Record<ProvenanceMode, boolean>;
  searchQuery: string;
  dateRange: {
    start: string;
    end: string;
  };
}

export type Case = CaseItem;

// 14 Tactical Views supported by TraceX
export type ViewType =
  | 'overview'
  | 'sources'
  | 'datasources'
  | 'records'
  | 'entities'
  | 'resolution'
  | 'graph'
  | 'path'
  | 'pathexplorer'
  | 'patterns'
  | 'timeline'
  | 'insights'
  | 'evidence'
  | 'analytics'
  | 'reports'
  | 'audit';

export type EvidenceType =
  | 'police_report'
  | 'communication'
  | 'financial'
  | 'surveillance'
  | 'organisation_activity';

export interface ExtractedEntityOccurrence {
  text: string;
  type: EntityType;
  entityId?: string;
  startIndex?: number;
  endIndex?: number;
}

export interface EvidenceRecord {
  id: string;
  title: string;
  type: EvidenceType;
  typeLabel: string;
  source: string;
  date: string;
  timestamp: string;
  status: 'Processed' | 'Verified' | 'Pending Review';
  summary: string;
  rawContent: string;
  structuredDetails?: Record<string, any>;
  extractedEntities: ExtractedEntityOccurrence[];
  supportedRelationships: string[];
  relatedInsightIds: string[];
  custodyChain?: string;
  hashChecksum?: string;
}

export interface DataSourceItem {
  id: string;
  name: string;
  category: string;
  recordCount: number;
  status: 'Processed' | 'Ingesting' | 'Verified';
  lastUpdated: string;
  sourceSystem: string;
  fileFormat: string;
  integrityHash: string;
  records: string[];
  description: string;
}

export interface TimelineEvent {
  id: string;
  time: string;
  date: string;
  datetime: string;
  title: string;
  description: string;
  source: string;
  sourceType: EvidenceType;
  evidenceId: string;
  entities: string[];
  category: 'movement' | 'meeting' | 'communication' | 'financial' | 'surveillance' | 'system';
  amount?: string;
  duration?: string;
  location?: string;
  highlightInHiddenPath?: boolean;
}

export interface AIInsight {
  id: string;
  priority: 'high' | 'medium' | 'low';
  priorityLabel: string;
  title: string;
  category: 'Hidden Relationship' | 'Entity Resolution' | 'Location Pattern' | 'Financial Structuring';
  whatFound: string;
  whyFlagged: string;
  whyItMatters?: string;
  supportingEvidenceIds: string[];
  relatedEntityIds: string[];
  status: 'AI-Generated' | 'Under Review' | 'Verified by Investigator' | 'Included in Report';
  confidenceScore?: number;
  recommendedSteps?: string[];
  actionLabel?: string;
  actionTargetView?: ViewType;
}

export interface EntityMatchItem {
  matchId: string;
  confidence: number;
  status: 'pending' | 'approved' | 'rejected';
  leftEntity: {
    name: string;
    sourceType: string;
    phone: string;
    location: string;
    evidenceId: string;
    role: string;
  };
  rightEntity: {
    name: string;
    sourceType: string;
    phoneMetadata: string;
    linkedAccount: string;
    evidenceId: string;
    role: string;
  };
  supportingSignals: {
    title: string;
    description: string;
    verified: boolean;
  }[];
  approvedAt?: string;
  approvedBy?: string;
  investigatorNotes?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: EntityType;
  risk: RiskLevel;
  x: number;
  y: number;
  connections: number;
  role?: string;
  identifier?: string;
  isResolvedMerged?: boolean;
  partOfHiddenPath?: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type: 'communication' | 'meeting' | 'financial' | 'entity_match' | 'location' | 'ownership';
  evidenceId?: string;
  time?: string;
  amount?: string;
  partOfHiddenPath?: boolean;
  isApprovedLink?: boolean;
  labelRatio?: number;
  labelOffsetX?: number;
  labelOffsetY?: number;
}

export interface PatternItem {
  id: string;
  type: 'centrality' | 'path' | 'cluster' | 'temporal';
  title: string;
  observation: string;
  supportingRecords: string[];
  entitiesInvolved: string[];
  severity: 'high' | 'medium' | 'low';
}
