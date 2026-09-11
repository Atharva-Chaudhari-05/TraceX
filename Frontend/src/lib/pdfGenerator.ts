import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Case, Entity, Relationship } from '../types';

export const generateCaseReport = (
  caseData: Case,
  entities: Entity[],
  relationships: Relationship[]
) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.width;

  // Colors
  const primaryColor = '#0F172A';
  const textColor = '#1E293B';

  // --- Header ---
  doc.setFont('times', 'bold');
  doc.setFontSize(22);
  doc.setTextColor(primaryColor);
  doc.text('TraceX Investigation Report', pageWidth / 2, 20, { align: 'center' });

  doc.setFontSize(10);
  doc.setTextColor(textColor);
  doc.text(`Generated: ${new Date().toISOString()}`, pageWidth / 2, 28, {
    align: 'center',
  });

  doc.setLineWidth(0.5);
  doc.setDrawColor(primaryColor);
  doc.line(14, 32, pageWidth - 14, 32);

  // --- Case Metadata ---
  doc.setFontSize(14);
  doc.setFont('times', 'bold');
  doc.text('Case Metadata', 14, 45);

  doc.setFontSize(11);
  doc.setFont('times', 'normal');
  const metadataStartY = 55;
  const lineHeight = 7;

  doc.text(`Case ID: ${caseData.id}`, 14, metadataStartY);
  doc.text(`Title: ${caseData.title}`, 14, metadataStartY + lineHeight);
  doc.text(`Status: ${caseData.status.toUpperCase()}`, 14, metadataStartY + lineHeight * 2);
  doc.text(`Lead Agency: ${(caseData as any).leadAgency || caseData.department || 'Special Task Force'}`, 14, metadataStartY + lineHeight * 3);
  doc.text(`Priority: ${caseData.priority.toUpperCase()}`, 14, metadataStartY + lineHeight * 4);
  
  // Wrap description
  const splitDesc = doc.splitTextToSize(
    `Description: ${caseData.description}`,
    pageWidth - 28
  );
  doc.text(splitDesc, 14, metadataStartY + lineHeight * 5);

  let currentY = metadataStartY + lineHeight * 5 + splitDesc.length * 5 + 10;

  // --- Entities Table ---
  doc.setFontSize(14);
  doc.setFont('times', 'bold');
  doc.text('Key Network Entities', 14, currentY);
  currentY += 5;

  const entityTableData = entities.map((e) => [
    e.name,
    e.type.toUpperCase(),
    e.identifier || 'N/A',
    e.role || 'N/A',
    e.confidenceLevel.toUpperCase(),
  ]);

  autoTable(doc, {
    startY: currentY,
    head: [['Name', 'Type', 'Identifier', 'Role', 'Confidence']],
    body: entityTableData,
    theme: 'grid',
    headStyles: { fillColor: [15, 23, 42], textColor: 255, font: 'times', fontStyle: 'bold' },
    styles: { font: 'times', fontSize: 9 },
    alternateRowStyles: { fillColor: [248, 250, 252] },
  });

  currentY = (doc as any).lastAutoTable.finalY + 15;

  // Check if we need a new page for relationships
  if (currentY > doc.internal.pageSize.height - 40) {
    doc.addPage();
    currentY = 20;
  }

  // --- Relationships Table ---
  doc.setFontSize(14);
  doc.setFont('times', 'bold');
  doc.text('Analyzed Relationships', 14, currentY);
  currentY += 5;

  const getEntityName = (id: string) => {
    return entities.find((e) => e.id === id)?.name || id;
  };

  const relTableData = relationships.map((r) => [
    getEntityName(r.source),
    r.label,
    getEntityName(r.target),
    r.provenance.mode.toUpperCase(),
  ]);

  autoTable(doc, {
    startY: currentY,
    head: [['Source Entity', 'Relationship', 'Target Entity', 'Provenance']],
    body: relTableData,
    theme: 'grid',
    headStyles: { fillColor: [15, 23, 42], textColor: 255, font: 'times', fontStyle: 'bold' },
    styles: { font: 'times', fontSize: 9 },
    alternateRowStyles: { fillColor: [248, 250, 252] },
  });

  // --- Footer IT ACT SEC 65B ---
  const pageCount = (doc.internal as any).getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setFont('times', 'italic');
    doc.setTextColor(100);
    doc.text(
      'CONFIDENTIAL LAW ENFORCEMENT REPORT - IT ACT SEC 65B COMPLIANT',
      pageWidth / 2,
      doc.internal.pageSize.height - 10,
      { align: 'center' }
    );
    doc.text(
      `Page ${i} of ${pageCount}`,
      pageWidth - 20,
      doc.internal.pageSize.height - 10,
      { align: 'right' }
    );
  }

  doc.save(`TraceX_Report_${caseData.id}.pdf`);
};
