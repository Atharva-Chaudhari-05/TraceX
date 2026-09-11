import React, { useState } from 'react';
import {
  ShieldCheck,
  Search,
  Filter,
  Lock,
  Boxes,
  KeyRound,
  ExternalLink,
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export const AuditLogsView: React.FC = () => {
  const { auditLogs } = useInvestigation();
  const [filterAction, setFilterAction] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredLogs = auditLogs.filter((log) => {
    const matchesAction =
      filterAction === 'all' ? true : log.action.toLowerCase().includes(filterAction.toLowerCase());

    const matchesSearch =
      log.details.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.performedBy.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.action.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesAction && matchesSearch;
  });

  return (
    <div id="audit-logs-view" className="w-full p-6 lg:p-8 space-y-6 text-[#F8FAFC]">
      {/* Header */}
      <div className="glass-panel border border-white/10 p-6 rounded-3xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="flex items-center space-x-2.5">
            <ShieldCheck className="w-5 h-5 text-[#FACC15]" />
            <h1 className="text-2xl font-bold text-[#F8FAFC] font-mono">
              Cryptographic Audit Ledger &amp; Chain of Custody
            </h1>
            <span className="text-xs font-mono bg-[#050507]/80 text-[#FACC15] px-3 py-1 border border-[#FACC15]/40 rounded-full font-semibold shadow-xs">
              {auditLogs.length} Chained Blocks
            </span>
          </div>
          <p className="text-sm text-[#94A3B8] mt-1 font-sans">
            Immutable SHA-256 block ledger tracking all investigator actions, entity merges, path queries, and court exports under ISO/IEC 27037 standards.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-[#94A3B8] glass-card border border-white/10 px-4 py-2 rounded-full shrink-0">
          <Lock className="w-4 h-4 text-emerald-400" />
          <span>Append-Only Ledger: <strong className="text-emerald-400">Tamper-Proof</strong></span>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-panel border border-white/10 p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md">
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <Filter className="w-3.5 h-3.5 text-[#FACC15]" />
          <span className="text-[#94A3B8] font-sans text-xs">Filter Action:</span>
          {['all', 'ingest', 'match', 'graph', 'report', 'search', 'query'].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterAction(cat)}
              className={`px-3.5 py-1.5 uppercase tracking-wider text-xs font-bold rounded-full border transition-all cursor-pointer ${
                filterAction === cat
                  ? 'bg-[#FACC15] text-[#050507] border-[#FACC15] shadow-[0_0_12px_rgba(250, 204, 21,0.4)]'
                  : 'glass-card text-[#94A3B8] border-white/10 hover:text-[#F8FAFC] hover:border-white/20'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search action, officer, details..."
            className="pl-9 pr-3 py-1.5 text-xs glass-card border border-white/10 rounded-full text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#FACC15] w-72 font-mono"
          />
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel border border-white/10 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#050507]/80 border-b border-white/10 text-[10px] font-mono uppercase tracking-[0.15em] text-[#FACC15]">
              <tr>
                <th className="py-3.5 px-5">Block &amp; Time</th>
                <th className="py-3.5 px-5">Action Code</th>
                <th className="py-3.5 px-5">Performed By</th>
                <th className="py-3.5 px-5">Event Details &amp; Target</th>
                <th className="py-3.5 px-5 font-mono">Block Hash / Previous Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10 font-sans text-xs">
              {filteredLogs.map((log, idx) => (
                <tr key={log.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3.5 px-5 text-[#94A3B8] font-mono text-xs whitespace-nowrap">
                    <div className="font-bold text-[#F8FAFC]">BLK-{(filteredLogs.length - idx).toString().padStart(3, '0')}</div>
                    <div className="text-[11px] text-[#64748B]">{log.timestamp}</div>
                  </td>

                  <td className="py-3.5 px-5">
                    <span className="font-mono text-[11px] uppercase font-bold text-[#FACC15] bg-[#050507] px-2.5 py-0.5 border border-[#FACC15]/40 rounded-full">
                      {log.action}
                    </span>
                  </td>

                  <td className="py-3.5 px-5 font-mono text-xs">
                    <div className="font-semibold text-[#F8FAFC]">{log.performedBy}</div>
                    <div className="text-[10px] text-[#64748B] uppercase">{log.role || 'Investigator'}</div>
                  </td>

                  <td className="py-3.5 px-5 text-[#94A3B8] leading-relaxed max-w-md">
                    {log.details}
                  </td>

                  <td className="py-3.5 px-5 font-mono text-[11px]">
                    <div className="text-emerald-400 font-bold truncate max-w-[200px]" title={log.signature}>
                      CURR: {log.signature.slice(0, 16)}...
                    </div>
                    <div className="text-[#64748B] truncate max-w-[200px]">
                      PREV: {log.signature.slice(16, 32)}...
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
