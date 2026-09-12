import React from 'react';
import {
  Network,
  ArrowRight,
  GitBranch,
  Layers,
  Clock,
  AlertTriangle,
  Zap,
  TrendingUp,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export const PatternAnalysisView: React.FC = () => {
  const { navigateTo, setShowHiddenConnection, theme, networkAnalytics, activePatterns } = useInvestigation();
  const isLight = theme === 'light';
  const [selectedBrokerId, setSelectedBrokerId] = React.useState<string | null>(null);
  const [hoveredBrokerId, setHoveredBrokerId] = React.useState<string | null>(null);

  const keyEntities = networkAnalytics?.key_entities || activePatterns.map((p, i) => ({
    entity_id: p.name,
    metric: 'betweenness',
    score: p.confidence / 100,
    explanation: { why: p.description, what: '', supporting_evidence: [] }
  }));

  const communities = networkAnalytics?.communities || [];

  return (
    <div id="pattern-analysis-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header Banner */}
      <div className="glass-panel border border-white/10 p-6 sm:p-8 rounded-3xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="text-[10px] font-mono font-bold tracking-[0.2em] text-[#FACC15] uppercase">
              Topology &amp; Behavioral Intelligence
            </span>
            <span className="text-xs font-mono bg-[#050507]/80 text-[#FACC15] px-3 py-1 border border-[#FACC15]/40 rounded-full font-semibold shadow-xs">
              Betweenness Centrality &amp; Communities
            </span>
          </div>
          <h1 className="text-2xl font-bold text-[#F8FAFC] mt-1.5 font-mono">
            Graph Centrality, Clustering &amp; Anomaly Patterns
          </h1>
          <p className="text-sm text-[#94A3B8] mt-1 font-sans">
            Quantitative network centrality scoring, 3 functional criminal cells, smurfing threshold evasion, and multi-hop hawala conduit tracing.
          </p>
        </div>

        <button
          onClick={() => {
            setShowHiddenConnection(true);
            navigateTo('graph', { highlightPath: true });
          }}
          className="px-5 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center space-x-2 rounded-full shadow-lg transition-all shrink-0 cursor-pointer"
        >
          <Network className="w-4 h-4" />
          <span>Reveal 5-Hop Conduit on Graph</span>
        </button>
      </div>

      {/* Grid: Key Centrality Rankings + Connection Paths */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Key Entities Connectivity Ranking */}
        <div className="lg:col-span-12 glass-panel border border-white/10 p-6 rounded-3xl space-y-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                Centrality Rankings
              </div>
              <h2 className="text-lg font-bold text-[#F8FAFC] mt-0.5 font-mono">Key Network Brokers</h2>
            </div>
            <span className="text-xs text-[#94A3B8] font-mono">By Betweenness</span>
          </div>

          <div className="space-y-3.5">
            {keyEntities.map((broker: any, index: number) => {
              const isSelected = selectedBrokerId === broker.entity_id;
              const isHovered = hoveredBrokerId === broker.entity_id;
              const isHighlighted = isSelected || isHovered;
              
              let badgeLight = 'bg-rose-50 text-rose-600 border-rose-200';
              let badgeDark = 'bg-rose-950/50 text-rose-400 border-rose-800/60';
              if (index === 2) {
                badgeLight = 'bg-amber-50 text-amber-600 border-amber-200';
                badgeDark = 'bg-amber-950/50 text-amber-400 border-amber-800/60';
              }
              
              return (
                <div
                  key={broker.entity_id || index}
                  onClick={() => {
                    setSelectedBrokerId(broker.entity_id);
                    navigateTo('entities', { entityId: broker.entity_id });
                  }}
                  onMouseEnter={() => setHoveredBrokerId(broker.id)}
                  onMouseLeave={() => setHoveredBrokerId(null)}
                  className={`p-4.5 rounded-2xl border cursor-pointer transition-all duration-200 shadow-sm ${
                    isHighlighted
                      ? isLight
                        ? 'border-[#4F46E5] bg-indigo-50/40 shadow-md ring-1 ring-[#4F46E5]/30'
                        : 'border-[#FACC15] bg-[#FACC15]/5 shadow-md ring-1 ring-[#FACC15]/30'
                      : isLight
                      ? 'glass-card border-slate-200 hover:border-[#4F46E5]/60'
                      : 'glass-card border-white/10 hover:border-[#FACC15]/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center space-x-2.5">
                      <span
                        className={`w-6 h-6 rounded-lg border text-xs font-bold flex items-center justify-center font-mono transition-all duration-200 shadow-xs ${
                          isHighlighted
                            ? isLight
                              ? 'bg-[#4F46E5] border-[#4F46E5] text-white shadow-sm ring-2 ring-[#4F46E5]/20'
                              : 'bg-[#FACC15] border-[#FACC15] text-[#050507] shadow-sm'
                            : isLight
                            ? 'bg-slate-100 border-slate-300 text-slate-900'
                            : 'bg-[#0D0D11] border-white/20 text-[#94A3B8]'
                        }`}
                        style={
                          isLight
                            ? isHighlighted
                              ? { backgroundColor: '#4F46E5', color: '#FFFFFF', borderColor: '#4F46E5' }
                              : { backgroundColor: '#F1F5F9', color: '#050507', borderColor: '#CBD5E1' }
                            : isHighlighted
                            ? { backgroundColor: '#FACC15', color: '#050507', borderColor: '#FACC15' }
                            : undefined
                        }
                      >
                        <span
                          className="font-extrabold select-none"
                          style={
                            isLight
                              ? isHighlighted
                                ? { color: '#FFFFFF' }
                                : { color: '#050507' }
                              : undefined
                          }
                        >
                          {index + 1}
                        </span>
                      </span>
                      <span
                        className={`font-bold text-base transition-colors ${
                          isHighlighted
                            ? isLight
                              ? 'text-[#4F46E5]'
                              : 'text-[#FACC15]'
                            : isLight
                            ? 'text-[#0F172A]'
                            : 'text-[#F8FAFC]'
                        }`}
                      >
                        {broker.entity_id}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-bold font-mono px-2 py-0.5 border rounded-full ${
                        isLight ? badgeLight : badgeDark
                      }`}
                    >
                      {broker.metric.toUpperCase()}: {broker.score}
                    </span>
                  </div>
                  <div className={`text-xs mt-1.5 leading-relaxed font-sans ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'}`}>
                    {broker.explanation?.why || broker.explanation?.what || 'Critical node in the network.'}
                  </div>
                  <div className={`text-xs font-mono mt-3 flex items-center justify-between pt-2.5 border-t ${
                    isLight ? 'border-slate-200/80 text-slate-500' : 'border-white/10 text-[#64748B]'
                  }`}>
                    <span>Evidence: {broker.explanation?.supporting_evidence?.join(', ') || 'N/A'}</span>
                    <span className={`font-semibold flex items-center space-x-1 ${
                      isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'
                    }`}>
                      <span>Inspect Dossier</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>


      </div>

      {/* Clustered Groups & Behavioral Anomalies */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Functional Cluster Communities */}
        <div className="glass-panel border border-white/10 p-6 rounded-3xl space-y-4 shadow-xl">
          <div className="flex items-center space-x-2.5 border-b border-white/10 pb-4">
            <Layers className="w-4 h-4 text-[#FACC15]" />
            <h3 className="text-lg font-bold text-[#F8FAFC] font-mono">Functional Cluster Communities</h3>
          </div>

          <div className="space-y-3.5 text-xs">
            {communities.length > 0 ? communities.map((comm: any, i: number) => (
              <div key={comm.community_id} className="p-4.5 glass-card rounded-2xl border border-white/10 space-y-1">
                <div className="font-bold text-[#FACC15] text-sm mb-1 font-mono">Cluster {comm.community_id} (Size: {comm.size})</div>
                <p className="text-[#94A3B8] mb-2.5 leading-relaxed font-sans">
                  {comm.explanation?.what || `Central Entity: ${comm.central_entity_id}`}
                </p>
                <div className="text-xs font-mono text-[#64748B]">Evidentiary Basis: {comm.explanation?.supporting_evidence?.join(', ') || 'N/A'}</div>
              </div>
            )) : (
              <div className="p-4.5 glass-card rounded-2xl border border-white/10 text-center text-[#94A3B8]">
                No community clusters detected in this case graph.
              </div>
            )}
          </div>
        </div>

        {/* Behavioral Anomalies Flagged */}
        <div className="glass-panel border border-white/10 p-6 rounded-2xl space-y-4 shadow-xl">
          <div className="flex items-center space-x-2.5 border-b border-white/10 pb-4">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h3 className="text-lg font-bold text-[#F8FAFC] font-mono">Behavioral Anomalies Flagged</h3>
          </div>

          <div className="space-y-3.5 text-xs">
            <div className="p-4 glass-card rounded-xl border border-white/10 space-y-1">
              <div className="font-bold text-[#F8FAFC] text-sm mb-1 flex items-center justify-between font-mono">
                <span>Threshold Avoidance (Smurfing)</span>
                <span className="text-xs font-mono text-rose-400 bg-rose-950/50 px-2.5 py-0.5 border border-rose-800/60 font-bold rounded-full">&lt; ₹50,000 Trigger</span>
              </div>
              <p className="text-[#94A3B8] leading-relaxed font-sans">
                Transaction batches calibrated specifically below ₹50,000 (e.g. ₹50,000 and ₹48,200) to deliberately bypass mandatory Form 60 / PAN reporting thresholds under Indian tax enforcement guidelines.
              </p>
            </div>

            <div className="p-4 glass-card rounded-xl border border-white/10 space-y-1">
              <div className="font-bold text-[#F8FAFC] text-sm mb-1 flex items-center justify-between font-mono">
                <span>Disposable Burner Handset Churn</span>
                <span className="text-xs font-mono text-amber-400 bg-amber-950/50 px-2.5 py-0.5 border border-amber-800/60 font-bold rounded-full">&lt; 48h Churn</span>
              </div>
              <p className="text-[#94A3B8] leading-relaxed font-sans">
                Burner phone line +91-91230-00991 activated exclusively for tactical command bursts and discarded within 48 hours to evade regular IMSI surveillance sweeps.
              </p>
            </div>

            <div className="p-4 glass-card rounded-xl border border-white/10 space-y-1">
              <div className="font-bold text-[#F8FAFC] text-sm mb-1 flex items-center justify-between font-mono">
                <span>Cell Tower Co-Location Convergence</span>
                <span className="text-xs font-mono text-emerald-400 bg-emerald-950/50 px-2.5 py-0.5 border border-emerald-800/60 font-bold rounded-full">Sector MUM-C4-89</span>
              </div>
              <p className="text-[#94A3B8] leading-relaxed font-sans">
                Two separate mobile devices (+91-98765-43210 and +91-98234-11876) synchronized on the exact cell tower sector within 30 seconds of physical observation, followed by an immediate voice call.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
