import React, { useState, useMemo } from 'react';
import {
  Clock,
  Filter,
  Users,
  CreditCard,
  MapPin,
  FileSpreadsheet,
  Network,
  ExternalLink,
  PhoneCall,
  Sparkles,
  Car,
  Radio,
  Eye,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { TimelineEvent } from '../../types';

export const TimelineView: React.FC = () => {
  const { timelineEvents, navigateTo, theme } = useInvestigation();
  const isLight = theme === 'light';

  const [selectedEntityFilter, setSelectedEntityFilter] = useState<string>('all');
  const [selectedSourceFilter, setSelectedSourceFilter] = useState<string>('all');
  const [selectedEventId, setSelectedEventId] = useState<string>(
    timelineEvents[timelineEvents.length - 1]?.id || 'time-07'
  );

  const getTimelineEventIcon = (evt: TimelineEvent) => {
    if (evt.category === 'movement' || evt.title.toLowerCase().includes('creta') || evt.title.toLowerCase().includes('departs'))
      return Car;
    if (evt.category === 'meeting' || evt.title.toLowerCase().includes('handover') || evt.title.toLowerCase().includes('meeting'))
      return Users;
    if (evt.category === 'communication' || evt.sourceType === 'communication' || evt.title.toLowerCase().includes('call'))
      return PhoneCall;
    if (evt.category === 'financial' || evt.sourceType === 'financial' || evt.amount)
      return CreditCard;
    if (evt.category === 'surveillance' || evt.sourceType === 'surveillance')
      return Eye;
    return Clock;
  };

  const filteredEvents = timelineEvents.filter((evt) => {
    const matchesEntity =
      selectedEntityFilter === 'all'
        ? true
        : evt.entities.some((entName) =>
            entName.toLowerCase().includes(selectedEntityFilter.toLowerCase())
          );

    const matchesSource =
      selectedSourceFilter === 'all'
        ? true
        : evt.sourceType === selectedSourceFilter ||
          (selectedSourceFilter === 'system' && evt.category === 'system');

    return matchesEntity && matchesSource;
  });

  // Flipped event timeline: Latest / Newest events at TOP, Oldest events at BOTTOM
  const orderedEvents = useMemo(() => {
    return [...filteredEvents].reverse();
  }, [filteredEvents]);

  // Keep activeEvent valid
  const activeEvent =
    timelineEvents.find((e) => e.id === selectedEventId) || orderedEvents[0] || timelineEvents[0];

  return (
    <div id="timeline-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header & Filter Controls - Balanced Space Utilization & Proper Alignment */}
      <div className="glass-panel border border-white/10 p-6 md:p-8 rounded-3xl grid grid-cols-1 lg:grid-cols-12 gap-6 items-center shadow-2xl backdrop-blur-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-yellow-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Left Column: Title & Metadata (7 cols) */}
        <div className="lg:col-span-7 space-y-2 relative z-10">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-[0.2em] text-[#FACC15] uppercase flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-[#FACC15] animate-pulse"></span>
              <span>Chronological Reconstruction</span>
            </span>
            <span className="text-xs font-mono bg-white/[0.04] text-[#FACC15] px-3 py-1 border border-white/10 rounded-full font-semibold shadow-xs">
              12 MAY 2026 • OPERATION NEXUS
            </span>
            <span className="text-[10px] font-mono text-[#10B981] px-2.5 py-0.5 rounded-full bg-[#10B981]/15 border border-[#10B981]/40 font-semibold">
              Latest First ↓
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#F8FAFC] tracking-tight font-mono">
            Chronological Event Timeline
          </h1>
          <p className="text-xs text-[#94A3B8] leading-relaxed max-w-2xl font-sans">
            Synchronized sequence of physical surveillance rendezvous, cellular tower colocation logs, core banking SFMS wire transfers, and satellite command bursts.
          </p>
        </div>

        {/* Right Column: Status Summary & Aligned Filter Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-3 relative z-10">
          {/* Quick Metrics Cluster */}
          <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
            <div className="glass-card border border-white/10 p-2.5 rounded-2xl">
              <div className="text-[10px] text-[#64748B] uppercase">Intercepts</div>
              <div className="text-sm font-bold text-[#FACC15] mt-0.5">{orderedEvents.length} Events</div>
            </div>
            <div className="glass-card border border-white/10 p-2.5 rounded-2xl">
              <div className="text-[10px] text-[#64748B] uppercase">Window</div>
              <div className="text-sm font-bold text-[#F8FAFC] mt-0.5">08:35–14:30</div>
            </div>
            <div className="glass-card border border-white/10 p-2.5 rounded-2xl">
              <div className="text-[10px] text-[#64748B] uppercase">Custody</div>
              <div className="text-sm font-bold text-[#10B981] mt-0.5">100% Sealed</div>
            </div>
          </div>

          {/* Filter Controls Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs font-mono">
            {/* Entity Filter */}
            <div className="flex items-center space-x-2 glass-card px-3.5 py-2.5 rounded-2xl border border-white/10 shadow-inner">
              <Users className="w-3.5 h-3.5 text-[#FACC15] shrink-0" />
              <span className="text-[#64748B] text-[10px] uppercase font-semibold shrink-0">Subject:</span>
              <select
                value={selectedEntityFilter}
                onChange={(e) => setSelectedEntityFilter(e.target.value)}
                className="bg-transparent text-[#F8FAFC] font-medium focus:outline-none cursor-pointer text-xs font-mono w-full truncate"
              >
                <option value="all" className="bg-[#0D0D11] text-white">All Subjects</option>
                <option value="Rahul" className="bg-[#0D0D11] text-white">Rahul Sharma</option>
                <option value="Ajay" className="bg-[#0D0D11] text-white">Ajay Patil</option>
                <option value="Neha" className="bg-[#0D0D11] text-white">Neha Verma</option>
                <option value="XYZ" className="bg-[#0D0D11] text-white">XYZ Traders</option>
                <option value="Vikram" className="bg-[#0D0D11] text-white">Vikram Singhania</option>
              </select>
            </div>

            {/* Source Filter */}
            <div className="flex items-center space-x-2 glass-card px-3.5 py-2.5 rounded-2xl border border-white/10 shadow-inner">
              <Filter className="w-3.5 h-3.5 text-[#FACC15] shrink-0" />
              <span className="text-[#64748B] text-[10px] uppercase font-semibold shrink-0">Feed:</span>
              <select
                value={selectedSourceFilter}
                onChange={(e) => setSelectedSourceFilter(e.target.value)}
                className="bg-transparent text-[#F8FAFC] font-medium focus:outline-none cursor-pointer text-xs font-mono w-full truncate"
              >
                <option value="all" className="bg-[#0D0D11] text-white">All Feeds</option>
                <option value="police_report" className="bg-[#0D0D11] text-white">Police / ANPR</option>
                <option value="communication" className="bg-[#0D0D11] text-white">Telecom CDR</option>
                <option value="financial" className="bg-[#0D0D11] text-white">SFMS Banking</option>
                <option value="surveillance" className="bg-[#0D0D11] text-white">Covert Tracking</option>
                <option value="system" className="bg-[#0D0D11] text-white">AI Engine</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Timeline Stepper (7 cols) & Event Provenance Inspector (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Interactive Chronological Timeline */}
        <div className="lg:col-span-7 glass-panel border border-white/10 p-6 rounded-2xl shadow-xl">
          <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15] mb-6 flex items-center justify-between">
            <span>Chronological Incident Chain (Newest to Oldest)</span>
            <span className="text-[#94A3B8] font-normal font-mono">{orderedEvents.length} Recorded Intercepts</span>
          </div>

          <div className="relative pl-8 space-y-6 before:absolute before:left-3.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-[#FACC15]/40 before:via-white/10 before:to-[#FACC15]/40">
            {orderedEvents.map((evt) => {
              const isSelected = activeEvent?.id === evt.id;
              const EventIcon = getTimelineEventIcon(evt);
              return (
                <div
                  key={evt.id}
                  onClick={() => setSelectedEventId(evt.id)}
                  className="relative group cursor-pointer"
                >
                  {/* Timeline Node Icon: Dynamic Highlight on Hover and Click */}
                  <div
                    title="Click to inspect this timeline event"
                    className={`absolute -left-8 top-1.5 w-7 h-7 rounded-full flex items-center justify-center transition-all duration-300 z-10 cursor-pointer ${
                      isSelected
                        ? isLight
                          ? 'bg-[#4F46E5] text-white border-2 border-[#4F46E5] shadow-[0_0_22px_rgba(79,70,229,0.5)] ring-4 ring-[#4F46E5]/40 scale-125'
                          : 'bg-[#FACC15] text-[#050507] border-2 border-[#FACC15] shadow-[0_0_22px_rgba(250, 204, 21,0.95)] ring-4 ring-[#FACC15]/40 scale-125'
                        : isLight
                          ? 'bg-white border-2 border-slate-400 text-slate-900 shadow-xs group-hover:scale-125 group-hover:bg-[#4F46E5] group-hover:text-white group-hover:border-[#4F46E5] group-hover:shadow-[0_0_16px_rgba(79,70,229,0.5)] group-hover:ring-4 group-hover:ring-[#4F46E5]/30'
                          : 'bg-[#0D0D11] border border-white/20 text-[#94A3B8] group-hover:scale-125 group-hover:bg-[#FACC15] group-hover:text-[#050507] group-hover:border-[#FACC15] group-hover:shadow-[0_0_16px_rgba(250, 204, 21,0.85)] group-hover:ring-4 group-hover:ring-[#FACC15]/30'
                    }`}
                    style={
                      isLight
                        ? isSelected
                          ? { backgroundColor: '#4F46E5', color: '#FFFFFF' }
                          : { backgroundColor: '#FFFFFF', color: '#050507' }
                        : undefined
                    }
                  >
                    <EventIcon 
                      className={`w-3.5 h-3.5 transition-transform duration-200 group-hover:scale-110 ${
                        isSelected
                          ? 'text-white'
                          : isLight
                          ? 'text-slate-900 group-hover:text-white'
                          : 'text-[#94A3B8] group-hover:text-[#050507]'
                      }`}
                      style={
                        isLight
                          ? isSelected
                            ? { color: '#FFFFFF' }
                            : { color: '#050507' }
                          : undefined
                      }
                    />
                  </div>

                  {/* Event Card */}
                  <div
                    className={`p-5 rounded-2xl border transition-all ${
                      isSelected
                        ? isLight
                          ? 'bg-white border-[#4F46E5]/50 shadow-[0_0_25px_rgba(79,70,229,0.15)] ring-1 ring-[#4F46E5]/40'
                          : 'glass-card border-[#FACC15] shadow-[0_0_25px_rgba(250, 204, 21,0.25)] ring-1 ring-[#FACC15]/40'
                        : isLight
                          ? 'bg-white/80 border-slate-200 hover:border-[#4F46E5]/50 hover:bg-white hover:shadow-sm'
                          : 'bg-[#050507]/70 border-white/10 hover:border-[#FACC15]/50 hover:bg-[#141418]/60 hover:shadow-[0_0_15px_rgba(250, 204, 21,0.15)]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2.5">
                        <span className={`font-mono font-bold text-xs px-2.5 py-0.5 rounded-full ${
                          isSelected 
                            ? (isLight ? 'bg-[#4F46E5] text-white' : 'bg-[#FACC15] text-[#050507]') 
                            : (isLight ? 'bg-slate-100 text-[#4F46E5] border border-slate-200' : 'bg-[#0D0D11] text-[#FACC15] border border-white/10')
                        }`}>
                          {evt.time} IST
                        </span>
                        <h2 className={`text-sm font-bold transition-colors ${isLight ? 'text-[#0F172A] group-hover:text-[#4F46E5]' : 'text-[#F8FAFC] group-hover:text-[#FACC15]'}`}>
                          {evt.title}
                        </h2>
                      </div>
                      <span className={`text-[11px] font-mono px-2.5 py-0.5 border rounded-full ${isLight ? 'text-slate-500 bg-slate-50 border-slate-200' : 'text-[#94A3B8] bg-[#0D0D11] border-white/10'}`}>
                        {evt.source}
                      </span>
                    </div>

                    <p className={`text-xs mt-2 leading-relaxed font-sans ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'}`}>
                      {evt.description}
                    </p>

                    {/* Metadata chips */}
                    <div className={`mt-3.5 flex flex-wrap items-center gap-2 text-xs pt-3 border-t ${isLight ? 'border-slate-200' : 'border-white/10'}`}>
                      {evt.amount && (
                        <span className={`font-mono font-bold px-2.5 py-0.5 border rounded-full ${isLight ? 'bg-amber-50 text-amber-600 border-amber-200' : 'bg-amber-950/40 text-amber-400 border-amber-800/60'}`}>
                          {evt.amount}
                        </span>
                      )}
                      {evt.duration && (
                        <span className={`font-mono px-2.5 py-0.5 border rounded-full ${isLight ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-emerald-950/40 text-emerald-400 border-emerald-800/60'}`}>
                          ⏱ {evt.duration}
                        </span>
                      )}
                      {evt.location && (
                        <span className={`px-2.5 py-0.5 font-sans text-xs border rounded-full ${isLight ? 'bg-slate-50 text-slate-500 border-slate-200' : 'bg-[#0D0D11] text-[#94A3B8] border-white/10'}`}>
                          📍 {evt.location}
                        </span>
                      )}
                      <span className={`font-mono text-xs font-bold ml-auto ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`}>
                        Evidence: {evt.evidenceId}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Event Detail & Provenance Inspector */}
        <div className="lg:col-span-5">
          {activeEvent ? (
            <div className="glass-panel border border-white/10 p-6 rounded-2xl space-y-5 sticky top-20 shadow-xl">
              <div className="border-b border-white/10 pb-4">
                <div className="flex items-center space-x-2 text-xs text-[#64748B] font-mono mb-1">
                  <span>{activeEvent.datetime}</span>
                  <span>•</span>
                  <span className="font-bold text-[#FACC15]">{activeEvent.evidenceId}</span>
                </div>
                <h3 className="text-lg font-bold text-[#F8FAFC] mt-1 font-mono">{activeEvent.title}</h3>
                <span className="text-xs text-[#94A3B8] font-mono mt-1 block">Feed Source: {activeEvent.source}</span>
              </div>

              <div className="text-xs text-[#94A3B8] glass-card p-4 rounded-xl border border-white/10 leading-relaxed font-sans">
                <strong className="block text-[#FACC15] font-mono text-[10px] uppercase mb-1.5 tracking-wider font-bold">
                  SITREP / Intercept Narrative
                </strong>
                {activeEvent.description}
              </div>

              {/* Entities Involved */}
              <div>
                <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15] mb-3">
                  Entities Involved
                </div>
                <div className="flex flex-wrap gap-2">
                  {activeEvent.entities.map((entName, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 glass-card border border-white/10 rounded-full text-xs font-mono font-medium text-[#F8FAFC]"
                    >
                      {entName}
                    </span>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="pt-4 border-t border-white/10 space-y-2.5">
                <button
                  onClick={() => navigateTo('evidence', { evidenceId: activeEvent.evidenceId })}
                  className="w-full py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center justify-center space-x-2 rounded-full shadow-lg transition-all cursor-pointer"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Open Evidence Record ({activeEvent.evidenceId})</span>
                </button>
                <button
                  onClick={() => navigateTo('graph', { highlightPath: activeEvent.highlightInHiddenPath })}
                  className="w-full py-2.5 glass-card hover:bg-white/10 text-[#F8FAFC] text-xs font-mono uppercase tracking-wider font-semibold flex items-center justify-center space-x-2 border border-white/10 rounded-full transition-all cursor-pointer"
                >
                  <Network className="w-4 h-4 text-[#FACC15]" />
                  <span>Locate Entities on Graph</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="glass-panel border border-white/10 p-8 rounded-2xl text-center text-[#64748B] text-xs font-mono">
              Select an event to inspect evidentiary records.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
