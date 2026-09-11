import React, { useState, useMemo, useEffect, useRef } from 'react';
import {
  Search,
  X,
  FileSpreadsheet,
  CreditCard,
  Phone,
  MapPin,
  Building,
  User,
  ArrowRight,
  Shield,
  Car,
  Clock,
  Sparkles,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { EntityType } from '../../types';

export const GlobalSearchModal: React.FC = () => {
  const {
    isSearchOpen,
    setIsSearchOpen,
    entities,
    evidenceRecords,
    navigateTo,
    setSelectedEntityId,
    setSelectedRecordId,
  } = useInvestigation();

  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isSearchOpen) {
      setTimeout(() => inputRef.current?.focus(), 60);
    }
  }, [isSearchOpen]);

  // Global Keyboard shortcut Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen(!isSearchOpen);
      }
      if (e.key === 'Escape' && isSearchOpen) {
        setIsSearchOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isSearchOpen, setIsSearchOpen]);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) {
      return {
        entities: entities.slice(0, 6),
        records: evidenceRecords.slice(0, 4),
      };
    }

    const matchedEntities = entities.filter(
      (e) =>
        e.name.toLowerCase().includes(q) ||
        (e.role && e.role.toLowerCase().includes(q)) ||
        (e.identifier && e.identifier.toLowerCase().includes(q)) ||
        e.type.toLowerCase().includes(q)
    );

    const matchedRecords = evidenceRecords.filter(
      (r) =>
        r.id.toLowerCase().includes(q) ||
        r.title.toLowerCase().includes(q) ||
        r.summary.toLowerCase().includes(q) ||
        r.source.toLowerCase().includes(q)
    );

    return {
      entities: matchedEntities,
      records: matchedRecords,
    };
  }, [query, entities, evidenceRecords]);

  const getEntityIcon = (type: EntityType) => {
    switch (type) {
      case 'person':
        return <User className="w-4 h-4 text-[#FACC15]" />;
      case 'phone':
        return <Phone className="w-4 h-4 text-[#10B981]" />;
      case 'account':
        return <CreditCard className="w-4 h-4 text-[#F59E0B]" />;
      case 'location':
        return <MapPin className="w-4 h-4 text-[#EF4444]" />;
      case 'organisation':
        return <Building className="w-4 h-4 text-[#A855F7]" />;
      case 'vehicle':
        return <Car className="w-4 h-4 text-[#EC4899]" />;
      default:
        return <Clock className="w-4 h-4 text-[#64748B]" />;
    }
  };

  if (!isSearchOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 bg-[#050507]/85 backdrop-blur-xs flex items-start justify-center pt-20 px-4"
      onClick={() => setIsSearchOpen(false)}
    >
      <div
        className="w-full max-w-2xl bg-[#0E0E12] border border-white/10 shadow-2xl rounded-2xl overflow-hidden flex flex-col max-h-[80vh] text-[#F8FAFC]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-white/10 bg-[#050507]/60">
          <Search className="w-4 h-4 text-[#FACC15] shrink-0 mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search all 15 indexed entities, evidence records, phone IMEIs, or accounts (e.g. Rahul, 889922, EV-001)..."
            className="flex-1 bg-transparent border-none text-xs font-mono text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:ring-0"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="p-1 text-[#64748B] hover:text-[#F8FAFC]"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <kbd className="hidden sm:inline font-mono text-[9px] bg-[#18181C] px-1.5 py-0.5 border border-white/10 rounded-xs text-[#64748B] ml-2">
            ESC
          </kbd>
        </div>

        {/* Results Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Entities Section */}
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] font-bold mb-2 flex items-center justify-between">
              <span>Indexed Entities ({results.entities.length})</span>
              <span className="text-[#FACC15]">OPERATION NEXUS</span>
            </div>

            {results.entities.length === 0 ? (
              <div className="p-3 text-center text-xs font-mono text-[#64748B] bg-[#050507] rounded-xl border border-white/10">
                No matching identities found.
              </div>
            ) : (
              <div className="space-y-1.5">
                {results.entities.map((e) => (
                  <div
                    key={e.id}
                    onClick={() => {
                      setSelectedEntityId(e.id);
                      navigateTo('entities');
                      setIsSearchOpen(false);
                    }}
                    className="p-2.5 bg-[#050507] hover:bg-[#18181C] border border-white/10 hover:border-[#FACC15]/40 rounded-xl flex items-center justify-between cursor-pointer transition-colors group"
                  >
                    <div className="flex items-center space-x-3 min-w-0">
                      <div className="p-1.5 bg-[#141418] rounded-xl border border-white/10">
                        {getEntityIcon(e.type)}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-xs text-[#F8FAFC] group-hover:text-[#FACC15] transition-colors truncate">
                            {e.name}
                          </span>
                          <span className="text-[9px] font-mono px-1.5 py-0.2 bg-[#141418] text-[#64748B] border border-white/10 uppercase rounded-full">
                            {e.type}
                          </span>
                          {e.risk === 'high' && (
                            <span className="text-[9px] font-mono px-1.5 py-0.2 bg-[#EF4444]/15 text-[#EF4444] border border-[#EF4444]/30 font-semibold rounded-full">
                              HIGH RISK
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-[#94A3B8] truncate mt-0.5">
                          {e.role || e.identifier || 'Operation Nexus Entity'}
                        </div>
                      </div>
                    </div>

                    <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:text-[#FACC15] shrink-0 ml-2" />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Records Section */}
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] font-bold mb-2 flex items-center justify-between">
              <span>Forensic Evidence Records ({results.records.length})</span>
              <span className="text-[#10B981]">SHA-256 LEDGER</span>
            </div>

            {results.records.length === 0 ? (
              <div className="p-3 text-center text-xs font-mono text-[#64748B] bg-[#050507] rounded-xl border border-white/10">
                No matching evidence documents found.
              </div>
            ) : (
              <div className="space-y-1.5">
                {results.records.map((r) => (
                  <div
                    key={r.id}
                    onClick={() => {
                      setSelectedRecordId(r.id);
                      navigateTo('records');
                      setIsSearchOpen(false);
                    }}
                    className="p-2.5 bg-[#050507] hover:bg-[#18181C] border border-white/10 hover:border-[#FACC15]/40 rounded-xl flex items-center justify-between cursor-pointer transition-colors group"
                  >
                    <div className="flex items-center space-x-3 min-w-0">
                      <div className="p-1.5 bg-[#141418] rounded-xl border border-white/10">
                        <FileSpreadsheet className="w-4 h-4 text-[#FACC15]" />
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-bold text-[#FACC15]">{r.id}</span>
                          <span className="text-xs text-[#F8FAFC] truncate font-medium">{r.title}</span>
                        </div>
                        <div className="text-[11px] text-[#64748B] font-mono truncate mt-0.5">
                          Source: {r.source} • Status: {r.status}
                        </div>
                      </div>
                    </div>

                    <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:text-[#FACC15] shrink-0 ml-2" />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 bg-[#050507] border-t border-white/10 flex items-center justify-between text-[10px] font-mono text-[#64748B]">
          <span>Tip: Press [Ctrl+K] anytime to search</span>
          <span>15 Entities • 9 Evidence Records</span>
        </div>
      </div>
    </div>
  );
};
