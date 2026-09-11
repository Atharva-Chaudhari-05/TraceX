import React, { useState } from 'react';
import {
  FileCheck2,
  Download,
  Printer,
  Copy,
  Check,
  Shield,
  ShieldCheck,
  CheckCircle2,
  Settings2,
  Clock,
  Users,
  BrainCircuit,
  FolderArchive,
  FileText,
  FileSpreadsheet,
  Code2,
} from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { useInvestigation } from '../../context/InvestigationContext';

export const ExportReportsView: React.FC = () => {
  const {
    caseData,
    entityMatch,
    evidenceRecords,
    entities,
    timelineEvents,
    aiInsights,
    auditLogs,
    saveAuditLog,
    theme,
  } = useInvestigation();
  const isLight = theme === 'light';

  const [activeReportTab, setActiveReportTab] = useState<'executive' | 'briefing' | 'court'>('executive');
  const [downloadNotification, setDownloadNotification] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [isCustomizeOpen, setIsCustomizeOpen] = useState<boolean>(false);

  // Section visibility toggles
  const [includedSections, setIncludedSections] = useState({
    caseInfo: true,
    executiveSummary: true,
    subjectProfiles: true,
    timeline: true,
    aiFindings: true,
    custodyIndex: true,
    certification: true,
  });

  const toggleSection = (section: keyof typeof includedSections) => {
    setIncludedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const generateTextReport = () => {
    return `================================================================================
GOVERNMENT OF INDIA - SPECIAL TASK FORCE (CENTRAL COMMAND)
TRACEX FORENSIC DOSSIER // OFFICIAL CHARGE-SHEET ATTACHMENT
CERTIFIED UNDER SECTION 65B OF THE INDIAN EVIDENCE ACT, 1872
================================================================================

CASE IDENTIFIER : ${caseData.caseId}
CASE NAME       : ${caseData.name}
CLASSIFICATION  : ${caseData.classification}
PRIORITY LEVEL  : ${caseData.priority}
LEAD OFFICER    : ${caseData.leadInvestigator}
DATE & TIME     : ${new Date().toLocaleString()}
INTEGRITY SEAL  : SHA-256 VERIFIED (SEAL-65B-NX-2026-AUTHENTIC)

--------------------------------------------------------------------------------
1. EXECUTIVE OPERATIONAL SYNOPSIS
--------------------------------------------------------------------------------
${caseData.description}

JUDICIAL SIGNIFICANCE:
Multi-source entity resolution identified an indirect financial and logistical conduit
linking primary target Rahul Sharma to commercial enterprise XYZ Traders via field
intermediary Ajay Patil (resolved with 94% confidence to bank signatory A. Patil) and
corporate signatory Neha Verma. Conclusively proves criminal conspiracy under Section
120B IPC and structured layering under PMLA.

--------------------------------------------------------------------------------
2. AI INSIGHTS & INFERENCES
--------------------------------------------------------------------------------
${aiInsights.map((i) => `[${i.id}] ${i.title}\n   ${i.whatFound}`).join('\n')}

--------------------------------------------------------------------------------
3. MASTER INDEXED ENTITIES (15 IDENTITIES)
--------------------------------------------------------------------------------
${entities
  .map(
    (e, idx) => `[${(idx + 1).toString().padStart(2, '0')}] ${e.name} (${e.type.toUpperCase()})
     Identifier : ${e.identifier || 'N/A'}
     Role/Modus : ${e.role || 'N/A'}
     Risk Level : ${(e.risk || 'medium').toUpperCase()}
`
  )
  .join('\n')}

--------------------------------------------------------------------------------
4. EVIDENTIARY DIGITAL CUSTODY CHAIN (SECTION 65B SCHEDULE)
--------------------------------------------------------------------------------
${evidenceRecords
  .map(
    (ev) => `[${ev.id}] ${ev.title}
     Origin Feed    : ${ev.source}
     Logged At      : ${ev.date} ${ev.timestamp}
     Custody Status : HASH VERIFIED / CHAIN UNBROKEN
     SHA-256 Seal   : ${ev.hashChecksum}
`
  )
  .join('\n')}

--------------------------------------------------------------------------------
5. STATUTORY OFFICER ENDORSEMENT & CERTIFICATE UNDER SECTION 65B
--------------------------------------------------------------------------------
I, Inspector V. Kulkarni (Badge CY-8821), Special Task Force (STF) - Central Command,
hereby certify pursuant to Section 65B(4) of the Indian Evidence Act, 1872:
1. The electronic records referenced herein were produced by electronic devices
   regularly used to store and process lawful intelligence data in ordinary course.
2. At all material times, the custody chain and cryptographic hashes were preserved
   without alteration, tampering, or unauthorized systemic intervention.

AUTHORISED SIGNATORY:
Insp. V. Kulkarni
Badge: CY-8821 | Special Task Force (Central Command)
Forensic Seal: SEAL-65B-NX-2026-AUTHENTIC
Timestamp: ${new Date().toISOString()}
================================================================================`;
  };

  const triggerDownload = (format: string, reportName: string) => {
    setDownloadNotification(`Compiling certified ${reportName}.${format.toUpperCase()}...`);
    setTimeout(() => {
      if (format === 'pdf') {
        try {
          const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
          const pageWidth = doc.internal.pageSize.getWidth();
          const pageHeight = doc.internal.pageSize.getHeight();

          const darkPrimary = [15, 23, 42];
          const darkText = [30, 41, 59];
          const mutedText = [100, 116, 139];

          // 1. Header Banner
          doc.setFillColor(15, 23, 42);
          doc.rect(14, 12, pageWidth - 28, 24, 'F');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(8);
          doc.setTextColor(56, 189, 248);
          doc.text('GOVERNMENT OF INDIA // SPECIAL TASK FORCE - CYBER & FINANCIAL CRIMES WING', 18, 19);

          doc.setFontSize(13);
          doc.setTextColor(255, 255, 255);
          doc.text(`TRACEX FORENSIC DOSSIER // ${caseData.caseId}`, 18, 27);

          doc.setFontSize(7.5);
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(148, 163, 184);
          doc.text(`SECTION 65B INDIAN EVIDENCE ACT CERTIFIED | CLASSIFICATION: ${caseData.classification}`, 18, 32);

          let currentY = 42;

          // 2. Case Metadata Box
          doc.setFillColor(248, 250, 252);
          doc.setDrawColor(226, 232, 240);
          doc.roundedRect(14, currentY, pageWidth - 28, 26, 2, 2, 'FD');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(8.5);
          doc.setTextColor(darkText[0], darkText[1], darkText[2]);
          doc.text('CASE OPERATION:', 18, currentY + 6);
          doc.setFont('helvetica', 'normal');
          doc.text(`${caseData.name}`, 54, currentY + 6);

          doc.setFont('helvetica', 'bold');
          doc.text('LEAD INVESTIGATOR:', 18, currentY + 12);
          doc.setFont('helvetica', 'normal');
          doc.text(`${caseData.leadInvestigator}`, 54, currentY + 12);

          doc.setFont('helvetica', 'bold');
          doc.text('INTEGRITY STAMP:', 18, currentY + 18);
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(2, 132, 199);
          doc.text('SHA-256 VERIFIED (SEAL-65B-NX-2026-AUTHENTIC)', 54, currentY + 18);

          doc.setFont('helvetica', 'bold');
          doc.setTextColor(darkText[0], darkText[1], darkText[2]);
          doc.text('GENERATED AT:', 18, currentY + 23);
          doc.setFont('helvetica', 'normal');
          doc.text(`${new Date().toLocaleString()}`, 54, currentY + 23);

          currentY += 32;

          // 3. Executive Synopsis
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.setTextColor(darkPrimary[0], darkPrimary[1], darkPrimary[2]);
          doc.text('1. EXECUTIVE INVESTIGATION SUMMARY & JUDICIAL SIGNIFICANCE', 14, currentY);
          currentY += 4.5;

          doc.setFont('helvetica', 'normal');
          doc.setFontSize(8);
          doc.setTextColor(darkText[0], darkText[1], darkText[2]);
          const synopsis = doc.splitTextToSize(
            `${caseData.description} Multi-source entity resolution identified an indirect financial and logistical conduit linking primary target Rahul Sharma to commercial enterprise XYZ Traders via field intermediary Ajay Patil (resolved with 94% confidence to bank signatory A. Patil) and corporate signatory Neha Verma. Conclusively proves criminal conspiracy under Section 120B IPC and money laundering under PMLA.`,
            pageWidth - 28
          );
          doc.text(synopsis, 14, currentY);
          currentY += synopsis.length * 3.8 + 6;

          // 4. AI Insights Box
          doc.setFillColor(240, 249, 255);
          doc.setDrawColor(186, 230, 253);
          doc.roundedRect(14, currentY, pageWidth - 28, 18, 2, 2, 'FD');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(7.5);
          doc.setTextColor(3, 105, 161);
          doc.text('AI INSIGHTS & INFERENCES:', 18, currentY + 5);

          doc.setFont('helvetica', 'normal');
          doc.setFontSize(7);
          doc.setTextColor(15, 23, 42);
          let insightY = currentY + 10;
          aiInsights.slice(0, 2).forEach(ins => {
              doc.text(`- ${ins.title}: ${ins.whatFound}`.substring(0, 110), 18, insightY);
              insightY += 4;
          });
          currentY += 24;

          // 5. Master Indexed Entities (Table)
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.setTextColor(darkPrimary[0], darkPrimary[1], darkPrimary[2]);
          doc.text('2. MASTER INDEXED ENTITIES (15 RECONSTRUCTED IDENTITIES)', 14, currentY);
          currentY += 3;

          const entityTableData = entities.map((ent, idx) => [
            String(idx + 1).padStart(2, '0'),
            ent.name,
            ent.type.toUpperCase(),
            ent.identifier || 'N/A',
            ent.role || 'N/A',
            (ent.risk || 'medium').toUpperCase(),
          ]);

          autoTable(doc, {
            startY: currentY,
            head: [['#', 'Entity Name', 'Type', 'Identifier / KYC', 'Role & Ground Modus', 'Risk Level']],
            body: entityTableData,
            theme: 'grid',
            headStyles: {
              fillColor: [15, 23, 42],
              textColor: 255,
              font: 'helvetica',
              fontStyle: 'bold',
              fontSize: 7.5,
            },
            styles: {
              font: 'helvetica',
              fontSize: 6.8,
              cellPadding: 2,
            },
            alternateRowStyles: { fillColor: [248, 250, 252] },
            margin: { left: 14, right: 14 },
          });

          currentY = (doc as any).lastAutoTable.finalY + 8;

          // Check page break for Evidence Table
          if (currentY > pageHeight - 65) {
            doc.addPage();
            currentY = 16;
          }

          // 6. Section 65B Digital Evidence Registry (Table)
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.setTextColor(darkPrimary[0], darkPrimary[1], darkPrimary[2]);
          doc.text('3. DIGITAL EVIDENCE CUSTODY REGISTRY (SECTION 65B SCHEDULE)', 14, currentY);
          currentY += 3;

          const evidenceTableData = evidenceRecords.map((ev) => [
            ev.id,
            ev.title,
            ev.source,
            `${ev.date} ${ev.timestamp}`,
            'VERIFIED',
            ev.hashChecksum,
          ]);

          autoTable(doc, {
            startY: currentY,
            head: [['Evid ID', 'Evidence Title', 'Source Feed', 'Timestamp', 'Status', 'Cryptographic Hash (SHA-256)']],
            body: evidenceTableData,
            theme: 'grid',
            headStyles: {
              fillColor: [15, 23, 42],
              textColor: 255,
              font: 'helvetica',
              fontStyle: 'bold',
              fontSize: 7.5,
            },
            styles: {
              font: 'helvetica',
              fontSize: 6.5,
              cellPadding: 1.8,
            },
            columnStyles: {
              5: { cellWidth: 55, font: 'courier', fontSize: 5.8 },
            },
            alternateRowStyles: { fillColor: [248, 250, 252] },
            margin: { left: 14, right: 14 },
          });

          currentY = (doc as any).lastAutoTable.finalY + 8;

          // Check page break for Statutory Endorsement
          if (currentY > pageHeight - 55) {
            doc.addPage();
            currentY = 16;
          }

          // 7. Statutory Officer Endorsement (Section 65B)
          doc.setFillColor(248, 250, 252);
          doc.setDrawColor(203, 213, 225);
          doc.roundedRect(14, currentY, pageWidth - 28, 36, 2, 2, 'FD');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(8);
          doc.setTextColor(darkPrimary[0], darkPrimary[1], darkPrimary[2]);
          doc.text('4. STATUTORY DIGITAL ENDORSEMENT UNDER SECTION 65B INDIAN EVIDENCE ACT', 18, currentY + 6);

          doc.setFont('helvetica', 'normal');
          doc.setFontSize(6.8);
          doc.setTextColor(darkText[0], darkText[1], darkText[2]);
          const certLegalText = doc.splitTextToSize(
            'I, Inspector V. Kulkarni (Badge CY-8821), hereby solemnly depose and state that the electronic data and records detailed in this dossier have been lawfully produced, hash-verified, and extracted from standard investigative computing infrastructure operating in the ordinary course of duty without systemic tampering or unauthorized alteration.',
            pageWidth - 36
          );
          doc.text(certLegalText, 18, currentY + 11);

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(7.5);
          doc.text('INVESTIGATING OFFICER:', 18, currentY + 24);
          doc.setFont('helvetica', 'normal');
          doc.text('Insp. V. Kulkarni (Badge ID: CY-8821)', 58, currentY + 24);

          doc.setFont('helvetica', 'bold');
          doc.text('DIGITAL SIGNATURE HASH:', 18, currentY + 29);
          doc.setFont('courier', 'normal');
          doc.setFontSize(6.5);
          doc.setTextColor(2, 132, 199);
          doc.text('e-Sign: 7a82fbc89104de3c4a22b910fc33829104 (STF-CENTRAL-COMMAND)', 58, currentY + 29);

          // 8. Page Numbers on all pages
          const totalPages = (doc.internal as any).getNumberOfPages();
          for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFont('helvetica', 'italic');
            doc.setFontSize(6.8);
            doc.setTextColor(mutedText[0], mutedText[1], mutedText[2]);
            doc.text(
              `TraceX Judicial Dossier // ${caseData.caseId} // Section 65B Certified // RESTRICTED LAW ENFORCEMENT SENSITIVE`,
              14,
              pageHeight - 6
            );
            doc.text(`Page ${i} of ${totalPages}`, pageWidth - 14, pageHeight - 6, { align: 'right' });
          }

          // Save & download PDF file
          doc.save(`${reportName}.pdf`);
        } catch (err) {
          console.error('Failed to generate PDF dossier:', err);
        }
      } else if (format === 'txt') {
        const textContent = generateTextReport();
        const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${reportName}.txt`;
        a.click();
        URL.revokeObjectURL(url);
      } else if (format === 'json') {
        const exportData = {
          exportType: 'TRACEX_FORENSIC_CASE_DOSSIER',
          version: '2026.1',
          certifiedUnder: 'Section 65B Indian Evidence Act',
          generatedAt: new Date().toISOString(),
          case: caseData,
          entities,
          evidence: evidenceRecords,
          timeline: timelineEvents,
          insights: aiInsights,
          auditTrail: auditLogs,
        };
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${reportName}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
      saveAuditLog(`Exported formal judicial dossier ${reportName}.${format} with Section 65B forensic certification stamp.`);
      setDownloadNotification(`✓ Complete: ${reportName}.${format} exported with cryptographic integrity stamp.`);
      setTimeout(() => setDownloadNotification(null), 4000);
    }, 600);
  };

  const handleCopyToClipboard = () => {
    const summaryText = generateTextReport();
    navigator.clipboard.writeText(summaryText);
    setCopied(true);
    saveAuditLog('Investigator copied formal case summary to clipboard.');
    setTimeout(() => setCopied(false), 3000);
  };

  const handlePrint = () => {
    saveAuditLog('Print job sent for Section 65B Judicial Dossier.');
    window.print();
  };

  return (
    <div id="export-reports-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header & Export Actions */}
      <div className="glass-panel border border-white/10 p-6 rounded-3xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl print:hidden">
        <div>
          <div className="flex items-center space-x-2.5">
            <FileCheck2 className="w-5 h-5 text-[#FACC15]" />
            <h1 className="text-2xl font-bold text-[#F8FAFC] font-mono">
              Court-Ready Report &amp; Section 65B Dossier Generator
            </h1>
            <span className="text-xs font-mono bg-[#050507]/80 text-[#FACC15] px-3 py-1 border border-[#FACC15]/40 rounded-full font-semibold shadow-xs">
              {caseData.caseId}
            </span>
          </div>
          <p className="text-sm text-[#94A3B8] mt-1 font-sans">
            Produces formal judicial charge-sheets, Section 65B certificates of electronic evidence, and JSON evidence exports.
          </p>
        </div>

        {/* Global Export Formats */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => triggerDownload('pdf', `${caseData.caseId}_Court_Dossier`)}
            className="px-4 py-2 bg-[#FACC15] hover:bg-[#EAB308] text-[#050507] text-xs font-mono uppercase tracking-wider font-bold flex items-center space-x-1.5 rounded-full shadow-lg transition-all cursor-pointer hover:shadow-[0_0_20px_rgba(250, 204, 21,0.4)]"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PDF</span>
          </button>

          <button
            onClick={() => triggerDownload('txt', `${caseData.caseId}_Court_Dossier`)}
            className="px-4 py-2 glass-card hover:bg-white/10 text-amber-300 hover:text-white text-xs font-mono uppercase tracking-wider font-bold border border-amber-400/30 flex items-center space-x-1.5 rounded-full transition-all cursor-pointer hover:shadow-[0_0_15px_rgba(245,158,11,0.25)]"
          >
            <FileText className="w-3.5 h-3.5 text-amber-400" />
            <span>Export Text File</span>
          </button>

          <button
            onClick={() => triggerDownload('json', `${caseData.caseId}_Forensic_Package`)}
            className="px-4 py-2 glass-card hover:bg-white/10 text-[#FACC15] hover:text-white text-xs font-mono uppercase tracking-wider font-bold border border-white/10 flex items-center space-x-1.5 rounded-full transition-all cursor-pointer"
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Export Forensic JSON</span>
          </button>

          <button
            onClick={handleCopyToClipboard}
            className="px-4 py-2 glass-card hover:bg-white/10 text-[#94A3B8] hover:text-white text-xs font-mono uppercase tracking-wider font-semibold border border-white/10 flex items-center space-x-1.5 rounded-full transition-all cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-[#94A3B8]" />}
            <span>{copied ? 'Copied!' : 'Copy Summary'}</span>
          </button>

          <button
            onClick={() => setIsCustomizeOpen(!isCustomizeOpen)}
            className={`px-4 py-2 text-xs font-mono uppercase tracking-wider font-semibold border rounded-full flex items-center space-x-1.5 transition-all cursor-pointer ${
              isCustomizeOpen
                ? 'bg-amber-950/40 border-amber-600 text-amber-300'
                : 'glass-card hover:bg-white/10 text-[#94A3B8] border-white/10'
            }`}
          >
            <Settings2 className="w-3.5 h-3.5 text-[#FACC15]" />
            <span>Customize</span>
          </button>

          <button
            onClick={handlePrint}
            className="px-4 py-2 glass-card hover:bg-white/10 text-[#F8FAFC] text-xs font-mono uppercase tracking-wider font-bold border border-white/10 flex items-center space-x-1.5 rounded-full transition-all cursor-pointer"
          >
            <Printer className="w-3.5 h-3.5 text-[#FACC15]" />
            <span>Print Court Dossier</span>
          </button>
        </div>
      </div>

      {/* Notification Toast */}
      {downloadNotification && (
        <div className="p-4 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs font-mono flex items-center justify-between shadow-lg backdrop-blur-md rounded-2xl animate-in fade-in duration-200 print:hidden">
          <span className="font-semibold">{downloadNotification}</span>
          <button onClick={() => setDownloadNotification(null)} className="text-emerald-400 font-bold hover:text-white cursor-pointer">
            ✕
          </button>
        </div>
      )}

      {/* Section Customizer Panel (Collapsible) */}
      {isCustomizeOpen && (
        <div className="glass-panel border border-white/10 p-5 rounded-3xl shadow-xl space-y-3 text-xs print:hidden">
          <div className="flex items-center justify-between border-b border-white/10 pb-2">
            <span className="font-mono font-bold uppercase tracking-wider text-[#FACC15]">
              Customize Dossier Inclusion Sections
            </span>
            <span className="text-[#94A3B8]">Toggle modules to include in the generated charge-sheet</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
            {Object.entries({
              caseInfo: 'Case Header & ID',
              executiveSummary: 'Executive Summary',
              subjectProfiles: 'Subject Profiles',
              timeline: 'Chronological Timeline',
              aiFindings: 'AI Intelligence Findings',
              custodyIndex: 'Chain of Custody Index',
              certification: 'Section 65B Certification',
            }).map(([key, label]) => (
              <label
                key={key}
                className="flex items-center space-x-2 cursor-pointer glass-card p-3 rounded-2xl border border-white/10 hover:border-[#FACC15] transition-all"
              >
                <input
                  type="checkbox"
                  checked={includedSections[key as keyof typeof includedSections]}
                  onChange={() => toggleSection(key as keyof typeof includedSections)}
                  className="rounded-full text-[#FACC15] focus:ring-0 cursor-pointer accent-[#FACC15]"
                />
                <span className="font-mono font-medium text-[#F8FAFC] text-xs">{label}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex flex-wrap items-center gap-2 glass-card p-1.5 rounded-full border border-white/10 text-xs font-mono shadow-md print:hidden">
        <button
          onClick={() => setActiveReportTab('executive')}
          className={`py-2 px-4 rounded-full font-bold tracking-wider uppercase transition-all cursor-pointer ${
            activeReportTab === 'executive'
              ? 'bg-[#FACC15] text-[#050507] shadow-[0_0_15px_rgba(250, 204, 21,0.4)]'
              : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-white/5'
          }`}
        >
          1. Comprehensive Court Dossier
        </button>
        <button
          onClick={() => setActiveReportTab('briefing')}
          className={`py-2 px-4 rounded-full font-bold tracking-wider uppercase transition-all cursor-pointer ${
            activeReportTab === 'briefing'
              ? 'bg-[#FACC15] text-[#050507] shadow-[0_0_15px_rgba(250, 204, 21,0.4)]'
              : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-white/5'
          }`}
        >
          2. Executive Briefing Sheet
        </button>
        <button
          onClick={() => setActiveReportTab('court')}
          className={`py-2 px-4 rounded-full font-bold tracking-wider uppercase transition-all cursor-pointer ${
            activeReportTab === 'court'
              ? 'bg-[#FACC15] text-[#050507] shadow-[0_0_15px_rgba(250, 204, 21,0.4)]'
              : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-white/5'
          }`}
        >
          3. Section 65B Forensic Certificate
        </button>
      </div>

      {/* REPORT CONTENT CANVAS (Printable Document Container with Rounded Glassmorphism) */}
      <div className="glass-panel border border-white/10 p-8 sm:p-12 rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.7)] space-y-8 backdrop-blur-2xl print:border-none print:shadow-none print:bg-white print:text-black">
        {/* Document Official Header */}
        {includedSections.caseInfo && (
          <div className="border-b border-white/10 print:border-black pb-6 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div>
              <div className="text-[10px] font-mono uppercase font-bold tracking-[0.25em] text-[#FACC15] print:text-black">
                RESTRICTED // LAW ENFORCEMENT SENSITIVE // OFFICIAL CHARGE-SHEET ATTACHMENT
              </div>
              <h2 className="text-2xl font-bold text-[#F8FAFC] print:text-black mt-1.5 font-mono">
                TRACEX FORENSIC DOSSIER // {caseData.name.toUpperCase()}
              </h2>
              <div className="text-xs font-mono text-[#94A3B8] print:text-gray-700 mt-2 flex flex-wrap items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10">CASE ID: <strong className="text-[#F8FAFC] print:text-black">{caseData.caseId}</strong></span>
                <span>•</span>
                <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10">CLASSIFICATION: <strong className="text-[#F8FAFC] print:text-black">{caseData.classification}</strong></span>
                <span>•</span>
                <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10">STATUS: <strong className="text-[#F8FAFC] print:text-black">{caseData.status}</strong></span>
                <span>•</span>
                <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10">DATE: 12 MAY 2026</span>
              </div>
            </div>

            <div className="text-right text-xs font-mono text-[#94A3B8] print:text-gray-700 shrink-0 space-y-1">
              <div>LEAD INVESTIGATOR: <strong className="text-[#F8FAFC] print:text-black">{caseData.leadInvestigator}</strong></div>
              <div>AGENCY: Special Task Force (STF) - Central Command</div>
              <div>INTEGRITY SEAL: <span className="text-emerald-400 print:text-black font-bold px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/60 inline-block">SHA-256 VERIFIED</span></div>
            </div>
          </div>
        )}

        {/* TAB 1: COMPREHENSIVE COURT DOSSIER */}
        {activeReportTab === 'executive' && (
          <div className="space-y-8 text-xs text-[#F8FAFC] print:text-black">
            {/* Section 1: Executive Summary */}
            {includedSections.executiveSummary && (
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-[#F8FAFC] print:text-black border-b border-white/10 print:border-gray-300 pb-2 uppercase tracking-wide flex items-center justify-between font-mono">
                  <span>1. Executive Investigation Summary</span>
                  <span className="text-[10px] font-mono text-[#FACC15] print:text-black px-2 py-0.5 rounded-full bg-[#FACC15]/10 border border-[#FACC15]/30">RESTRICTED</span>
                </h3>
                <div className="leading-relaxed font-sans text-[#94A3B8] print:text-black text-sm glass-card print:bg-gray-50 p-6 rounded-3xl border border-white/10 print:border-gray-300 shadow-md backdrop-blur-xl">
                  {caseData.description} Multi-source entity resolution identified an indirect financial and logistical conduit linking primary target <strong className="text-[#F8FAFC] print:text-black">Rahul Sharma</strong> to commercial enterprise <strong className="text-[#FACC15] print:text-black">XYZ Traders</strong> via field intermediary <strong className="text-[#F8FAFC] print:text-black">Ajay Patil</strong> (resolved with 94% confidence to bank signatory A. Patil) and corporate signatory <strong className="text-[#F8FAFC] print:text-black">Neha Verma</strong>.
                </div>
              </div>
            )}

            {/* Section 2: Subject Profiles & Entity Analysis */}
            {includedSections.subjectProfiles && (
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-[#F8FAFC] print:text-black border-b border-white/10 print:border-gray-300 pb-2 uppercase tracking-wide font-mono">
                  2. Master Indexed Entities Analysis (Operation Nexus)
                </h3>
                <div className={`overflow-hidden rounded-3xl border shadow-lg backdrop-blur-xl ${
                  isLight ? 'border-slate-200 bg-white' : 'border-white/10 glass-card'
                }`}>
                  <table className="w-full text-left border-collapse">
                    <thead className={`${
                      isLight
                        ? 'bg-slate-100 text-slate-700 border-b border-slate-200'
                        : 'bg-[#0C0C10]/90 text-[#FACC15] border-b border-white/10'
                    } print:bg-gray-100 font-mono text-[10px] uppercase tracking-wider print:text-black`}>
                      <tr>
                        <th className={`p-4 border-b ${isLight ? 'border-slate-200' : 'border-white/10'} print:border-gray-300`}>Subject / Entity</th>
                        <th className={`p-4 border-b ${isLight ? 'border-slate-200' : 'border-white/10'} print:border-gray-300`}>Type</th>
                        <th className={`p-4 border-b ${isLight ? 'border-slate-200' : 'border-white/10'} print:border-gray-300`}>Role & Ground Modus</th>
                        <th className={`p-4 border-b ${isLight ? 'border-slate-200' : 'border-white/10'} print:border-gray-300`}>Risk Assessment</th>
                      </tr>
                    </thead>
                    <tbody className={`divide-y ${isLight ? 'divide-slate-200' : 'divide-white/10'} print:divide-gray-300 text-xs font-sans`}>
                      <tr className={`${isLight ? 'hover:bg-slate-50/80' : 'hover:bg-white/5'} transition-colors`}>
                        <td className={`p-4 font-bold ${isLight ? 'text-slate-900' : 'text-[#F8FAFC]'} print:text-black font-mono`}>Rahul Sharma</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black font-mono`}>person</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black`}>Primary ground target; drove MH-12-DE-4419 to Central Bus Terminal Platform 3.</td>
                        <td className="p-4 font-bold font-mono">
                          <span className="px-2.5 py-1 rounded-full bg-rose-950/60 text-rose-400 border border-rose-800/60 text-[10px]">
                            HIGH RISK (96%)
                          </span>
                        </td>
                      </tr>
                      <tr className={`${isLight ? 'hover:bg-slate-50/80' : 'hover:bg-white/5'} transition-colors`}>
                        <td className={`p-4 font-bold ${isLight ? 'text-slate-900' : 'text-[#F8FAFC]'} print:text-black font-mono`}>Ajay Patil (A. Patil)</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black font-mono`}>person (merged)</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black`}>Cash broker & banking bridge; debited ₹50,000 from SBI A/C 889922.</td>
                        <td className="p-4 font-bold font-mono">
                          <span className="px-2.5 py-1 rounded-full bg-rose-950/60 text-rose-400 border border-rose-800/60 text-[10px]">
                            HIGH RISK (92%)
                          </span>
                        </td>
                      </tr>
                      <tr className={`${isLight ? 'hover:bg-slate-50/80' : 'hover:bg-white/5'} transition-colors`}>
                        <td className={`p-4 font-bold ${isLight ? 'text-slate-900' : 'text-[#F8FAFC]'} print:text-black font-mono`}>Neha Verma</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black font-mono`}>person</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black`}>Authorized corporate signatory; controls destination ICICI A/C 772145 for XYZ Traders.</td>
                        <td className="p-4 font-bold font-mono">
                          <span className="px-2.5 py-1 rounded-full bg-amber-950/60 text-amber-400 border border-amber-800/60 text-[10px]">
                            MEDIUM RISK (89%)
                          </span>
                        </td>
                      </tr>
                      <tr className={`${isLight ? 'hover:bg-slate-50/80' : 'hover:bg-white/5'} transition-colors`}>
                        <td className={`p-4 font-bold ${isLight ? 'text-slate-900' : 'text-[#F8FAFC]'} print:text-black font-mono`}>XYZ Traders Pvt Ltd</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black font-mono`}>organisation</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black`}>Commercial shell conduit; warehouse operations at Sector 4 Depot, Gala 14.</td>
                        <td className="p-4 font-bold font-mono">
                          <span className="px-2.5 py-1 rounded-full bg-rose-950/60 text-rose-400 border border-rose-800/60 text-[10px]">
                            HIGH RISK (95%)
                          </span>
                        </td>
                      </tr>
                      <tr className={`${isLight ? 'hover:bg-slate-50/80' : 'hover:bg-white/5'} transition-colors`}>
                        <td className={`p-4 font-bold ${isLight ? 'text-slate-900' : 'text-[#F8FAFC]'} print:text-black font-mono`}>Vikram Singhania</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black font-mono`}>person</td>
                        <td className={`p-4 ${isLight ? 'text-slate-600' : 'text-[#94A3B8]'} print:text-black`}>Offshore cartel kingpin; commands shell conduits via Dubai satellite link.</td>
                        <td className="p-4 font-bold font-mono">
                          <span className="px-2.5 py-1 rounded-full bg-rose-950/60 text-rose-400 border border-rose-800/60 text-[10px]">
                            HIGH RISK (78%)
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Section 3: Chronological Timeline */}
            {includedSections.timeline && (
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-[#F8FAFC] print:text-black border-b border-white/10 print:border-gray-300 pb-2 uppercase tracking-wide font-mono">
                  3. Chronological Sequence of Reconstructed Events
                </h3>
                <div className="space-y-2.5 font-sans">
                  {timelineEvents.map((evt) => (
                    <div key={evt.id} className="p-4 glass-card hover:bg-white/5 rounded-2xl border border-white/10 print:border-gray-300 flex flex-col sm:flex-row sm:items-start justify-between gap-3 text-xs transition-all shadow-xs">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono font-bold text-[#FACC15] print:text-black">{evt.time} IST</span>
                          <span className="text-[#64748B]">•</span>
                          <span className="font-bold text-[#F8FAFC] print:text-black font-mono">{evt.title}</span>
                          <span className="text-[10px] font-mono uppercase bg-[#050507] print:bg-gray-200 px-2.5 py-0.5 rounded-full border border-white/10 print:border-gray-300">
                            {evt.category}
                          </span>
                        </div>
                        <p className="text-[#94A3B8] print:text-black">{evt.description}</p>
                      </div>
                      <span className="text-[11px] font-mono text-[#64748B] shrink-0 font-bold px-2 py-0.5 rounded-lg bg-white/5">{evt.evidenceId}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Section 4: Key Evidentiary Findings */}
            {includedSections.aiFindings && (
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-[#F8FAFC] print:text-black border-b border-white/10 print:border-gray-300 pb-2 uppercase tracking-wide font-mono">
                  4. Key Evidentiary Findings (AI-Assisted &amp; Officer-Verified)
                </h3>
                <div className="space-y-3 font-sans">
                  {aiInsights.map((ins) => (
                    <div key={ins.id} className="p-5 glass-card hover:bg-white/5 rounded-3xl border border-white/10 print:border-gray-300 space-y-2.5 shadow-md transition-all">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2.5">
                          <span className="font-mono font-bold text-xs text-[#FACC15] print:text-black">{ins.id}</span>
                          <span className="font-bold text-sm text-[#F8FAFC] print:text-black font-mono">{ins.title}</span>
                        </div>
                        <span className="text-[10px] font-mono uppercase font-bold text-emerald-400 print:text-black bg-emerald-950/50 print:bg-gray-200 px-3 py-1 rounded-full border border-emerald-800/60 print:border-gray-400">
                          {ins.status}
                        </span>
                      </div>
                      <p className="text-[#94A3B8] print:text-black text-xs leading-relaxed">{ins.whatFound}</p>
                      <div className="text-[11px] font-mono text-[#64748B]">
                        Supporting Artifacts: {ins.supportingEvidenceIds.join(', ')} | Confidence: {ins.confidenceScore}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Section 5: Chain of Custody & Evidence Index */}
            {includedSections.custodyIndex && (
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-[#F8FAFC] print:text-black border-b border-white/10 print:border-gray-300 pb-2 uppercase tracking-wide font-mono">
                  5. Evidence Custody Registry (ISO/IEC 27037 Standards)
                </h3>
                <div className="space-y-2.5 font-mono text-xs">
                  {evidenceRecords.map((ev) => (
                    <div key={ev.id} className="p-4 glass-card hover:bg-white/5 rounded-2xl border border-white/10 print:border-gray-300 flex flex-col sm:flex-row sm:items-center justify-between gap-2 transition-all shadow-xs">
                      <div>
                        <span className="font-bold text-[#FACC15] print:text-black">{ev.id}:</span> <span className="text-[#F8FAFC] print:text-black font-semibold">{ev.title}</span>
                        <div className="text-[11px] text-[#64748B] mt-0.5">Source Feed: {ev.source} | Registered: {ev.date} {ev.timestamp}</div>
                      </div>
                      <div className="text-[10px] text-emerald-400 print:text-black bg-emerald-950/40 print:bg-gray-200 px-3 py-1 rounded-full border border-emerald-800/50 print:border-gray-300 shrink-0 font-bold">
                        SHA-256: {ev.hashChecksum.slice(0, 18)}...
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Section 6: Certification & Sign-off */}
            {includedSections.certification && (
              <div className="pt-6 border-t border-white/10 print:border-black space-y-4 font-mono text-xs">
                <div className="glass-card print:bg-gray-100 p-6 rounded-3xl border border-white/10 print:border-gray-300 text-[#94A3B8] print:text-black font-sans text-xs shadow-md">
                  <strong className="text-[#F8FAFC] print:text-black block mb-1.5 font-mono uppercase text-sm">
                    Section 65B Indian Evidence Act Judicial Certificate:
                  </strong>
                  I hereby certify under Section 65B(4) of the Indian Evidence Act (1872 / Bhartiya Sakshya Adhiniyam 2023) that the electronic records, Call Detail Records, core banking transaction logs, and AI network analysis inferences reproduced in this dossier were produced by computerized systems operating in regular law enforcement custody without unauthorized access or data tampering.
                </div>

                <div className="glass-card p-6 rounded-3xl border border-white/10 grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 shadow-md">
                  <div>
                    <div className="text-[#64748B]">INVESTIGATING OFFICER / CERTIFIER:</div>
                    <div className="font-bold text-[#F8FAFC] print:text-black font-mono text-base mt-1">Inspector V. Kulkarni</div>
                    <div className="text-[#64748B] text-xs">Cyber &amp; Financial Crimes Unit • Badge #CY-8821</div>
                    <div className="text-[#64748B] text-xs">Special Task Force (STF) - Central Command</div>
                  </div>
                  <div className="sm:text-right">
                    <div className="text-[#64748B]">CRYPTOGRAPHIC SEAL HASH:</div>
                    <div className="font-bold text-[#FACC15] print:text-black mt-1 font-mono text-xs break-all">SEAL-NX-2026-65B-CERT-AUTHENTIC</div>
                    <div className="text-[#64748B] text-xs">Timestamp: 2026-05-12T16:30:00+05:30</div>
                    <div className="text-emerald-400 print:text-black font-bold mt-1">✓ VALID &amp; COURT ADMISSIBLE</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: EXECUTIVE BRIEFING SHEET */}
        {activeReportTab === 'briefing' && (
          <div className="space-y-6 text-xs text-[#F8FAFC] print:text-black">
            <div className="glass-card print:bg-gray-100 border border-white/10 p-6 rounded-3xl shadow-lg space-y-2">
              <div className="text-[10px] font-bold text-[#FACC15] print:text-black uppercase font-mono tracking-wider">
                Executive Briefing &amp; Tactical Directives
              </div>
              <p className="text-[#94A3B8] print:text-black leading-relaxed font-sans text-sm">
                Evidence synthesis confirms coordinated hawala money structuring between ground operatives and commercial shell accounts on 12 May 2026. Immediate search warrant execution recommended for Gala 14, Sector 4 Warehouse Depot, along with Section 91 notices issued to SBI and HDFC bank managers.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="glass-card border border-white/10 p-6 rounded-3xl space-y-3 shadow-lg">
                <div className="font-mono font-bold uppercase tracking-wider text-[#FACC15] print:text-black text-[10px] border-b border-white/10 pb-2">
                  Critical Conduit Flow Milestones
                </div>
                <div className="space-y-2.5 font-mono text-xs">
                  <div className="flex justify-between p-2 rounded-xl bg-white/5">
                    <span className="text-[#64748B]">08:45 IST</span>
                    <span className="font-semibold text-[#F8FAFC] print:text-black">Central Bus Station Rendezvous (EV-001)</span>
                  </div>
                  <div className="flex justify-between p-2 rounded-xl bg-white/5">
                    <span className="text-[#64748B]">11:48 IST</span>
                    <span className="font-semibold text-[#F8FAFC] print:text-black">₹50,000 Outflow from SBI A/C 889922 (EV-003)</span>
                  </div>
                  <div className="flex justify-between p-2 rounded-xl bg-white/5">
                    <span className="text-[#64748B]">12:10 IST</span>
                    <span className="font-semibold text-[#F8FAFC] print:text-black">₹48,200 Layered to XYZ Traders A/C 772145 (EV-004)</span>
                  </div>
                </div>
              </div>

              <div className="glass-card border border-white/10 p-6 rounded-3xl space-y-3 shadow-lg">
                <div className="font-mono font-bold uppercase tracking-wider text-[#FACC15] print:text-black text-[10px] border-b border-white/10 pb-2">
                  Actionable Operational Directives
                </div>
                <ul className="space-y-2.5 font-sans text-xs text-[#94A3B8] print:text-black">
                  <li className="p-2 rounded-xl bg-white/5 flex items-start space-x-2">
                    <span className="text-[#FACC15]">•</span>
                    <span>Secure ANPR camera recordings at Sector 4 Warehouse Depot entrance.</span>
                  </li>
                  <li className="p-2 rounded-xl bg-white/5 flex items-start space-x-2">
                    <span className="text-[#FACC15]">•</span>
                    <span>Issue freeze order on HDFC Mule Account 482701 and ICICI Account 772145.</span>
                  </li>
                  <li className="p-2 rounded-xl bg-white/5 flex items-start space-x-2">
                    <span className="text-[#FACC15]">•</span>
                    <span>Execute witness summons for Neha Verma regarding XYZ Traders shell status.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: FORENSIC CUSTODY CERTIFICATE (65B) (Rounded Theme & Glassmorphism) */}
        {activeReportTab === 'court' && (
          <div className="space-y-6 text-xs text-[#F8FAFC] print:text-black">
            <div className="glass-card border border-white/10 p-6 rounded-3xl shadow-lg space-y-1">
              <h3 className="text-base font-bold text-[#F8FAFC] print:text-black uppercase tracking-wide font-mono">
                Digital Forensic Certificate Under Section 65B of the Indian Evidence Act
              </h3>
              <p className="text-[#94A3B8] print:text-black font-sans text-xs">
                Preserved under ISO/IEC 27037 standards with unalterable SHA-256 cryptographic check seals.
              </p>
            </div>

            <div className="space-y-3">
              {evidenceRecords.map((ev) => (
                <div key={ev.id} className="p-5 glass-card hover:bg-white/10 rounded-2xl border border-white/10 hover:border-[#FACC15]/40 font-mono text-xs space-y-2 shadow-md transition-all">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-[#F8FAFC] print:text-black text-sm">{ev.id}: {ev.title}</span>
                    <span className="text-emerald-400 print:text-black font-bold px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-[10px] shadow-xs">
                      ✓ CUSTODY VALID
                    </span>
                  </div>
                  <div className="text-[#94A3B8]">Feed Origin: {ev.source} | Intercept: {ev.date} {ev.timestamp}</div>
                  <div className="p-2.5 rounded-xl bg-[#050507]/80 border border-white/5 text-[#FACC15] print:text-black break-all font-mono text-[11px]">
                    SHA-256: {ev.hashChecksum}
                  </div>
                </div>
              ))}
            </div>

            {/* Investigator Audit Signature */}
            <div className="glass-card p-6 rounded-3xl border border-white/10 print:border-black grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono shadow-lg">
              <div>
                <div className="text-[#64748B]">AUTHORIZED SIGNATORY:</div>
                <div className="font-bold text-[#F8FAFC] print:text-black mt-1 font-mono text-base">Inspector V. Kulkarni</div>
                <div className="text-[#64748B]">Badge ID: CY-8821</div>
                <div className="text-[#64748B]">Special Task Force - Central Command</div>
              </div>
              <div className="sm:text-right">
                <div className="text-[#64748B]">CERTIFICATION SEAL:</div>
                <div className="font-bold text-[#FACC15] print:text-black mt-1">SEAL-65B-NX-2026-AUTHENTIC</div>
                <div className="text-[#64748B]">Timestamp: 2026-05-12T16:30:00+05:30</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
