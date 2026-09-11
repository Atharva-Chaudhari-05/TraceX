import React, { useState } from 'react';
import {
  Database,
  Plus,
  CheckCircle2,
  FileText,
  PhoneCall,
  CreditCard,
  Radio,
  Clock,
  UploadCloud,
  Cpu,
  ArrowRight,
  Sparkles,
  Layers,
  FileSpreadsheet,
  Building,
  Car,
  Globe,
  ShieldAlert,
  Eye,
  X,
  FileUp,
  File,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export const DataSourcesView: React.FC = () => {
  const { dataSources, addDataSource, navigateTo } = useInvestigation();

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedSourceType, setSelectedSourceType] = useState<string>('cctns');
  const [sourceName, setSourceName] = useState<string>('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [ingestionStep, setIngestionStep] = useState<number>(0);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const getSourceIcon = (name: string) => {
    if (name.includes('Police') || name.includes('CCTNS') || name.includes('FIR'))
      return <FileText className="w-5 h-5 text-[#FACC15]" />;
    if (name.includes('Telecom') || name.includes('CDR') || name.includes('Airtel'))
      return <PhoneCall className="w-5 h-5 text-emerald-400" />;
    if (name.includes('Banking') || name.includes('SFMS') || name.includes('SBI'))
      return <CreditCard className="w-5 h-5 text-amber-400" />;
    if (name.includes('Corporate') || name.includes('MCA'))
      return <Building className="w-5 h-5 text-indigo-400" />;
    if (name.includes('Social') || name.includes('OSINT') || name.includes('Dark Web'))
      return <Globe className="w-5 h-5 text-pink-400" />;
    if (name.includes('Criminal') || name.includes('ICJS') || name.includes('Warrant'))
      return <ShieldAlert className="w-5 h-5 text-red-400" />;
    if (name.includes('FIU') || name.includes('Intelligence') || name.includes('STR'))
      return <Eye className="w-5 h-5 text-yellow-300" />;
    return <Radio className="w-5 h-5 text-rose-400" />;
  };

  const handleStartIngestion = () => {
    setIsProcessing(true);
    setIngestionStep(1);

    setTimeout(() => {
      setIngestionStep(2);
      setTimeout(() => {
        setIngestionStep(3);
        setTimeout(() => {
          setIngestionStep(4);
          setIsProcessing(false);

          const name =
            sourceName.trim() ||
            (selectedSourceType === 'cctns'
              ? 'State CCTNS Police FIR Supplementary Dairy'
              : selectedSourceType === 'cdr'
              ? 'Airtel & Jio Intercept Tower Dump (MUM-C4-89)'
              : selectedSourceType === 'banking'
              ? 'Core Banking SFMS Swift Wire Matrix'
              : selectedSourceType === 'anpr'
              ? 'Smart City ANPR Camera Optical Stream'
              : selectedSourceType === 'osint'
              ? 'Telegram Hawala Escrow & Darknet Forum Chatter'
              : selectedSourceType === 'criminal_records'
              ? 'ICJS Central Offender Database & Inter-State Warrants'
              : 'FIU-IND Suspicious Transaction Report (STR/SAR)');

          addDataSource({
            name,
            category: 'State Integrated Multimodal Feed',
            recordCount: Math.floor(Math.random() * 4) + 2,
            sourceSystem: 'State Integrated Ingestion Pipeline',
            fileFormat: selectedSourceType.toUpperCase(),
            records: ['EV-001', 'EV-002'],
            description: 'Automated data feed ingested and resolved into Operation Nexus graph ontology.',
          });
        }, 800);
      }, 700);
    }, 700);
  };

  const resetModal = () => {
    setIsModalOpen(false);
    setIngestionStep(0);
    setIsProcessing(false);
    setSourceName('');
    setUploadedFile(null);
    setIsDragging(false);
  };

  const handleFileSelect = (file: File) => {
    setUploadedFile(file);
    if (!sourceName) {
      const cleanName = file.name
        .replace(/\.[^/.]+$/, '')
        .toUpperCase()
        .replace(/[^A-Z0-9_]/g, '_');
      setSourceName(cleanName);
    }
  };

  const STREAM_FORMAT_HINTS: Record<string, { label: string; formats: string; accept: string }> = {
    cctns: {
      label: 'Police Reports & FIRs (CCTNS Case Diaries)',
      formats: '.pdf, .txt, .docx',
      accept: '.pdf,.txt,.docx',
    },
    cdr: {
      label: 'Communication Records (Telecom CDR & Tower Logs)',
      formats: '.csv, .xlsx, .tsv',
      accept: '.csv,.xlsx,.tsv',
    },
    banking: {
      label: 'Financial Records (Core Banking SFMS & RTGS)',
      formats: '.xml, .csv, .json, .xlsx',
      accept: '.xml,.csv,.json,.xlsx',
    },
    anpr: {
      label: 'Surveillance & Transit (Smart City ANPR Optical)',
      formats: '.csv, .json, .jpg, .png',
      accept: '.csv,.json,.jpg,.jpeg,.png',
    },
    osint: {
      label: 'Social Media OSINT (Dark Web & Telegram Feeds)',
      formats: '.json, .txt, .html',
      accept: '.json,.txt,.html',
    },
    criminal_records: {
      label: 'Criminal History (ICJS Warrants & Prior Arrests)',
      formats: '.pdf, .xml, .csv',
      accept: '.pdf,.xml,.csv',
    },
    intel_reports: {
      label: 'Intelligence Agency (FIU-IND STR/SAR Alerts)',
      formats: '.xml, .str, .pdf, .json',
      accept: '.xml,.str,.pdf,.json',
    },
  };

  return (
    <div id="data-sources-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header & Ingestion Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel border border-white/10 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center space-x-2 text-[10px] uppercase tracking-[0.25em] text-[#FACC15] font-mono mb-1 font-semibold">
            Multimodal Ingestion Pipeline • 7 Input Feeds
          </div>
          <h1 className="text-2xl font-bold font-mono text-[#F8FAFC] flex items-center space-x-3">
            <span>Data Feeds &amp; NLP Ingestion Hub</span>
            <span className="text-xs font-mono bg-[#050507]/80 text-[#FACC15] px-3 py-1 border border-[#FACC15]/40 rounded-full font-semibold shadow-xs">
              {dataSources.length} Connected State Feeds
            </span>
          </h1>
          <p className="text-xs text-[#94A3B8] mt-1.5 max-w-2xl font-sans leading-relaxed">
            TraceX unifies fragmented data across 7 core input factors: CCTNS case diaries, telecom CDR dumps, core banking SFMS wires, smart city ANPR, social media OSINT, criminal records (ICJS), and FIU-IND suspicious activity reports.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-5 py-2.5 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-bold font-mono uppercase tracking-wider flex items-center space-x-2 rounded-full shadow-lg transition-all shrink-0 cursor-pointer"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Ingest Data Stream</span>
        </button>
      </div>

      {/* Pipeline Status Overview */}
      <div className="glass-panel p-6 border border-white/10 rounded-2xl shadow-lg space-y-4">
        <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#FACC15] font-semibold flex items-center justify-between">
          <span>Automated Ingestion &amp; Entity Resolution Pipeline</span>
          <span className="text-xs text-[#64748B] font-mono">ISO/IEC 27037 Certified</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div className="p-4.5 glass-card border border-white/10 rounded-2xl space-y-1 shadow-sm">
            <span className="text-[#64748B] block text-[10px] uppercase">STAGE 1</span>
            <strong className="text-[#F8FAFC] block font-mono">Raw Data Acquisition</strong>
            <span className="text-[#94A3B8] text-[11px] font-sans">7 Input Feeds &amp; Multi-Agency Connectors</span>
          </div>
          <div className="p-4.5 glass-card border border-white/10 rounded-2xl space-y-1 shadow-sm">
            <span className="text-[#64748B] block text-[10px] uppercase">STAGE 2</span>
            <strong className="text-[#FACC15] block font-mono">Forensic Checksum</strong>
            <span className="text-[#94A3B8] text-[11px] font-sans">SHA-256 ISO/IEC 27037 Chain of Custody Seal</span>
          </div>
          <div className="p-4.5 glass-card border border-white/10 rounded-2xl space-y-1 shadow-sm">
            <span className="text-[#64748B] block text-[10px] uppercase">STAGE 3</span>
            <strong className="text-amber-400 block font-mono">spaCy NLP Extraction</strong>
            <span className="text-[#94A3B8] text-[11px] font-sans">NER Token Tagging &amp; Identifier Disambiguation</span>
          </div>
          <div className="p-4.5 glass-card border border-white/10 rounded-2xl space-y-1 shadow-sm">
            <span className="text-[#64748B] block text-[10px] uppercase">STAGE 4</span>
            <strong className="text-emerald-400 block font-mono">Graph Ingestion</strong>
            <span className="text-[#94A3B8] text-[11px] font-sans">Topological Graph Injection &amp; Path Indexing</span>
          </div>
        </div>
      </div>

      {/* Connected Feeds Grid (7 Input Factors) */}
      <div className="space-y-4">
        <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#FACC15] font-semibold flex items-center justify-between">
          <span>Active 7-Factor Intelligence Repositories</span>
          <span className="text-xs text-[#94A3B8] font-mono">{dataSources.length} Feeds Streamed Live</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {dataSources.map((source, index) => (
            <div
              key={index}
              className="glass-card glass-card-hover border border-white/10 p-6 rounded-3xl shadow-lg transition-all flex flex-col justify-between group"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="p-3 glass-card rounded-2xl border border-white/10 group-hover:border-[#FACC15]/40 transition-colors">
                    {getSourceIcon(source.name)}
                  </div>
                  <span className="text-[10px] font-mono px-2.5 py-1 border border-emerald-800/60 bg-emerald-950/40 text-emerald-400 font-bold uppercase rounded-full">
                    ACTIVE FEED
                  </span>
                </div>

                <div>
                  <h2 className="text-base font-bold text-[#F8FAFC] group-hover:text-[#FACC15] transition-colors font-mono">
                    {source.name}
                  </h2>
                  <div className="text-xs text-[#64748B] font-mono mt-0.5">
                    {source.category} • Format: {source.fileFormat}
                  </div>
                </div>

                <p className="text-xs text-[#94A3B8] leading-relaxed font-sans">
                  {source.description}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono">
                <span className="text-[#94A3B8]">
                  Records: <strong className="text-[#F8FAFC]">{source.recordCount}</strong>
                </span>
                <button
                  onClick={() => navigateTo('records')}
                  className="text-[#FACC15] hover:underline flex items-center space-x-1 cursor-pointer font-semibold"
                >
                  <span>Inspect Records</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Ingestion Modal Simulator */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-md">
          <div className="w-full max-w-xl glass-panel border border-white/20 rounded-3xl shadow-2xl overflow-hidden backdrop-blur-2xl">
            <div className="p-5 border-b border-white/10 flex items-center justify-between bg-[#050507]/60">
              <div className="flex items-center space-x-2">
                <UploadCloud className="w-5 h-5 text-[#FACC15]" />
                <h3 className="font-bold text-[#F8FAFC] font-mono text-sm">
                  Simulate 7-Factor Feed Ingestion &amp; Extraction
                </h3>
              </div>
              <button
                onClick={resetModal}
                className="w-7 h-7 rounded-full flex items-center justify-center text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-white/10 transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-5 text-xs">
              {ingestionStep === 0 && (
                <>
                  <div className="space-y-2">
                    <label className="text-[#94A3B8] font-mono block uppercase tracking-wider text-[11px]">
                      Select 1 of 7 State Data Stream Classifications:
                    </label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {[
                        { id: 'cctns', label: '1. Police Reports & FIRs', sub: 'CCTNS Case Diaries' },
                        { id: 'cdr', label: '2. Communication Records', sub: 'Telecom CDR & Tower Logs' },
                        { id: 'banking', label: '3. Financial Records', sub: 'Core Banking SFMS & RTGS' },
                        { id: 'anpr', label: '4. Surveillance & Transit', sub: 'Smart City ANPR Optical' },
                        { id: 'osint', label: '5. Social Media OSINT', sub: 'Dark Web & Telegram Feeds' },
                        { id: 'criminal_records', label: '6. Criminal History (ICJS)', sub: 'NCRB Warrants & Prior Arrests' },
                        { id: 'intel_reports', label: '7. Intelligence Agency (FIU)', sub: 'FIU-IND STR/SAR Suspicious Alerts' },
                      ].map((type) => (
                        <button
                          key={type.id}
                          onClick={() => setSelectedSourceType(type.id)}
                          className={`p-3 text-left border rounded-xl font-mono transition-all cursor-pointer ${
                            selectedSourceType === type.id
                              ? 'bg-[#FACC15]/15 border-[#FACC15] text-[#FACC15] font-bold shadow-md'
                              : 'glass-card border-white/10 text-[#94A3B8] hover:border-white/20'
                          }`}
                        >
                          <div className="font-semibold text-xs text-[#F8FAFC]">{type.label}</div>
                          <div className="text-[10px] text-[#64748B] mt-0.5 font-sans">{type.sub}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* File Upload Dropzone for the 7 Input Factors */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-[#94A3B8] font-mono block uppercase tracking-wider text-[11px]">
                        Upload Source Evidence / Intercept File:
                      </label>
                      <span className="text-[10px] font-mono text-[#FACC15]">
                        Formats: {STREAM_FORMAT_HINTS[selectedSourceType]?.formats || '.pdf, .csv, .json'}
                      </span>
                    </div>

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept={STREAM_FORMAT_HINTS[selectedSourceType]?.accept || '*'}
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          handleFileSelect(e.target.files[0]);
                        }
                      }}
                      className="hidden"
                    />

                    {!uploadedFile ? (
                      <div
                        onDragOver={(e) => {
                          e.preventDefault();
                          setIsDragging(true);
                        }}
                        onDragLeave={() => setIsDragging(false)}
                        onDrop={(e) => {
                          e.preventDefault();
                          setIsDragging(false);
                          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                            handleFileSelect(e.dataTransfer.files[0]);
                          }
                        }}
                        onClick={() => fileInputRef.current?.click()}
                        className={`border-2 border-dashed rounded-2xl p-4 text-center cursor-pointer transition-all ${
                          isDragging
                            ? 'border-[#FACC15] bg-[#FACC15]/10'
                            : 'border-white/20 hover:border-[#FACC15]/60 bg-[#050507]/60 hover:bg-white/5'
                        }`}
                      >
                        <div className="flex flex-col items-center justify-center space-y-2">
                          <div className="w-10 h-10 rounded-full bg-[#FACC15]/10 border border-[#FACC15]/30 flex items-center justify-center text-[#FACC15]">
                            <FileUp className="w-5 h-5" />
                          </div>
                          <div>
                            <span className="text-xs font-semibold text-[#F8FAFC]">
                              Click to browse or drop {STREAM_FORMAT_HINTS[selectedSourceType]?.label.split(' ')[0]} file here
                            </span>
                            <p className="text-[10px] text-[#64748B] font-mono mt-0.5">
                              Accepts {STREAM_FORMAT_HINTS[selectedSourceType]?.formats} (Max 100MB • Auto SHA-256 Hashing)
                            </p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="p-3 glass-card rounded-2xl border border-[#FACC15]/40 bg-[#FACC15]/5 flex items-center justify-between">
                        <div className="flex items-center space-x-3 min-w-0">
                          <div className="w-9 h-9 rounded-xl bg-[#FACC15]/20 border border-[#FACC15]/40 flex items-center justify-center text-[#FACC15] shrink-0">
                            <File className="w-5 h-5" />
                          </div>
                          <div className="min-w-0">
                            <div className="text-xs font-bold text-[#F8FAFC] truncate font-mono">
                              {uploadedFile.name}
                            </div>
                            <div className="text-[10px] font-mono text-[#64748B] flex items-center space-x-2">
                              <span>{(uploadedFile.size / 1024).toFixed(1)} KB</span>
                              <span>•</span>
                              <span className="text-emerald-400 font-semibold">SHA-256 Verified</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2 shrink-0">
                          <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            className="px-2.5 py-1 text-[10px] font-mono text-[#FACC15] hover:bg-[#FACC15]/10 rounded-lg border border-[#FACC15]/30 transition-colors cursor-pointer"
                          >
                            Change
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setUploadedFile(null);
                              setSourceName('');
                            }}
                            className="p-1 text-[#EF4444] hover:bg-[#EF4444]/10 rounded-lg transition-colors cursor-pointer"
                            title="Remove file"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-[#94A3B8] font-mono block uppercase tracking-wider text-[11px]">
                      Feed Identifier / File Name:
                    </label>
                    <input
                      type="text"
                      value={sourceName}
                      onChange={(e) => setSourceName(e.target.value)}
                      placeholder="e.g. CCTNS_FIR_2026_094_CRIMINAL_DIARY"
                      className="w-full p-2.5 glass-card rounded-xl border border-white/10 text-[#F8FAFC] font-mono text-xs focus:outline-none focus:border-[#FACC15]"
                    />
                  </div>

                  <button
                    onClick={handleStartIngestion}
                    className="w-full py-3 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] font-mono font-bold uppercase tracking-wider text-xs transition-all rounded-full shadow-lg cursor-pointer"
                  >
                    Execute Ingestion Pipeline
                  </button>
                </>
              )}

              {isProcessing && (
                <div className="py-6 space-y-4 text-center font-mono">
                  <Cpu className="w-8 h-8 text-[#FACC15] mx-auto animate-spin" />
                  <div className="space-y-1">
                    <div className="text-sm font-bold text-[#F8FAFC]">
                      {ingestionStep === 1 && 'Acquiring Stream & Hashing SHA-256...'}
                      {ingestionStep === 2 && 'Executing spaCy Named Entity Recognition...'}
                      {ingestionStep === 3 && 'Aligning Probabilistic Deduplication Vectors...'}
                      {ingestionStep === 4 && 'Injecting Nodes & Edges into Knowledge Graph...'}
                    </div>
                    <div className="text-xs text-[#64748B]">
                      ISO/IEC 27037 compliance verification in progress...
                    </div>
                  </div>
                </div>
              )}

              {ingestionStep === 4 && !isProcessing && (
                <div className="py-6 space-y-4 text-center font-mono">
                  <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
                  <div className="space-y-1">
                    <div className="text-sm font-bold text-[#F8FAFC]">
                      Feed Ingestion &amp; Graph Mapping Complete
                    </div>
                    <p className="text-xs text-[#94A3B8] font-sans">
                      Entities successfully extracted and linked to Operation Nexus topology.
                    </p>
                  </div>
                  <div className="pt-2 flex items-center justify-center space-x-2">
                    <button
                      onClick={() => {
                        resetModal();
                        navigateTo('records');
                      }}
                      className="px-4 py-2 bg-[#FACC15] text-[#050507] font-bold text-xs uppercase"
                    >
                      View Extracted Records
                    </button>
                    <button
                      onClick={resetModal}
                      className="px-4 py-2 bg-[#050507] text-[#94A3B8] border border-[#334155] text-xs uppercase"
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
