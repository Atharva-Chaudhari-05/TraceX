import React, { createContext, useContext, useState, useEffect, useMemo, ReactNode } from 'react';
import { api } from '../lib/api';
import {
  ViewType,
  Entity,
  EvidenceRecord,
  DataSourceItem,
  TimelineEvent,
  AIInsight,
  EntityMatchItem,
  GraphNode,
  GraphEdge,
  PatternItem,
  AuditLogEntry,
  UserRole,
  UserProfile,
} from '../types';
import {
  CASE_METADATA,
  INITIAL_ENTITIES,
  INITIAL_EVIDENCE_RECORDS,
  INITIAL_DATA_SOURCES,
  INITIAL_TIMELINE_EVENTS,
  INITIAL_AI_INSIGHTS,
  INITIAL_ENTITY_MATCH,
  INITIAL_GRAPH_NODES,
  INITIAL_GRAPH_EDGES,
  PATTERNS_SUMMARY,
  INITIAL_AUDIT_LOGS,
} from '../data/mockData';

export const DEMO_USERS_MAP: Record<UserRole, UserProfile & { password: string }> = {
  Investigator: {
    id: 'USR-INV-01',
    name: 'Investigator User',
    email: 'investigator@tracex.local',
    password: 'investigatorpassword',
    role: 'Investigator',
    rank: 'Senior Inspector of Police (Cyber Crime)',
    badgeNumber: 'SCB-88219',
    department: 'Special Task Force - Central Command',
    station: 'Central Cyber Investigation Cell, Mumbai',
    jurisdiction: 'National & Inter-State Economic Offenses',
    clearance: 'LEVEL-4 TOP SECRET // SEC 65B CERTIFIED',
    contact: '+91-22-2618-8821',
    casesAssigned: [],
    photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&auto=format&fit=crop&q=80',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&auto=format&fit=crop&q=80',
    status: 'Active',
    lastLogin: 'Today, 14:02 IST',
  },
  'Intelligence Analyst': {
    id: 'USR-ANA-02',
    name: 'Analyst User',
    email: 'analyst@tracex.local',
    password: 'analystpassword',
    role: 'Intelligence Analyst',
    rank: 'Deputy Superintendent of Police (Forensic Intel)',
    badgeNumber: 'NCB-INTEL-440',
    department: 'Directorate of Forensic Intelligence & Cyber Forensics',
    station: 'National Cyber Coordination Centre (I4C), New Delhi',
    jurisdiction: 'National Intelligence Grid & Cross-Border Telemetry',
    clearance: 'LEVEL-5 SPECIAL FORENSIC CLEARANCE',
    contact: '+91-11-2309-4401',
    casesAssigned: [],
    photo: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&auto=format&fit=crop&q=80',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&auto=format&fit=crop&q=80',
    status: 'Active',
    lastLogin: 'Today, 11:15 IST',
  },
  'System Administrator': {
    id: 'USR-ADM-04',
    name: 'Admin User',
    email: 'admin@tracex.local',
    password: 'adminpassword',
    role: 'System Administrator',
    rank: 'Director of Systems & Cryptographic Infrastructure',
    badgeNumber: 'NIC-SYS-104',
    department: 'National Informatics Centre / Command Cyber Wing',
    station: 'Central Security Operations Centre (CSOC), Bengaluru',
    jurisdiction: 'Platform Wide Infrastructure, IAM & Evidence Custody Audit',
    clearance: 'ROOT SYSTEM SECURITY ADMINISTRATOR',
    contact: '+91-80-2559-1040',
    casesAssigned: [],
    photo: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&auto=format&fit=crop&q=80',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&auto=format&fit=crop&q=80',
    status: 'Active',
    lastLogin: 'Today, 09:00 IST',
  },
};

interface NotificationItem {
  id: string;
  time: string;
  title: string;
  description: string;
  type: 'alert' | 'match' | 'system' | 'info';
  read: boolean;
  targetView: ViewType;
}

interface InvestigationContextType {
  // Auth & RBAC
  currentUser: UserProfile;
  isAuthenticated: boolean;
  isInitializingAuth: boolean;
  loginUser: (email: string, password?: string, role?: UserRole) => Promise<boolean>;
  logoutUser: () => void;

  // Navigation & Views
  currentView: ViewType;
  setCurrentView: (view: ViewType) => void;
  navigateTo: (view: ViewType, options?: { entityId?: string; recordId?: string; evidenceId?: string; insightId?: string; highlightPath?: boolean }) => void;

  // Case Metadata
  caseData: any;
  cases: any[];
  currentCaseId: string;
  switchCase: (caseId: string) => void;

