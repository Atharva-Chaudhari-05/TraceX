/**
 * TRACEX: AI-POWERED CRIMINAL NETWORK ANALYSIS & INVESTIGATION INTELLIGENCE PLATFORM
 * Smart India Hackathon (SIH 2026) | Problem Statement ID: 26189
 * Classification: RESTRICTED // LAW ENFORCEMENT SENSITIVE // OFFICIAL SUBMISSION
 */

import React from 'react';
import { InvestigationProvider, useInvestigation } from './context/InvestigationContext';
import { TopBar } from './components/layout/TopBar';
import { Sidebar } from './components/layout/Sidebar';
import { DemoWalkthroughBanner } from './components/layout/DemoWalkthroughBanner';
import { GlobalSearchModal } from './components/layout/GlobalSearchModal';

// 14 Tactical Views
import { CaseOverviewView } from './components/views/CaseOverviewView';
import { DataSourcesView } from './components/views/DataSourcesView';
import { InvestigationRecordsView } from './components/views/InvestigationRecordsView';
import { EntityExplorerView } from './components/views/EntityExplorerView';
import { EntityResolutionView } from './components/views/EntityResolutionView';
import { InvestigationGraphView } from './components/views/InvestigationGraphView';
import { RelationshipPathExplorerView } from './components/views/RelationshipPathExplorerView';
import { PatternAnalysisView } from './components/views/PatternAnalysisView';
import { TimelineView } from './components/views/TimelineView';
import { AIInsightsView } from './components/views/AIInsightsView';
import { EvidenceExplorerView } from './components/views/EvidenceExplorerView';
import { CrossCaseAnalyticsView } from './components/views/CrossCaseAnalyticsView';
import { ExportReportsView } from './components/views/ExportReportsView';
import { AuditLogsView } from './components/views/AuditLogsView';
import { LoginView } from './components/views/LoginView';

const MainInvestigationStage: React.FC = () => {
  const { currentView, isSidebarOpen } = useInvestigation();

  const renderActiveView = () => {
    switch (currentView) {
      case 'overview':
        return <CaseOverviewView />;
      case 'sources':
      case 'datasources':
        return <DataSourcesView />;
      case 'records':
        return <InvestigationRecordsView />;
      case 'entities':
        return <EntityExplorerView />;
      case 'resolution':
        return <EntityResolutionView />;
      case 'graph':
        return <InvestigationGraphView />;
      case 'path':
      case 'pathexplorer':
        return <RelationshipPathExplorerView />;
      case 'patterns':
        return <PatternAnalysisView />;
      case 'timeline':
        return <TimelineView />;
      case 'insights':
        return <AIInsightsView />;
      case 'evidence':
        return <EvidenceExplorerView />;
      case 'analytics':
        return <CrossCaseAnalyticsView />;
      case 'reports':
        return <ExportReportsView />;
      case 'audit':
        return <AuditLogsView />;
      default:
        return <CaseOverviewView />;
    }
  };

  return (
    <main
      className={`flex-1 w-full min-w-0 overflow-y-auto overflow-x-hidden min-h-0 bg-[#050507] flex flex-col relative transition-all duration-300 ease-in-out ${
        currentView === 'graph' ? 'pl-0' : !isSidebarOpen ? 'pl-14' : 'pl-0'
      }`}
    >
      {renderActiveView()}
    </main>
  );
};

const AppContent: React.FC = () => {
  const { isAuthenticated } = useInvestigation();

  if (!isAuthenticated) {
    return <LoginView />;
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-[#050507] text-[#F8FAFC] font-sans overflow-hidden select-none antialiased">
      {/* Top Header with Case Status & User Menu */}
      <TopBar />

      {/* Guided 6-Step Hackathon Demo Banner */}
      <DemoWalkthroughBanner />

      {/* Main Tactical Investigation Shell (Full Screen Width) */}
      <div className="flex-1 w-full flex overflow-hidden min-h-0 relative">
        {/* Left Navigation Sidebar Dropdown (Floating Overlay, does not shorten main stage) */}
        <Sidebar />

        {/* Central Workspace Stage - Expanded in Full Screen View */}
        <MainInvestigationStage />
      </div>
    </div>
  );
};

export default function App() {
  return (
    <InvestigationProvider>
      <AppContent />
    </InvestigationProvider>
  );
}
