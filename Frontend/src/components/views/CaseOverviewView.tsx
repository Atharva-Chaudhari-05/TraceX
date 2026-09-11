import React, { useState } from 'react';
import {
  Users,
  CreditCard,
  MapPin,
  FileSpreadsheet,
  BrainCircuit,
  AlertTriangle,
  GitMerge,
  ArrowRight,
  Clock,
  Shield,
  Activity,
  CheckCircle2,
  Sparkles,
  Network,
  ChevronRight,
  Building,
  Car,
  Phone,
  Server,
  Database,
  Cpu,
  Search,
  ExternalLink,
  Lock,
  Layers,
  FileText,
  UserCheck,
  Zap,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

// ==========================================
// 1. INVESTIGATOR DASHBOARD ("What needs my attention?")
// ==========================================
const InvestigatorDashboard: React.FC = () => {
  const { cases, currentCaseId, navigateTo, setSelectedEntityId, theme } = useInvestigation();
  const isLight = theme === 'light';

  const activeCasesList = cases.slice(0, 5).map((c: any) => ({
    id: c.id,
    title: c.payload?.title || c.payload?.name || `Case ${c.id}`,
    priority: c.payload?.priority || 'HIGH',
    status: c.payload?.status || 'Active',
    lastActivity: 'Updated recently',
    entitiesSummary: c.payload?.description || 'No detailed summary available',
    assignedTeam: c.payload?.jurisdiction || c.payload?.agency || 'General Jurisdiction',
    lastUpdated: c.payload?.last_updated || 'Unknown Date',
    isCurrent: c.id === currentCaseId,
  }));

  // Ensure current case is always at the top if it exists
  const currentCaseIdx = activeCasesList.findIndex(c => c.isCurrent);
  if (currentCaseIdx > 0) {
    const current = activeCasesList.splice(currentCaseIdx, 1)[0];
    activeCasesList.unshift(current);
  } else if (currentCaseIdx === -1 && cases.length > 0) {
    const c = cases.find(c => c.id === currentCaseId) || cases[0];
    activeCasesList.unshift({
      id: c.id,
      title: c.payload?.title || c.payload?.name || `Case ${c.id}`,
      priority: c.payload?.priority || 'HIGH',
      status: c.payload?.status || 'Active',
      lastActivity: 'Updated recently',
      entitiesSummary: c.payload?.description || 'No detailed summary available',
      assignedTeam: c.payload?.jurisdiction || c.payload?.agency || 'General Jurisdiction',
      lastUpdated: c.payload?.last_updated || 'Unknown Date',
      isCurrent: c.id === currentCaseId,
    });
  }

  return (
    <div className="space-y-6">
      {/* Role Banner / Context */}
      <div className="glass-panel border border-white/10 p-6 rounded-3xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-[10px] uppercase font-mono tracking-[0.25em] text-[#FACC15] font-semibold">
            <span>Investigative Command Console</span>
            <span>•</span>
            <span className="text-[#10B981]">Case-Centric Operations</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#F8FAFC] tracking-tight mt-1">
            Investigator Workspace
          </h1>
          <p className="text-xs text-[#94A3B8] mt-1 max-w-2xl">
            Focus on what needs your operational decision: prioritize high-confidence entity matches, review urgent intelligence alerts, and coordinate case evidence.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigateTo('resolution')}
          className="px-5 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase tracking-wider rounded-full shadow-lg flex items-center space-x-2 transition-all shrink-0 cursor-pointer"
        >
          <GitMerge className="w-4 h-4" />
          <span>Review Resolution Queue</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card border border-white/10 p-5 rounded-2xl shadow-lg">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">Active Cases</div>
          <div className="text-3xl font-bold font-mono text-[#F8FAFC] mt-2">{activeCasesList.length}</div>
          <div className="text-[10px] font-mono text-[#FACC15] mt-1 flex items-center space-x-1">
            <span>Assigned to you</span>
          </div>
        </div>

        <div className="glass-card border border-white/10 p-5 rounded-2xl shadow-lg">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">High Priority</div>
          <div className="text-3xl font-bold font-mono text-[#EF4444] mt-2">0</div>
          <div className="text-[10px] font-mono text-[#EF4444] mt-1">Direct supervisor assignment</div>
        </div>

        <div
          onClick={() => navigateTo('resolution')}
          className="glass-card border border-white/10 hover:border-[#FACC15]/50 p-5 rounded-2xl shadow-lg cursor-pointer transition-all group"
        >
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] flex items-center justify-between">
            <span>Pending Resolutions</span>
            <GitMerge className="w-3.5 h-3.5 text-[#FACC15] group-hover:translate-x-0.5 transition-transform" />
          </div>
          <div className="text-3xl font-bold font-mono text-[#FACC15] mt-2">0</div>
          <div className="text-[10px] font-mono text-[#94A3B8] mt-1">Awaiting review</div>
        </div>

        <div
          onClick={() => navigateTo('insights')}
          className="glass-card border border-white/10 hover:border-[#FACC15]/50 p-5 rounded-2xl shadow-lg cursor-pointer transition-all group"
        >
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] flex items-center justify-between">
            <span>New Intelligence</span>
            <Sparkles className="w-3.5 h-3.5 text-[#FACC15] animate-pulse" />
          </div>
          <div className="text-3xl font-bold font-mono text-emerald-400 mt-2">0</div>
          <div className="text-[10px] font-mono text-emerald-400/80 mt-1">Incoming AI cross-case alerts</div>
        </div>
      </div>

      {/* Main Grid: Left (Active Cases + Alerts) & Right (AI Highlights, ER Queue, Network Snapshot) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* 1. My Active Cases */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Shield className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  My Active Cases
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#64748B]">Showing 3 Assigned</span>
            </div>

            <div className="space-y-3">
              {activeCasesList.map((c) => (
                <div
                  key={c.id}
                  className={`p-4 glass-card border rounded-2xl transition-all ${
                    c.isCurrent
                      ? 'border-[#FACC15]/50 bg-[#FACC15]/5'
                      : 'border-white/10 hover:border-white/20'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center space-x-2.5">
                      <span className="font-mono font-bold text-xs text-[#FACC15] bg-[#050507] px-2.5 py-1 border border-white/10 rounded-lg">
                        {c.id}
                      </span>
                      <span className="text-xs font-bold text-[#F8FAFC]">{c.title}</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded-full ${
                          c.priority === 'HIGH'
                            ? 'bg-[#EF4444]/15 text-[#EF4444] border border-[#EF4444]/30'
                            : 'bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/30'
                        }`}
                      >
                        {c.priority}
                      </span>
                      <span className="text-[9px] font-mono px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full">
                        {c.status}
                      </span>
                    </div>
                  </div>

                  <div className="text-xs text-[#94A3B8] mt-2 font-mono flex flex-wrap items-center gap-x-4 gap-y-1">
                    <span>{c.entitiesSummary}</span>
                    <span>•</span>
                    <span className="text-[#64748B]">Last updated: {c.lastActivity}</span>
                  </div>

                  <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between">
                    <span className="text-[10px] text-[#64748B] font-mono">{c.assignedTeam}</span>
                    <button
                      type="button"
                      onClick={() => navigateTo('graph')}
                      className="px-3.5 py-1.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-[11px] uppercase rounded-full shadow-xs flex items-center space-x-1.5 cursor-pointer transition-all"
                    >
                      <span>Open Investigation</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Investigation Alerts / Items Requiring Attention */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  Investigation Alerts
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#F59E0B] animate-pulse">Scanning for alerts...</span>
            </div>

            <div className="space-y-2.5">
              <div className="p-4 text-center text-[#64748B] text-xs font-mono">
                No immediate alerts for the selected case.
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* 3. AI / Intelligence Highlights */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  AI / Intelligence Highlights
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#FACC15]">Curated Digest</span>
            </div>

            <div className="space-y-3">
              <div className="p-4 text-center text-[#64748B] text-xs font-mono">
                No active highlights for the selected case.
              </div>
            </div>
          </div>

          {/* 4. Resolution Queue */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <GitMerge className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  Resolution Queue
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#FACC15]">0 Awaiting</span>
            </div>

            <div className="p-4 bg-[#050507]/80 border border-white/10 rounded-2xl space-y-3">
              <div className="text-xs font-bold text-[#F8FAFC]">
                Pending Entity Resolution
              </div>
              <p className="text-[11px] text-[#94A3B8]">
                No matches awaiting investigator review based on probabilistic phonetic matching.
              </p>

              <div className="space-y-1.5 font-mono text-xs pt-1">
                <div className="flex items-center justify-between p-2 bg-white/5 rounded-xl">
                  <span className="text-[#FACC15]">High confidence</span>
                  <span className="font-bold text-[#F8FAFC]">0</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white/5 rounded-xl">
                  <span className="text-[#F59E0B]">Medium confidence</span>
                  <span className="font-bold text-[#F8FAFC]">0</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => navigateTo('resolution')}
                className="w-full py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase rounded-full shadow-md transition-all cursor-pointer"
              >
                Review Queue
              </button>
            </div>
          </div>

          {/* 5. Case Network Snapshot */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Network className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  Case Network Snapshot
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#64748B]">Preview</span>
            </div>

            <div className="p-4 bg-[#050507]/80 border border-white/10 rounded-2xl space-y-3">
              <div className="p-4 font-mono text-[11px] text-[#FACC15] bg-black/40 rounded-xl border border-white/5 text-center leading-relaxed">
                <div className="text-[#94A3B8]">Graph preview not available for this case.</div>
                <div className="text-[#64748B] mt-1">Open full network to explore entities.</div>
              </div>

              <button
                type="button"
                onClick={() => navigateTo('graph')}
                className={`w-full py-2.5 font-mono font-bold text-xs uppercase rounded-full shadow-xs flex items-center justify-center space-x-2 transition-all cursor-pointer ${isLight ? 'bg-[#4F46E5] text-white hover:bg-[#4338CA] shadow-[0_4px_14px_rgba(79,70,229,0.3)] border border-[#4F46E5]' : 'bg-transparent border border-white/20 text-[#F8FAFC] hover:bg-[#FACC15] hover:text-[#050507] hover:border-[#FACC15]'}`}
              >
                <span>Open Full Network</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 2. ANALYST DASHBOARD ("What does the data tell me?")
// ==========================================
const AnalystDashboard: React.FC = () => {
  const { navigateTo, theme } = useInvestigation();
  const isLight = theme === 'light';
  const [analystSearch, setAnalystSearch] = useState('');

  return (
    <div className="space-y-6">
      {/* Role Banner / Context */}
      <div className="glass-panel border border-white/10 p-6 rounded-3xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-[10px] uppercase font-mono tracking-[0.25em] text-[#FACC15] font-semibold">
            <span>Intelligence Analytics Console</span>
            <span>•</span>
            <span className="text-[#A855F7]">Pattern Discovery &amp; Graph Mining</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#F8FAFC] tracking-tight mt-1">
            Analyst Intelligence Hub
          </h1>
          <p className="text-xs text-[#94A3B8] mt-1 max-w-2xl">
            Uncover hidden patterns, multi-hop syndicates, behavioral anomalies, and cross-source intelligence across the master dataset.
          </p>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            type="button"
            onClick={() => navigateTo('graph')}
            className="px-4 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase tracking-wider rounded-full shadow-lg flex items-center space-x-1.5 transition-all cursor-pointer"
          >
            <Network className="w-4 h-4" />
            <span>Interactive Graph</span>
          </button>
          <button
            type="button"
            onClick={() => navigateTo('patterns')}
            className="px-4 py-2.5 glass-card hover:bg-white/10 border border-white/10 text-[#F8FAFC] font-mono font-bold text-xs uppercase tracking-wider rounded-full shadow-sm flex items-center space-x-1.5 transition-all cursor-pointer"
          >
            <BrainCircuit className="w-4 h-4 text-[#A855F7]" />
            <span>Patterns</span>
          </button>
        </div>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card border border-white/10 p-5 rounded-2xl shadow-lg">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">Cases Analyzed</div>
          <div className="text-3xl font-bold font-mono text-[#F8FAFC] mt-2">0</div>
          <div className="text-[10px] font-mono text-[#FACC15] mt-1">Cross-jurisdictional scope</div>
        </div>

        <div className="glass-card border border-white/10 p-5 rounded-2xl shadow-lg">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">Key Individuals</div>
          <div className="text-3xl font-bold font-mono text-[#FACC15] mt-2">0</div>
          <div className="text-[10px] font-mono text-[#FACC15] mt-1">High eigenvector centrality</div>
        </div>

        <div
          onClick={() => navigateTo('patterns')}
          className="glass-card border border-white/10 hover:border-[#FACC15]/50 p-5 rounded-2xl shadow-lg cursor-pointer transition-all"
        >
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">Clusters</div>
          <div className="text-3xl font-bold font-mono text-[#A855F7] mt-2">0</div>
          <div className="text-[10px] font-mono text-[#A855F7] mt-1">Louvain community partitions</div>
        </div>

        <div
          onClick={() => navigateTo('patterns')}
          className="glass-card border border-white/10 hover:border-[#FACC15]/50 p-5 rounded-2xl shadow-lg cursor-pointer transition-all"
        >
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">Anomalies</div>
          <div className="text-3xl font-bold font-mono text-[#EF4444] mt-2">0</div>
          <div className="text-[10px] font-mono text-[#EF4444] mt-1">Isolation Forest triggers</div>
        </div>
      </div>

      {/* 5. Prominent Analytical Search & Exploration Area */}
      <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
        <div className="flex items-center space-x-2">
          <Search className="w-4 h-4 text-[#FACC15]" />
          <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
            Analytical Search &amp; Exploratory Intelligence
          </h2>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-[#FACC15] absolute left-4 top-3.5" />
            <input
              type="text"
              value={analystSearch}
              onChange={(e) => setAnalystSearch(e.target.value)}
              placeholder="Search / Explore [ Person, Phone, Account, Location, Syndicate Hash... ]"
              className="w-full pl-11 pr-4 py-3 glass-search-bar rounded-full text-xs font-mono text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none"
            />
          </div>

          <div className="flex items-center space-x-2 shrink-0">
            <button
              type="button"
              onClick={() => navigateTo('entities')}
              className="px-4 py-2.5 glass-card hover:bg-white/10 border border-white/20 text-xs font-mono font-bold text-[#F8FAFC] rounded-full transition-all cursor-pointer"
            >
              Compare Entities
            </button>
            <button
              type="button"
              onClick={() => navigateTo('path')}
              className="px-4 py-2.5 glass-card hover:bg-white/10 border border-white/20 text-xs font-mono font-bold text-[#F8FAFC] rounded-full transition-all cursor-pointer"
            >
              Find Path
            </button>
            <button
              type="button"
              onClick={() => navigateTo('graph')}
              className="px-4 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono font-bold rounded-full transition-all shadow-md cursor-pointer"
            >
              Explore Network
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Network Intelligence */}
        <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center space-x-2">
              <Network className="w-4 h-4 text-[#FACC15]" />
              <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                Network Intelligence
              </h2>
            </div>
            <span className="text-[10px] font-mono text-[#64748B]">Top Degree Centrality</span>
          </div>

          <div className="space-y-3">
            <div className="text-xs font-bold text-[#94A3B8] uppercase font-mono">Most Connected Entities</div>

            <div className="space-y-2">
              <div className="p-4 text-center text-[#64748B] text-xs font-mono">
                Network intelligence data not available for this case.
              </div>
            </div>

            <button
              type="button"
              onClick={() => navigateTo('graph')}
              className="w-full py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase rounded-full shadow-md transition-all cursor-pointer"
            >
              Explore Network
            </button>
          </div>
        </div>

        {/* 2. Detected Clusters */}
        <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-[#A855F7]" />
              <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                Detected Clusters
              </h2>
            </div>
            <span className="text-[10px] font-mono text-[#A855F7]">Community Detection</span>
          </div>

          <div className="space-y-3">
            <div className="p-4 text-center text-[#64748B] text-xs font-mono">
              No clusters detected for this case.
            </div>

            <button
              onClick={() => navigateTo('patterns')}
              className={`w-full py-3 font-mono font-bold text-xs uppercase rounded-full shadow-lg transition-all cursor-pointer ${isLight ? 'bg-[#4F46E5] text-white hover:bg-[#4338CA] shadow-[0_4px_14px_rgba(79,70,229,0.3)] border border-[#4F46E5]' : 'bg-transparent border border-white/20 text-[#F8FAFC] hover:bg-[#FACC15] hover:text-[#050507] hover:border-[#FACC15]'}`}
            >
              Explore Clusters
            </button>
          </div>
        </div>

        {/* 3. Anomaly Detection (Isolation Forest) */}
        <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-[#EF4444]" />
              <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                Anomaly Detection (M8 Isolation Forest)
              </h2>
            </div>
            <span className="text-[10px] font-mono text-[#EF4444]">0 Anomalies</span>
          </div>

          <div className="p-4 bg-[#050507]/80 border border-white/10 rounded-2xl space-y-3">
            <div className="p-4 text-center text-[#64748B] text-xs font-mono">
              No anomalies detected for this case.
            </div>

            <button
              type="button"
              onClick={() => navigateTo('patterns')}
              className="w-full py-2.5 bg-[#EF4444]/15 hover:bg-[#EF4444]/25 text-[#EF4444] border border-[#EF4444]/40 font-mono font-bold text-xs uppercase rounded-full transition-all cursor-pointer"
            >
              Investigate Anomalies
            </button>
          </div>
        </div>

        {/* 4. AI Intelligence */}
        <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center space-x-2">
              <BrainCircuit className="w-4 h-4 text-[#FACC15]" />
              <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                AI Intelligence &amp; Findings
              </h2>
            </div>
            <span className="text-[10px] font-mono text-[#FACC15]">Automated Synthesis</span>
          </div>

          <div className="p-4 bg-[#050507]/80 border border-white/10 rounded-2xl space-y-3 font-mono text-xs">
            <div className="p-4 text-center text-[#64748B] text-xs font-mono">
              No AI intelligence findings available for this case.
            </div>

            <button
              type="button"
              onClick={() => navigateTo('insights')}
              className="w-full py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase rounded-full shadow-md transition-all cursor-pointer"
            >
              Explore Findings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 3. ADMIN DASHBOARD ("Is the system working?")
// ==========================================
const AdminDashboard: React.FC = () => {
  const { caseData, theme, navigateTo } = useInvestigation();
  const isLight = theme === 'light';

  return (
    <div className="space-y-6">
      {/* Role Banner / Context */}
      <div className="glass-panel border border-white/10 p-6 rounded-3xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-[10px] uppercase font-mono tracking-[0.25em] text-[#FACC15] font-semibold">
            <span>Infrastructure &amp; Governance Console</span>
            <span>•</span>
            <span className="text-[#FACC15]">Platform Operations</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#F8FAFC] tracking-tight mt-1">
            System Administration
          </h1>
          <p className="text-xs text-[#94A3B8] mt-1 max-w-2xl">
            Monitor infrastructure health, ETL data ingestion pipelines, ISO/IEC 27037 compliance audit seals, and law enforcement user role allocations.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigateTo('audit')}
          className="px-5 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase tracking-wider rounded-full shadow-[0_0_20px_rgba(250,204,21,0.3)] hover:shadow-[0_0_25px_rgba(250,204,21,0.5)] flex items-center space-x-2 transition-all shrink-0 cursor-pointer"
        >
          <Shield className="w-4 h-4 text-[#050507]" />
          <span>Audit Logs &amp; Integrity</span>
        </button>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card border border-white/10 p-5 rounded-2xl shadow-lg">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">System Users</div>
          <div className="text-3xl font-bold font-mono text-[#F8FAFC] mt-2">3</div>
          <div className="text-[10px] font-mono text-[#FACC15] mt-1">1 Inv • 1 Ana • 1 Adm</div>
        </div>

        <div className="glass-card border border-white/10 p-5 rounded-2xl shadow-lg">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">Active Cases</div>
          <div className="text-3xl font-bold font-mono text-[#F8FAFC] mt-2">{cases?.length || 0}</div>
          <div className="text-[10px] font-mono text-[#FACC15] mt-1">Demo Case Data</div>
        </div>

        <div
          onClick={() => navigateTo('datasources')}
          className="glass-card border border-white/10 hover:border-[#FACC15]/50 p-5 rounded-2xl shadow-lg cursor-pointer transition-all"
        >
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">Data Jobs</div>
          <div className="text-3xl font-bold font-mono text-[#FACC15] mt-2">0</div>
          <div className="text-[10px] font-mono text-[#FACC15] mt-1">Active batch extractions</div>
        </div>

        <div className="glass-card border border-emerald-500/30 bg-emerald-950/10 p-5 rounded-2xl shadow-lg">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B]">System Status</div>
          <div className="text-2xl font-bold font-mono text-[#10B981] mt-2 flex items-center space-x-1.5">
            <span>HEALTHY</span>
            <CheckCircle2 className="w-5 h-5 text-[#10B981]" />
          </div>
          <div className="text-[10px] font-mono text-[#10B981]/80 mt-1">All 4 core clusters operational</div>
        </div>
      </div>

      {/* Main Grid: Left (System Health + Data Processing) & Right (User Access, System Alerts, Audit) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (6 cols) */}
        <div className="lg:col-span-6 space-y-6">
          {/* 1. System Health */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Server className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  System Health &amp; Microservices
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#10B981] bg-[#10B981]/10 border border-[#10B981]/30 px-2.5 py-0.5 rounded-full font-bold">
                100% Uptime
              </span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3.5 bg-[#050507]/80 border border-white/10 rounded-2xl flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Database className="w-4 h-4 text-[#FACC15]" />
                  <div>
                    <div className="font-bold text-[#F8FAFC]">PostgreSQL Database</div>
                    <div className="text-[10px] text-[#64748B]">Port 5432 • Latency: 2ms • Connections: 18/100</div>
                  </div>
                </div>
                <div className="flex items-center space-x-1.5 text-[#10B981] font-bold bg-[#10B981]/10 border border-[#10B981]/30 px-2.5 py-1 rounded-full text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                  <span>Healthy</span>
                </div>
              </div>

              <div className="p-3.5 bg-[#050507]/80 border border-white/10 rounded-2xl flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Network className="w-4 h-4 text-[#FACC15]" />
                  <div>
                    <div className="font-bold text-[#F8FAFC]">Neo4j Knowledge Graph</div>
                    <div className="text-[10px] text-[#64748B]">Bolt 7687 • 1.42M Nodes • Latency: 4ms</div>
                  </div>
                </div>
                <div className="flex items-center space-x-1.5 text-[#10B981] font-bold bg-[#10B981]/10 border border-[#10B981]/30 px-2.5 py-1 rounded-full text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                  <span>Healthy</span>
                </div>
              </div>

              <div className="p-3.5 bg-[#050507]/80 border border-white/10 rounded-2xl flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Cpu className="w-4 h-4 text-[#FACC15]" />
                  <div>
                    <div className="font-bold text-[#F8FAFC]">Backend API (FastAPI)</div>
                    <div className="text-[10px] text-[#64748B]">Port 8000 • 8 Workers • P99: 18ms</div>
                  </div>
                </div>
                <div className="flex items-center space-x-1.5 text-[#10B981] font-bold bg-[#10B981]/10 border border-[#10B981]/30 px-2.5 py-1 rounded-full text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                  <span>Healthy</span>
                </div>
              </div>

              <div className="p-3.5 bg-[#050507]/80 border border-white/10 rounded-2xl flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Activity className="w-4 h-4 text-[#FACC15]" />
                  <div>
                    <div className="font-bold text-[#F8FAFC]">Frontend SPA (Vite/React)</div>
                    <div className="text-[10px] text-[#64748B]">Glassmorphism Engine • Memory: 18MB</div>
                  </div>
                </div>
                <div className="flex items-center space-x-1.5 text-[#10B981] font-bold bg-[#10B981]/10 border border-[#10B981]/30 px-2.5 py-1 rounded-full text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                  <span>Healthy</span>
                </div>
              </div>
            </div>
          </div>

          {/* 2. Data Processing */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  Data Processing Pipelines
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#FACC15]">7 Input Factors</span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-4 text-center text-[#64748B] text-xs font-mono">
                No active data processing pipelines.
              </div>

              <button
                type="button"
                onClick={() => navigateTo('datasources')}
                className="w-full py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase rounded-full shadow-md transition-all cursor-pointer"
              >
                Manage Processing
              </button>
            </div>
          </div>
        </div>

        {/* Right Column (6 cols) */}
        <div className="lg:col-span-6 space-y-6">
          {/* 3. User & Access Overview */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  User &amp; Access Overview
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#FACC15]">3 RBAC Tiers</span>
            </div>

            <div className="p-4 bg-[#050507]/80 border border-white/10 rounded-2xl space-y-3 font-mono text-xs">
              <div className="text-xs font-bold text-[#F8FAFC] font-sans">Active User Tiers:</div>

              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 bg-white/5 rounded-xl flex items-center justify-between">
                  <span className="text-[#94A3B8]">Administrators</span>
                  <span className="font-bold text-[#FACC15]">1</span>
                </div>
                <div className="p-2.5 bg-white/5 rounded-xl flex items-center justify-between">
                  <span className="text-[#94A3B8]">Investigators</span>
                  <span className="font-bold text-[#FACC15]">1</span>
                </div>
                <div className="p-2.5 bg-white/5 rounded-xl flex items-center justify-between">
                  <span className="text-[#94A3B8]">Analysts</span>
                  <span className="font-bold text-[#FACC15]">1</span>
                </div>
                <div className="p-2.5 bg-white/5 rounded-xl flex items-center justify-between">
                  <span className="text-[#64748B]">Inactive users</span>
                  <span className="font-bold text-[#64748B]">0</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => alert('User Management: 3 Officers registered.')}
                className={`w-full py-2.5 font-mono font-bold text-xs uppercase rounded-full shadow-lg transition-all cursor-pointer ${isLight ? 'bg-[#4F46E5] text-white hover:bg-[#4338CA] shadow-[0_4px_14px_rgba(79,70,229,0.3)] border border-[#4F46E5]' : 'bg-[#FACC15]/10 border border-white/20 hover:border-[#FACC15]/50 text-[#F8FAFC] hover:text-[#FACC15]'}`}
              >
                Manage Users
              </button>
            </div>
          </div>

          {/* 4. System Alerts */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  System Alerts
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#FACC15]">Healthy</span>
            </div>

            <div className="space-y-2.5 font-mono text-xs">
              <div className="p-4 text-center text-[#64748B] text-xs font-mono">
                No active system alerts.
              </div>
            </div>
          </div>

          {/* 5. Recent Administrative Activity */}
          <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-[#FACC15]" />
                <h2 className="font-bold text-sm text-[#F8FAFC] font-mono uppercase tracking-wider">
                  Recent Administrative Activity
                </h2>
              </div>
              <span className="text-[10px] font-mono text-[#FACC15]">Audit Feed</span>
            </div>

            <div className="space-y-2 font-mono text-xs">
              <div className="p-4 text-center text-[#64748B] text-xs font-mono">
                Activity logs will appear here.
              </div>
            </div>

            <button
              type="button"
              onClick={() => navigateTo('audit')}
              className="w-full py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase rounded-full shadow-md transition-all cursor-pointer"
            >
              View Audit Logs
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// MAIN CASE OVERVIEW VIEW (Switches dashboard based on currentUser.role)
// ==========================================
export const CaseOverviewView: React.FC = () => {
  const { currentUser } = useInvestigation();

  const role = currentUser?.role || 'Investigator';

  return (
    <div id="case-overview-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {role === 'System Administrator' ? (
        <AdminDashboard />
      ) : role === 'Intelligence Analyst' ? (
        <AnalystDashboard />
      ) : (
        <InvestigatorDashboard />
      )}
    </div>
  );
};
