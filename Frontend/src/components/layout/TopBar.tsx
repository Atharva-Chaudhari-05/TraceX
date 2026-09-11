import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Search,
  Sparkles,
  User,
  Shield,
  LogOut,
  ChevronDown,
  X,
  FileSpreadsheet,
  CreditCard,
  Phone,
  MapPin,
  Building,
  Car,
  ArrowRight,
  Check,
  ShieldCheck,
  BadgeCheck,
  Fingerprint,
  Clock,
  Briefcase,
  PhoneCall,
  Award,
  Menu,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { UserRole, EntityType } from '../../types';
import { ThemeToggle } from './ThemeToggle';

export const TopBar: React.FC = () => {
  const {
    navigateTo,
    entities,
    evidenceRecords,
    setSelectedEntityId,
    setSelectedRecordId,
    currentUser,
    logoutUser,
    theme,
  } = useInvestigation();
  const isLight = theme === 'light';

  // Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // User Profile Menu State
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Global Ctrl+K / Cmd+K listener to focus directly into the search bar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
        setIsSearchFocused(true);
      }
      if (e.key === 'Escape') {
        setIsSearchFocused(false);
        setIsUserMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Click outside listener for search dropdown and user menu
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target as Node)) {
        setIsSearchFocused(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search results computed in real-time
  const searchResults = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) {
      return {
        entities: entities.slice(0, 4),
        records: evidenceRecords.slice(0, 3),
        total: 7,
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
      entities: matchedEntities.slice(0, 5),
      records: matchedRecords.slice(0, 4),
      total: matchedEntities.length + matchedRecords.length,
    };
  }, [searchQuery, entities, evidenceRecords]);

  const getEntityIcon = (type: EntityType) => {
    switch (type) {
      case 'person':
        return <User className={`w-4 h-4 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />;
      case 'phone':
        return <Phone className="w-4 h-4 text-[#10B981]" />;
      case 'account':
        return <CreditCard className={`w-4 h-4 ${isLight ? 'text-[#7C3AED]' : 'text-[#F59E0B]'}`} />;
      case 'location':
        return <MapPin className="w-4 h-4 text-[#EF4444]" />;
      case 'organisation':
        return <Building className="w-4 h-4 text-[#818CF8]" />;
      case 'vehicle':
        return <Car className="w-4 h-4 text-[#10B981]" />;
      default:
        return <User className="w-4 h-4 text-[#94A3B8]" />;
    }
  };

  const handleSignOut = () => {
    setIsUserMenuOpen(false);
    logoutUser();
  };

  const userInitials = currentUser?.name
    ? currentUser.name
        .split(' ')
        .filter(Boolean)
        .map((n) => n[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : 'TX';

  return (
    <header className={`h-16 glass-panel border-b flex items-center justify-between px-6 z-40 relative select-none shrink-0 gap-6 ${isLight ? 'border-slate-200 bg-white/95' : 'border-white/10'}`}>
      {/* Left: Brand Identity with Animated Logo */}
      <div
        onClick={() => navigateTo('overview')}
        className="flex items-center space-x-3 cursor-pointer group shrink-0"
        title="TraceX Intelligence Platform"
      >
        {/* Animated Cyber Hologram Logo Badge */}
        <div
          className={`relative w-10 h-10 rounded-2xl flex items-center justify-center font-mono font-bold text-sm transition-all overflow-hidden ${
            isLight
              ? 'bg-gradient-to-br from-[#EEF2FF] via-[#FFFFFF] to-[#E0E7FF] border border-[#4F46E5]/50 shadow-[0_0_20px_rgba(79,70,229,0.35)] group-hover:border-[#4F46E5]'
              : 'bg-gradient-to-br from-[#111115] via-[#18181D] to-[#050507] border border-[#FACC15]/50 shadow-[0_0_20px_rgba(250,204,21,0.35)] group-hover:border-[#FACC15]'
          }`}
        >
          {/* Animated Ambient Sweeping Aura */}
          <div
            className={`absolute inset-0 animate-spin ${
              isLight
                ? 'bg-gradient-to-tr from-[#4F46E5]/30 via-transparent to-[#7C3AED]/30'
                : 'bg-gradient-to-tr from-[#FACC15]/30 via-transparent to-[#F59E0B]/30'
            }`}
            style={{ animationDuration: '5s' }}
          />
          <span className="relative z-10 font-black text-sm tracking-tight flex items-center">
            <span className={isLight ? 'text-[#0F172A] drop-shadow-[0_0_8px_rgba(79,70,229,0.5)]' : 'text-[#FACC15] drop-shadow-[0_0_8px_rgba(250,204,21,0.7)]'}>T</span>
            <span 
              className={`drop-shadow-[0_0_10px_rgba(250,204,21,0.8)] animate-pulse ${isLight ? '' : 'text-[#F59E0B]'}`}
              style={isLight ? { color: '#FACC15', WebkitTextStroke: '0.8px #09090D', textShadow: '0 1px 2px rgba(0,0,0,0.2)' } : {}}
            >X</span>
          </span>
        </div>

        <div className="hidden sm:block">
          <div className="flex items-center space-x-2">
            <span className={`font-extrabold text-base tracking-tight font-mono ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>
              TRACE<span 
                className={`font-black animate-pulse inline-block ${isLight ? 'drop-shadow-[0_0_12px_rgba(250,204,21,0.8)]' : 'text-[#F59E0B] drop-shadow-[0_0_12px_rgba(245,158,11,0.95)]'}`}
                style={isLight ? { color: '#FACC15', WebkitTextStroke: '1px #09090D', textShadow: '0 1px 2px rgba(0,0,0,0.2)' } : {}}
              >X</span>
            </span>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold shadow-xs border ${
              isLight ? 'bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]' : 'bg-[#FACC15]/10 text-[#FACC15] border-[#FACC15]/30'
            }`}>
              SIH-26189
            </span>
          </div>
          <div className="text-[9px] font-mono text-[#64748B] tracking-wider uppercase">
            CYBER &amp; FINANCIAL CRIMES WING
          </div>
        </div>
      </div>

      {/* Center: DIRECT LONG GLASS SEARCH BAR (Type directly, live results dropdown attached) */}
      <div ref={searchContainerRef} className="flex-1 max-w-5xl mx-auto px-6 md:px-12 relative">
        <div className="relative flex items-center">
          <Search className={`w-4 h-4 absolute left-4.5 pointer-events-none z-10 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setIsSearchFocused(true)}
            placeholder="Search suspects (Rahul Sharma, Ajay Patil), phone intercepts, bank accounts, vehicles..."
            className="w-full h-11 pl-11 pr-24 glass-search-bar rounded-full text-xs sm:text-sm font-sans text-[#F8FAFC] placeholder:text-[#94A3B8] focus:outline-none transition-all shadow-lg"
          />

          <div className="absolute right-3 flex items-center space-x-2">
            {searchQuery ? (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  searchInputRef.current?.focus();
                }}
                className="p-1 hover:bg-white/10 rounded-full text-[#94A3B8] hover:text-[#F8FAFC] transition-colors cursor-pointer"
                title="Clear query"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            ) : (
              <span className={`hidden md:inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono border ${
                isLight ? 'bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]' : 'bg-[#050507]/80 border-white/10 text-[#FACC15]'
              }`}>
                <Sparkles className={`w-3 h-3 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'} animate-pulse`} />
                <span>AI</span>
              </span>
            )}
            <kbd className={`hidden sm:inline-flex items-center px-2 py-0.5 font-mono text-[10px] font-semibold rounded-lg shadow-xs border ${
              isLight ? 'bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]' : 'bg-[#050507]/90 text-[#FACC15] border-[#FACC15]/40'
            }`}>
              Ctrl+K
            </kbd>
          </div>
        </div>

        {/* Real-time Inline Search Results Dropdown (Attached directly below the search bar) */}
        {isSearchFocused && (
          <div className="absolute top-full left-0 right-0 mt-2 glass-panel border border-[#FACC15]/30 rounded-2xl shadow-2xl p-4 z-50 max-h-[70vh] overflow-y-auto space-y-4 backdrop-blur-2xl">
            {/* Quick Header */}
            <div className="flex items-center justify-between text-[11px] font-mono border-b border-white/10 pb-2">
              <span className="text-[#FACC15] font-semibold">
                {searchQuery ? `Results for "${searchQuery}" (${searchResults.total})` : 'Recent & Recommended Intelligence Assets'}
              </span>
              <span className="text-[#64748B] text-[10px]">Press ESC to close</span>
            </div>

            {/* Entities Section */}
            <div>
              <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] font-bold mb-2 flex items-center justify-between">
                <span>Indexed Entities & Targets ({searchResults.entities.length})</span>
                <span className="text-[#FACC15]">Graph Nodes</span>
              </div>

              {searchResults.entities.length === 0 ? (
                <div className="p-3 text-center text-xs font-mono text-[#64748B] bg-[#050507]/70 rounded-xl border border-white/5">
                  No matching entities found for this query.
                </div>
              ) : (
                <div className="space-y-1.5">
                  {searchResults.entities.map((e) => (
                    <div
                      key={e.id}
                      onClick={() => {
                        setSelectedEntityId(e.id);
                        navigateTo('entities');
                        setIsSearchFocused(false);
                      }}
                      className="p-2.5 glass-card hover:bg-white/10 border border-white/10 hover:border-[#FACC15]/50 rounded-xl flex items-center justify-between cursor-pointer transition-all group"
                    >
                      <div className="flex items-center space-x-3 min-w-0">
                        <div className="p-2 bg-[#050507] rounded-xl border border-white/10">
                          {getEntityIcon(e.type)}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-xs text-[#F8FAFC] group-hover:text-[#FACC15] transition-colors truncate">
                              {e.name}
                            </span>
                            <span className="text-[9px] font-mono px-2 py-0.2 bg-[#050507] text-[#64748B] border border-white/10 uppercase rounded-full">
                              {e.type}
                            </span>
                            {e.risk === 'high' && (
                              <span className="text-[9px] font-mono px-2 py-0.2 bg-[#EF4444]/15 text-[#EF4444] border border-[#EF4444]/30 font-semibold rounded-full whitespace-nowrap">
                                HIGH RISK
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-[#94A3B8] truncate mt-0.5 font-sans">
                            {e.role || e.identifier || 'Operation Nexus Target'}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 shrink-0 ml-2">
                        <span className="text-[10px] font-mono text-[#FACC15] opacity-0 group-hover:opacity-100 transition-opacity">
                          View Dossier
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 text-[#64748B] group-hover:text-[#FACC15]" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Evidence Records Section */}
            <div>
              <div className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] font-bold mb-2 flex items-center justify-between">
                <span>Forensic Evidence & Intercepts ({searchResults.records.length})</span>
                <span className="text-[#10B981]">SHA-256 Verified</span>
              </div>

              {searchResults.records.length === 0 ? (
                <div className="p-3 text-center text-xs font-mono text-[#64748B] bg-[#050507]/70 rounded-xl border border-white/5">
                  No matching forensic records found.
                </div>
              ) : (
                <div className="space-y-1.5">
                  {searchResults.records.map((r) => (
                    <div
                      key={r.id}
                      onClick={() => {
                        setSelectedRecordId(r.id);
                        navigateTo('records');
                        setIsSearchFocused(false);
                      }}
                      className="p-2.5 glass-card hover:bg-white/10 border border-white/10 hover:border-[#FACC15]/50 rounded-xl flex items-center justify-between cursor-pointer transition-all group"
                    >
                      <div className="flex items-center space-x-3 min-w-0">
                        <div className="p-2 bg-[#050507] rounded-xl border border-white/10">
                          <FileSpreadsheet className="w-4 h-4 text-[#FACC15]" />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono text-xs font-bold text-[#FACC15]">{r.id}</span>
                            <span className="text-xs text-[#F8FAFC] truncate font-medium group-hover:text-[#FACC15] transition-colors">{r.title}</span>
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
        )}
      </div>

      {/* Right Controls: Theme Toggle & Logged-in User Profile */}
      <div className="flex items-center space-x-3 shrink-0">
        <ThemeToggle />

        <div ref={userMenuRef} className="relative shrink-0">
        <button
          type="button"
          onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
          className={`flex items-center space-x-3 p-1.5 pr-3.5 glass-card rounded-full transition-all cursor-pointer shadow-md group ${
            isLight
              ? 'hover:bg-slate-100 border border-slate-200 hover:border-[#C7D2FE]'
              : 'hover:bg-white/10 border border-white/10 hover:border-[#FACC15]/40'
          }`}
          title="Click to view full officer profile & active session credentials"
        >
          {/* User Photo / Avatar Circle */}
          <div className={`relative w-8 h-8 rounded-full overflow-hidden shadow-xs shrink-0 ring-1 ${
            isLight ? 'ring-[#C7D2FE] bg-slate-100' : 'ring-[#FACC15]/60 bg-[#0D0D11]'
          }`}>
            {currentUser?.photo ? (
              <img
                src={currentUser.photo}
                alt={currentUser.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
              />
            ) : (
              <div className={`w-full h-full flex items-center justify-center font-bold text-xs ${
                isLight ? 'bg-gradient-to-tr from-[#4F46E5] to-[#7C3AED] text-white' : 'bg-gradient-to-tr from-[#EAB308] to-[#FACC15] text-[#050507]'
              }`}>
                {userInitials}
              </div>
            )}
          </div>

          {/* User Name and Role */}
          <div className="text-left hidden md:block">
            <div className={`text-xs font-bold tracking-tight transition-colors flex items-center space-x-1 ${
              isLight ? 'text-[#0F172A] group-hover:text-[#4F46E5]' : 'text-[#F8FAFC] group-hover:text-[#FACC15]'
            }`}>
              <span>{currentUser?.name || 'Authorized Officer'}</span>
              <BadgeCheck className={`w-3.5 h-3.5 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
            </div>
            <div className={`text-[10px] font-mono flex items-center space-x-1 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`}>
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] inline-block" />
              <span>{currentUser?.role || 'Investigator'}</span>
            </div>
          </div>

          <ChevronDown className="w-3.5 h-3.5 text-[#64748B] group-hover:text-[#4F46E5] transition-colors" />
        </button>

        {/* Comprehensive Officer Credentials & Profile Card */}
        {isUserMenuOpen && (
          <div className={`absolute right-0 top-full mt-2 w-96 sm:w-[420px] rounded-3xl p-5 z-50 backdrop-blur-2xl space-y-4 animate-in fade-in zoom-in-95 duration-150 border shadow-2xl ${
            isLight 
              ? 'bg-white/90 border-[#C7D2FE] shadow-[0_25px_60px_rgba(79,70,229,0.16)]' 
              : 'glass-panel border-[#FACC15]/40 shadow-[0_25px_60px_rgba(0,0,0,0.85)]'
          }`}>
            {/* Officer ID Card Header with Photo */}
            <div className={`relative p-4 rounded-2xl border space-y-3 overflow-hidden ${
              isLight 
                ? 'bg-gradient-to-br from-[#EEF2FF]/90 via-white/90 to-[#E0E7FF]/80 border-[#C7D2FE] shadow-sm backdrop-blur-xl' 
                : 'bg-gradient-to-br from-[#111115] via-[#18181D] to-[#050507] border-[#FACC15]/30 shadow-lg'
            }`}>
              {/* Holographic Watermark Crest */}
              <div className={`absolute -right-4 -bottom-4 w-28 h-28 rounded-full blur-xl pointer-events-none ${isLight ? 'bg-[#4F46E5]/10' : 'bg-[#FACC15]/5'}`} />
              <div className="flex items-start justify-between">
                <span className={`text-[9px] font-mono uppercase tracking-[0.2em] font-bold flex items-center space-x-1 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`}>
                  <ShieldCheck className={`w-3 h-3 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
                  <span>Official Law Enforcement Identity</span>
                </span>
                <span className={`text-[9px] font-mono border px-2 py-0.5 rounded-full font-bold ${isLight ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60'}`}>
                  Active Duty
                </span>
              </div>

              {/* Photo & Primary Bio */}
              <div className="flex items-center space-x-4">
                <div className={`relative w-16 h-16 rounded-2xl overflow-hidden shrink-0 isolate border-2 ${
                  isLight 
                    ? 'border-[#4F46E5] shadow-[0_4px_16px_rgba(79,70,229,0.25)] bg-white' 
                    : 'border-[#FACC15] shadow-[0_0_15px_rgba(250,204,21,0.4)] bg-[#050507]'
                }`}>
                  {currentUser?.photo ? (
                    <img
                      src={currentUser.photo}
                      alt={currentUser.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className={`w-full h-full flex items-center justify-center font-black text-xl select-none ${
                      isLight ? 'bg-gradient-to-tr from-[#4F46E5] to-[#7C3AED] text-white' : 'bg-gradient-to-tr from-[#EAB308] to-[#FACC15] text-[#050507]'
                    }`}>
                      {userInitials}
                    </div>
                  )}
                  <span 
                    className={`absolute bottom-0 inset-x-0 text-[8px] font-mono text-center py-0.5 tracking-wider font-bold border-t select-none rounded-b-[14px] ${
                      isLight 
                        ? 'bg-white/95 text-[#050507] border-indigo-200/80 shadow-xs backdrop-blur-md' 
                        : 'bg-[#050507]/90 text-white border-white/10 backdrop-blur-sm'
                    }`}
                    style={isLight ? { color: '#050507' } : { color: '#FFFFFF' }}
                  >
                    VERIFIED
                  </span>
                </div>

                <div className="min-w-0 flex-1">
                  <div className={`text-base font-bold tracking-tight font-sans flex items-center space-x-1.5 ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>
                    <span className="truncate">{currentUser?.name}</span>
                    <Award className={`w-4 h-4 shrink-0 ${isLight ? 'text-[#4F46E5]' : 'text-amber-400'}`} />
                  </div>
                  <div className={`text-[11px] font-medium font-mono truncate ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`}>
                    {currentUser?.rank || 'Senior Investigating Officer'}
                  </div>
                  <div className="text-[10px] font-mono text-[#94A3B8] mt-0.5">
                    Badge ID: <strong className={`font-mono ${isLight ? 'text-[#0F172A]' : 'text-white'}`}>{currentUser?.badgeNumber || 'SCB-88219'}</strong>
                  </div>
                  <div className="text-[10px] text-[#94A3B8] font-mono truncate mt-0.5">
                    {currentUser?.email}
                  </div>
                </div>
              </div>
            </div>

            {/* Officer Information & Operational Metrics Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className={`p-3 rounded-2xl border space-y-1 ${isLight ? 'bg-white/80 border-[#C7D2FE] shadow-xs' : 'bg-[#050507]/80 border-white/10'}`}>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] flex items-center space-x-1">
                  <Briefcase className={`w-3 h-3 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
                  <span>Assigned Role</span>
                </div>
                <div className={`font-bold text-[11px] truncate ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`}>
                  {currentUser?.role}
                </div>
              </div>

              <div className={`p-3 rounded-2xl border space-y-1 ${isLight ? 'bg-white/80 border-[#C7D2FE] shadow-xs' : 'bg-[#050507]/80 border-white/10'}`}>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] flex items-center space-x-1">
                  <Fingerprint className="w-3 h-3 text-emerald-500" />
                  <span>Authentication</span>
                </div>
                <div className="text-emerald-500 font-bold text-[11px] truncate">
                  Biometric 2FA Valid
                </div>
              </div>

              <div className={`p-3 rounded-2xl border space-y-1 col-span-2 ${isLight ? 'bg-white/80 border-[#C7D2FE] shadow-xs' : 'bg-[#050507]/80 border-white/10'}`}>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] flex items-center space-x-1">
                  <Building className={`w-3 h-3 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
                  <span>Department & Command Post</span>
                </div>
                <div className={`font-semibold text-[11px] ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>
                  {currentUser?.department || 'Special Task Force - Central Command'}
                </div>
                <div className="text-[10px] text-[#94A3B8]">
                  {currentUser?.station || 'Central Cyber Investigation Cell, Mumbai'}
                </div>
              </div>

              <div className={`p-3 rounded-2xl border space-y-1 col-span-2 ${isLight ? 'bg-white/80 border-[#C7D2FE] shadow-xs' : 'bg-[#050507]/80 border-white/10'}`}>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] flex items-center space-x-1">
                  <Shield className={`w-3 h-3 ${isLight ? 'text-[#4F46E5]' : 'text-amber-400'}`} />
                  <span>Security Clearance & Jurisdiction</span>
                </div>
                <div className={`font-bold text-[10px] tracking-wide ${isLight ? 'text-[#4F46E5]' : 'text-amber-300'}`}>
                  {currentUser?.clearance || 'LEVEL-4 TOP SECRET // SEC 65B CERTIFIED'}
                </div>
                <div className="text-[10px] text-[#94A3B8]">
                  Jurisdiction: {currentUser?.jurisdiction || 'National & Inter-State Economic Offenses'}
                </div>
              </div>

              <div className={`p-3 rounded-2xl border space-y-1 ${isLight ? 'bg-white/80 border-[#C7D2FE] shadow-xs' : 'bg-[#050507]/80 border-white/10'}`}>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] flex items-center space-x-1">
                  <PhoneCall className={`w-3 h-3 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
                  <span>Direct Secure Line</span>
                </div>
                <div className={`text-[10px] truncate ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>
                  {currentUser?.contact || '+91-22-2618-8821'}
                </div>
              </div>

              <div className={`p-3 rounded-2xl border space-y-1 ${isLight ? 'bg-white/80 border-[#C7D2FE] shadow-xs' : 'bg-[#050507]/80 border-white/10'}`}>
                <div className="text-[9px] uppercase tracking-wider text-[#64748B] flex items-center space-x-1">
                  <Clock className={`w-3 h-3 ${isLight ? 'text-[#4F46E5]' : 'text-[#FACC15]'}`} />
                  <span>Last Login</span>
                </div>
                <div className={`text-[10px] truncate ${isLight ? 'text-[#0F172A]' : 'text-[#F8FAFC]'}`}>
                  {currentUser?.lastLogin || 'Today, 14:02 IST'}
                </div>
              </div>
            </div>

            {/* Active Cases Assigned Chips */}
            <div className={`p-3 rounded-2xl border space-y-1.5 ${isLight ? 'bg-white/80 border-[#C7D2FE] shadow-xs' : 'bg-[#050507]/80 border-white/10'}`}>
              <div className="text-[9px] font-mono uppercase tracking-wider text-[#64748B] font-bold">
                Active Assigned Operations ({currentUser?.casesAssigned?.length || 3})
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(currentUser?.casesAssigned || [
                  'Operation Nexus (CASE-NX-2026-001)',
                  'Operation Falcon (CASE-FL-2026-042)',
                  'Syndicate Pegasus (CASE-PG-2026-109)',
                ]).map((c, idx) => (
                  <span
                    key={idx}
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                      isLight 
                        ? 'bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]'
                        : 'bg-[#FACC15]/10 text-[#FACC15] border-[#FACC15]/30'
                    }`}
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>

            {/* Sign Out Action Button */}
            <div className="pt-1">
              <button
                type="button"
                onClick={handleSignOut}
                className={`w-full py-3 rounded-2xl border text-xs font-mono font-bold flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-xs group ${
                  isLight 
                    ? 'bg-[#EF4444]/10 hover:bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30 hover:border-[#EF4444]'
                    : 'bg-[#EF4444]/15 hover:bg-[#EF4444]/25 text-[#EF4444] border-[#EF4444]/30 hover:border-[#EF4444]'
                }`}
              >
                <LogOut className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                <span>Sign Out Session</span>
              </button>
            </div>
          </div>
        )}
        </div>
      </div>
    </header>
  );
};