  // Entities & Selection
  entities: Entity[];
  selectedEntityId: string | null;
  setSelectedEntityId: (id: string | null) => void;
  selectedEntity: Entity | null;

  // Records & Selection
  evidenceRecords: EvidenceRecord[];
  selectedRecordId: string | null;
  setSelectedRecordId: (id: string | null) => void;
  selectedRecord: EvidenceRecord | null;

  // Evidence Explorer Selection
  selectedEvidenceId: string | null;
  setSelectedEvidenceId: (id: string | null) => void;
  selectedEvidence: EvidenceRecord | null;

  // Data Sources
  dataSources: DataSourceItem[];
  addDataSource: (newSource: Omit<DataSourceItem, 'id' | 'lastUpdated' | 'status' | 'integrityHash'>) => void;
  isIngestingModalOpen: boolean;
  setIsIngestingModalOpen: (open: boolean) => void;

  // Entity Resolution
  entityMatch: EntityMatchItem;
  approveEntityMatch: (investigatorNotes?: string) => void;
  rejectEntityMatch: (investigatorNotes?: string) => void;
  resetEntityMatch: () => void;

  // Graph Analysis & Hidden Connection
  graphNodes: GraphNode[];
  graphEdges: GraphEdge[];
  selectedGraphNodeId: string | null;
  setSelectedGraphNodeId: (id: string | null) => void;
  selectedGraphEdgeId: string | null;
  setSelectedGraphEdgeId: (id: string | null) => void;
  showHiddenConnection: boolean;
  setShowHiddenConnection: (show: boolean) => void;
  toggleHiddenConnection: () => void;

  // Timeline
  timelineEvents: TimelineEvent[];

  // AI Insights
  aiInsights: AIInsight[];
  selectedInsightId: string | null;
  setSelectedInsightId: (id: string | null) => void;
  verifyInsight: (id: string) => void;
  toggleInsightReportStatus: (id: string) => void;
  updateInsightStatus: (id: string, status: AIInsight['status']) => void;

  // Pattern Analysis
  patterns: PatternItem[];

  // Global Search
  isSearchOpen: boolean;
  setIsSearchOpen: (open: boolean) => void;
  globalSearchQuery: string;
  setGlobalSearchQuery: (query: string) => void;

  // Demo Guided Walkthrough (Steps 1 to 6)
  demoStep: number;
  setDemoStep: (step: number) => void;
  isDemoBannerVisible: boolean;
  setIsDemoBannerVisible: (visible: boolean) => void;
  nextDemoStep: () => void;
  prevDemoStep: () => void;
  resetDemoStep: () => void;

  // Investigator Notes
  investigatorNotes: string;
  setInvestigatorNotes: (notes: string) => void;
  saveAuditLog: (action: string, details?: string) => void;
  auditLogs: AuditLogEntry[];

  // Left Sidebar State (Collapsible drawer, shifts main stage right when open)
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean | ((prev: boolean) => boolean)) => void;
  toggleSidebar: () => void;
  isSidebarDropdownOpen: boolean;
  setIsSidebarDropdownOpen: (open: boolean | ((prev: boolean) => boolean)) => void;
  toggleSidebarDropdown: () => void;

  // Notifications
  notifications: NotificationItem[];
  setIsNotificationsOpen: (open: boolean) => void;
  isNotificationsOpen: boolean;
  markAllNotificationsRead: () => void;

  // Theme State (Light by default, toggleable to Dark)
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
  activePatterns: PatternItem[];
  networkAnalytics: any;
}

const InvestigationContext = createContext<InvestigationContextType | undefined>(undefined);

