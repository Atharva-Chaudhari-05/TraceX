import React, { useState } from 'react';
import {
  Users,
  Search,
  Phone,
  CreditCard,
  MapPin,
  Building,
  Clock,
  Network,
  ExternalLink,
  ChevronRight,
  Car,
  ShieldAlert,
  GitPullRequest,
  CheckCircle2,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { EntityType } from '../../types';

export const EntityExplorerView: React.FC = () => {
  const {
    entities,
    selectedEntityId,
    setSelectedEntityId,
    selectedEntity,
    navigateTo,
    evidenceRecords,
    theme,
    caseData,
  } = useInvestigation();

  const isLight = theme === 'light';

  const [activeTypeFilter, setActiveTypeFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filterTabs: { id: string; label: string; type?: EntityType }[] = [
    { id: 'all', label: 'All Entities' },
    { id: 'person', label: 'People', type: 'person' },
    { id: 'phone', label: 'Phones', type: 'phone' },
    { id: 'account', label: 'Accounts', type: 'account' },
    { id: 'organisation', label: 'Organisations', type: 'organisation' },
    { id: 'location', label: 'Locations', type: 'location' },
    { id: 'vehicle', label: 'Vehicles', type: 'vehicle' },
  ];

  const filteredEntities = entities.filter((ent) => {
    const matchesType =
      activeTypeFilter === 'all' ? true : ent.type === activeTypeFilter;

    const matchesSearch =
      ent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (ent.role && ent.role.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (ent.identifier && ent.identifier.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesType && matchesSearch;
  });

  const activeEntity = selectedEntity || entities[0];

  const getEntityIcon = (type: EntityType) => {
    switch (type) {
      case 'person':
        return <Users className="w-4 h-4 text-[#FACC15]" />;
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
      case 'event':
        return <Clock className="w-4 h-4 text-[#64748B]" />;
      default:
        return <Users className="w-4 h-4 text-[#94A3B8]" />;
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'high':
        return (
          <span className="text-[10px] font-semibold font-mono px-2.5 py-0.5 bg-[#EF4444]/15 text-[#EF4444] border border-[#EF4444]/40 rounded-full whitespace-nowrap inline-flex items-center justify-center">
            HIGH RISK
          </span>
        );
      case 'medium':
        return (
          <span className="text-[10px] font-semibold font-mono px-2.5 py-0.5 bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/40 rounded-full whitespace-nowrap inline-flex items-center justify-center">
            MEDIUM
          </span>
        );
      case 'low':
        return (
          <span className="text-[10px] font-semibold font-mono px-2.5 py-0.5 bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/40 rounded-full whitespace-nowrap inline-flex items-center justify-center">
            LOW RISK
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-mono px-2.5 py-0.5 bg-[#050507] text-[#64748B] border border-white/10 rounded-full whitespace-nowrap inline-flex items-center justify-center">
            INFO
          </span>
        );
    }
  };

  return (
    <div id="entity-explorer-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header & Filter Bar */}
      <div className="glass-panel border border-white/10 p-6 md:p-8 rounded-3xl shadow-2xl backdrop-blur-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-[10px] uppercase tracking-[0.25em] text-[#FACC15] font-mono mb-1 font-bold">
            Master Entity Directory • {caseData?.name || 'Active Case'}
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#F8FAFC] flex items-center space-x-3 tracking-tight">
            <span>Entity Explorer</span>
            <span className="text-xs font-mono bg-[#050507]/80 text-[#FACC15] px-3 py-0.5 border border-[#FACC15]/40 rounded-full">
              {filteredEntities.length} / {entities.length} Indexed
            </span>
          </h1>
          <p className="text-xs text-[#94A3B8] mt-1">
            Master directory of all {entities.length} indexed identities across field surveillance, lawful telephony intercepts, core banking SFMS wires, and corporate filings.
          </p>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-[#FACC15] absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search entity name, role, ID..."
            className="pl-9 pr-4 py-2 text-xs glass-card border border-white/10 focus:border-[#FACC15] text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none w-72 font-mono rounded-full"
          />
        </div>
      </div>

      {/* Type Filter Pills - Clean Wrap, No Scrollbars */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTypeFilter(tab.id)}
            className={`px-4 py-1.5 font-mono text-xs uppercase tracking-wider transition-all whitespace-nowrap rounded-full border cursor-pointer ${
              activeTypeFilter === tab.id
                ? 'bg-[#FACC15] text-[#050507] border-[#FACC15] font-bold shadow-md'
                : 'glass-card text-[#94A3B8] hover:text-[#F8FAFC] border-white/10 hover:border-white/20'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Grid: Entity Table (7-8 cols) + Entity Detail Inspector (4-5 cols) - Resized & Perfectly Aligned */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Entity Table Window (Resized with exact column alignment) */}
        <div className="lg:col-span-7 xl:col-span-8 glass-panel border border-white/10 rounded-3xl shadow-2xl backdrop-blur-xl overflow-hidden">
          <div className="w-full">
            <table className="w-full text-left text-xs table-auto">
              <thead className="bg-[#050507]/80 border-b border-white/10 text-[10px] font-mono uppercase tracking-[0.15em] text-[#64748B]">
                <tr>
                  <th className="py-3.5 px-4 w-[34%]">Entity</th>
                  <th className="py-3.5 px-3 w-[15%]">Type</th>
                  <th className="py-3.5 px-3 w-[15%]">Connections</th>
                  <th className="py-3.5 px-3 w-[20%]">Risk Level</th>
                  <th className="py-3.5 px-4 w-[16%] text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono">
                {filteredEntities.map((ent) => {
                  const isSelected = activeEntity?.id === ent.id;
                  return (
                    <tr
                      key={ent.id}
                      onClick={() => setSelectedEntityId(ent.id)}
                      className={`hover:bg-white/5 cursor-pointer transition-colors ${
                        isSelected ? 'bg-white/10 border-l-2 border-[#FACC15]' : ''
                      }`}
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-xl shrink-0 border ${isLight ? 'bg-[#F8FAFC] border-[#CBD5E1] shadow-sm' : 'bg-[#050507] border-white/10'}`}>
                            {getEntityIcon(ent.type)}
                          </div>
                          <div>
                            <div className="font-bold text-xs text-[#F8FAFC] flex items-center space-x-2">
                              <span>{ent.name}</span>
                              {ent.isResolvedDuplicate && (
                                <span className="text-[9px] bg-[#F59E0B]/15 text-[#F59E0B] px-2 py-0.2 border border-dashed border-[#F59E0B] font-mono rounded-full">
                                  Resolved Match
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] text-[#94A3B8] font-sans truncate max-w-[220px] mt-0.5">
                              {ent.role || ent.identifier}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-[10px] uppercase font-mono tracking-wider px-2.5 py-0.5 bg-[#050507] text-[#F8FAFC] border border-white/10 rounded-full">
                          {ent.type}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-xs text-[#FACC15]">
                        {ent.connectionsCount} links
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap">
                        {getRiskBadge(ent.risk)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedEntityId(ent.id);
                          }}
                          className={`text-xs uppercase font-mono px-4 py-1.5 border rounded-full transition-all cursor-pointer font-bold inline-flex items-center justify-center ${
                            isSelected
                              ? 'bg-[#FACC15] text-[#050507] border-[#FACC15] shadow-sm shadow-[#FACC15]/30'
                              : 'bg-[#050507] hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC] border-white/10'
                          }`}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Entity Detail Inspector Window (Resized with balanced sticky card) */}
        <div className="lg:col-span-5 xl:col-span-4">
          {activeEntity ? (
            <div className="glass-panel border border-white/10 p-6 rounded-3xl shadow-2xl backdrop-blur-xl space-y-6 sticky top-4">
              {/* Header */}
              <div className="flex items-start justify-between border-b border-white/10 pb-4">
                <div className="flex items-center space-x-3.5">
                  <div className={`p-3 rounded-2xl border ${isLight ? 'bg-[#F8FAFC] border-[#CBD5E1] shadow-sm' : 'bg-[#050507] border-white/10'}`}>
                    {getEntityIcon(activeEntity.type)}
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-[#F8FAFC]">
                      {activeEntity.name}
                    </h2>
                    <div className="flex items-center space-x-2 mt-1 font-mono">
                      <span className="text-[10px] uppercase tracking-wider px-2.5 py-0.5 bg-[#050507] text-[#FACC15] border border-[#FACC15]/40 rounded-full font-semibold">
                        {activeEntity.type}
                      </span>
                      {activeEntity.identifier && (
                        <span className="text-[11px] text-[#64748B]">
                          ID: {activeEntity.identifier}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  {getRiskBadge(activeEntity.risk)}
                </div>
              </div>

              {/* Role & Operational Notes */}
              <div className="space-y-2">
                <div className="text-[10px] font-mono text-[#64748B] uppercase tracking-wider font-bold">
                  Operational Role & Assessment
                </div>
                <div className="p-3.5 bg-[#050507]/80 border border-white/10 rounded-xl text-xs font-sans text-[#94A3B8] leading-relaxed">
                  <div className="font-bold text-[#F8FAFC] mb-1 font-mono text-xs">{activeEntity.role}</div>
                  {activeEntity.notes || 'No adverse remarks recorded.'}
                </div>
              </div>

              {/* Metadata Key-Value List */}
              {activeEntity.metadata && Object.keys(activeEntity.metadata).length > 0 && (
                <div className="space-y-2">
                  <div className="text-[10px] font-mono text-[#64748B] uppercase tracking-wider font-bold">
                    Forensic Identifiers
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
                    {Object.entries(activeEntity.metadata).map(([k, v]) => (
                      <div key={k} className="p-2.5 bg-[#050507]/80 border border-white/10 rounded-xl">
                        <span className="text-[10px] text-[#64748B] block uppercase tracking-wider">{k}</span>
                        <span className="font-bold text-[#F8FAFC] text-xs mt-0.5 block truncate">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="pt-2 flex items-center space-x-2.5">
                <button
                  type="button"
                  onClick={() => navigateTo('graph')}
                  className="flex-1 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono font-bold rounded-full flex items-center justify-center space-x-1.5 transition-all shadow-md cursor-pointer"
                >
                  <Network className="w-3.5 h-3.5" />
                  <span>Inspect in 2D Graph</span>
                </button>
                <button
                  type="button"
                  onClick={() => navigateTo('path')}
                  className="py-2.5 px-4 glass-card hover:bg-white/10 text-[#FACC15] border border-white/15 text-xs font-mono rounded-full flex items-center space-x-1.5 transition-all cursor-pointer"
                  title="Trace Path to Target"
                >
                  <GitPullRequest className="w-3.5 h-3.5" />
                  <span>Trace Path</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center glass-card border border-white/10 rounded-2xl text-[#64748B] text-xs font-mono">
              Select an entity to inspect forensic dossier.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
