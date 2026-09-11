import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Phone,
  CreditCard,
  RotateCcw,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Building,
  MapPin,
  Clock,
  Network,
  X,
} from 'lucide-react';
import { api } from '../../lib/api';
import { useInvestigation } from '../../context/InvestigationContext';

export const EntityResolutionView: React.FC = () => {
  const {
    entityMatch,
    approveEntityMatch,
    rejectEntityMatch,
    resetEntityMatch,
    navigateTo,
    currentCaseId,
    isAuthenticated,
  } = useInvestigation();

  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    if (!isAuthenticated) return;
    const fetchMatches = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/v1/resolution/matches');
        if (res.data) {
          setMatches(res.data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchMatches();
  }, [isAuthenticated, currentCaseId]);

  const [investigatorNote, setInvestigatorNote] = useState<string>('');

  if (loading) {
    return (
      <div className="w-full h-96 flex flex-col items-center justify-center space-y-4">
        <div className="w-8 h-8 rounded-full border-4 border-amber-500/20 border-t-amber-500 animate-spin"></div>
        <p className="text-sm font-mono text-[#94A3B8]">Scanning for probabilistic identity overlaps...</p>
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="w-full h-96 flex flex-col items-center justify-center space-y-4">
        <ShieldCheck className="w-16 h-16 text-emerald-500 opacity-80" />
        <h2 className="text-xl font-bold font-mono text-[#F8FAFC]">No Pending Resolutions</h2>
        <p className="text-sm font-mono text-[#94A3B8]">The master graph for this case is fully consolidated. No new aliases detected.</p>
      </div>
    );
  }

  const currentMatch = matches[0];

  return (
    <div id="entity-resolution-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header - Rounded Theme & Glassmorphism */}
      <div className="glass-panel border border-white/10 p-6 sm:p-8 rounded-3xl shadow-2xl backdrop-blur-xl flex flex-col sm:flex-row sm:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-yellow-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center space-x-2 text-[10px] uppercase tracking-[0.25em] text-[#FACC15] font-mono mb-2 font-bold">
            <span className="w-2 h-2 rounded-full bg-[#FACC15] animate-pulse"></span>
            <span>Disambiguation & Deduplication Engine • Probabilistic AI Matcher</span>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#F8FAFC] tracking-tight font-mono">
              Entity Resolution Queue
            </h1>
            <span className="text-xs font-mono bg-yellow-500/15 text-[#FACC15] px-3.5 py-1 border border-[#FACC15]/40 rounded-full font-bold shadow-xs">
              MATCH-{currentMatch.id.split('-')[0].toUpperCase()} • {Math.round(currentMatch.final_weighted_score * 100)}% Match
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-2 max-w-3xl leading-relaxed">
            TraceX cross-references identity fragments across telecom, banking, and physical surveillance streams to discover concealed duplicates and aliases used to evade automated watchlists.
          </p>
        </div>

        {entityMatch.status !== 'pending' && (
          <button
            type="button"
            onClick={resetEntityMatch}
            className="text-xs font-mono uppercase tracking-wider text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-white/10 bg-white/[0.04] px-4 py-2.5 flex items-center space-x-2 border border-white/10 rounded-full transition-all cursor-pointer shrink-0 shadow-sm"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset Demo State</span>
          </button>
        )}
      </div>

      {/* AI Advisory Banner - Glassmorphic Warning Callout */}
      <div className="glass-panel border border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-amber-950/20 to-black/40 p-5 rounded-2xl text-xs text-[#F8FAFC] flex items-start space-x-3.5 shadow-xl backdrop-blur-xl">
        <div className="p-2 bg-amber-500/20 border border-amber-500/40 rounded-xl shrink-0 mt-0.5">
          <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
        </div>
        <div className="text-xs leading-relaxed font-mono">
          <strong className="text-amber-400 uppercase tracking-wider">Forensic Advisory (Section 65B): </strong>
          Probabilistic identity convergence detected across disparate data streams (CCTNS vs SBI SFMS). Section 65B legal standards require explicit investigator sign-off before committing identity consolidation into the master judicial graph.
        </div>
      </div>

      {/* Main Side-by-Side Comparison Container - Rounded Glassmorphism */}
      <div className="glass-panel border border-white/10 p-6 sm:p-8 rounded-3xl shadow-2xl backdrop-blur-xl space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
          {/* Central Comparison Connector Badge */}
          <div className="hidden md:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20 flex-col items-center">
            <div className="w-11 h-11 bg-[#0A0A0E] text-[#FACC15] flex items-center justify-center shadow-[0_0_20px_rgba(250, 204, 21,0.4)] border border-[#FACC15]/60 font-mono text-xs font-extrabold rounded-full backdrop-blur-xl">
              VS
            </div>
          </div>

          {/* LEFT: Communication / Field Record */}
          <div className="glass-card border border-white/10 p-6 rounded-2xl space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <span className="text-[10px] font-mono font-bold uppercase text-[#FACC15] tracking-[0.2em] flex items-center space-x-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#FACC15]"></span>
                <span>Source: Police CCTNS & Lawful CDR</span>
              </span>
              <span className="text-xs font-mono font-bold text-[#F8FAFC] bg-white/[0.05] px-3 py-1 border border-white/10 rounded-full">
                EV-001 & EV-002
              </span>
            </div>

            <div>
              <div className="text-[10px] uppercase font-mono text-[#64748B]">Candidate Identity A</div>
              <h3 className="text-xl font-bold text-[#F8FAFC] mt-0.5">Ajay Patil</h3>
              <span className="text-xs text-[#94A3B8] font-mono">Ground Facilitator & Cash Broker</span>
            </div>

            <div className="space-y-2.5 text-xs bg-black/40 p-4 border border-white/10 rounded-2xl font-mono shadow-inner">
              <div className="flex items-center justify-between">
                <span className="text-[#94A3B8] flex items-center">
                  <Phone className="w-3.5 h-3.5 mr-1.5 text-[#10B981]" />
                  Intercepted MSISDN:
                </span>
                <span className="font-bold text-[#F8FAFC] bg-white/[0.06] px-2.5 py-0.5 border border-white/10 rounded-xl">
                  +91-98234-11876
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#94A3B8] flex items-center">
                  <MapPin className="w-3.5 h-3.5 mr-1.5 text-[#EF4444]" />
                  Observation Sites:
                </span>
                <span className="text-[#F8FAFC]">Central Terminal / Sector 4 Depot</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#94A3B8] flex items-center">
                  <Clock className="w-3.5 h-3.5 mr-1.5 text-[#64748B]" />
                  Surveillance Window:
                </span>
                <span className="text-[#F8FAFC]">12 May • 08:45 - 11:15 IST</span>
              </div>
            </div>
          </div>

          {/* RIGHT: Core Banking Wire Record */}
          <div className="glass-card border border-white/10 p-6 rounded-2xl space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <span className="text-[10px] font-mono font-bold uppercase text-[#10B981] tracking-[0.2em] flex items-center space-x-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]"></span>
                <span>Source: SBI Core Banking SFMS</span>
              </span>
              <span className="text-xs font-mono font-bold text-[#F8FAFC] bg-white/[0.05] px-3 py-1 border border-white/10 rounded-full">
                EV-003
              </span>
            </div>

            <div>
              <div className="text-[10px] uppercase font-mono text-[#64748B]">Candidate Identity B</div>
              <h3 className="text-xl font-bold text-[#F8FAFC] mt-0.5">A. Patil</h3>
              <span className="text-xs text-[#94A3B8] font-mono">Originating Bank Account Holder</span>
            </div>

            <div className="space-y-2.5 text-xs bg-black/40 p-4 border border-white/10 rounded-2xl font-mono shadow-inner">
              <div className="flex items-center justify-between">
                <span className="text-[#94A3B8] flex items-center">
                  <Phone className="w-3.5 h-3.5 mr-1.5 text-[#10B981]" />
                  Registered KYC Phone:
                </span>
                <span className="font-bold text-[#10B981] bg-emerald-950/40 px-2.5 py-0.5 border border-emerald-500/40 rounded-xl">
                  +91-98234-11876
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#94A3B8] flex items-center">
                  <CreditCard className="w-3.5 h-3.5 mr-1.5 text-[#F59E0B]" />
                  Debit Account:
                </span>
                <span className="text-[#F8FAFC]">A/C 889922 (SBI Commercial)</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#94A3B8] flex items-center">
                  <Clock className="w-3.5 h-3.5 mr-1.5 text-[#64748B]" />
                  Wire Timestamp:
                </span>
                <span className="text-[#F8FAFC]">12 May • 11:48:32 IST</span>
              </div>
            </div>
          </div>
        </div>

        {/* Multi-Signal Similarity Matrix */}
        <div className="space-y-3 pt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
              Multi-Signal Similarity Matrix (Overall: {Math.round(currentMatch.final_weighted_score * 100)}% Match)
            </span>
            <span className="text-xs font-mono text-[#10B981] font-bold bg-[#10B981]/15 px-3 py-0.5 border border-[#10B981]/40 rounded-full">
              Verified Indicators
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 text-xs font-mono">
            <div className="p-3.5 glass-card border border-emerald-500/40 rounded-2xl shadow-sm">
              <div className="flex items-center justify-between text-[#64748B] text-[10px] uppercase">
                <span>Exact Mobile Match</span>
                <span className="text-[#10B981] font-bold">{Math.round((currentMatch.shared_phone_score || 0) * 100)}%</span>
              </div>
              <div className="font-bold text-sm text-[#10B981] mt-1">Found</div>
            </div>

            <div className="p-3.5 glass-card border border-white/10 rounded-2xl shadow-sm">
              <div className="flex items-center justify-between text-[#64748B] text-[10px] uppercase">
                <span>Fuzzy KYC Address</span>
                <span className="text-[#FACC15] font-bold">N/A</span>
              </div>
            </div>

            <div className="p-3.5 glass-card border border-white/10 rounded-2xl shadow-sm">
              <div className="flex items-center justify-between text-[#64748B] text-[10px] uppercase">
                <span>Phonetic Soundex</span>
                <span className="text-[#FACC15] font-bold">{Math.round((currentMatch.name_similarity_score || 0) * 100)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Investigator Certification Memorandum */}
        <div className="space-y-2 pt-3 border-t border-white/10">
          <label className="block text-[11px] font-mono uppercase tracking-wider text-[#94A3B8] font-semibold">
            Officer Verification Memorandum (Section 65B Digital Endorsement):
          </label>
          <textarea
            value={investigatorNote}
            onChange={(e) => setInvestigatorNote(e.target.value)}
            rows={2}
            className="w-full p-4 bg-black/40 border border-white/10 focus:border-[#FACC15] text-xs font-mono text-[#F8FAFC] rounded-2xl focus:outline-none shadow-inner transition-all"
          />
        </div>

        {/* Action Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-white/10">
          <div>
            {entityMatch.status === 'approved' ? (
              <div className="flex items-center space-x-2 text-xs font-mono text-[#10B981] font-bold">
                <CheckCircle2 className="w-4 h-4" />
                <span>Consolidated: Ajay Patil &amp; A. Patil merged into unified identity node.</span>
              </div>
            ) : entityMatch.status === 'rejected' ? (
              <div className="flex items-center space-x-2 text-xs font-mono text-[#EF4444] font-bold">
                <XCircle className="w-4 h-4" />
                <span>Proposal Rejected: Entities retained as independent identities.</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-xs font-mono text-[#F59E0B]">
                <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
                <span>Pending Officer Authorization to consolidate graph nodes.</span>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3 self-end sm:self-auto">
            {entityMatch.status === 'pending' ? (
              <>
                <button
                  type="button"
                  onClick={async () => {
                    await api.post(`/api/v1/resolution/match/${currentMatch.id}/decision`, { decision: 'REJECT' });
                    setMatches(matches.filter(m => m.id !== currentMatch.id));
                  }}
                  className="px-5 py-2.5 bg-[#EF4444]/15 hover:bg-[#EF4444] text-[#EF4444] hover:text-[#050507] border border-[#EF4444]/40 hover:border-[#EF4444] hover:shadow-[0_0_20px_rgba(239,68,68,0.5)] text-xs font-mono font-bold rounded-full flex items-center space-x-1.5 transition-all cursor-pointer group"
                >
                  <X className="w-4 h-4 text-[#EF4444] group-hover:text-[#050507] transition-colors" />
                  <span>Reject Proposal</span>
                </button>
                <button
                  type="button"
                  onClick={async () => {
                    await api.post(`/api/v1/resolution/match/${currentMatch.id}/decision`, { decision: 'CONFIRM' });
                    setMatches(matches.filter(m => m.id !== currentMatch.id));
                  }}
                  className="px-5 py-2.5 bg-[#10B981] hover:bg-[#059669] text-[#050507] font-mono font-bold text-xs uppercase tracking-wider rounded-full flex items-center space-x-2 transition-all shadow-lg hover:shadow-[0_0_20px_rgba(16,185,129,0.5)] cursor-pointer"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve Match &amp; Fuse Nodes</span>
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={() => navigateTo('graph')}
                className="px-5 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold text-xs uppercase tracking-wider rounded-full flex items-center space-x-2 transition-all shadow-lg hover:shadow-[0_0_20px_rgba(250, 204, 21,0.5)] cursor-pointer"
              >
                <Network className="w-4 h-4" />
                <span>Inspect Unified Node in Graph</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
