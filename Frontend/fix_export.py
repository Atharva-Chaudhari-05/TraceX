import sys
with open('src/components/views/ExportReportsView.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

text_to_replace = '''--------------------------------------------------------------------------------
2. 5-HOP HIDDEN HAWALA TRAVERSAL CONDUIT (ZERO DIRECT CALLS / ZERO DIRECT WIRES)
--------------------------------------------------------------------------------
Hop 1: Rahul Sharma (Ground Target / SUBJ-NX-01) ➔ Physical Meet & 241s Encrypted CDR Call
Hop 2: Ajay Patil (Financial Conduit / Cash Broker) ➔ ₹48,200 Cash Token Handover
Hop 3: A/C 889922 (SBI Commercial / A. Patil) ➔ Rapid Smurfing IMPS Layering Wire
Hop 4: A/C 482701 (HDFC Layering Mule / Dinesh Kumar) ➔ Cross-Syndicate Relay Conduit
Hop 5: Neha Verma & XYZ Traders Pvt Ltd (Corporate Signatory / Shell Front Enterprise)'''

replacement = '''--------------------------------------------------------------------------------
2. AI INSIGHTS & INFERENCES
--------------------------------------------------------------------------------
${aiInsights.map((i) => `[${i.id}] ${i.title}\\n   ${i.whatFound}`).join('\\n')}'''

content = content.replace(text_to_replace, replacement)

pdf_replace = '''// 4. 5-Hop Hidden Hawala Conduit Box
          doc.setFillColor(240, 249, 255);
          doc.setDrawColor(186, 230, 253);
          doc.roundedRect(14, currentY, pageWidth - 28, 18, 2, 2, 'FD');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(7.5);
          doc.setTextColor(3, 105, 161);
          doc.text('IDENTIFIED 5-HOP HIDDEN HAWALA CONDUIT (ZERO DIRECT CALLS / ZERO DIRECT BANK TRANSFERS):', 18, currentY + 5);

          doc.setFont('helvetica', 'normal');
          doc.setFontSize(7);
          doc.setTextColor(15, 23, 42);
          doc.text('Hop 1: Rahul Sharma (Ground Target) -> Hop 2: Ajay Patil (Cash Broker) -> Hop 3: A/C 889922 (SBI Commercial)', 18, currentY + 10);
          doc.text('-> Hop 4: A/C 482701 (HDFC Mule / Dinesh Kumar) -> Hop 5: Neha Verma & XYZ Traders Pvt Ltd (Corporate Entity)', 18, currentY + 14);

          currentY += 24;'''

pdf_repl = '''// 4. AI Insights Box
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
          currentY += 24;'''

content = content.replace(pdf_replace, pdf_repl)

with open('src/components/views/ExportReportsView.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