export const InvestigationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Authentication & RBAC (3 Roles: Investigator, Intelligence Analyst, System Administrator)
  const [currentUser, setCurrentUser] = useState<UserProfile>(DEMO_USERS_MAP.Investigator);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isInitializingAuth, setIsInitializingAuth] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('tracex_auth_token');
      if (token) {
        try {
          const meResponse = await api.get('/api/v1/auth/me');
          const { roles: backendRoles, email: backendEmail, id: backendId } = meResponse.data;
          
          let mappedRole: UserRole = 'Investigator';
          if (backendRoles.includes('Admin')) mappedRole = 'System Administrator';
          else if (backendRoles.includes('Analyst')) mappedRole = 'Intelligence Analyst';
          else if (backendRoles.includes('Investigator')) mappedRole = 'Investigator';

          const userProfile: UserProfile = {
            id: backendId,
            name: backendEmail.split('@')[0],
            email: backendEmail,
            role: mappedRole,
            badgeNumber: `TRACEX-${mappedRole.substring(0,3).toUpperCase()}`,
            department: 'Cyber Forensics Division',
            status: 'Active',
            lastLogin: 'Just now',
          };
          setCurrentUser(userProfile);
          setIsAuthenticated(true);
        } catch (e) {
          localStorage.removeItem('tracex_auth_token');
          setIsAuthenticated(false);
        }
      }
      setIsInitializingAuth(false);
    };
    initAuth();
  }, []);

  const loginUser = async (email: string, password?: string, role?: UserRole): Promise<boolean> => {
    try {
      const response = await api.post('/api/v1/auth/login', {
        email,
        password: password || '',
      });
      
      const { access_token } = response.data;
      localStorage.setItem('tracex_auth_token', access_token);

      // Fetch actual role from backend
      const meResponse = await api.get('/api/v1/auth/me');
      const { roles: backendRoles, email: backendEmail, id: backendId } = meResponse.data;
      
      let mappedRole: UserRole = 'Investigator';
      if (backendRoles.includes('Admin')) mappedRole = 'System Administrator';
      else if (backendRoles.includes('Analyst')) mappedRole = 'Intelligence Analyst';
      else if (backendRoles.includes('Investigator')) mappedRole = 'Investigator';

      const userProfile: UserProfile = {
        id: backendId,
        name: backendEmail.split('@')[0],
        email: backendEmail,
        role: mappedRole,
        badgeNumber: `TRACEX-${mappedRole.substring(0,3).toUpperCase()}`,
        department: 'Cyber Forensics Division',
        status: 'Active',
        lastLogin: 'Just now',
      };

      setCurrentUser(userProfile);
      setIsAuthenticated(true);
      localStorage.setItem('tracex_auth_user', JSON.stringify(userProfile));
      localStorage.setItem('tracex_is_authenticated', 'true');
      setCurrentView('overview');

      const now = new Date();
      const formatted = `12 May 2026 • ${now.toTimeString().substring(0, 8)} IST`;
      const actorDesc = `${userProfile.name} (${userProfile.role}, ${userProfile.badgeNumber})`;
      setAuditLogs((prev) => [
        {
          id: `aud-${Date.now().toString().slice(-4)}`,
          timestamp: formatted,
          action: 'USER_LOGIN',
          performedBy: actorDesc,
          details: `Successful authenticated session establishment for ${userProfile.name} (${userProfile.role}). JWT token issued.`,
          signature: `SHA256:${Math.random().toString(16).slice(2, 10)}...verified`,
        },
        ...prev,
      ]);

      return true;
    } catch (error) {
      console.error('Login failed', error);
      throw error;
    }
  };

  const logoutUser = () => {
    const now = new Date();
    const formatted = `12 May 2026 • ${now.toTimeString().substring(0, 8)} IST`;
    const actorDesc = currentUser
      ? `${currentUser.name} (${currentUser.role}, ${currentUser.badgeNumber})`
      : 'Session User';
    setAuditLogs((prev) => [
      {
        id: `aud-${Date.now().toString().slice(-4)}`,
        timestamp: formatted,
        action: 'USER_LOGOUT',
        performedBy: actorDesc,
        details: `Cryptographic session terminated and memory cache wiped for ${actorDesc}.`,
        signature: `SHA256:${Math.random().toString(16).slice(2, 10)}...verified`,
      },
      ...prev,
    ]);
    setIsAuthenticated(false);
    localStorage.setItem('tracex_is_authenticated', 'false');
    localStorage.removeItem('tracex_auth_token');
  };

  const [currentView, setCurrentView] = useState<ViewType>('overview');
  const [currentCaseId, setCurrentCaseId] = useState<string>('');
  const [cases, setCases] = useState<any[]>([]);
  const [caseData, setCaseData] = useState<any>(CASE_METADATA);
  
  const [entities, setEntities] = useState<Entity[]>([]);
  const [evidenceRecords, setEvidenceRecords] = useState<EvidenceRecord[]>([]);
  const [dataSources, setDataSources] = useState<DataSourceItem[]>([]);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [patterns, setPatterns] = useState<PatternItem[]>([]);
  const [networkAnalytics, setNetworkAnalytics] = useState<any>(null);

  const [realPatterns, setRealPatterns] = useState<PatternItem[] | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    const loadCases = async () => {
      try {
        const res = await api.get(`/api/v1/cases`);
        if (res.data && res.data.length > 0) {
          setCases(res.data);
          if (!currentCaseId) {
            setCurrentCaseId(res.data[0].id);
          }
        }
      } catch (e) {
        console.error("Cases fetch failed", e);
      }
    };
    loadCases();
  }, [isAuthenticated]);

  useEffect(() => {
    if (cases.length > 0 && currentCaseId) {
      const activeCase = cases.find(c => c.id === currentCaseId);
      if (activeCase) {
        const payload = activeCase.payload || {};
        setCaseData({
          caseId: activeCase.id,
          name: payload.title || payload.name || activeCase.label || 'Unknown Case',
          description: payload.description || payload.summary || 'No description available.',
          classification: payload.classification || 'RESTRICTED',
          priority: payload.priority || 'High',
          status: payload.status || 'ACTIVE',
          leadInvestigator: payload.leadOfficer || 'Demo Investigator',
          jurisdiction: payload.jurisdiction || payload.agency || 'General Jurisdiction',
          stats: {
            entities: payload.entities_count || 0,
            relationships: payload.relationships_count || 0,
            events: payload.events_count || 0,
            documents: payload.documents_count || 0,
          }
        });
      }
    }
  }, [cases, currentCaseId]);

  useEffect(() => {
    if (!isAuthenticated || !currentCaseId) return;
    const loadAnalytics = async () => {
      try {
        const res = await api.get(`/api/v1/analytics/network?case_id=${currentCaseId}`);
        if (res.data) {
          setNetworkAnalytics(res.data);
          if (res.data.key_entities) {
            setRealPatterns(res.data.key_entities.map((p: any, i: number) => ({
              id: `PAT-REAL-${i}`,
              name: p.entity_id || 'Network Pattern',
              description: p.explanation?.why || 'Behavioral anomaly detected.',
              confidence: Math.round((p.score || 0.8) * 100),
              impact: 'high',
              relatedCases: 2
            })));
          }
        } else {
          setNetworkAnalytics(null);
        }
      } catch (e) {
        console.error("Analytics fetch failed", e);
        setNetworkAnalytics(null);
      }
    };
    loadAnalytics();
  }, [currentCaseId, isAuthenticated]);

  const activePatterns = realPatterns || patterns;

  // Selection states
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [selectedInsightId, setSelectedInsightId] = useState<string | null>(null);
  const [selectedGraphNodeId, setSelectedGraphNodeId] = useState<string | null>(null);
  const [selectedGraphEdgeId, setSelectedGraphEdgeId] = useState<string | null>(null);

  // Resolution & Graph state
  const [entityMatch, setEntityMatch] = useState<{
    status: 'pending' | 'resolved' | 'rejected' | 'idle';
    confidence: number;
    matchScore: number;
    matchedAttributes: string[];
    discrepancies: string[];
  }>({
    status: 'idle',
    confidence: 0,
    matchScore: 0,
    matchedAttributes: [],
    discrepancies: [],
  });
  const [showHiddenConnection, setShowHiddenConnection] = useState<boolean>(false);
  const [isIngestingModalOpen, setIsIngestingModalOpen] = useState<boolean>(false);

  // Search & Demo states
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);
  const [globalSearchQuery, setGlobalSearchQuery] = useState<string>('');
  const [demoStep, setDemoStep] = useState<number>(0);
  const [isDemoBannerVisible, setIsDemoBannerVisible] = useState<boolean>(true);

  // Notes & Audit
  const [investigatorNotes, setInvestigatorNotes] = useState<string>(
    `INVESTIGATOR WORKING MEMORANDUM\nDate: 12 May 2026\nInvestigator: Demo User\n\nPreliminary Assessment:\n- Physical surveillance confirms direct meeting between primary subject Rahul Sharma and Ajay Patil at Central Bus Station (09:15).\n- CDR telephony corroborates 4-minute voice contact immediately post-meeting (09:18).\n- Core banking records establish a two-tier transfer (₹50k -> ₹48.2k) terminating at XYZ Traders via Neha Verma.\n- Recommend approving identity link between Ajay Patil and A. Patil based on matching phone metadata and temporal correlation.\n- Recommend formal subpoena for XYZ Traders GSTIN filings and Warehouse Sector 4 lease agreements.`
  );
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>(INITIAL_AUDIT_LOGS);

  // Notifications
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: 'notif-1',
      time: '15:42 IST',
      title: 'Hidden Relationship Path Identified',
      description: 'Indirect multi-hop path detected between Rahul Sharma and XYZ Traders.',
      type: 'alert',
      read: false,
      targetView: 'insights',
    },
    {
      id: 'notif-2',
      time: '15:39 IST',
      title: 'Entity Resolution Match Available',
      description: 'Candidate match between Ajay Patil and A. Patil requires investigator review (92% confidence).',
      type: 'match',
      read: false,
      targetView: 'resolution',
    },
    {
      id: 'notif-3',
      time: '15:35 IST',
      title: 'Data Sources Processed',
      description: 'All 4 multi-source ingestion channels updated for Operation Nexus.',
      type: 'info',
      read: true,
      targetView: 'sources',
    },
  ]);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(() => {
    return localStorage.getItem('tracex_sidebar_open') === 'true';
  });
  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => {
      const next = !prev;
      localStorage.setItem('tracex_sidebar_open', String(next));
      return next;
    });
  };
  const [isSidebarDropdownOpen, setIsSidebarDropdownOpen] = useState<boolean>(false);
  const toggleSidebarDropdown = toggleSidebar;

  // Theme State (Light mode by default, toggleable to Dark mode)
  const [theme, setThemeState] = useState<'light' | 'dark'>(() => {
    try {
      const saved = localStorage.getItem('tracex_theme');
      if (saved === 'dark' || saved === 'light') return saved;
    } catch (e) {}
    return 'light'; // Initially website should be in light mode
  });

  const setTheme = (newTheme: 'light' | 'dark') => {
    setThemeState(newTheme);
    try {
      localStorage.setItem('tracex_theme', newTheme);
    } catch (e) {}
    if (newTheme === 'light') {
      document.documentElement.classList.add('light-theme');
      document.documentElement.classList.remove('dark-theme');
    } else {
      document.documentElement.classList.remove('light-theme');
      document.documentElement.classList.add('dark-theme');
    }
  };

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light-theme');
      document.documentElement.classList.remove('dark-theme');
    } else {
      document.documentElement.classList.remove('light-theme');
      document.documentElement.classList.add('dark-theme');
    }
  }, [theme]);

  // Real graph state
  const [realGraphNodes, setRealGraphNodes] = useState<GraphNode[] | null>(null);
  const [realGraphEdges, setRealGraphEdges] = useState<GraphEdge[] | null>(null);

  useEffect(() => {
    if (!isAuthenticated || !currentCaseId) return;
    const fetchGraph = async () => {
      try {
        // Use currentCaseId as the anchor — always returns real graph data
        const anchorId = selectedGraphNodeId && !selectedGraphNodeId.startsWith('ent-') 
          ? selectedGraphNodeId 
          : currentCaseId;
        const res = await api.get(`/api/v1/graph/neighborhood/${anchorId}?depth=2&limit=500`);
        if (res.data && res.data.nodes && res.data.nodes.length > 0) {
          const backendNodes = res.data.nodes.map((n: any) => ({
             id: n.id,
             label: n.properties?.name || n.properties?.title || n.id,
             type: (n.labels && n.labels.length > 0 ? n.labels[0].toLowerCase() : 'person'),
             x: 200 + Math.random() * 400,
             y: 100 + Math.random() * 300,
             risk: 'medium',
             role: 'Extracted Entity',
             metadata: n.properties || {}
          }));
          const backendEdges = res.data.edges.map((e: any, i: number) => ({
             id: e.id,
             source: e.source,
             target: e.target,
             label: e.type,
             type: 'communication'
          }));
          setRealGraphNodes(backendNodes);
          setRealGraphEdges(backendEdges);
          
          // Extract Entities from Nodes
          const newEntities = backendNodes
            .filter((n: any) => !n.type.includes('event') && !n.type.includes('document') && !n.type.includes('incident') && !n.type.includes('transaction'))
            .map((n: any) => ({
              id: n.id,
              name: n.label,
              type: n.type,
              role: n.role,
              identifier: n.id,
              risk: n.risk,
              connectionsCount: backendEdges.filter((e: any) => e.source === n.id || e.target === n.id).length,
              connectedEntityIds: [],
              metadata: n.metadata,
              notes: ''
            }));
          setEntities(newEntities);
          
          // Extract Timeline Events from Nodes
          const newTimelineEvents = backendNodes
            .filter((n: any) => n.type.includes('event') || n.type.includes('transaction') || n.type.includes('incident'))
            .map((n: any) => ({
              id: n.id,
              time: (n.metadata?.timestamp || n.metadata?.date || '12:00').substring(11, 16),
              date: (n.metadata?.timestamp || n.metadata?.date || 'Unknown Date').substring(0, 10),
              datetime: n.metadata?.timestamp || n.metadata?.date || 'Unknown Date',
              title: n.label,
              description: n.metadata?.description || n.metadata?.details || 'Event recorded in system',
              category: n.type.includes('transaction') ? 'financial' : 'system',
              source: 'Graph Data',
              sourceType: 'system',
              evidenceId: '',
              entities: [],
              amount: n.metadata?.amount || undefined,
            }));
          setTimelineEvents(newTimelineEvents);
          
          // Extract Evidence from Nodes
          const newEvidence = backendNodes
            .filter((n: any) => n.type.includes('document'))
            .map((n: any) => ({
              id: n.id,
              title: n.label,
              type: 'document',
              dateAdded: n.metadata?.date || 'Unknown',
              summary: 'Document extracted during ingestion',
              relatedEntities: [],
              source: 'Ingestion'
            }));
          setEvidenceRecords(newEvidence);
          
        }
      } catch (e) {
        console.error("Graph fetch failed", e);
      }
    };
    fetchGraph();
  }, [selectedGraphNodeId, currentCaseId, isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated || !currentCaseId) return;
    const loadML = async () => {
      try {
        const res = await api.get(`/api/v1/ml/case/${currentCaseId}/signals`);
        if (res.data && res.data.signals && res.data.signals.length > 0) {
          setAiInsights(res.data.signals.map((s: any, i: number) => {
            // ML Backend usually sends signal_type, description, risk_score, source_nodes, etc.
            const priority = (s.risk_score && s.risk_score > 0.7) ? 'high' : ((s.risk_score && s.risk_score > 0.4) ? 'medium' : 'low');
            return {
               id: `INS-REAL-${i}`,
               priority: priority,
               priorityLabel: priority === 'high' ? 'High Severity' : 'Medium Severity',
               title: s.signal_type || 'ML Signal',
               category: s.signal_type || 'Hidden Relationship',
               whatFound: s.description || 'ML Inference generated.',
               whyFlagged: s.reasoning || 'Automated behavioral anomaly detected.',
               whyItMatters: s.impact || 'Requires investigator review.',
               supportingEvidenceIds: [],
               relatedEntityIds: s.source_nodes || [],
               status: 'Pending Verification'
            };
          }));
        } else {
          setAiInsights([]);
        }
      } catch (e) {
        console.error("ML fetch failed", e);
        setAiInsights([]);
      }
    };
    loadML();
  }, [currentCaseId, isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated || !currentCaseId) return;
    const loadAnalytics = async () => {
      try {
        const res = await api.get(`/api/v1/analytics/network?case_id=${currentCaseId}`);
        if (res.data) setNetworkAnalytics(res.data);
      } catch (e) {
        console.error("Analytics fetch failed", e);
        setNetworkAnalytics(null);
      }
    };
    loadAnalytics();
  }, [currentCaseId, isAuthenticated]);

  const saveAuditLog = (action: string, details?: string) => {
    const now = new Date();
    const formatted = `12 May 2026 • ${now.toTimeString().substring(0, 8)} IST`;
    const performedBy = currentUser
      ? `${currentUser.name} (${currentUser.role}, ${currentUser.badgeNumber})`
      : 'Insp. V. Kulkarni (Investigator, SCB-88219)';
    const newLog: AuditLogEntry = {
      id: `aud-${Date.now().toString().slice(-4)}`,
      timestamp: formatted,
      action: action.includes(':') ? action.split(':')[0].trim() : (action.toUpperCase().replace(/\s+/g, '_').slice(0, 24)),
      performedBy,
      details: details || action,
      signature: `SHA256:${Math.random().toString(16).slice(2, 10)}...verified`,
    };
    setAuditLogs((prev) => [newLog, ...prev]);
  };

  const switchCase = (caseId: string) => {
    setCurrentCaseId(caseId);
    // Reset selection state to prevent cross-case data leakage
    setSelectedEntityId(null);
    setSelectedRecordId(null);
    setSelectedEvidenceId(null);
    setSelectedInsightId(null);
    setSelectedGraphNodeId(null);
    setSelectedGraphEdgeId(null);
    setRealGraphNodes(null);
    setRealGraphEdges(null);
    setEntityMatch(INITIAL_ENTITY_MATCH);
    saveAuditLog('CASE_SWITCH', `Switched active investigation case context to ${caseId}.`);
  };

  const markAllNotificationsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  // Cross-Navigation helper
  const navigateTo = (
    view: ViewType,
    options?: {
      entityId?: string;
      recordId?: string;
      evidenceId?: string;
      insightId?: string;
      highlightPath?: boolean;
    }
  ) => {
    setCurrentView(view);
    if (options?.entityId) setSelectedEntityId(options.entityId);
    if (options?.recordId) setSelectedRecordId(options.recordId);
    if (options?.evidenceId) setSelectedEvidenceId(options.evidenceId);
    if (options?.insightId) setSelectedInsightId(options.insightId);
    if (options?.highlightPath !== undefined) setShowHiddenConnection(options.highlightPath);
    if (options?.entityId) setSelectedGraphNodeId(options.entityId);
  };

  // Approval of Entity Match
  const approveEntityMatch = async (notes?: string) => {
    const actorName = currentUser ? `${currentUser.name} (${currentUser.role})` : 'Investigator Demo User';
    
    try {
      await api.post('/api/v1/match/match-1/decision', { decision: "approved", notes });
    } catch(e) {
      console.error("Failed to sync decision to backend", e);
    }
    
    setEntityMatch((prev) => ({
      ...prev,
      status: 'approved',
      approvedAt: '12 May 2026 • 15:50 IST',
      approvedBy: actorName,
      investigatorNotes: notes || 'Verified: Exact phone metadata match + temporal overlap confirms single identity.',
    }));
    saveAuditLog(
      'ENTITY_MATCH_APPROVED',
      `Officer approved probabilistic match. Nodes merged into unified identity on master judicial graph. Note: "${notes || 'Phone & temporal correlation match verified.'}"`
    );
  };

  const rejectEntityMatch = (notes?: string) => {
    const actorName = currentUser ? `${currentUser.name} (${currentUser.role})` : 'Investigator Demo User';
    setEntityMatch((prev) => ({
      ...prev,
      status: 'rejected',
      approvedAt: '12 May 2026 • 15:50 IST',
      approvedBy: actorName,
      investigatorNotes: notes || 'Rejected: Entities maintain distinct identity records pending further evidence.',
    }));
    saveAuditLog(
      'ENTITY_MATCH_REJECTED',
      `Officer rejected entity merge proposal (Ajay Patil ↔ A. Patil). Candidates preserved as distinct unmerged nodes on graph. Note: "${notes || 'Rejected pending further evidence.'}"`
    );
  };

  const resetEntityMatch = () => {
    setEntityMatch((prev) => ({
      ...prev,
      status: 'pending',
      approvedAt: undefined,
      approvedBy: undefined,
      investigatorNotes: undefined,
    }));
    saveAuditLog('ENTITY_MATCH_RESET', 'Investigator reset entity match status to Pending Review.');
  };

  // AI Insight Actions
  const verifyInsight = (id: string) => {
    setAiInsights((prev) =>
      prev.map((ins) =>
        ins.id === id
          ? { ...ins, status: 'Verified by Investigator' }
          : ins
      )
    );
    saveAuditLog('INSIGHT_VERIFIED', `Investigator verified AI finding ${id} as legally substantiated.`);
  };

  const toggleInsightReportStatus = (id: string) => {
    setAiInsights((prev) =>
      prev.map((ins) => {
        if (ins.id === id) {
          const nextStatus =
            ins.status === 'Included in Report' ? 'Verified by Investigator' : 'Included in Report';
          return { ...ins, status: nextStatus };
        }
        return ins;
      })
    );
    saveAuditLog('INSIGHT_REPORT_TOGGLED', `Toggled report inclusion status for finding ${id}.`);
  };

  const updateInsightStatus = (id: string, status: AIInsight['status']) => {
    setAiInsights((prev) =>
      prev.map((ins) => (ins.id === id ? { ...ins, status } : ins))
    );
    saveAuditLog('INSIGHT_STATUS_UPDATE', `Updated finding ${id} status to ${status}.`);
  };

  // Graph dynamic state based on match approval
  const graphNodes = useMemo(() => {
    if (realGraphNodes) return realGraphNodes;
    return INITIAL_GRAPH_NODES.map((node) => {
      if (node.id === 'ent-apatil' && entityMatch.status === 'approved') {
        return {
          ...node,
          label: 'A. Patil (Linked to Ajay)',
          isResolvedMerged: true,
          role: 'Verified Alias (Approved)',
        };
      }
      return node;
    });
  }, [entityMatch.status, realGraphNodes]);

  const graphEdges = useMemo(() => {
    if (realGraphEdges) return realGraphEdges;
    return INITIAL_GRAPH_EDGES.map((edge) => {
      if (edge.id === 'e4' && entityMatch.status === 'approved') {
        return {
          ...edge,
          label: 'Verified Identity Match (Approved)',
          isApprovedLink: true,
        };
      }
      return edge;
    });
  }, [entityMatch.status, realGraphEdges]);

  const toggleHiddenConnection = () => {
    setShowHiddenConnection((prev) => !prev);
  };

  // Add mock data source / file upload
  const addDataSource = async (newSource: Omit<DataSourceItem, 'id' | 'lastUpdated' | 'status' | 'integrityHash'>) => {
    const id = `ds-${Date.now().toString().slice(-4)}`;
    const fullSource: DataSourceItem = {
      ...newSource,
      id,
      status: 'Processing',
      lastUpdated: 'Just now',
      integrityHash: `MD5: PENDING`,
    };
    setDataSources((prev) => [...prev, fullSource]);
    saveAuditLog(
      'DATA_FILE_UPLOADED',
      `New forensic feed/file uploaded: ${newSource.name}. Starting ingestion pipeline.`
    );

    try {
      await api.post('/api/v1/ingestion/trigger');
      setDataSources((prev) => prev.map(ds => ds.id === id ? { ...ds, status: 'Processed' } : ds));
      saveAuditLog('INGESTION_COMPLETE', `Ingestion completed successfully for ${newSource.name}`);
    } catch (e) {
      console.error("Ingestion failed", e);
      setDataSources((prev) => prev.map(ds => ds.id === id ? { ...ds, status: 'Failed' } : ds));
      saveAuditLog('INGESTION_FAILED', `Ingestion failed for ${newSource.name}`);
    }
  };

  // Demo walkthrough steps
  const nextDemoStep = () => {
    if (demoStep < 6) {
      const next = demoStep + 1;
      setDemoStep(next);
      executeDemoStepAction(next);
    }
  };

  const prevDemoStep = () => {
    if (demoStep > 1) {
      const prev = demoStep - 1;
      setDemoStep(prev);
      executeDemoStepAction(prev);
    }
  };

  const resetDemoStep = () => {
    setDemoStep(1);
    executeDemoStepAction(1);
  };

  const executeDemoStepAction = (step: number) => {
    switch (step) {
      case 1:
        setCurrentView('overview');
        break;
      case 2:
        setCurrentView('records');
        setSelectedRecordId('EV-001');
        break;
      case 3:
        setCurrentView('resolution');
        break;
      case 4:
        setCurrentView('graph');
        setShowHiddenConnection(false);
        break;
      case 5:
        setCurrentView('graph');
        setShowHiddenConnection(true);
        break;
      case 6:
        setCurrentView('evidence');
        setSelectedEvidenceId('EV-002');
        break;
      default:
        break;
    }
  };

  const selectedEntity = useMemo(
    () => entities.find((e) => e.id === selectedEntityId) || null,
    [entities, selectedEntityId]
  );

  const selectedRecord = useMemo(
    () => evidenceRecords.find((r) => r.id === selectedRecordId) || null,
    [evidenceRecords, selectedRecordId]
  );

  const selectedEvidence = useMemo(
    () => evidenceRecords.find((r) => r.id === selectedEvidenceId) || null,
    [evidenceRecords, selectedEvidenceId]
  );

  return (
    <InvestigationContext.Provider
      value={{
        currentUser,
        isAuthenticated,
        isInitializingAuth,
        loginUser,
        logoutUser,
        currentView,
        setCurrentView,
        navigateTo,
        caseData,
        cases,
        currentCaseId,
        switchCase,
        entities,
        selectedEntityId,
        setSelectedEntityId,
        selectedEntity,
        evidenceRecords,
        selectedRecordId,
        setSelectedRecordId,
        selectedRecord,
        selectedEvidenceId,
        setSelectedEvidenceId,
        selectedEvidence,
        dataSources,
        addDataSource,
        isIngestingModalOpen,
        setIsIngestingModalOpen,
        entityMatch,
        approveEntityMatch,
        rejectEntityMatch,
        resetEntityMatch,
        graphNodes,
        graphEdges,
        selectedGraphNodeId,
        setSelectedGraphNodeId,
        selectedGraphEdgeId,
        setSelectedGraphEdgeId,
        showHiddenConnection,
        setShowHiddenConnection,
        toggleHiddenConnection,
        timelineEvents,
        aiInsights,
        selectedInsightId,
        setSelectedInsightId,
        verifyInsight,
        toggleInsightReportStatus,
        updateInsightStatus,
        patterns: activePatterns,
        isSearchOpen,
        setIsSearchOpen,
        globalSearchQuery,
        setGlobalSearchQuery,
        demoStep,
        setDemoStep,
        isDemoBannerVisible,
        setIsDemoBannerVisible,
        nextDemoStep,
        prevDemoStep,
        resetDemoStep,
        investigatorNotes,
        setInvestigatorNotes,
        saveAuditLog,
        auditLogs,
        notifications,
        isNotificationsOpen,
        setIsNotificationsOpen,
        markAllNotificationsRead,
        isSidebarOpen,
        setIsSidebarOpen,
        toggleSidebar,
        isSidebarDropdownOpen,
        setIsSidebarDropdownOpen,
        toggleSidebarDropdown,
        theme,
        setTheme,
        toggleTheme,
        activePatterns,
        networkAnalytics,
      }}
    >
      {children}
    </InvestigationContext.Provider>
  );
};

export const useInvestigation = (): InvestigationContextType => {
  const context = useContext(InvestigationContext);
  if (!context) {
    throw new Error('useInvestigation must be used within an InvestigationProvider');
  }
  return context;
};
