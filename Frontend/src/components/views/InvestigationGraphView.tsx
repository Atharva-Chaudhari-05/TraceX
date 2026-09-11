import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Users,
  Phone,
  CreditCard,
  MapPin,
  Building,
  Clock,
  Car,
  Search,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  Sparkles,
  ArrowRight,
  ExternalLink,
  Filter,
  CheckCircle2,
  GitMerge,
  Eye,
  Shield,
  X,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import { EntityType, RiskLevel } from '../../types';

export const InvestigationGraphView: React.FC = () => {
  const {
    graphNodes,
    graphEdges,
    selectedGraphNodeId,
    setSelectedGraphNodeId,
    selectedGraphEdgeId,
    setSelectedGraphEdgeId,
    showHiddenConnection,
    setShowHiddenConnection,
    toggleHiddenConnection,
    entityMatch,
    entities,
    navigateTo,
    theme,
  } = useInvestigation();
  const isLight = theme === 'light';

  // Graph Filters
  const [filterTypes, setFilterTypes] = useState<Record<EntityType, boolean>>({
    person: true,
    phone: true,
    account: true,
    location: true,
    organisation: true,
    vehicle: true,
    event: true,
  });

  const [filterRisk, setFilterRisk] = useState<string>('all');
  const [graphSearchQuery, setGraphSearchQuery] = useState<string>('');

  // Fullscreen State (User requested: full web size screen with complete functionality)
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  // Canvas / SVG Transformations (Pan & Zoom)
  const [zoom, setZoom] = useState<number>(0.95);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 130, y: 30 });
  const [isDraggingCanvas, setIsDraggingCanvas] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Node Dragging State (Fixes icon jumping far away on click/drag)
  const [nodePositions, setNodePositions] = useState<Record<string, { x: number; y: number }>>({});
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const [nodeDragOffset, setNodeDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const containerRef = useRef<HTMLDivElement>(null);

  // Close fullscreen on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

  // Initialize node positions
  useEffect(() => {
    const initialPos: Record<string, { x: number; y: number }> = {};
    graphNodes.forEach((node) => {
      initialPos[node.id] = { x: node.x, y: node.y };
    });
    setNodePositions(initialPos);
  }, [graphNodes]);

  // Handle Canvas Drag / Pan & Background click deselection
  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === 'svg' || (e.target as HTMLElement).id === 'graph-canvas-bg') {
      setIsDraggingCanvas(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
      // When clicking on empty canvas, deselect node and edge to close right info window
      setSelectedGraphNodeId(null);
      setSelectedGraphEdgeId(null);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDraggingCanvas) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    } else if (draggingNodeId) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        // Calculate canvas space coordinates accounting for container offset, pan, and zoom
        const mouseCanvasX = (e.clientX - rect.left - pan.x) / zoom;
        const mouseCanvasY = (e.clientY - rect.top - pan.y) / zoom;
        const newX = mouseCanvasX - nodeDragOffset.x;
        const newY = mouseCanvasY - nodeDragOffset.y;
        setNodePositions((prev) => ({
          ...prev,
          [draggingNodeId]: { x: Math.round(newX), y: Math.round(newY) },
        }));
      }
    }
  };

  const handleMouseUp = () => {
    setIsDraggingCanvas(false);
    setDraggingNodeId(null);
  };

  const resetFit = () => {
    setZoom(0.95);
    setPan({ x: 80, y: 30 });
  };

  const handleZoom = (delta: number) => {
    setZoom((prev) => Math.min(Math.max(prev + delta, 0.4), 2.5));
  };

  // Filtered Nodes & Edges
  const visibleNodes = useMemo(() => {
    return graphNodes.filter((node) => {
      if (!filterTypes[node.type]) return false;
      if (filterRisk !== 'all' && node.risk !== filterRisk) return false;
      return true;
    });
  }, [graphNodes, filterTypes, filterRisk]);

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((n) => n.id)), [visibleNodes]);

  const visibleEdges = useMemo(() => {
    return graphEdges.filter(
      (edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
    );
  }, [graphEdges, visibleNodeIds]);

  const hiddenPathNodeIds = useMemo(() => {
    return new Set([
      'ent-rahul',
      'ent-ajay',
      'ent-apatil',
      'ent-acc-889922',
      'ent-acc-482701',
      'ent-neha',
      'ent-xyz',
    ]);
  }, []);

  const hiddenPathEdgeIds = useMemo(() => {
    return new Set(['e1', 'e4', 'e5', 'e7', 'e8', 'e9']);
  }, []);

  // Selected Node/Edge Details
  const selectedNode = graphNodes.find((n) => n.id === selectedGraphNodeId) || null;
  const selectedEdge = graphEdges.find((e) => e.id === selectedGraphEdgeId) || null;
  const selectedNodeEntity = selectedNode ? entities.find((e) => e.id === selectedNode.id) : null;

  // Search Jump within Graph
  const searchedNodeId = useMemo(() => {
    if (!graphSearchQuery.trim()) return null;
    const match = graphNodes.find(
      (n) =>
        n.label.toLowerCase().includes(graphSearchQuery.toLowerCase()) ||
        n.id.toLowerCase().includes(graphSearchQuery.toLowerCase())
    );
    return match ? match.id : null;
  }, [graphNodes, graphSearchQuery]);

  const getNodeColorConfig = (type: EntityType, isHighlighted: boolean) => {
    if (isHighlighted) {
      return isLight
        ? { bg: '#EEF2FF', border: '#4F46E5', text: '#0F172A', glow: 'rgba(79, 70, 229, 0.4)' }
        : { bg: '#1C1910', border: '#FACC15', text: '#F8FAFC', glow: 'rgba(250, 204, 21, 0.6)' };
    }
    if (isLight) {
      switch (type) {
        case 'person':
          return { bg: '#EEF2FF', border: '#4F46E5', text: '#0F172A', glow: 'rgba(79, 70, 229, 0.25)' };
        case 'phone':
          return { bg: '#ECFDF5', border: '#10B981', text: '#0F172A', glow: 'rgba(16, 185, 129, 0.25)' };
        case 'account':
          return { bg: '#F5F3FF', border: '#7C3AED', text: '#0F172A', glow: 'rgba(124, 58, 237, 0.25)' };
        case 'location':
          return { bg: '#FFF1F2', border: '#F43F5E', text: '#0F172A', glow: 'rgba(244, 63, 94, 0.25)' };
        case 'organisation':
          return { bg: '#EEF2FF', border: '#6366F1', text: '#0F172A', glow: 'rgba(99, 102, 241, 0.25)' };
        case 'vehicle':
          return { bg: '#F7FEE7', border: '#84CC16', text: '#0F172A', glow: 'rgba(132, 204, 22, 0.25)' };
        case 'event':
          return { bg: '#F8FAFC', border: '#94A3B8', text: '#0F172A', glow: 'rgba(148, 163, 184, 0.25)' };
        default:
          return { bg: '#EEF2FF', border: '#4F46E5', text: '#0F172A', glow: 'rgba(79, 70, 229, 0.25)' };
      }
    }
    switch (type) {
      case 'person':
        return { bg: '#18181C', border: '#60A5FA', text: '#F8FAFC', glow: 'rgba(96, 165, 250, 0.4)' };
      case 'phone':
        return { bg: '#064E3B', border: '#34D399', text: '#F8FAFC', glow: 'rgba(52, 211, 153, 0.4)' };
      case 'account':
        return { bg: '#451A03', border: '#FBBF24', text: '#F8FAFC', glow: 'rgba(251, 191, 36, 0.4)' };
      case 'location':
        return { bg: '#4C0519', border: '#F43F5E', text: '#F8FAFC', glow: 'rgba(244, 63, 94, 0.4)' };
      case 'organisation':
        return { bg: '#312E81', border: '#818CF8', text: '#F8FAFC', glow: 'rgba(129, 140, 248, 0.4)' };
      case 'vehicle':
        return { bg: '#365314', border: '#A3E635', text: '#F8FAFC', glow: 'rgba(163, 230, 53, 0.4)' };
      case 'event':
        return { bg: '#18181C', border: '#94A3B8', text: '#F8FAFC', glow: 'rgba(148, 163, 184, 0.4)' };
      default:
        return { bg: '#18181C', border: '#FACC15', text: '#F8FAFC', glow: 'rgba(250, 204, 21, 0.4)' };
    }
  };

  const entityTypePills: { id: EntityType; label: string; icon: any; color: string }[] = [
    { id: 'person', label: 'People', icon: Users, color: isLight ? 'text-[#4F46E5]' : 'text-yellow-400' },
    { id: 'phone', label: 'Phones', icon: Phone, color: 'text-emerald-400' },
    { id: 'account', label: 'Accounts', icon: CreditCard, color: isLight ? 'text-[#7C3AED]' : 'text-amber-400' },
    { id: 'location', label: 'Locations', icon: MapPin, color: 'text-rose-400' },
    { id: 'organisation', label: 'Organisations', icon: Building, color: 'text-indigo-400' },
    { id: 'vehicle', label: 'Vehicles', icon: Car, color: 'text-lime-400' },
    { id: 'event', label: 'Events', icon: Clock, color: 'text-slate-400' },
  ];

  return (
    <div
      id="investigation-graph-view"
      className={`${
        isFullscreen
          ? 'fixed inset-0 z-50 w-screen h-screen'
          : 'h-[calc(100vh-4rem)]'
      } flex flex-col overflow-hidden bg-[#050507] text-[#F8FAFC]`}
    >
      {/* ========================================================================= */}
      {/* Item 4: UPPER CONTROL RIBBON (Header with 2D Animated Vehicle/Person Logo) */}
      {/* ========================================================================= */}
      <div className="glass-panel border-b border-white/10 px-6 py-3 flex flex-wrap items-center justify-between gap-4 shrink-0 z-20 shadow-md">
        {/* Left: 2D Animated Vehicle & Person Graph Logo */}
        <div className="flex items-center space-x-3.5">
          <div className={`relative flex items-center justify-center p-2.5 rounded-2xl border transition-all ${
            isLight
              ? 'bg-gradient-to-br from-indigo-50/90 via-white to-blue-50/90 border-indigo-200 shadow-[0_4px_20px_rgba(79,70,229,0.18)] ring-2 ring-indigo-500/10'
              : 'bg-gradient-to-br from-[#0D0D11] to-[#18181C] border-[#FACC15]/40 shadow-[0_0_15px_rgba(250, 204, 21,0.25)]'
          }`}>
            {/* Animated SVG Graphic: 2D Vehicle & Person */}
            <svg
              className="w-9 h-9 text-[#FACC15] animate-vehicle"
              viewBox="0 0 48 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient id="graphIconGradLight" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#4F46E5" />
                  <stop offset="100%" stopColor="#7C3AED" />
                </linearGradient>
                <linearGradient id="graphIconVehLight" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#10B981" />
                  <stop offset="100%" stopColor="#059669" />
                </linearGradient>
              </defs>

              {/* Radar pulse ripples behind */}
              <circle cx="24" cy="24" r="20" stroke={isLight ? "#4F46E5" : "#FACC15"} strokeWidth="1.5" strokeDasharray="3 3" opacity={isLight ? "0.3" : "0.4"} />
              <circle cx="16" cy="18" r="8" stroke={isLight ? "#4F46E5" : "#FACC15"} strokeWidth="1.5" opacity={isLight ? "0.25" : "0.3"} className="animate-radar" />

              {/* 2D Person Silhouette */}
              <circle cx="16" cy="16" r="5" fill={isLight ? "url(#graphIconGradLight)" : "#FACC15"} />
              <path
                d="M8 27C8 23 11.5 20.5 16 20.5C20.5 20.5 24 23 24 27"
                stroke={isLight ? "url(#graphIconGradLight)" : "#FACC15"}
                strokeWidth="2.5"
                strokeLinecap="round"
              />

              {/* Tactical beam connecting person to vehicle */}
              <line x1="20" y1="20" x2="27" y2="29" stroke={isLight ? "#6366F1" : "#FACC15"} strokeWidth="1.5" strokeDasharray="2 2" opacity={isLight ? "0.8" : "1"} />

              {/* 2D Vehicle Silhouette */}
              <path
                d="M24 33H40L38 27H29L27 30H24V33Z"
                fill={isLight ? "url(#graphIconVehLight)" : "#A3E635"}
                stroke={isLight ? "#059669" : "#A3E635"}
                strokeWidth="1.5"
                strokeLinejoin="round"
              />
              <circle cx="28" cy="34" r="2.5" fill={isLight ? "#FFFFFF" : "#050507"} stroke={isLight ? "#059669" : "#A3E635"} strokeWidth="1.5" />
              <circle cx="37" cy="34" r="2.5" fill={isLight ? "#FFFFFF" : "#050507"} stroke={isLight ? "#059669" : "#A3E635"} strokeWidth="1.5" />
            </svg>
            <span className="absolute -bottom-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10B981] opacity-75"></span>
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 bg-[#10B981] ${isLight ? 'ring-2 ring-white' : 'border border-[#050507]'}`}></span>
            </span>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xs font-mono font-bold uppercase tracking-[0.2em] text-[#F8FAFC]">
                Topological Graph Explorer
              </h1>
              <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-[#FACC15]/15 text-[#FACC15] border border-[#FACC15]/30 font-semibold">
                {graphNodes.length} Nodes Live
              </span>
            </div>
            <div className="text-[10px] text-[#94A3B8] font-sans">
              Tactical Surveillance Correlator • Person & Vehicle Topology
            </div>
          </div>
        </div>

        {/* Center: Search nodes on canvas */}
        <div className="relative w-72 hidden xl:block">
          <Search className="w-3.5 h-3.5 text-[#64748B] absolute left-3 top-2.5" />
          <input
            type="text"
            value={graphSearchQuery}
            onChange={(e) => setGraphSearchQuery(e.target.value)}
            placeholder="Search canvas nodes (e.g. MH-12, Rahul)..."
            className="w-full pl-9 pr-3 py-1.5 text-xs glass-card rounded-full border border-white/10 text-[#F8FAFC] placeholder:text-[#64748B] focus:border-[#FACC15] focus:outline-none font-mono"
          />
        </div>

        {/* Right: Hidden Path Toggle & Zoom/Fullscreen Controls */}
        <div className="flex items-center space-x-3">
          <button
            id="show-hidden-connection-btn"
            onClick={toggleHiddenConnection}
            className={`px-4 py-1.5 text-xs font-mono uppercase tracking-wider font-semibold flex items-center space-x-2 transition-all rounded-full border cursor-pointer ${
              showHiddenConnection
                ? isLight
                  ? 'bg-indigo-100/80 text-slate-900 border-2 border-indigo-300 shadow-xs font-bold backdrop-blur-md'
                  : 'bg-[#FACC15] text-[#050507] border-[#FACC15] shadow-[0_0_15px_rgba(250, 204, 21,0.5)] font-bold'
                : isLight
                  ? 'bg-white text-slate-900 border-2 border-slate-300 hover:border-indigo-400 hover:bg-indigo-50/70 shadow-xs font-semibold'
                  : 'glass-card hover:bg-white/10 text-[#FACC15] border-[#FACC15]/40'
            }`}
            style={isLight ? { color: '#050507' } : undefined}
          >
            <Sparkles 
              className={`w-3.5 h-3.5 ${showHiddenConnection ? (isLight ? 'text-slate-900' : 'text-[#050507]') : (isLight ? 'text-slate-900 animate-pulse' : 'text-[#FACC15] animate-pulse')}`}
              style={isLight ? { color: '#050507' } : undefined}
            />
            <span 
              className={isLight ? 'text-slate-900 font-bold' : ''}
              style={isLight ? { color: '#050507' } : undefined}
            >
              {showHiddenConnection ? 'Hide Conduit Path' : 'Reveal 5-Hop Hawala Conduit'}
            </span>
          </button>

          <div className="flex items-center space-x-1 glass-card p-1 rounded-full border border-white/10">
            <button
              onClick={() => handleZoom(-0.15)}
              className="p-1.5 hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC] rounded-full transition-colors cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-xs font-mono text-[#94A3B8] px-1.5 min-w-[42px] text-center font-semibold">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={() => handleZoom(0.15)}
              className="p-1.5 hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC] rounded-full transition-colors cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className={`p-1.5 rounded-full transition-colors cursor-pointer ${
                isFullscreen
                  ? 'bg-[#FACC15] text-[#050507] font-bold shadow-[0_0_10px_rgba(250, 204, 21,0.5)]'
                  : 'hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC]'
              }`}
              title={isFullscreen ? 'Exit Full Screen (Esc)' : 'Full Web Screen Mode'}
            >
              {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* Item 4: UPPER HORIZONTAL FILTER BAR (Moved from leftside bar to upper side) */}
      {/* ========================================================================= */}
      <div className="glass-panel border-b border-white/10 px-6 py-2.5 flex flex-wrap items-center justify-between gap-3 shrink-0 z-10 text-xs font-mono">
        {/* Left: Ontology Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1.5 text-[10px] font-bold text-[#FACC15] uppercase tracking-wider mr-1">
            <Filter className="w-3 h-3 text-[#FACC15]" />
            <span>Filters:</span>
          </div>

          {entityTypePills.map((t) => {
            const Icon = t.icon;
            const checked = filterTypes[t.id];
            return (
              <button
                key={t.id}
                type="button"
                onClick={() =>
                  setFilterTypes((prev) => ({
                    ...prev,
                    [t.id]: !prev[t.id],
                  }))
                }
                className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-mono border transition-all cursor-pointer ${
                  checked
                    ? 'glass-card border-[#FACC15]/40 text-[#F8FAFC] shadow-xs'
                    : 'bg-[#050507]/60 border-white/5 text-[#64748B] opacity-60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${t.color}`} />
                <span>{t.label}</span>
                <span className={`w-1.5 h-1.5 rounded-full ${checked ? 'bg-[#FACC15]' : 'bg-[#64748B]'}`} />
              </button>
            );
          })}
        </div>

        {/* Right: Risk Level Filters & Entity Resolution Quick-Link */}
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-mono text-[#64748B] uppercase tracking-wider">Risk:</span>
          {['all', 'high', 'medium', 'low'].map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setFilterRisk(r)}
              className={`px-3 py-0.5 rounded-full text-[11px] font-mono uppercase font-semibold transition-all cursor-pointer border ${
                filterRisk === r
                  ? 'bg-[#FACC15]/20 text-[#FACC15] border-[#FACC15] shadow-xs'
                  : 'glass-card text-[#94A3B8] border-white/10 hover:border-white/20'
              }`}
            >
              {r}
            </button>
          ))}

          <div className="h-4 w-px bg-white/10 mx-1" />

          {/* Identity Resolution pill */}
          <div
            onClick={() => navigateTo('resolution')}
            className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[#F59E0B]/15 border border-[#F59E0B]/30 hover:bg-[#F59E0B]/25 text-[10px] text-[#F59E0B] font-bold cursor-pointer transition-colors"
            title="Candidate Match: Ajay Patil ↔ A. Patil"
          >
            <GitMerge className="w-3 h-3 text-[#F59E0B]" />
            <span>Ajay ↔ A. Patil</span>
            <span className="px-1.5 py-0.2 bg-[#050507] rounded-full border border-[#F59E0B]/40 text-[9px]">
              {entityMatch.status === 'approved' ? '✓' : '94%'}
            </span>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* Main Graph Canvas Area & Right Inspector */}
      {/* ========================================================================= */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* CENTER INTERACTIVE GRAPH CANVAS */}
        <div
          ref={containerRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className="flex-1 bg-[#050507] relative overflow-hidden cursor-grab active:cursor-grabbing"
          style={{ backgroundImage: 'radial-gradient(#18181C 1px, transparent 1px)', backgroundSize: '24px 24px' }}
        >

          {/* SVG Canvas Rendering Nodes & Edges */}
          <svg
            id="investigation-graph-svg"
            className="w-full h-full"
            style={{ minWidth: '100%', minHeight: '100%' }}
          >
            {/* Definitions for Markers (Arrows) & Glow Filters */}
            <defs>
              <marker
                id="arrow-default"
                viewBox="0 0 10 10"
                refX="26"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#888880" />
              </marker>

              <marker
                id="arrow-highlight"
                viewBox="0 0 10 10"
                refX="26"
                refY="5"
                markerWidth="7"
                markerHeight="7"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#22D3EE" />
              </marker>

              <marker
                id="arrow-selected"
                viewBox="0 0 10 10"
                refX="26"
                refY="5"
                markerWidth="8"
                markerHeight="8"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill={isLight ? '#4F46E5' : '#FACC15'} />
              </marker>

              {/* Glowing Drop Shadows for Nodes */}
              <filter id="glow-cyan" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#FACC15" floodOpacity="0.8" />
              </filter>
              <filter id="glow-vehicle" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#A3E635" floodOpacity="0.7" />
              </filter>
              <filter id="glow-phone" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="5" floodColor="#34D399" floodOpacity="0.7" />
              </filter>
            </defs>

            {/* Background Rect for Drag Handling */}
            <rect id="graph-canvas-bg" width="100%" height="100%" fill="transparent" />

            {/* Transformed Canvas Layer */}
            <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
              {/* RENDER RELATIONSHIP EDGES */}
              {visibleEdges.map((edge) => {
                const sourcePos = nodePositions[edge.source];
                const targetPos = nodePositions[edge.target];
                if (!sourcePos || !targetPos) return null;

                const isSelected = selectedGraphEdgeId === edge.id;
                const isPartOfHidden = showHiddenConnection && hiddenPathEdgeIds.has(edge.id);

                const ratio = edge.labelRatio ?? 0.5;
                const offsetX = edge.labelOffsetX ?? 0;
                const offsetY = edge.labelOffsetY ?? 0;

                const midX = sourcePos.x + (targetPos.x - sourcePos.x) * ratio + offsetX;
                const midY = sourcePos.y + (targetPos.y - sourcePos.y) * ratio + offsetY;

                const labelText = edge.amount ? edge.amount : edge.label;
                // Dynamic pill width based on text length to keep text strictly within box boundary
                const pillWidth = Math.max(72, Math.round(labelText.length * 6.3) + 24);
                const halfPillWidth = pillWidth / 2;

                return (
                  <g
                    key={edge.id}
                    className="cursor-pointer group"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedGraphEdgeId(edge.id);
                      setSelectedGraphNodeId(null);
                    }}
                  >
                    {/* Edge Line */}
                    <line
                      x1={sourcePos.x}
                      y1={sourcePos.y}
                      x2={targetPos.x}
                      y2={targetPos.y}
                      stroke={
                        isSelected
                          ? isLight ? '#4F46E5' : '#FACC15'
                          : isPartOfHidden
                          ? isLight ? '#4F46E5' : '#FACC15'
                          : edge.type === 'entity_match'
                          ? isLight ? '#7C3AED' : '#F59E0B'
                          : isLight ? '#94A3B8' : '#475569'
                      }
                      strokeWidth={isSelected ? 3.5 : isPartOfHidden ? 3 : 1.5}
                      strokeDasharray={edge.type === 'entity_match' || isPartOfHidden ? '5,4' : undefined}
                      markerEnd={
                        isSelected
                          ? 'url(#arrow-selected)'
                          : isPartOfHidden
                          ? 'url(#arrow-highlight)'
                          : 'url(#arrow-default)'
                      }
                      className={
                        isPartOfHidden
                          ? 'animate-pulse transition-all'
                          : `transition-all ${isLight ? 'group-hover:stroke-[#4F46E5]' : 'group-hover:stroke-[#FACC15]'}`
                      }
                    />

                    {/* Edge Label Pill with proper box boundary */}
                    <g transform={`translate(${midX}, ${midY})`}>
                      <rect
                        x={-halfPillWidth}
                        y="-11"
                        width={pillWidth}
                        height="22"
                        rx="11"
                        fill={
                          isSelected
                            ? isLight ? '#4F46E5' : '#FACC15'
                            : isPartOfHidden
                            ? isLight ? '#EEF2FF' : '#1C1910'
                            : isLight ? '#FFFFFF' : '#0D0D11'
                        }
                        stroke={
                          isSelected
                            ? isLight ? '#4F46E5' : '#FACC15'
                            : isPartOfHidden
                            ? isLight ? '#C7D2FE' : '#FACC15'
                            : isLight ? '#CBD5E1' : '#334155'
                        }
                        strokeWidth={isSelected ? 1.5 : 1}
                        className="shadow-sm"
                      />
                      <text
                        x="0"
                        y="3.5"
                        textAnchor="middle"
                        fill={
                          isSelected
                            ? '#FFFFFF'
                            : isPartOfHidden
                            ? isLight ? '#4F46E5' : '#F8FAFC'
                            : isLight ? '#0F172A' : '#94A3B8'
                        }
                        fontSize="9"
                        fontFamily="IBM Plex Mono, monospace"
                        fontWeight="600"
                        className="select-none pointer-events-none"
                      >
                        {labelText}
                      </text>
                    </g>
                  </g>
                );
              })}

              {/* RENDER NODES WITH 2D ANIMATED ICONS */}
              {visibleNodes.map((node) => {
                const pos = nodePositions[node.id] || { x: node.x, y: node.y };
                const isSelected = selectedGraphNodeId === node.id;
                const isPartOfHidden = showHiddenConnection && hiddenPathNodeIds.has(node.id);
                const isSearched = searchedNodeId === node.id;

                const styling = getNodeColorConfig(node.type, isPartOfHidden);

                return (
                  <g
                    key={node.id}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    onMouseDown={(e) => {
                      e.stopPropagation();
                      const rect = containerRef.current?.getBoundingClientRect();
                      const currentPos = nodePositions[node.id] || { x: node.x, y: node.y };
                      if (rect) {
                        const mouseCanvasX = (e.clientX - rect.left - pan.x) / zoom;
                        const mouseCanvasY = (e.clientY - rect.top - pan.y) / zoom;
                        setNodeDragOffset({
                          x: mouseCanvasX - currentPos.x,
                          y: mouseCanvasY - currentPos.y,
                        });
                      } else {
                        setNodeDragOffset({ x: 0, y: 0 });
                      }
                      setDraggingNodeId(node.id);
                      setSelectedGraphNodeId(node.id);
                      setSelectedGraphEdgeId(null);
                    }}
                    className="cursor-pointer group select-none"
                  >
                    {/* Search / Hidden / Selected Outer Pulsing Ring */}
                    {(isSelected || isSearched || isPartOfHidden) && (
                      <circle
                        r="32"
                        fill="none"
                        stroke={isSearched ? (isLight ? '#4F46E5' : '#F8FAFC') : isPartOfHidden ? (isLight ? '#4F46E5' : '#FACC15') : (isLight ? '#4F46E5' : '#FACC15')}
                        strokeWidth={isSearched ? 3 : 2}
                        strokeDasharray={isPartOfHidden ? '4,3' : undefined}
                        className={isPartOfHidden ? 'animate-radar' : undefined}
                      />
                    )}

                    {/* Node Main Circle / Translucent Glass Container */}
                    <circle
                      r="22"
                      fill={styling.bg}
                      stroke={styling.border}
                      strokeWidth={isSelected ? 3 : 2}
                      filter={isSelected || isPartOfHidden ? 'url(#glow-cyan)' : undefined}
                      className="shadow-md transition-all group-hover:scale-105"
                    />

                    {/* Node Risk Indicator Badge (Top Right) */}
                    <circle
                      r="6"
                      cx="14"
                      cy="-14"
                      fill={
                        node.risk === 'high'
                          ? '#EF4444'
                          : node.risk === 'medium'
                          ? '#F59E0B'
                          : '#64748B'
                      }
                      stroke={isLight ? '#FFFFFF' : '#050507'}
                      strokeWidth="1.5"
                    />

                    {/* ============================================================== */}
                    {/* 2D Animated Icons Rendered Inside Nodes */}
                    {/* ============================================================== */}
                    {node.type === 'person' && (
                      <g transform="translate(-10, -10)" className="pointer-events-none">
                        <circle cx="10" cy="7" r="4" fill={isLight ? '#4F46E5' : '#60A5FA'} />
                        <path
                          d="M4 17C4 13.7 6.7 11 10 11C13.3 11 16 13.7 16 17"
                          stroke={isLight ? '#4F46E5' : '#60A5FA'}
                          strokeWidth="2"
                          strokeLinecap="round"
                        />
                      </g>
                    )}

                    {node.type === 'vehicle' && (
                      <g transform="translate(-10, -10)" className="pointer-events-none">
                        <svg
                          width="20"
                          height="20"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke={isLight ? '#059669' : '#A3E635'}
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
                          <circle cx="7" cy="17" r="2" fill={isLight ? '#FFFFFF' : '#050507'} stroke={isLight ? '#059669' : 'none'} strokeWidth={isLight ? 1 : 0} />
                          <path d="M9 17h6" />
                          <circle cx="17" cy="17" r="2" fill={isLight ? '#FFFFFF' : '#050507'} stroke={isLight ? '#059669' : 'none'} strokeWidth={isLight ? 1 : 0} />
                        </svg>
                      </g>
                    )}

                    {node.type === 'phone' && (
                      <g transform="translate(-6, -9)" className="pointer-events-none">
                        <rect x="0" y="0" width="12" height="18" rx="2.5" fill={isLight ? '#D1FAE5' : '#064E3B'} stroke={isLight ? '#059669' : '#34D399'} strokeWidth="1.5" />
                        <circle cx="6" cy="14" r="1" fill={isLight ? '#059669' : '#34D399'} />
                        <line x1="4" y1="3" x2="8" y2="3" stroke={isLight ? '#059669' : '#34D399'} strokeWidth="1" strokeLinecap="round" />
                      </g>
                    )}

                    {node.type === 'account' && (
                      <g transform="translate(-8, -8)" className="pointer-events-none">
                        <rect x="0" y="2" width="16" height="12" rx="2" fill={isLight ? '#EEF2FF' : '#451A03'} stroke={isLight ? '#4F46E5' : '#FBBF24'} strokeWidth="1.5" />
                        <line x1="0" y1="6" x2="16" y2="6" stroke={isLight ? '#4F46E5' : '#FBBF24'} strokeWidth="1" />
                        <circle cx="4" cy="10" r="1.2" fill={isLight ? '#4F46E5' : '#FBBF24'} />
                      </g>
                    )}

                    {node.type === 'location' && (
                      <g transform="translate(-6, -9)" className="pointer-events-none">
                        <path
                          d="M6 0C2.7 0 0 2.7 0 6C0 10.5 6 17 6 17C6 17 12 10.5 12 6C12 2.7 9.3 0 6 0Z"
                          fill={isLight ? '#FFE4E6' : '#4C0519'}
                          stroke={isLight ? '#E11D48' : '#F43F5E'}
                          strokeWidth="1.5"
                        />
                        <circle cx="6" cy="6" r="2.5" fill={isLight ? '#FFFFFF' : '#050507'} stroke={isLight ? '#E11D48' : 'none'} strokeWidth={isLight ? 0.75 : 0} />
                      </g>
                    )}

                    {node.type === 'organisation' && (
                      <g transform="translate(-8, -8)" className="pointer-events-none">
                        <rect x="2" y="3" width="12" height="13" rx="1.5" fill={isLight ? '#EEF2FF' : '#1E1B4B'} stroke={isLight ? '#4F46E5' : '#818CF8'} strokeWidth="1.5" />
                        <rect x="5" y="6" width="2" height="2" fill={isLight ? '#4F46E5' : '#818CF8'} />
                        <rect x="9" y="6" width="2" height="2" fill={isLight ? '#4F46E5' : '#818CF8'} />
                        <rect x="5" y="10" width="2" height="2" fill={isLight ? '#4F46E5' : '#818CF8'} />
                        <rect x="9" y="10" width="2" height="2" fill={isLight ? '#4F46E5' : '#818CF8'} />
                      </g>
                    )}

                    {node.type === 'event' && (
                      <g transform="translate(-8, -8)" className="pointer-events-none">
                        <circle cx="8" cy="8" r="7" fill={isLight ? '#F1F5F9' : '#0D0D11'} stroke={isLight ? '#64748B' : '#94A3B8'} strokeWidth="1.5" />
                        <polyline points="8,4 8,8 11,8" stroke={isLight ? '#64748B' : '#94A3B8'} strokeWidth="1.5" strokeLinecap="round" />
                      </g>
                    )}

                    {/* Node Text Label Card with dynamic box boundary */}
                    <g transform="translate(0, 34)">
                      {(() => {
                        const nodeLabelText = node.label;
                        const cardWidth = Math.max(86, Math.round(nodeLabelText.length * 6.6) + 24);
                        const halfCardWidth = cardWidth / 2;
                        return (
                          <>
                            <rect
                              x={-halfCardWidth}
                              y="-10"
                              width={cardWidth}
                              height="20"
                              rx="10"
                              fill={isLight ? '#FFFFFF' : '#050507'}
                              stroke={
                                isSelected
                                  ? isLight ? '#4F46E5' : '#FACC15'
                                  : isLight ? '#CBD5E1' : '#334155'
                              }
                              strokeWidth={isSelected ? 1.5 : 1}
                              className="pointer-events-none shadow-xs"
                            />
                            <text
                              x="0"
                              y="3.5"
                              textAnchor="middle"
                              fill={
                                isSelected
                                  ? isLight ? '#4F46E5' : '#FACC15'
                                  : isLight ? '#0F172A' : '#F8FAFC'
                              }
                              fontSize="10"
                              fontFamily="Inter, sans-serif"
                              fontWeight="600"
                              className="pointer-events-none select-none"
                            >
                              {nodeLabelText}
                            </text>
                          </>
                        );
                      })()}
                    </g>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* RIGHT DETAIL INSPECTOR (Glassmorphic Drawer - Hidden when none is clicked) */}
        {(selectedNode || selectedEdge) && (
          <div className="w-84 glass-panel border-l border-white/10 p-6 shrink-0 overflow-y-auto z-10 shadow-xl relative animate-in slide-in-from-right duration-200">
            {/* Close Button to off the right side info window */}
            <button
              type="button"
              onClick={() => {
                setSelectedGraphNodeId(null);
                setSelectedGraphEdgeId(null);
              }}
              className="absolute top-4 right-4 p-1.5 rounded-full hover:bg-white/10 text-[#94A3B8] hover:text-[#F8FAFC] transition-colors cursor-pointer"
              title="Close Panel"
            >
              <X className="w-4 h-4" />
            </button>

            {selectedNode ? (
              <div className="space-y-6">
                <div className="flex items-start justify-between border-b border-white/10 pb-4 pr-6">
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                      Node Dossier
                    </span>
                    <h2 className="text-base font-bold text-[#F8FAFC] mt-1">{selectedNode.label}</h2>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 bg-[#050507] text-[#94A3B8] border border-white/10 rounded-full">
                        {selectedNode.type}
                      </span>
                      {selectedNode.role && (
                        <span className="text-xs text-[#94A3B8]">
                          {selectedNode.role}
                        </span>
                      )}
                    </div>
                  </div>

                  <span
                    className={`text-[10px] font-bold font-mono px-2.5 py-1 rounded-full border ${
                      selectedNode.risk === 'high'
                        ? 'bg-rose-950/50 text-rose-400 border-rose-800/60'
                        : selectedNode.risk === 'medium'
                        ? 'bg-amber-950/50 text-amber-400 border-amber-800/60'
                        : 'bg-slate-900 text-slate-400 border-slate-700'
                    }`}
                  >
                    {selectedNode.risk.toUpperCase()}
                  </span>
                </div>

                {/* Connections count */}
                <div className="glass-card p-3.5 rounded-2xl border border-white/10 text-xs">
                  <span className="text-[#64748B] block text-[10px] uppercase font-mono tracking-wider font-semibold">
                    Graph Centrality
                  </span>
                  <span className="text-base font-bold text-[#F8FAFC] font-mono">
                    {selectedNode.connections} Graph Connections
                  </span>
                </div>

                {/* Entity Context details if available */}
                {selectedNodeEntity && selectedNodeEntity.metadata && (
                  <div className="space-y-2 text-xs">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                      Metadata Signals
                    </span>
                    {Object.entries(selectedNodeEntity.metadata).map(([k, v]) => (
                      <div
                        key={k}
                        className="p-2.5 glass-card rounded-xl border border-white/10 flex items-center justify-between text-xs"
                      >
                        <span className="text-[#64748B] font-mono text-[11px] uppercase">{k}:</span>
                        <span className="font-mono text-[#F8FAFC] font-medium">{v}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Related Evidence */}
                {selectedNodeEntity && selectedNodeEntity.relatedEvidenceIds.length > 0 && (
                  <div className="space-y-2 text-xs">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                      Evidentiary Citations
                    </span>
                    {selectedNodeEntity.relatedEvidenceIds.map((evId) => (
                      <div
                        key={evId}
                        onClick={() => navigateTo('evidence', { evidenceId: evId })}
                        className="p-2.5 glass-card rounded-xl hover:border-[#FACC15] cursor-pointer flex items-center justify-between transition-colors group"
                      >
                        <span className="font-mono font-bold text-[#F8FAFC] group-hover:text-[#FACC15]">{evId}</span>
                        <span className="text-xs text-[#94A3B8]">View Dossier</span>
                        <ExternalLink className="w-3.5 h-3.5 text-[#FACC15]" />
                      </div>
                    ))}
                  </div>
                )}

                {/* Cross Navigation Actions */}
                <div className="pt-4 border-t border-white/10 space-y-2.5">
                  <button
                    onClick={() => navigateTo('entities', { entityId: selectedNode.id })}
                    className="w-full py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center justify-center space-x-2 rounded-full shadow-lg transition-all cursor-pointer"
                  >
                    <Users className="w-3.5 h-3.5" />
                    <span>Open Full Entity Dossier</span>
                  </button>
                  <button
                    onClick={() => navigateTo('timeline')}
                    className="w-full py-2.5 glass-card hover:bg-white/10 text-[#F8FAFC] text-xs font-mono uppercase tracking-wider font-semibold flex items-center justify-center space-x-2 rounded-full border border-white/15 transition-all cursor-pointer"
                  >
                    <Clock className="w-3.5 h-3.5" />
                    <span>View Timeline Events</span>
                  </button>
                </div>
              </div>
            ) : selectedEdge ? (
              <div className="space-y-6">
                <div className="border-b border-white/10 pb-4 pr-6">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                    Relationship Inspector
                  </span>
                  <h3 className="text-base font-bold text-[#F8FAFC] mt-1">{selectedEdge.label}</h3>
                  <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 bg-[#050507] text-[#94A3B8] border border-white/10 rounded-full inline-block mt-2">
                    Type: {selectedEdge.type}
                  </span>
                </div>

                <div className="glass-card p-4 rounded-2xl border border-white/10 space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-[#64748B] block font-mono uppercase tracking-wider">Origin Node</span>
                    <span className="font-mono font-semibold text-[#F8FAFC] text-xs">{selectedEdge.source}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#64748B] block font-mono uppercase tracking-wider">Target Node</span>
                    <span className="font-mono font-semibold text-[#F8FAFC] text-xs">{selectedEdge.target}</span>
                  </div>
                  {selectedEdge.time && (
                    <div>
                      <span className="text-[10px] text-[#64748B] block font-mono uppercase tracking-wider">Recorded Timestamp</span>
                      <span className="font-mono text-[#FACC15] font-semibold">{selectedEdge.time} IST</span>
                    </div>
                  )}
                  {selectedEdge.amount && (
                    <div>
                      <span className="text-[10px] text-[#64748B] block font-mono uppercase tracking-wider">Transaction Amount</span>
                      <span className="font-mono font-bold text-[#F8FAFC] text-sm">{selectedEdge.amount}</span>
                    </div>
                  )}
                </div>

                {selectedEdge.evidenceId && (
                  <div className="p-4 bg-amber-950/30 rounded-2xl border border-amber-800/60 text-xs space-y-3">
                    <div className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#FACC15]">
                      Supporting Evidence
                    </div>
                    <div className="font-mono font-bold text-[#F8FAFC] text-sm">{selectedEdge.evidenceId}</div>
                    <button
                      onClick={() => navigateTo('records', { recordId: selectedEdge.evidenceId })}
                      className="w-full py-2 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center justify-center space-x-1.5 transition-colors rounded-full cursor-pointer"
                    >
                      <span>Inspect Evidence Record</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};
