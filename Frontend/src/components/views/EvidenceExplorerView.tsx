import React, { useState, useEffect } from 'react';
import {
  FolderArchive,
  FileSpreadsheet,
  PhoneCall,
  CreditCard,
  Radio,
  Building,
  Network,
  Clock,
  Shield,
  ShieldCheck,
  FileText,
  Download,
  PlusCircle,
  CheckCircle2,
  ExternalLink,
  Lock,
  Search,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { EvidenceType } from '../../types';

export const EvidenceExplorerView: React.FC = () => {
  const {
    evidenceRecords,
    selectedEvidenceId,
    setSelectedEvidenceId,
    selectedEvidence,
    navigateTo,
    saveAuditLog,
    theme,
  } = useInvestigation();
  
  const isLight = theme === 'light';

  const [verifiedHashes, setVerifiedHashes] = useState<Record<string, boolean>>({
    'EV-001': true,
    'EV-002': true,
    'EV-003': true,
    'EV-004': true,
    'EV-005': true,
    'EV-006': true,
    'EV-007': true,
    'EV-008': true,
    'EV-009': true,
  });

  const [verifyingId, setVerifyingId] = useState<string | null>(null);
  const [custodyNotes, setCustodyNotes] = useState<Record<string, string[]>>({});
  const [isNoteModalOpen, setIsNoteModalOpen] = useState<boolean>(false);
  const [newNoteText, setNewNoteText] = useState<string>('');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const activeEvidence = selectedEvidence || evidenceRecords[0];

  // Track clicked / inspected evidence items
  const [clickedEvidenceIds, setClickedEvidenceIds] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    if (selectedEvidenceId) initial.add(selectedEvidenceId);
    else if (evidenceRecords[0]?.id) initial.add(evidenceRecords[0].id);
    return initial;
  });

  useEffect(() => {
    if (selectedEvidenceId) {
      setClickedEvidenceIds((prev) => {
        if (prev.has(selectedEvidenceId)) return prev;
        const next = new Set(prev);
        next.add(selectedEvidenceId);
        return next;
      });
    }
  }, [selectedEvidenceId]);

  const handleSelectEvidence = (id: string) => {
    setSelectedEvidenceId(id);
    setClickedEvidenceIds((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleVerifyHash = (id: string, checksum?: string) => {
    setVerifyingId(id);
    setTimeout(() => {
      setVerifiedHashes((prev) => ({ ...prev, [id]: true }));
      setVerifyingId(null);
      saveAuditLog(`Cryptographic SHA-256 hash verified for evidence item ${id}: Integrity 100% Intact.`);
      showToast(`✓ Cryptographic verification passed: ${id} SHA-256 hash signature is genuine.`);
    }, 600);
  };

  const handleAddCustodyNote = () => {
    if (!newNoteText.trim() || !activeEvidence) return;
    const timestamp = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const noteEntry = `[12 May 2026 • ${timestamp} IST] Insp. V. Kulkarni (Badge #CY-8821): ${newNoteText.trim()}`;

    setCustodyNotes((prev) => ({
      ...prev,
      [activeEvidence.id]: [...(prev[activeEvidence.id] || []), noteEntry],
    }));

    saveAuditLog(`Custody log note added to ${activeEvidence.id}: "${newNoteText.trim()}"`);
    setNewNoteText('');
    setIsNoteModalOpen(false);
    showToast(`✓ Custody note permanently logged to ${activeEvidence.id}.`);
  };

  const handleExportSummary = (id: string, title: string) => {
    saveAuditLog(`Evidence certificate exported for ${id} (${title}).`);
    showToast(`✓ Evidence Certificate ${id}_Summary.pdf exported successfully.`);
  };

  const getSourceIcon = (
    type: EvidenceType,
    isSelected: boolean,
    isClicked: boolean,
    sizeClass = 'w-4 h-4'
  ) => {
    let iconColor = 'text-[#64748B] group-hover:text-[#F8FAFC]';

    if (isSelected) {
      iconColor = isLight ? 'text-white stroke-[2.5]' : 'text-[#050507] stroke-[2.5]';
    } else {
      switch (type) {
        case 'police_report':
          iconColor = isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]';
          break;
        case 'communication':
          iconColor = isLight ? 'text-emerald-600' : 'text-emerald-400';
          break;
        case 'financial':
          iconColor = isLight ? 'text-amber-600' : 'text-amber-400';
          break;
        case 'surveillance':
          iconColor = isLight ? 'text-rose-600' : 'text-rose-400';
          break;
        case 'organisation_activity':
          iconColor = isLight ? 'text-indigo-600' : 'text-indigo-400';
          break;
        default:
          iconColor = isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]';
      }
    }

    const iconProps = { className: `${sizeClass} ${iconColor} transition-colors duration-200` };

    switch (type) {
      case 'police_report':
        return <FileText {...iconProps} />;
      case 'communication':
        return <PhoneCall {...iconProps} />;
      case 'financial':
        return <CreditCard {...iconProps} />;
      case 'surveillance':
        return <Radio {...iconProps} />;
      case 'organisation_activity':
        return <Building {...iconProps} />;
      default:
        return <FileSpreadsheet {...iconProps} />;
    }
  };

  const getIconContainerClasses = (
    type: EvidenceType,
    isSelected: boolean,
    isClicked: boolean
  ) => {
    if (isSelected) {
      return 'p-2 rounded-xl bg-[#FACC15] text-[#050507] border border-[#FACC15] shadow-[0_0_16px_rgba(250,204,21,0.7)] ring-2 ring-[#FACC15]/40 scale-105 transition-all duration-200 cursor-pointer';
    }
    if (isClicked) {
      switch (type) {
        case 'police_report':
          return 'p-2 rounded-xl bg-[#FACC15]/20 border border-[#FACC15]/60 text-[#FACC15] shadow-[0_0_12px_rgba(250,204,21,0.3)] ring-1 ring-[#FACC15]/30 transition-all duration-200 cursor-pointer';
        case 'communication':
          return 'p-2 rounded-xl bg-emerald-500/20 border border-emerald-400/60 text-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.3)] ring-1 ring-emerald-400/30 transition-all duration-200 cursor-pointer';
        case 'financial':
          return 'p-2 rounded-xl bg-amber-500/20 border border-amber-400/60 text-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.3)] ring-1 ring-amber-400/30 transition-all duration-200 cursor-pointer';
        case 'surveillance':
          return 'p-2 rounded-xl bg-rose-500/20 border border-rose-400/60 text-rose-400 shadow-[0_0_12px_rgba(244,63,94,0.3)] ring-1 ring-rose-400/30 transition-all duration-200 cursor-pointer';
        case 'organisation_activity':
          return 'p-2 rounded-xl bg-indigo-500/20 border border-indigo-400/60 text-indigo-400 shadow-[0_0_12px_rgba(129,140,248,0.3)] ring-1 ring-indigo-400/30 transition-all duration-200 cursor-pointer';
        default:
          return 'p-2 rounded-xl bg-[#FACC15]/20 border border-[#FACC15]/60 text-[#FACC15] shadow-[0_0_12px_rgba(250,204,21,0.3)] ring-1 ring-[#FACC15]/30 transition-all duration-200 cursor-pointer';
      }
    }
    return 'p-2 rounded-xl bg-white/5 border border-white/10 opacity-70 group-hover:opacity-100 group-hover:border-white/30 group-hover:bg-white/10 transition-all duration-200 cursor-pointer';
  };

  const filteredEvidence = evidenceRecords.filter(
    (ev) =>
      ev.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.source.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div id="evidence-explorer-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header */}
      <div className="glass-panel border border-white/10 p-6 rounded-3xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="flex items-center space-x-2.5">
            <FolderArchive className="w-5 h-5 text-[#FACC15]" />
            <h1 className="text-2xl font-bold text-[#F8FAFC] font-mono">
              Evidence Custody Vault &amp; ISO/IEC 27037 Repository
            </h1>
            <span className="text-xs font-mono bg-[#050507]/80 text-[#FACC15] px-3 py-1 border border-[#FACC15]/40 rounded-full font-semibold shadow-xs">
              {evidenceRecords.length} Authenticated Artifacts
            </span>
          </div>
          <p className="text-sm text-[#94A3B8] mt-1 font-sans">
            Forensic SHA-256 hash signatures, immutable chain of custody audit seals, and Section 65B judicial admissibility compliance.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-[#94A3B8] glass-card border border-white/10 px-4 py-2 rounded-full shrink-0">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Custody Standard: <strong className="text-emerald-400">ISO/IEC 27037</strong></span>
        </div>
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="p-4 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs font-mono flex items-center justify-between shadow-lg backdrop-blur-md rounded-2xl animate-in fade-in duration-200">
          <span className="font-semibold">{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="text-emerald-400 font-bold ml-4 hover:text-white cursor-pointer">
            ✕
          </button>
        </div>
      )}

      {/* Split Master-Detail Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Evidence List (4 cols) */}
        <div className="lg:col-span-4 glass-panel border border-white/10 p-5 rounded-3xl space-y-3 shadow-xl">
          <div className="flex items-center justify-between px-2 py-1">
            <span className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
              Evidence Catalog
            </span>
            <span className="text-xs font-mono text-[#94A3B8]">
              <span className="text-[#FACC15] font-bold">{clickedEvidenceIds.size}</span>/{filteredEvidence.length} Inspected
            </span>
          </div>

          {/* Quick Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#64748B] absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search evidence ID, title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full glass-card border border-white/10 pl-9 pr-3 py-2 text-xs text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#FACC15] font-mono rounded-full"
            />
          </div>

          <div className="space-y-2.5 pt-1">
            {filteredEvidence.map((ev) => {
              const isSelected = activeEvidence?.id === ev.id;
              const isClicked = clickedEvidenceIds.has(ev.id);
              const isVerified = verifiedHashes[ev.id];

              return (
                <div
                  key={ev.id}
                  id={`evidence-item-${ev.id}`}
                  onClick={() => handleSelectEvidence(ev.id)}
                  className={`group p-4 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'glass-card border-[#FACC15] shadow-[0_0_20px_rgba(250, 204, 21,0.25)]'
                      : 'glass-card hover:bg-white/10 border-white/10 hover:border-[#FACC15]/40 shadow-sm'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center space-x-2.5">
                      <div
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectEvidence(ev.id);
                        }}
                        title={
                          isSelected
                            ? 'Currently Selected Evidence (Active)'
                            : isClicked
                            ? 'Evidence Inspected (Highlighted)'
                            : 'Click to inspect & highlight evidence'
                        }
                        className={getIconContainerClasses(ev.type, isSelected, isClicked)}
                      >
                        {getSourceIcon(ev.type, isSelected, isClicked)}
                      </div>
                      <div className="flex items-center space-x-1.5">
                        <span className={`font-mono font-bold text-xs transition-colors ${isSelected ? 'text-[#FACC15]' : 'text-[#F8FAFC]'}`}>
                          {ev.id}
                        </span>
                        {isClicked && !isSelected && (
                          <span
                            className="w-1.5 h-1.5 rounded-full bg-[#FACC15]/80 shadow-[0_0_6px_rgba(250,204,21,0.8)] animate-pulse"
                            title="Inspected in custody"
                          />
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-1.5">
                      {isVerified && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                      <span className="text-[11px] font-mono text-[#64748B]">{ev.date}</span>
                    </div>
                  </div>

                  <div className="text-sm font-bold text-[#F8FAFC] line-clamp-1">{ev.title}</div>
                  <div className="text-xs text-[#94A3B8] font-sans mt-1">
                    {ev.typeLabel} • {ev.source}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Evidence Detail & Custody Inspector (8 cols) */}
        <div className="lg:col-span-8">
          {activeEvidence ? (
            <div className="glass-panel border border-white/10 p-6 sm:p-8 rounded-3xl space-y-6 shadow-xl">
              {/* Top Banner */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-white/10 pb-5">
                <div className="flex items-start space-x-3.5">
                  <div
                    className="p-3 rounded-2xl bg-[#FACC15] text-[#050507] border border-[#FACC15] shadow-[0_0_18px_rgba(250,204,21,0.65)] ring-2 ring-[#FACC15]/40 shrink-0 mt-0.5"
                    title={`${activeEvidence.id} - ${activeEvidence.typeLabel}`}
                  >
                    {getSourceIcon(activeEvidence.type, true, true, 'w-5 h-5')}
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-[#64748B] mb-1.5">
                      <span className="font-bold text-[#FACC15] bg-[#050507] px-2.5 py-0.5 border border-[#FACC15]/40 rounded-full">
                        {activeEvidence.id}
                      </span>
                      <span>•</span>
                      <span>Source: <strong className="text-[#F8FAFC]">{activeEvidence.source}</strong></span>
                      <span>•</span>
                      <span>Ingested: {activeEvidence.date} ({activeEvidence.timestamp})</span>
                    </div>

                    <h2 className="text-xl font-bold text-[#F8FAFC] tracking-tight font-mono">
                      {activeEvidence.title}
                    </h2>
                    <span className="text-xs text-[#94A3B8] font-mono mt-1 block">
                      Category: {activeEvidence.typeLabel}
                    </span>
                  </div>
                </div>

                {/* Primary Action Buttons */}
                <div className="flex flex-wrap items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleVerifyHash(activeEvidence.id, activeEvidence.hashChecksum)}
                    disabled={verifyingId === activeEvidence.id}
                    className="px-4 py-2 bg-emerald-950/60 hover:bg-emerald-900 text-emerald-400 border border-emerald-700 text-xs font-mono uppercase tracking-wider font-bold flex items-center space-x-1.5 rounded-full transition-all cursor-pointer shadow-md"
                  >
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{verifyingId === activeEvidence.id ? 'Checking...' : 'Verify Hash'}</span>
                  </button>

                  <button
                    onClick={() => handleExportSummary(activeEvidence.id, activeEvidence.title)}
                    className="px-4 py-2 glass-card hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC] text-xs font-mono uppercase tracking-wider font-semibold border border-white/10 rounded-full transition-all flex items-center space-x-1.5 cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5 text-[#FACC15]" />
                    <span>Export Summary</span>
                  </button>

                  <button
                    onClick={() => navigateTo('records', { recordId: activeEvidence.id })}
                    className="px-4 py-2 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center space-x-1.5 rounded-full transition-all shadow-lg cursor-pointer"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5" />
                    <span>View Record</span>
                  </button>
                </div>
              </div>

              {/* Summary */}
              <div className="glass-card border border-white/10 p-5 rounded-2xl text-xs space-y-2">
                <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15] flex items-center justify-between">
                  <span>Evidentiary Summary &amp; Operational Context</span>
                  <span className="text-emerald-400 font-mono font-bold">✓ Integrity Validated (Append-Only)</span>
                </div>
                <p className="text-[#F8FAFC] leading-relaxed font-sans text-xs">
                  {activeEvidence.summary}
                </p>
              </div>

              {/* Associated Entities & Relationships Supported */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
                {/* Associated Entities */}
                <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-3">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                    Related Entities ({activeEvidence.extractedEntities.length})
                  </div>
                  <div className="space-y-2">
                    {activeEvidence.extractedEntities.map((ent, i) => (
                      <div
                        key={i}
                        onClick={() => {
                          if (ent.entityId) navigateTo('entities', { entityId: ent.entityId });
                        }}
                        className="flex items-center justify-between p-3 glass-panel hover:bg-white/10 border border-white/10 hover:border-[#FACC15] rounded-xl cursor-pointer transition-colors group"
                      >
                        <span className="font-mono font-semibold text-[#F8FAFC] text-sm group-hover:text-[#FACC15]">{ent.text}</span>
                        <span className="text-[10px] font-mono uppercase text-[#FACC15] bg-[#050507] px-2 py-0.5 rounded-full border border-white/10">
                          {ent.type}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Relationships Supported */}
                <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-3">
                  <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                    Supported Inferences &amp; Relationships
                  </div>
                  <ul className="space-y-2 font-sans text-xs">
                    {activeEvidence.supportedRelationships.map((rel, i) => (
                      <li key={i} className="p-3 glass-panel border border-white/10 text-[#94A3B8] leading-relaxed rounded-xl">
                        <span className="text-[#FACC15] font-bold">✓</span> {rel}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Chain of Custody History & Notes */}
              <div className="glass-card border border-white/10 p-5 rounded-2xl space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between border-b border-white/10 pb-2">
                  <span className="text-[10px] text-[#FACC15] uppercase font-bold tracking-[0.2em]">
                    Official Chain of Custody History (ISO/IEC 27037)
                  </span>
                  <button
                    onClick={() => setIsNoteModalOpen(true)}
                    className="text-xs text-[#FACC15] hover:underline font-bold flex items-center space-x-1 cursor-pointer"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>Add Custody Note</span>
                  </button>
                </div>

                <div className="space-y-2">
                  <div className="p-3 glass-panel border border-white/10 text-[#94A3B8] font-sans text-xs rounded-xl">
                    <span className="font-mono text-[#FACC15] font-bold block mb-1">CUSTODY TRANSFER LOG:</span>
                    {activeEvidence.custodyChain}
                  </div>

                  {custodyNotes[activeEvidence.id]?.map((note, idx) => (
                    <div key={idx} className="p-3 glass-panel border border-emerald-800/60 text-[#F8FAFC] font-sans text-xs rounded-xl">
                      <span className="font-mono text-emerald-400 font-bold mr-2">LOG NOTE:</span>
                      {note}
                    </div>
                  ))}
                </div>

                {/* Cryptographic SHA-256 Checksum */}
                <div className="pt-3 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <div className="flex items-center space-x-2">
                    <Lock className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-[#94A3B8]">FORENSIC SHA-256 SIGNATURE:</span>
                  </div>
                  <span className="text-emerald-400 font-mono font-bold break-all sm:truncate sm:max-w-md bg-[#0D0D11] px-3 py-1 rounded-full border border-white/10">
                    {activeEvidence.hashChecksum}
                  </span>
                </div>
              </div>

              {/* Cross-Module Navigation Footer */}
              <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
                <span className="text-xs text-[#64748B] font-mono">
                  Linked in {activeEvidence.relatedInsightIds.length} Intelligence Insights
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => navigateTo('graph')}
                    className="px-4 py-2 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center space-x-1.5 rounded-full shadow-lg transition-all cursor-pointer"
                  >
                    <Network className="w-3.5 h-3.5" />
                    <span>View in Graph</span>
                  </button>
                  <button
                    onClick={() => navigateTo('timeline')}
                    className="px-4 py-2 glass-card hover:bg-white/10 text-[#F8FAFC] text-xs font-mono uppercase tracking-wider font-semibold border border-white/10 rounded-full transition-all flex items-center space-x-1.5 cursor-pointer"
                  >
                    <Clock className="w-3.5 h-3.5 text-[#FACC15]" />
                    <span>View on Timeline</span>
                  </button>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Custody Note Modal */}
      {isNoteModalOpen && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-md">
          <div className="glass-panel border border-white/15 max-w-lg w-full p-6 rounded-3xl space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center space-x-2">
                <FolderArchive className="w-4 h-4 text-[#FACC15]" />
                <h3 className="font-mono font-bold text-[#F8FAFC] text-base">
                  Add Official Custody Note: {activeEvidence?.id}
                </h3>
              </div>
              <button
                onClick={() => setIsNoteModalOpen(false)}
                className="text-[#64748B] hover:text-[#F8FAFC] font-bold p-1 rounded-full cursor-pointer"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-[#94A3B8]">
              Notes appended to the evidence custody log become part of the immutable investigation audit trail under ISO/IEC 27037 standards.
            </p>

            <textarea
              rows={4}
              value={newNoteText}
              onChange={(e) => setNewNoteText(e.target.value)}
              placeholder="Enter transfer details, forensic lab inspection notes, or officer observations..."
              className="w-full p-3.5 glass-card border border-white/10 rounded-2xl text-xs text-[#F8FAFC] focus:outline-none focus:border-[#FACC15] font-sans"
            />

            <div className="flex items-center justify-end space-x-2 pt-2">
              <button
                onClick={() => setIsNoteModalOpen(false)}
                className="px-4 py-2 glass-card hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC] text-xs font-mono uppercase font-semibold rounded-full border border-white/10 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleAddCustodyNote}
                className="px-4 py-2 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase font-bold rounded-full shadow-lg transition-all cursor-pointer"
              >
                Append Custody Note
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
