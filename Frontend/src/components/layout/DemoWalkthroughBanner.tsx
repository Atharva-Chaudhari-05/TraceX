import React from 'react';
import {
  Sparkles,
  ChevronRight,
  ChevronLeft,
  X,
  RotateCcw,
  CheckCircle2,
  GitPullRequest,
  ShieldCheck,
  FileText,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export const DemoWalkthroughBanner: React.FC = () => {
  const {
    demoStep,
    setDemoStep,
    nextDemoStep,
    prevDemoStep,
    resetDemoStep,
    isDemoBannerVisible,
    setIsDemoBannerVisible,
    entityMatch,
    approveEntityMatch,
    showHiddenConnection,
    setShowHiddenConnection,
    navigateTo,
  } = useInvestigation();

  if (!isDemoBannerVisible || demoStep === 0) {
    return null;
  }

  const stepsInfo = [
    {
      step: 1,
      title: 'Step 1: Case Overview & Priority Briefing',
      actionPrompt: 'Examine active Operation Nexus dossier, high-level KPIs, 82% Source vs 18% AI Synthetic provenance gauge.',
      badge: 'Case Ingestion',
      view: 'overview',
    },
    {
      step: 2,
      title: 'Step 2: Fragmented Investigation Records & NLP Extraction',
      actionPrompt: 'Review raw surveillance SITREP (EV-001) and lawful telecom CDR (EV-002) with live NER token highlighting.',
      badge: 'Data Processing',
      view: 'records',
    },
    {
      step: 3,
      title: 'Step 3: AI Entity Resolution (Deduplication)',
      actionPrompt: 'Review candidate identity match: Ajay Patil ↔ A. Patil (94% confidence, exact mobile + address match).',
      badge: 'Identity Linkage',
      view: 'resolution',
    },
    {
      step: 4,
      title: 'Step 4: Fullscreen Investigation Graph Exploration',
      actionPrompt: 'Interact with the 2D physics network graph of 15 nodes and inspect Cell Alpha, Beta, and Gamma clusters.',
      badge: 'Network Analysis',
      view: 'graph',
    },
    {
      step: 5,
      title: 'Step 5: Uncover the Hidden 5-Hop Hawala Conduit',
      actionPrompt: 'Observe the glowing 5-hop indirect path connecting street suspect Rahul Sharma to corporate shell XYZ Traders.',
      badge: 'AI Path Tracer',
      view: 'graph',
    },
    {
      step: 6,
      title: 'Step 6: Evidentiary Custody & Court-Ready Report Export',
      actionPrompt: 'Inspect ISO 27037 chain-of-custody seals and generate Section 65B certified court dossiers with JSON export.',
      badge: 'Court Admissibility',
      view: 'reports',
    },
  ];

  const currentStepInfo = stepsInfo[demoStep - 1] || stepsInfo[0];

  return (
    <div
      id="demo-walkthrough-banner"
      className="bg-[#0E0E12] border-b border-[#FACC15]/40 text-[#F8FAFC] px-4 sm:px-6 py-2.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xl transition-all sticky top-0 z-30 shrink-0 select-none"
    >
      {/* Left: Step Indicator & Story */}
      <div className="flex items-center space-x-3.5 min-w-0">
        <div className="flex items-center space-x-1.5 shrink-0">
          <div className="w-6 h-6 bg-[#FACC15] flex items-center justify-center text-[#050507] text-xs font-mono font-bold rounded-xs shadow-xs">
            {demoStep}
          </div>
          <span className="text-xs font-semibold text-[#FACC15] font-mono hidden md:inline">
            / 6
          </span>
        </div>

        <div className="min-w-0">
          <div className="flex items-center space-x-2.5">
            <span className="text-xs font-bold text-[#F8FAFC] tracking-wide truncate">
              {currentStepInfo.title}
            </span>
            <span className="text-[9px] font-mono uppercase tracking-widest px-2 py-0.5 bg-[#050507] text-[#FACC15] border border-[#FACC15]/40 rounded-xs shrink-0 font-semibold">
              {currentStepInfo.badge}
            </span>
          </div>
          <p className="text-[11px] text-[#94A3B8] truncate max-w-2xl mt-0.5">
            {currentStepInfo.actionPrompt}
          </p>
        </div>
      </div>

      {/* Center & Right: Contextual Quick-Action for this step */}
      <div className="flex items-center space-x-2.5 self-end sm:self-center shrink-0">
        {demoStep === 3 && entityMatch.status === 'pending' && (
          <button
            type="button"
            onClick={() => approveEntityMatch()}
            className="flex items-center space-x-1.5 px-3 py-1 text-xs font-mono font-bold uppercase tracking-wider bg-[#10B981] hover:bg-[#059669] text-[#050507] transition-colors rounded-xs shadow-xs"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Approve 94% Match</span>
          </button>
        )}

        {demoStep === 5 && !showHiddenConnection && (
          <button
            type="button"
            onClick={() => setShowHiddenConnection(true)}
            className="flex items-center space-x-1.5 px-3 py-1 text-xs font-mono font-bold uppercase tracking-wider bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] transition-colors rounded-xs shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Highlight 5-Hop Path</span>
          </button>
        )}

        {demoStep === 6 && (
          <button
            type="button"
            onClick={() => navigateTo('reports')}
            className="flex items-center space-x-1.5 px-3 py-1 text-xs font-mono font-bold uppercase tracking-wider bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] transition-colors rounded-xs shadow-xs"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>View Sec 65B Dossier</span>
          </button>
        )}

        {/* Step Navigation Controls */}
        <div className="flex items-center space-x-1 bg-[#050507] p-0.5 border border-[#27272A] rounded-xs">
          <button
            type="button"
            onClick={prevDemoStep}
            disabled={demoStep <= 1}
            className="p-1 text-[#94A3B8] hover:text-[#F8FAFC] disabled:opacity-30 disabled:hover:text-[#94A3B8] hover:bg-[#18181C] rounded-xs transition-colors"
            title="Previous Step"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>

          {/* Stepper Dots */}
          <div className="flex items-center space-x-1.5 px-2">
            {[1, 2, 3, 4, 5, 6].map((st) => (
              <button
                key={st}
                type="button"
                onClick={() => {
                  setDemoStep(st);
                  if (st === 1) navigateTo('overview');
                  if (st === 2) navigateTo('records');
                  if (st === 3) navigateTo('resolution');
                  if (st === 4) navigateTo('graph', { highlightPath: false });
                  if (st === 5) navigateTo('graph', { highlightPath: true });
                  if (st === 6) navigateTo('reports');
                }}
                className={`h-1.5 rounded-full transition-all ${
                  demoStep === st
                    ? 'bg-[#FACC15] w-4'
                    : demoStep > st
                    ? 'bg-[#10B981] w-2'
                    : 'bg-[#27272A] hover:bg-[#71717A] w-2'
                }`}
                title={`Jump to Step ${st}`}
              />
            ))}
          </div>

          <button
            type="button"
            onClick={nextDemoStep}
            disabled={demoStep >= 6}
            className="p-1 text-[#94A3B8] hover:text-[#F8FAFC] disabled:opacity-30 disabled:hover:text-[#94A3B8] hover:bg-[#18181C] rounded-xs transition-colors"
            title="Next Step"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Reset & Dismiss */}
        <button
          type="button"
          onClick={resetDemoStep}
          className="p-1.5 text-[#94A3B8] hover:text-[#FACC15] hover:bg-[#18181C] rounded-xs transition-colors"
          title="Restart Demo From Step 1"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          onClick={() => setIsDemoBannerVisible(false)}
          className="p-1.5 text-[#94A3B8] hover:text-[#EF4444] hover:bg-[#18181C] rounded-xs transition-colors"
          title="Dismiss Banner"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
