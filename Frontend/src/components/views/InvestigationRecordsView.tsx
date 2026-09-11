import React, { useState } from 'react';
import {
  FileSpreadsheet,
  Search,
  Users,
  MapPin,
  Clock,
  CreditCard,
  Building,
  CheckCircle2,
  ExternalLink,
  Network,
  ArrowRight,
  ShieldCheck,
  ChevronRight,
  Sparkles,
  Car,
  Lock,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export const InvestigationRecordsView: React.FC = () => {
  const {
    evidenceRecords,
    selectedRecordId,
    setSelectedRecordId,
    selectedRecord,
    navigateTo,
    setSelectedEntityId,
    theme,
  } = useInvestigation();

  const isLight = theme === 'light';

  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [highlightedEntityText, setHighlightedEntityText] = useState<string | null>(null);

  // Filter records
  const filteredRecords = evidenceRecords.filter((rec) => {
    const matchesFilter =
      activeFilter === 'all'
        ? true
        : activeFilter === 'police'
        ? rec.type === 'police_report'
        : activeFilter === 'communication'
        ? rec.type === 'communication'
        : activeFilter === 'financial'
        ? rec.type === 'financial' || rec.type === 'organisation_activity'
        : activeFilter === 'surveillance'
        ? rec.type === 'surveillance'
        : true;

    const matchesSearch =
      rec.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.typeLabel.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  const activeRecord = selectedRecord || evidenceRecords[0];

  const getEntityIcon = (type: string) => {
    switch (type) {
      case 'person':
        return <Users className="w-3.5 h-3.5 text-[#FACC15]" />;
      case 'location':
        return <MapPin className="w-3.5 h-3.5 text-[#EF4444]" />;
      case 'account':
        return <CreditCard className="w-3.5 h-3.5 text-[#F59E0B]" />;
      case 'organisation':
        return <Building className="w-3.5 h-3.5 text-[#A855F7]" />;
      case 'vehicle':
        return <Car className="w-3.5 h-3.5 text-[#EC4899]" />;
      case 'event':
        return <Clock className="w-3.5 h-3.5 text-[#94A3B8]" />;
      default:
        return <Sparkles className="w-3.5 h-3.5 text-[#FACC15]" />;
    }
  };

  const renderHighlightedContent = (text: string, highlightWord: string | null) => {
    if (!highlightWord) return text;
    const parts = text.split(new RegExp(`(${escapeRegExp(highlightWord)})`, 'gi'));
    return parts.map((part, idx) =>
      part.toLowerCase() === highlightWord.toLowerCase() ? (
        <mark
          key={idx}
          className="bg-[#FACC15]/30 text-[#FACC15] px-1.5 py-0.5 font-bold rounded-md border border-[#FACC15]"
        >
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  function escapeRegExp(string: string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  return (
    <div id="investigation-records-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Top Header & Table Controls - Rounded Theme & Glassmorphism */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-xl flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-yellow-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center space-x-2 text-[10px] uppercase tracking-[0.25em] text-[#FACC15] font-mono mb-2 font-bold">
            <span className="w-2 h-2 rounded-full bg-[#FACC15] animate-pulse"></span>
            <span>Forensic Evidence Catalog • ISO/IEC 27037</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#F8FAFC] flex flex-wrap items-center gap-3 tracking-tight">
            <span>Investigation Records</span>
            <span className="text-xs font-mono bg-white/[0.04] text-[#FACC15] px-3 py-1 border border-white/10 rounded-full shadow-inner">
              {filteredRecords.length} / {evidenceRecords.length} Authenticated
            </span>
          </h1>
          <p className="text-xs text-[#94A3B8] mt-2 max-w-2xl leading-relaxed">
            Raw CCTNS police diaries, lawful telecom CDR intercepts, core banking SFMS transfers, and Smart City ANPR logs with live NLP entity token tagging.
          </p>
        </div>

        {/* Search & Filter Tabs */}
        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <div className="relative">
            <Search className={`w-4 h-4 absolute left-3.5 top-3 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search EV-001, CDR, Airtel..."
              className={`pl-10 pr-4 py-2.5 text-xs border focus:outline-none w-56 sm:w-64 font-mono transition-all rounded-2xl shadow-inner ${isLight ? 'bg-white text-[#0F172A] border-[#CBD5E1] focus:border-[#4F46E5] placeholder:text-[#94A3B8] focus:ring-1 focus:ring-[#4F46E5]/40' : 'bg-black/40 border-white/10 focus:border-[#FACC15] text-[#F8FAFC] placeholder:text-[#64748B] focus:ring-1 focus:ring-[#FACC15]/40'}`}
            />
          </div>

          <div className={`flex items-center p-1.5 border rounded-2xl text-xs font-mono shadow-inner backdrop-blur-md ${isLight ? 'bg-white border-[#CBD5E1]' : 'bg-black/40 border-white/10'}`}>
            {[
              { id: 'all', label: 'All Feeds' },
              { id: 'police', label: 'Surveillance / CCTNS' },
              { id: 'communication', label: 'Telecom CDR' },
              { id: 'financial', label: 'Banking SFMS' },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveFilter(tab.id)}
                className={`px-3.5 py-1.5 text-xs font-medium rounded-xl transition-all cursor-pointer ${
                  activeFilter === tab.id
                    ? isLight
                      ? 'bg-indigo-100/80 text-slate-900 border border-indigo-300 shadow-xs font-bold'
                      : 'bg-[#FACC15] text-[#050507] shadow-sm font-bold border border-transparent'
                    : isLight
                      ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70 border border-transparent'
                      : 'text-[#94A3B8] hover:text-[#F8FAFC] border border-transparent'
                }`}
                style={activeFilter === tab.id && isLight ? { color: '#050507' } : undefined}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Record Table - Full Display Directly Without Scrolling */}
      <div className="glass-panel border border-white/10 rounded-3xl shadow-2xl backdrop-blur-xl overflow-hidden">
        <div className="w-full">
          <table className="w-full text-left text-xs table-auto">
            <thead className="bg-black/40 border-b border-white/10 text-[10px] font-mono uppercase tracking-[0.15em] text-[#64748B]">
              <tr>
                <th className="py-3.5 px-4 w-[10%]">Record ID</th>
                <th className="py-3.5 px-3 w-[18%]">Type</th>
                <th className="py-3.5 px-3 w-[22%]">Source Feed</th>
                <th className="py-3.5 px-2 w-[11%]">Timestamp</th>
                <th className="py-3.5 px-2 w-[13%]">Chain of Custody</th>
                <th className="py-3.5 px-3 w-[18%]">NLP Entities</th>
                <th className="py-3.5 px-4 w-[8%] text-center">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.06] font-mono">
              {filteredRecords.map((rec) => {
                const isSelected = activeRecord?.id === rec.id;
                return (
                  <tr
                    key={rec.id}
                    onClick={() => setSelectedRecordId(rec.id)}
                    className={`cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-yellow-500/10 border-l-4 border-yellow-400 backdrop-blur-md'
                        : 'hover:bg-white/[0.03]'
                    }`}
                  >
                    <td className="py-3.5 px-4 font-bold text-[#FACC15] whitespace-nowrap">
                      {rec.id}
                    </td>
                    <td className="py-3.5 px-3 text-[#F8FAFC] font-sans font-semibold truncate max-w-[180px]" title={rec.typeLabel}>
                      {rec.typeLabel}
                    </td>
                    <td className="py-3.5 px-3 text-[#94A3B8] font-sans truncate max-w-[210px]" title={rec.source}>
                      {rec.source}
                    </td>
                    <td className="py-3.5 px-2 text-[#94A3B8] text-xs whitespace-nowrap">
                      {rec.timestamp}
                    </td>
                    <td className="py-3.5 px-2 whitespace-nowrap">
                      <span className="inline-flex items-center text-[10px] font-semibold font-mono uppercase tracking-wider px-2 py-0.5 bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/40 rounded-full shadow-xs">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        {rec.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-3">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-[10px] text-[#F8FAFC] bg-black/40 px-2.5 py-0.5 border border-white/10 rounded-full font-semibold shrink-0 whitespace-nowrap shadow-inner">
                          {rec.extractedEntities.length} Entities
                        </span>
                        <span className="text-[11px] text-[#64748B] font-sans truncate max-w-[140px] hidden xl:inline">
                          ({rec.extractedEntities.slice(0, 2).map((e) => e.text).join(', ')}...)
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedRecordId(rec.id);
                        }}
                        className={`text-xs font-semibold px-3 py-1 rounded-xl border transition-all shadow-xs cursor-pointer ${
                          isSelected
                            ? 'bg-[#FACC15] text-[#050507] border-[#FACC15] font-bold shadow-yellow-500/20'
                            : 'bg-white/[0.04] hover:bg-white/[0.08] text-[#94A3B8] hover:text-[#F8FAFC] border-white/10'
                        }`}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* RECORD DETAIL — Split Inspector Rounded Theme & Glassmorphism */}
      {activeRecord && (
        <div className="glass-panel border border-white/10 p-6 lg:p-8 rounded-3xl shadow-2xl backdrop-blur-xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
            <div>
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="font-mono font-bold text-xs text-[#FACC15] bg-yellow-500/10 px-3 py-1 border border-yellow-400/30 rounded-xl shadow-inner">
                  {activeRecord.id}
                </span>
                <h2 className="text-lg sm:text-xl font-bold text-[#F8FAFC]">
                  {activeRecord.title}
                </h2>
                <span className="text-[10px] uppercase font-mono tracking-wider bg-white/[0.05] text-[#94A3B8] px-2.5 py-1 border border-white/10 rounded-full">
                  {activeRecord.typeLabel}
                </span>
              </div>
              <div className="text-xs text-[#94A3B8] mt-2.5 font-mono flex flex-wrap items-center gap-2">
                <span>Source: <strong className="text-[#F8FAFC]">{activeRecord.source}</strong></span>
                <span>•</span>
                <span>Timestamp: <strong className="text-[#F8FAFC]">{activeRecord.timestamp}</strong></span>
                <span>•</span>
                <span className="text-[#10B981] flex items-center space-x-1">
                  <Lock className="w-3 h-3" />
                  <span>SHA-256: {activeRecord.hashChecksum?.substring(0, 16)}...</span>
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-3 shrink-0">
              <button
                type="button"
                onClick={() => navigateTo('evidence', { evidenceId: activeRecord.id })}
                className="px-4 py-2 text-xs text-[#F8FAFC] bg-white/[0.04] hover:bg-white/[0.08] font-mono font-semibold border border-white/10 rounded-2xl flex items-center space-x-2 transition-colors shadow-xs"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-[#10B981]" />
                <span>Custody Seal</span>
              </button>
              <button
                type="button"
                onClick={() => navigateTo('graph')}
                className="px-4 py-2 text-xs text-[#050507] bg-[#FACC15] hover:bg-[#EAB308] font-mono font-bold rounded-2xl flex items-center space-x-2 transition-all shadow-md shadow-yellow-500/20"
              >
                <span>Inspect in Graph</span>
                <Network className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Split Inspector: Left Raw / Right AI Extracted */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Original Record (7 cols) */}
            <div className="lg:col-span-7 space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono font-bold tracking-[0.2em] text-[#FACC15] uppercase flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-[#FACC15] shadow-xs shadow-yellow-400" />
                  <span>Ingested Forensic Record (Raw Stream)</span>
                </div>
                {highlightedEntityText && (
                  <button
                    type="button"
                    onClick={() => setHighlightedEntityText(null)}
                    className="text-xs font-mono text-[#FACC15] hover:underline"
                  >
                    Clear entity highlight
                  </button>
                )}
              </div>

              {/* Raw Record Box with entity highlighting - Full Direct Display */}
              <div className="bg-black/50 text-[#F8FAFC] p-5 font-mono text-xs leading-relaxed whitespace-pre-wrap border border-white/10 rounded-2xl shadow-inner">
                {renderHighlightedContent(activeRecord.rawContent, highlightedEntityText)}
              </div>

              {/* Structured Parameters if available */}
              {activeRecord.structuredDetails && (
                <div className="glass-card border border-white/10 p-5 rounded-2xl text-xs space-y-3">
                  <div className="font-mono text-[10px] font-bold text-[#FACC15] uppercase tracking-[0.2em]">
                    Structured Forensic Attributes
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {Object.entries(activeRecord.structuredDetails).map(([key, val]) => (
                      <div key={key} className="bg-white/[0.03] p-3 border border-white/10 rounded-xl shadow-xs">
                        <span className="text-[10px] text-[#64748B] block uppercase font-mono tracking-wider">{key}</span>
                        <span className="font-mono font-semibold text-[#F8FAFC] text-xs mt-1 block truncate">{val}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right: Extracted Entities (5 cols) - Full Direct Display */}
            <div className="lg:col-span-5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono font-bold tracking-[0.2em] text-[#FACC15] uppercase flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-[#FACC15]" />
                  <span>Extracted NER Tokens ({activeRecord.extractedEntities.length})</span>
                </div>
                <span className="text-[10px] font-mono text-[#64748B]">Click token to locate in text</span>
              </div>

              <div className="space-y-2.5">
                {activeRecord.extractedEntities.map((ent, idx) => {
                  const isHighlighted = highlightedEntityText === ent.text;
                  return (
                    <div
                      key={idx}
                      onClick={() => setHighlightedEntityText(ent.text)}
                      className={`p-3.5 border rounded-2xl transition-all cursor-pointer backdrop-blur-md ${
                        isHighlighted
                          ? 'bg-yellow-500/15 border-[#FACC15] shadow-md shadow-yellow-500/10'
                          : 'glass-card border-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2.5">
                          <div className={`p-1.5 rounded-xl border ${isLight ? 'bg-[#F8FAFC] border-[#CBD5E1] shadow-sm' : 'bg-white/[0.06] border-white/10'}`}>
                            {getEntityIcon(ent.type)}
                          </div>
                          <span className={`font-bold text-xs ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>{ent.text}</span>
                        </div>
                        <span className="text-[9px] uppercase font-mono tracking-wider px-2.5 py-0.5 bg-white/[0.05] text-[#94A3B8] border border-white/10 rounded-full">
                          {ent.type}
                        </span>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-white/10 text-xs font-mono">
                        <span className="text-[#64748B] text-[11px]">
                          {isHighlighted ? '✓ Active highlight' : 'Click to highlight'}
                        </span>
                        <div className="flex items-center space-x-2">
                          {ent.entityId && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedEntityId(ent.entityId);
                                navigateTo('entities');
                              }}
                              className="text-[#FACC15] hover:underline inline-flex items-center uppercase tracking-wider text-[10px] font-semibold"
                            >
                              Profile <ChevronRight className="w-3 h-3 ml-0.5" />
                            </button>
                          )}
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigateTo('graph');
                            }}
                            className="text-[#94A3B8] hover:text-[#F8FAFC] uppercase tracking-wider text-[10px]"
                          >
                            Graph
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Supported Evidentiary Relationships */}
              <div className="glass-card border border-white/10 p-5 rounded-2xl text-xs space-y-2.5">
                <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                  Corroborated Facts
                </div>
                <ul className="space-y-2">
                  {activeRecord.supportedRelationships.map((rel, i) => (
                    <li key={i} className="flex items-start space-x-2 text-[#94A3B8] text-xs leading-relaxed">
                      <span className="text-[#10B981] font-bold mt-0.5">✓</span>
                      <span>{rel}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
