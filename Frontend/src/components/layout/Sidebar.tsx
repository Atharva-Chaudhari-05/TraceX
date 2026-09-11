import React, { useState, useRef, useEffect } from 'react';
import {
  LayoutDashboard,
  Database,
  FileSpreadsheet,
  Users,
  GitMerge,
  Network,
  GitPullRequest,
  Activity,
  Clock,
  Sparkles,
  Layers,
  ShieldCheck,
  FileText,
  Terminal,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  ChevronsUpDown,
  AlertTriangle,
  Check,
  FolderGit2,
  Menu,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { ViewType } from '../../types';

interface NavItem {
  id: ViewType;
  label: string;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  badge?: string | number;
  badgeColor?: 'cyan' | 'amber' | 'emerald' | 'rose' | 'muted';
  provenance?: 'source' | 'synthetic';
}

interface NavGroup {
  groupName: string;
  items: NavItem[];
}

export const Sidebar: React.FC = () => {
  const {
    currentView,
    navigateTo,
    entityMatch,
    aiInsights,
    currentCaseId,
    switchCase,
    currentUser,
    isSidebarOpen,
    setIsSidebarOpen,
    toggleSidebar,
    theme,
    cases,
    entities,
    timelineEvents,
    evidenceRecords,
  } = useInvestigation();
  const isLight = theme === 'light';

  // Dropdown states inside the sidebar
  const [isProvenanceOpen, setIsProvenanceOpen] = useState(true);
  const [isCaseDropdownOpen, setIsCaseDropdownOpen] = useState(false);
  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({});
  const caseDropdownRef = useRef<HTMLDivElement>(null);

  // Available investigation operations for the case selector
  const availableCases = cases.map(c => ({
    id: c.id,
    name: c.payload?.title || c.payload?.name || c.id,
    shortName: c.payload?.title || c.payload?.name || c.id,
    status: c.payload?.status || 'ACTIVE',
    lead: c.payload?.leadOfficer || 'Unassigned',
    command: c.payload?.jurisdiction || c.payload?.agency || 'General Jurisdiction',
  }));

  const activeCase = availableCases.find((c) => c.id === currentCaseId) || availableCases[0] || {
    id: 'NONE',
    name: 'No Active Case',
    shortName: 'No Active Case',
    status: 'UNKNOWN',
    lead: 'Unassigned',
    command: 'None',
  };

  // Close case dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (caseDropdownRef.current && !caseDropdownRef.current.contains(e.target as Node)) {
        setIsCaseDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isPendingMatch = entityMatch.status === 'pending';
  const unverifiedInsightsCount = aiInsights.filter((i) => i.status === 'AI-Generated').length;

  const navGroups: NavGroup[] = [
    {
      groupName: 'OPERATIONAL CASE',
      items: [
        {
          id: 'overview',
          label: 'Case Overview',
          icon: LayoutDashboard,
        },
        {
          id: 'sources',
          label: 'Data Sources',
          icon: Database,
          badge: 'Active',
          badgeColor: 'cyan',
        },
        {
          id: 'records',
          label: 'Investigation Records',
          icon: FileSpreadsheet,
          badge: evidenceRecords.length > 0 ? `${evidenceRecords.length} Docs` : undefined,
          badgeColor: 'muted',
        },
      ],
    },
    {
      groupName: 'NETWORK & GRAPH',
      items: [
        {
          id: 'entities',
          label: 'Entity Explorer',
          icon: Users,
          badge: entities.length > 0 ? `${entities.length} Nodes` : undefined,
          badgeColor: 'muted',
        },
        {
          id: 'resolution',
          label: 'Entity Resolution',
          icon: GitMerge,
          badge: isPendingMatch ? 'Pending' : 'Resolved',
          badgeColor: isPendingMatch ? 'amber' : 'emerald',
          provenance: 'synthetic',
        },
        {
          id: 'graph',
          label: 'Investigation Graph',
          icon: Network,
        },
        {
          id: 'path',
          label: 'Path Explorer',
          icon: GitPullRequest,
          badgeColor: 'emerald',
        },
        {
          id: 'patterns',
          label: 'Pattern Analysis',
          icon: Activity,
        },
      ],
    },
    {
      groupName: 'INTELLIGENCE & TIMELINE',
      items: [
        {
          id: 'timeline',
          label: 'Event Timeline',
          icon: Clock,
          badge: timelineEvents.length > 0 ? `${timelineEvents.length} Events` : undefined,
          badgeColor: 'muted',
        },
        {
          id: 'insights',
          label: 'AI Insights',
          icon: Sparkles,
          badge: unverifiedInsightsCount > 0 ? `${unverifiedInsightsCount} New` : undefined,
          badgeColor: 'amber',
          provenance: 'synthetic',
        },
        {
          id: 'analytics',
          label: 'Cross-Case Analytics',
          icon: Layers,
          badge: `${cases.length} Cases`,
          badgeColor: 'cyan',
        },
      ],
    },
    {
      groupName: 'FORENSICS & LEGAL',
      items: [
        {
          id: 'evidence',
          label: 'Evidence Custody',
          icon: ShieldCheck,
        },
        {
          id: 'reports',
          label: 'Court-Ready Report',
          icon: FileText,
        },
        ...(currentUser?.role === 'System Administrator'
          ? [
              {
                id: 'audit',
                label: 'Audit Logs',
                icon: Terminal,
              } as NavItem,
            ]
          : []),
      ],
    },
  ];

  const toggleGroup = (groupName: string) => {
    setCollapsedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }));
  };

  const allCollapsed = navGroups.every((g) => collapsedGroups[g.groupName]);

  const toggleAllGroups = () => {
    if (allCollapsed) {
      setCollapsedGroups({});
    } else {
      const next: Record<string, boolean> = {};
      navGroups.forEach((g) => {
        next[g.groupName] = true;
      });
      setCollapsedGroups(next);
    }
  };

  const getBadgeStyle = (color?: string) => {
    if (isLight) {
      switch (color) {
        case 'amber':
        case 'cyan':
        case 'yellow':
          return 'bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]';
        case 'emerald':
          return 'bg-emerald-50 text-emerald-700 border-emerald-200';
        case 'rose':
          return 'bg-rose-50 text-rose-700 border-rose-200';
        default:
          return 'bg-slate-100 text-[#475569] border-slate-200';
      }
    }
    switch (color) {
      case 'amber':
        return 'bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/40';
      case 'emerald':
        return 'bg-[#10B981]/20 text-[#10B981] border-[#10B981]/40';
      case 'rose':
        return 'bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/40';
      case 'cyan':
      case 'yellow':
        return 'bg-[#FACC15]/20 text-[#FACC15] border-[#FACC15]/40';
      default:
        return 'bg-[#18181C]/80 text-[#94A3B8] border-white/10';
    }
  };

  // When clicking any module: navigate, but DO NOT close the sidebar (stays open like Instagram)
  const handleSelectView = (viewId: ViewType) => {
    navigateTo(viewId);
  };

  // If sidebar is CLOSED: render ONLY the 3-lines hamburger button (☰) positioned at the top-left
  if (!isSidebarOpen) {
    return (
      <div className="absolute left-3.5 top-3.5 z-40">
        <button
          type="button"
          id="sidebar-toggle-hamburger"
          onClick={() => toggleSidebar()}
          className={`p-2.5 rounded-xl border backdrop-blur-md transition-all cursor-pointer hover:scale-105 active:scale-95 group flex items-center justify-center shadow-lg ${
            isLight
              ? 'bg-white/95 hover:bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE] hover:border-[#4F46E5]'
              : 'bg-[#0e0e13]/95 hover:bg-[#1c1c24] text-[#FACC15] border-[#FACC15]/40 hover:border-[#FACC15] shadow-[0_4px_20px_rgba(0,0,0,0.8)]'
          }`}
          title="Open Navigation Menu (☰)"
          aria-label="Open Navigation Menu"
        >
          <Menu className={`w-5 h-5 group-hover:rotate-90 transition-transform duration-200 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
        </button>
      </div>
    );
  }

  // If sidebar is OPEN: render the full sidebar in the document flow, pushing the main window to the right
  return (
    <aside
      id="tactical-navigation-sidebar"
      className={`w-72 border-r flex flex-col h-full shrink-0 select-none z-30 transition-all duration-300 ease-in-out overflow-hidden ${
        isLight ? 'bg-white border-slate-200' : 'bg-[#09090D] border-white/10'
      }`}
    >
      {/* Top Header Bar with ONLY 3-lines icon button to close the sidebar */}
      <div
        className={`p-3.5 pb-2.5 border-b flex items-center justify-between shrink-0 ${
          isLight ? 'bg-white border-slate-200' : 'bg-[#111116] border-white/10'
        }`}
      >
        <div className="flex items-center space-x-2.5">
          <button
            type="button"
            id="sidebar-close-hamburger"
            onClick={() => toggleSidebar()}
            className={`p-2 rounded-xl border transition-all cursor-pointer group ${
              isLight
                ? 'bg-slate-100 hover:bg-[#EEF2FF] text-[#4F46E5] border-slate-200 hover:border-[#C7D2FE]'
                : 'bg-white/5 hover:bg-[#FACC15]/20 text-[#FACC15] border-white/10 hover:border-[#FACC15]/40'
            }`}
            title="Close Navigation Menu (☰)"
          >
            <Menu className={`w-5 h-5 group-hover:rotate-90 transition-transform duration-200 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
          </button>
          <span className={`text-xs font-mono font-bold tracking-wider uppercase ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>
            Navigation
          </span>
        </div>
      </div>

      {/* Highlighted Operational & Provenance Card with Dropdown Toggle */}
      <div className={`p-3 pb-1 shrink-0 ${isLight ? 'bg-white' : 'bg-[#09090D]'}`}>
        <div
          className={`rounded-2xl p-3 border space-y-2.5 shadow-sm transition-all ${
            isLight ? 'bg-[#F8FAFC] border-[#C7D2FE]' : 'bg-[#121218] border-[#FACC15]/30 shadow-lg'
          }`}
        >
          {/* Dropdown Header Toggle */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setIsProvenanceOpen((prev) => !prev)}
              className="flex items-center space-x-1.5 text-left group cursor-pointer"
              title={isProvenanceOpen ? 'Collapse Intelligence Panel' : 'Expand Intelligence Panel'}
            >
              <Layers className={`w-3.5 h-3.5 shrink-0 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
              <span className={`text-[10px] font-mono font-bold uppercase tracking-wider transition-colors ${
                isLight ? 'text-[#4F46E5] group-hover:text-[#4338CA]' : 'text-[#FACC15] group-hover:text-white'
              }`}>
                Operational Intel
              </span>
            </button>

            <button
              type="button"
              onClick={() => setIsProvenanceOpen((prev) => !prev)}
              className={`flex items-center space-x-1 px-2 py-0.5 rounded-md text-[9px] font-mono transition-all cursor-pointer ${
                isLight
                  ? 'bg-slate-200/70 hover:bg-[#EEF2FF] text-[#475569] hover:text-[#4F46E5]'
                  : 'bg-white/5 hover:bg-[#FACC15]/20 text-[#94A3B8] hover:text-[#FACC15]'
              }`}
              title={isProvenanceOpen ? 'Collapse panel' : 'Expand panel'}
            >
              <span>{isProvenanceOpen ? 'Collapse' : 'Expand'}</span>
              <ChevronDown
                className={`w-3 h-3 transition-transform duration-200 ${
                  isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'
                } ${isProvenanceOpen ? 'rotate-180' : 'rotate-0'}`}
              />
            </button>
          </div>

          {/* Collapsed State: Compact Single-Line Bar */}
          {!isProvenanceOpen ? (
            <div
              onClick={() => setIsProvenanceOpen(true)}
              className="pt-1 flex items-center justify-between text-[10px] font-mono text-[#94A3B8] cursor-pointer hover:text-[#F8FAFC] transition-colors"
              title="Click to expand operational provenance details"
            >
              <div className="flex items-center space-x-1.5 truncate">
                <span className="text-[#10B981] font-bold">82% Src</span>
                <span className="text-[#64748B]">/</span>
                <span className="text-[#FACC15] font-bold">18% AI</span>
              </div>
              <span className="text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded-full border border-amber-800/40 text-[9px] font-bold shrink-0">
                2 Alerts
              </span>
            </div>
          ) : (
            /* Expanded State: Active Case Dropdown Selector + Evidentiary Provenance Split + Attention items */
            <div className="space-y-3 pt-0.5">
              {/* Active Case Dropdown Selector */}
              <div className="relative" ref={caseDropdownRef}>
                <button
                  type="button"
                  onClick={() => setIsCaseDropdownOpen((prev) => !prev)}
                  className={`w-full flex items-center justify-between p-2 rounded-xl text-left transition-all cursor-pointer group ${
                    isLight
                      ? 'bg-white border border-slate-200/80 hover:border-indigo-400 shadow-xs'
                      : 'bg-[#09090D] border border-white/10 hover:border-[#FACC15]/50 shadow-inner'
                  }`}
                  title="Click to switch active case context"
                >
                  <div className="min-w-0 pr-2">
                    <div className="text-[9px] font-mono uppercase tracking-wider flex items-center space-x-1">
                      <FolderGit2 className={`w-2.5 h-2.5 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
                      <span className={isLight ? 'text-slate-500' : 'text-[#64748B]'}>Active Case</span>
                    </div>
                    <div className={`text-[11px] font-mono font-bold truncate transition-colors ${
                      isLight
                        ? 'text-slate-900 group-hover:text-[#4F46E5]'
                        : 'text-[#F8FAFC] group-hover:text-[#FACC15]'
                    }`}>
                      {activeCase.shortName}
                    </div>
                  </div>
                  <div className={`p-1 rounded-md shrink-0 transition-colors ${
                    isLight
                      ? 'bg-indigo-50 group-hover:bg-indigo-100 text-[#4F46E5]'
                      : 'bg-white/5 group-hover:bg-[#FACC15]/20 text-[#FACC15]'
                  }`}>
                    <ChevronDown
                      className={`w-3.5 h-3.5 transition-transform duration-200 ${
                        isCaseDropdownOpen ? 'rotate-180' : 'rotate-0'
                      }`}
                    />
                  </div>
                </button>

                {/* Floating Dropdown Menu for Case Selection */}
                {isCaseDropdownOpen && (
                  <div
                    className={`absolute top-full left-0 right-0 mt-1.5 z-50 rounded-2xl shadow-2xl p-1.5 space-y-1 max-h-64 overflow-y-auto custom-scrollbar border ${
                      isLight
                        ? 'bg-white/95 backdrop-blur-xl border-slate-200/90 shadow-indigo-100/50 ring-1 ring-slate-900/5'
                        : 'border-[#FACC15]/40'
                    }`}
                    style={isLight ? { backgroundColor: '#FFFFFF' } : { backgroundColor: '#0D0D14' }}
                  >
                    <div className={`px-2 py-1 text-[9px] font-mono uppercase tracking-wider border-b flex items-center justify-between ${
                      isLight ? 'text-slate-500 border-slate-200' : 'text-[#64748B] border-white/10'
                    }`}>
                      <span>Switch Investigation Case</span>
                      <span className={`font-bold ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`}>
                        {availableCases.length} Cases
                      </span>
                    </div>
                    {availableCases.map((c) => {
                      const isSelected = c.id === currentCaseId;
                      return (
                        <button
                          key={c.id}
                          type="button"
                          onClick={() => {
                            switchCase(c.id);
                            setIsCaseDropdownOpen(false);
                          }}
                          className={`w-full p-2 rounded-xl text-left font-mono transition-all cursor-pointer flex items-center justify-between ${
                            isSelected
                              ? isLight
                                ? '!bg-[#4F46E5] !text-white border border-[#4338CA] shadow-sm'
                                : 'bg-[#FACC15]/20 text-[#FACC15] border border-[#FACC15]/40'
                              : isLight
                              ? 'hover:bg-slate-100 text-slate-700 hover:text-slate-900'
                              : 'hover:bg-white/5 text-[#94A3B8] hover:text-[#F8FAFC]'
                          }`}
                        >
                          <div className="min-w-0 pr-2">
                            <div className={`text-[10px] font-bold truncate ${
                              isSelected && isLight ? '!text-white' : isLight ? 'text-slate-900' : 'text-[#F8FAFC]'
                            }`}>
                              {c.name}
                            </div>
                            <div className={`text-[9px] flex items-center space-x-1.5 mt-0.5 ${
                              isSelected && isLight ? '!text-indigo-100' : isLight ? 'text-slate-500' : 'text-[#64748B]'
                            }`}>
                              <span className={`font-semibold ${
                                isSelected && isLight ? '!text-white' : isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'
                              }`}>
                                {c.id}
                              </span>
                              <span>•</span>
                              <span>{c.lead}</span>
                            </div>
                          </div>
                          {isSelected && (
                            <Check className={`w-3.5 h-3.5 shrink-0 ml-1 ${
                              isLight ? '!text-white' : 'text-[#FACC15]'
                            }`} />
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Evidentiary Provenance Split */}
              <div className="space-y-1.5">
                <div className="text-[9px] font-mono text-[#64748B] uppercase tracking-wider font-semibold">
                  Evidentiary Provenance Split
                </div>
                <div className="flex items-center justify-between text-[11px] font-mono font-bold">
                  <span className="text-[#10B981] border-b border-solid border-[#10B981]">
                    82% Source
                  </span>
                  <span className="text-[#64748B]">/</span>
                  <span className={`${isLight ? 'text-[#4F46E5] border-[#4F46E5]' : 'text-[#FACC15] border-[#FACC15]'} border-b border-dashed`}>
                    18% AI Synthetic
                  </span>
                </div>
                {/* Visual Split Gauge Bar */}
                <div className={`w-full h-2 rounded-full overflow-hidden flex p-0.5 border ${isLight ? 'bg-slate-100 border-slate-200' : 'bg-[#050507] border-white/10'}`}>
                  <div className="bg-[#10B981] h-full rounded-l-full" style={{ width: '82%' }} />
                  <div className={`${isLight ? 'bg-[#4F46E5]' : 'bg-[#FACC15]'} h-full rounded-r-full`} style={{ width: '18%' }} />
                </div>
              </div>

              {/* Lead Investigating Officer */}
              <div className={`pt-2 border-t flex items-center justify-between text-[10px] font-mono ${isLight ? 'border-slate-200 text-[#475569]' : 'border-white/10 text-[#64748B]'}`}>
                <span className="uppercase">Lead Officer:</span>
                <span className={`font-bold ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>{activeCase.lead}</span>
              </div>

              {/* Attention Items Requiring Action */}
              <div
                onClick={() => handleSelectView('resolution')}
                className={`p-2 rounded-xl border cursor-pointer transition-colors ${
                  isLight
                    ? 'bg-[#EEF2FF] border-[#C7D2FE] hover:bg-[#E0E7FF]'
                    : 'bg-[#FACC15]/10 border-[#FACC15]/30 hover:bg-[#FACC15]/20'
                }`}
                title="Click to resolve pending attention items"
              >
                <div className={`flex items-center space-x-1.5 text-[10px] font-mono font-bold ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`}>
                  <AlertTriangle className={`w-3.5 h-3.5 animate-pulse shrink-0 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
                  <span>2 Attention Items Active</span>
                </div>
                <div className={`text-[9px] mt-0.5 font-sans ${isLight ? 'text-[#64748B]' : 'text-[#94A3B8]'}`}>
                  Entity Merge + 5-Hop Path Pending Sign-off
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tactical Views Navigation List with Dropdown Category Groups */}
      <nav className={`flex-1 py-2 px-3 overflow-y-auto space-y-3 custom-scrollbar ${isLight ? 'bg-white' : 'bg-[#09090D]'}`}>
        {/* Navigation Controls Bar */}
        <div className={`px-3 pb-1 flex items-center justify-between border-b ${isLight ? 'border-slate-200' : 'border-white/10'}`}>
          <span className="text-[9px] font-mono tracking-wider text-[#64748B] uppercase font-bold">
            Tactical Modules
          </span>
          <button
            type="button"
            onClick={toggleAllGroups}
            className={`text-[9px] font-mono flex items-center space-x-1 cursor-pointer transition-colors ${
              isLight ? 'text-[#4F46E5] hover:text-[#4338CA]' : 'text-[#FACC15] hover:text-[#EAB308]'
            }`}
            title={allCollapsed ? 'Expand all module sections' : 'Collapse all module sections'}
          >
            <ChevronsUpDown className="w-2.5 h-2.5" />
            <span>{allCollapsed ? 'Expand All' : 'Collapse All'}</span>
          </button>
        </div>

        {navGroups.map((group) => {
          const isCollapsed = collapsedGroups[group.groupName] ?? false;
          const groupHasActiveItem = group.items.some(
            (item) =>
              currentView === item.id ||
              (item.id === 'sources' && currentView === 'datasources') ||
              (item.id === 'path' && currentView === 'pathexplorer')
          );

          return (
            <div key={group.groupName} className="space-y-1">
              {/* Dropdown Section Header */}
              <button
                type="button"
                onClick={() => toggleGroup(group.groupName)}
                className={`w-full px-3 py-1.5 text-[9px] font-mono font-bold tracking-[0.18em] uppercase flex items-center justify-between cursor-pointer rounded-lg transition-colors group ${
                  isLight
                    ? 'text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100'
                    : 'text-[#64748B] hover:text-[#F8FAFC] hover:bg-white/5'
                }`}
                title={`${isCollapsed ? 'Expand' : 'Collapse'} ${group.groupName}`}
              >
                <div className="flex items-center space-x-1.5">
                  <span
                    className={
                      groupHasActiveItem
                        ? isLight
                          ? 'text-[#4F46E5] font-bold'
                          : 'text-[#FACC15]'
                        : isLight
                        ? 'group-hover:text-[#4F46E5] transition-colors'
                        : 'group-hover:text-[#FACC15] transition-colors'
                    }
                  >
                    {group.groupName}
                  </span>
                  {groupHasActiveItem && (
                    <span
                      className={`w-1.5 h-1.5 rounded-full inline-block ${
                        isLight ? 'bg-[#4F46E5]' : 'bg-[#FACC15] shadow-[0_0_6px_rgba(250,204,21,0.8)]'
                      }`}
                    />
                  )}
                </div>
                <ChevronDown
                  className={`w-3 h-3 transition-transform duration-200 ${
                    isLight
                      ? groupHasActiveItem
                        ? 'text-[#4F46E5]'
                        : 'text-[#64748B] group-hover:text-[#4F46E5]'
                      : 'text-[#64748B] group-hover:text-[#FACC15]'
                  } ${isCollapsed ? '-rotate-90' : 'rotate-0'}`}
                />
              </button>

              {/* Dropdown Section Items */}
              {!isCollapsed && (
                <div className="space-y-1 transition-all">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const isActive =
                      currentView === item.id ||
                      (item.id === 'sources' && currentView === 'datasources') ||
                      (item.id === 'path' && currentView === 'pathexplorer');

                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => handleSelectView(item.id)}
                        className={`w-full px-3.5 py-2.5 text-xs font-mono rounded-xl transition-all flex items-center justify-between group cursor-pointer ${
                          isActive
                            ? isLight
                              ? 'bg-indigo-100/70 text-slate-900 border border-indigo-300 font-bold shadow-xs'
                              : 'bg-[#FACC15]/20 text-[#FACC15] border border-[#FACC15]/50 font-semibold shadow-md'
                            : isLight
                            ? 'text-[#475569] hover:text-slate-900 hover:bg-slate-100/80 border border-transparent'
                            : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-white/10 border border-transparent'
                        }`}
                        style={isActive && isLight ? { color: '#050507' } : undefined}
                      >
                        <div className="flex items-center space-x-2.5 min-w-0">
                          <Icon
                            className={`w-4 h-4 shrink-0 transition-colors ${
                              isActive
                                ? isLight
                                  ? 'text-slate-900'
                                  : 'text-[#FACC15]'
                                : isLight
                                ? 'text-[#64748B] group-hover:text-slate-900'
                                : 'text-[#64748B] group-hover:text-[#94A3B8]'
                            }`}
                            style={isActive && isLight ? { color: '#050507' } : undefined}
                          />
                          <span 
                            className={`truncate text-left font-sans text-xs ${isActive && isLight ? 'text-slate-900 font-bold' : ''}`}
                            style={isActive && isLight ? { color: '#050507' } : undefined}
                          >
                            {item.label}
                          </span>
                        </div>

                        <div className="flex items-center space-x-1.5 shrink-0 ml-2">
                          {item.badge && (
                            <span
                              className={`text-[9px] font-mono px-2 py-0.5 rounded-full border font-medium ${
                                isActive && isLight
                                  ? 'bg-indigo-100 text-slate-900 border-indigo-300 font-bold'
                                  : getBadgeStyle(item.badgeColor)
                              } ${item.provenance === 'synthetic' ? 'border-dashed' : 'border-solid'}`}
                              style={isActive && isLight ? { color: '#050507' } : undefined}
                            >
                              {item.badge}
                            </span>
                          )}
                          {isActive && (
                            <ChevronRight
                              className={`w-3.5 h-3.5 shrink-0 ${isLight ? 'text-slate-900' : 'text-[#FACC15]'}`}
                              style={isLight ? { color: '#050507' } : undefined}
                            />
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
};
