import React, { useState } from 'react';
import {
  BrainCircuit,
  GitMerge,
  Sparkles,
  Network,
  ChevronRight,
  ShieldCheck,
  FileCheck2,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  Check,
  Clock,
  ArrowRight,
  Filter,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export const AIInsightsView: React.FC = () => {
  const {
    aiInsights,
    navigateTo,
    setShowHiddenConnection,
    evidenceRecords,
    entities,
    verifyInsight,
    toggleInsightReportStatus,
    updateInsightStatus,
    theme,
  } = useInvestigation();
  const isLight = theme === 'light';

  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [actionNotification, setActionNotification] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setActionNotification(msg);
    setTimeout(() => setActionNotification(null), 3500);
  };

  const handleVerify = (id: string) => {
    verifyInsight(id);
    showToast(`✓ Finding ${id} certified & verified by Investigating Officer.`);
  };

  const handleToggleReport = (id: string, currentStatus: string) => {
    toggleInsightReportStatus(id);
    const willInclude = currentStatus !== 'Included in Report';
    showToast(
      willInclude
        ? `✓ Finding ${id} appended to Section 65B Certified Court Dossier.`
        : `Removed ${id} from Court Report.`
    );
  };

  const filteredInsights = aiInsights.filter((ins) => {
    if (filterPriority !== 'all' && ins.priority !== filterPriority) return false;
    if (filterStatus !== 'all' && ins.status !== filterStatus) return false;
    return true;
  });

  const verifiedCount = aiInsights.filter((i) => i.status === 'Verified by Investigator' || i.status === 'Included in Report').length;
  const inReportCount = aiInsights.filter((i) => i.status === 'Included in Report').length;

  return (
    <div id="ai-insights-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header - Balanced Space Utilization & Proper Alignment */}
      <div className="glass-panel border border-white/10 p-6 md:p-8 rounded-3xl grid grid-cols-1 lg:grid-cols-12 gap-6 items-center shadow-2xl backdrop-blur-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-yellow-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Left Column: Title & Methodology (7 cols) */}
        <div className="lg:col-span-7 space-y-2 relative z-10">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-[0.2em] text-[#FACC15] uppercase flex items-center space-x-1.5">
              <BrainCircuit className="w-3.5 h-3.5 text-[#FACC15]" />
              <span>Multi-Source Inference Model</span>
            </span>
            <span className="text-xs font-mono bg-white/[0.04] text-[#FACC15] px-3 py-1 border border-white/10 rounded-full font-semibold shadow-xs">
              {aiInsights.length} Certified Inferences
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#F8FAFC] tracking-tight font-mono">
            AI Investigative Intelligence Findings
          </h1>
          <p className="text-xs text-[#94A3B8] leading-relaxed max-w-2xl font-sans">
            Automated criminal hypothesis generation citing authenticated evidence records. Inferences require explicit investigator verification prior to judicial report compilation.
          </p>
        </div>

        {/* Right Column: Governance KPI Cluster (5 cols) */}
        <div className="lg:col-span-5 relative z-10 space-y-3">
          <div className="grid grid-cols-3 gap-2.5 text-center text-xs font-mono">
            <div className="glass-card border border-white/10 p-3 rounded-2xl shadow-inner">
              <div className="text-[10px] text-[#64748B] uppercase">Inferences</div>
              <div className="text-base font-bold text-[#FACC15] mt-0.5">{aiInsights.length} Active</div>
            </div>
            <div className="glass-card border border-white/10 p-3 rounded-2xl shadow-inner">
              <div className="text-[10px] text-[#64748B] uppercase">Verified</div>
              <div className="text-base font-bold text-emerald-400 mt-0.5">{verifiedCount}/{aiInsights.length}</div>
            </div>
            <div className="glass-card border border-white/10 p-3 rounded-2xl shadow-inner">
              <div className="text-[10px] text-[#64748B] uppercase">Court Dossier</div>
              <div className="text-base font-bold text-[#F8FAFC] mt-0.5">{inReportCount} Added</div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Notification Toast */}
      {actionNotification && (
        <div className="p-4 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs font-mono flex items-center justify-between shadow-lg backdrop-blur-md rounded-2xl animate-in fade-in duration-200">
          <span className="font-semibold">{actionNotification}</span>
          <button onClick={() => setActionNotification(null)} className="text-emerald-400 font-bold ml-4 hover:text-white cursor-pointer">
            ✕
          </button>
        </div>
      )}

      {/* Filter & Controls Bar - Aligned & Full Width Utilization */}
      <div className="flex flex-wrap items-center justify-between gap-4 glass-panel border border-white/10 p-4 sm:p-5 rounded-2xl text-xs shadow-md">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-[#FACC15]" />
            <span className="text-[#94A3B8] font-mono uppercase tracking-wider font-semibold">Filter:</span>
          </div>

          <div className="flex items-center space-x-2 glass-card px-4 py-2 rounded-2xl border border-white/10 shadow-inner">
            <span className="text-[#64748B] font-mono">Severity:</span>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="bg-transparent font-semibold text-[#F8FAFC] focus:outline-none cursor-pointer font-mono text-xs"
            >
              <option value="all" className="bg-[#0D0D11] text-white">All Severities</option>
              <option value="high" className="bg-[#0D0D11] text-white">High Severity</option>
              <option value="medium" className="bg-[#0D0D11] text-white">Medium Severity</option>
              <option value="low" className="bg-[#0D0D11] text-white">Informational / Low</option>
            </select>
          </div>

          <div className="flex items-center space-x-2 glass-card px-4 py-2 rounded-2xl border border-white/10 shadow-inner">
            <span className="text-[#64748B] font-mono">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-transparent font-semibold text-[#F8FAFC] focus:outline-none cursor-pointer font-mono text-xs"
            >
              <option value="all" className="bg-[#0D0D11] text-white">All Verification Statuses</option>
              <option value="AI-Generated" className="bg-[#0D0D11] text-white">AI-Generated</option>
              <option value="Under Review" className="bg-[#0D0D11] text-white">Under Review</option>
              <option value="Verified by Investigator" className="bg-[#0D0D11] text-white">Verified by Investigator</option>
              <option value="Included in Report" className="bg-[#0D0D11] text-white">Included in Report</option>
            </select>
          </div>
        </div>

        <div className="text-xs text-[#94A3B8] font-mono">
          Displaying {filteredInsights.length} of {aiInsights.length} Analytical Hypotheses
        </div>
      </div>

      {/* Structured Insights List */}
      <div className="space-y-6">
        {filteredInsights.map((ins) => {
          const isHigh = ins.priority === 'high';
          const isMedium = ins.priority === 'medium';
          const isVerified = ins.status === 'Verified by Investigator' || ins.status === 'Included in Report';
          const isInReport = ins.status === 'Included in Report';

          return (
            <div
              key={ins.id}
              id={`insight-card-${ins.id}`}
              className={`glass-panel border p-6 sm:p-8 rounded-3xl shadow-xl transition-all ${
                isLight
                  ? isHigh
                    ? 'border-l-4 border-l-rose-500 border-slate-200'
                    : isMedium
                    ? 'border-l-4 border-l-[#4F46E5] border-slate-200'
                    : 'border-l-4 border-l-indigo-400 border-slate-200'
                  : isHigh
                  ? 'border-l-4 border-l-rose-500 border-white/10'
                  : isMedium
                  ? 'border-l-4 border-l-amber-500 border-white/10'
                  : 'border-l-4 border-l-[#FACC15] border-white/10'
              }`}
            >
              {/* Finding Header */}
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-white/10 pb-4">
                <div className="flex flex-wrap items-center gap-2.5">
                  <span
                    className={`text-[10px] font-mono font-bold px-3 py-1 uppercase tracking-wider rounded-full border ${
                      isLight
                        ? isHigh
                          ? 'bg-rose-50 text-rose-600 border-rose-200'
                          : isMedium
                          ? 'bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]'
                          : 'bg-indigo-50 text-indigo-600 border-indigo-200'
                        : isHigh
                        ? 'bg-rose-950/50 text-rose-400 border-rose-800/60'
                        : isMedium
                        ? 'bg-amber-950/50 text-amber-400 border-amber-800/60'
                        : 'bg-indigo-950/50 text-indigo-400 border-indigo-800/60'
                    }`}
                  >
                    {ins.priorityLabel}
                  </span>

                  <span className={`font-mono text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                    isLight
                      ? 'text-[#4F46E5] bg-indigo-50/70 border-indigo-200'
                      : 'text-[#FACC15] bg-[#050507] border-[#FACC15]/40'
                  }`}>
                    {ins.id}
                  </span>

                  <span className="text-xs font-mono text-[#94A3B8]">
                    Category: <strong className={isLight ? 'text-slate-900' : 'text-[#F8FAFC]'}>{ins.category}</strong>
                  </span>
                </div>

                {/* Status Badge & Confidence Score */}
                <div className="flex items-center space-x-3 text-xs font-mono">
                  {ins.confidenceScore && (
                    <span className="text-[#94A3B8]">
                      Confidence: <strong className={`${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'} font-bold`}>{ins.confidenceScore}%</strong>
                    </span>
                  )}

                  {/* Verification Status Pill */}
                  <div className="flex items-center space-x-1.5">
                    <span className="text-[#64748B]">Status:</span>
                    <select
                      value={ins.status}
                      onChange={(e) => updateInsightStatus(ins.id, e.target.value as any)}
                      className={`text-xs font-semibold px-3 py-1 border rounded-full cursor-pointer font-mono ${
                        isLight
                          ? isInReport
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                            : isVerified
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                            : ins.status === 'Under Review'
                            ? 'bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]'
                            : 'bg-white text-slate-700 border-slate-300'
                          : isInReport
                          ? 'bg-emerald-950/60 text-emerald-400 border-emerald-700'
                          : isVerified
                          ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60'
                          : ins.status === 'Under Review'
                          ? 'bg-amber-950/40 text-amber-400 border-amber-800/60'
                          : 'bg-[#050507] text-[#94A3B8] border-white/10'
                      }`}
                    >
                      <option value="AI-Generated" className={isLight ? 'bg-white text-slate-800' : 'bg-[#0D0D11] text-white'}>AI-Generated</option>
                      <option value="Under Review" className={isLight ? 'bg-white text-slate-800' : 'bg-[#0D0D11] text-white'}>Under Review</option>
                      <option value="Verified by Investigator" className={isLight ? 'bg-white text-slate-800' : 'bg-[#0D0D11] text-white'}>Verified by Investigator</option>
                      <option value="Included in Report" className={isLight ? 'bg-white text-slate-800' : 'bg-[#0D0D11] text-white'}>Included in Report</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Finding Title */}
              <div className="mt-4 mb-5">
                <h2 className="text-lg font-bold text-[#F8FAFC] tracking-tight font-mono">
                  {ins.title}
                </h2>
              </div>

              {/* 2-Column Core Investigative Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs mb-5">
                {/* What Was Detected */}
                <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-2">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15] flex items-center justify-between">
                    <span>1. What Was Detected</span>
                    <span className="text-[#64748B] font-normal">Pattern Analysis</span>
                  </div>
                  <p className="text-[#F8FAFC] leading-relaxed font-sans text-xs">
                    {ins.whatFound}
                  </p>
                </div>

                {/* Why It Matters */}
                <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-2">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15] flex items-center justify-between">
                    <span>2. Why It Matters</span>
                    <span className="text-[#64748B] font-normal">Investigative Significance</span>
                  </div>
                  <p className="text-[#94A3B8] leading-relaxed font-sans text-xs">
                    {ins.whyItMatters || ins.whyFlagged}
                  </p>
                </div>
              </div>

              {/* Key Entities & Supporting Evidence Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs mb-5">
                {/* Key Entities Involved */}
                <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-3">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                    Key Entities Involved ({ins.relatedEntityIds.length})
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {ins.relatedEntityIds.map((entId) => {
                      const ent = entities.find((e) => e.id === entId);
                      const name = ent ? ent.name : entId;
                      const type = ent ? ent.type : 'entity';
                      return (
                        <button
                          key={entId}
                          onClick={() => navigateTo('entities', { entityId: entId })}
                          className="flex items-center space-x-1.5 px-3 py-1.5 glass-panel hover:bg-white/10 border border-white/10 hover:border-[#FACC15] text-xs font-mono font-semibold text-[#F8FAFC] rounded-full transition-all cursor-pointer"
                        >
                          <span>{name}</span>
                          <span className="text-[9px] font-mono uppercase text-[#FACC15] bg-[#050507] px-1.5 py-0.2 rounded-full border border-white/10">
                            {type}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Supporting Evidence Records */}
                <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-3">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                    Supporting Evidence Records ({ins.supportingEvidenceIds.length})
                  </div>
                  <div className="space-y-1.5">
                    {ins.supportingEvidenceIds.map((evId) => {
                      const ev = evidenceRecords.find((r) => r.id === evId);
                      return (
                        <div
                          key={evId}
                          onClick={() => navigateTo('evidence', { evidenceId: evId })}
                          className="flex items-center justify-between p-2.5 glass-panel border border-white/10 hover:border-[#FACC15] rounded-xl cursor-pointer transition-colors group"
                        >
                          <div className="flex items-center space-x-2 min-w-0">
                            <FileSpreadsheet className="w-3.5 h-3.5 text-[#FACC15] shrink-0" />
                            <span className="font-mono font-bold text-[#FACC15] text-xs shrink-0">{evId}</span>
                            <span className="text-xs text-[#F8FAFC] font-sans truncate group-hover:text-[#FACC15]">
                              {ev?.title || 'Ingested Record'}
                            </span>
                          </div>
                          <ChevronRight className="w-3.5 h-3.5 text-[#64748B] group-hover:text-[#FACC15] shrink-0 ml-2" />
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Recommended Next Steps */}
              {ins.recommendedSteps && ins.recommendedSteps.length > 0 && (
                <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-3 text-xs mb-5">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15] flex items-center justify-between">
                    <span>Recommended Next Steps &amp; Tactical Directives</span>
                    <span className="text-[#FACC15] font-semibold font-mono">{ins.recommendedSteps.length} Action Items</span>
                  </div>
                  <ul className="space-y-2">
                    {ins.recommendedSteps.map((step, idx) => (
                      <li key={idx} className="flex items-start space-x-2.5 text-[#F8FAFC] font-sans text-xs leading-relaxed">
                        <span className="font-mono text-[#FACC15] font-bold mt-0.5">[{idx + 1}]</span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Card Action Controls */}
              <div className="pt-4 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  {/* Action 1: Verify Finding */}
                  <button
                    onClick={() => handleVerify(ins.id)}
                    className={`px-4 py-2 text-xs font-mono uppercase tracking-wider font-semibold border rounded-full flex items-center space-x-1.5 transition-all cursor-pointer ${
                      isVerified
                        ? 'bg-emerald-950/60 text-emerald-400 border-emerald-700'
                        : 'glass-card hover:bg-white/10 text-[#F8FAFC] border-white/10'
                    }`}
                  >
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{isVerified ? '✓ Officer Certified' : 'Certify Finding'}</span>
                  </button>

                  {/* Action 2: Add to Final Report */}
                  <button
                    onClick={() => handleToggleReport(ins.id, ins.status)}
                    className={`px-4 py-2 text-xs font-mono uppercase tracking-wider font-semibold border rounded-full flex items-center space-x-1.5 transition-all cursor-pointer ${
                      isInReport
                        ? 'bg-[#FACC15] text-[#050507] border-[#FACC15] font-bold shadow-[0_0_15px_rgba(250, 204, 21,0.4)]'
                        : 'glass-card hover:bg-white/10 text-[#F8FAFC] border-white/10'
                    }`}
                  >
                    <FileCheck2 className={`w-3.5 h-3.5 ${isInReport ? 'text-[#050507]' : 'text-[#FACC15]'}`} />
                    <span>{isInReport ? '✓ In Court Report' : 'Add to Court Dossier'}</span>
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {/* Action 3: View in Graph */}
                  <button
                    onClick={() => {
                      if (ins.id === 'INS-001') setShowHiddenConnection(true);
                      navigateTo('graph', { highlightPath: ins.id === 'INS-001' });
                    }}
                    className="px-4 py-2 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center space-x-1.5 transition-all rounded-full shadow-lg cursor-pointer"
                  >
                    <Network className="w-3.5 h-3.5" />
                    <span>Locate on Graph</span>
                  </button>

                  {/* Action 4: Inspect Evidence */}
                  <button
                    onClick={() => navigateTo('evidence', { evidenceId: ins.supportingEvidenceIds[0] })}
                    className="px-4 py-2 glass-card hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC] text-xs font-mono uppercase tracking-wider font-semibold border border-white/10 rounded-full transition-all flex items-center space-x-1.5 cursor-pointer"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5 text-[#FACC15]" />
                    <span>Inspect Evidence</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
