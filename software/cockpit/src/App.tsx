import React, { useState } from 'react';
import { CanvasView } from './components/canvas/CanvasView';
import { RoadmapView } from './components/roadmap/RoadmapView';
import { KanbanView } from './components/kanban/KanbanView';
import { FileDrawer } from './components/drawer/FileDrawer';
import { LayoutGrid, Calendar, CheckSquare, Check, AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'canvas' | 'roadmap' | 'kanban'>('canvas');
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('saved');

  return (
    <div className="w-screen h-screen flex flex-col bg-canvas-bg overflow-hidden text-slate-900 select-none">
      {/* Top Engineering Utility Header */}
      <header className="h-14 bg-white border-b border-slate-200 px-5 flex items-center justify-between z-20 flex-shrink-0 shadow-xs">
        {/* Project Branding & Breadcrumb */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center font-bold font-mono text-sm shadow-sm border border-amber-600">
            SCB
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-sm tracking-tight text-slate-900">
                Smart Crossword Board
              </h1>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                v1.0 COCKPIT
              </span>
            </div>
            <p className="text-[10px] font-mono text-slate-400">
              Living Canvas, Decisions & Tasks Web Dashboard
            </p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <nav className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 gap-1">
          <button
            onClick={() => setActiveTab('canvas')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'canvas'
                ? 'bg-white text-slate-900 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5 text-sky-600" />
            <span>Infinite Canvas</span>
          </button>

          <button
            onClick={() => setActiveTab('roadmap')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'roadmap'
                ? 'bg-white text-slate-900 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Calendar className="w-3.5 h-3.5 text-engineering-amber" />
            <span>Roadmap & ADL</span>
          </button>

          <button
            onClick={() => setActiveTab('kanban')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'kanban'
                ? 'bg-white text-slate-900 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5 text-emerald-600" />
            <span>Tasks Kanban</span>
          </button>
        </nav>

        {/* Right Status Badges */}
        <div className="flex items-center gap-3">
          {/* Phase Badge */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>Phase 1 (4x4 Bench)</span>
          </div>

          <div className="h-4 w-px bg-slate-200" />

          {/* Live Disk Sync Indicator */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            {syncStatus === 'saving' ? (
              <span className="flex items-center gap-1 text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
                <RefreshCw className="w-3 h-3 animate-spin text-amber-600" />
                <span>Saving to disk...</span>
              </span>
            ) : syncStatus === 'saved' ? (
              <span className="flex items-center gap-1 text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                <Check className="w-3 h-3 text-emerald-600" />
                <span>Saved to disk</span>
              </span>
            ) : syncStatus === 'error' ? (
              <span className="flex items-center gap-1 text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded">
                <AlertCircle className="w-3 h-3 text-red-600" />
                <span>Sync error</span>
              </span>
            ) : null}
          </div>
        </div>
      </header>

      {/* Main Content View Container */}
      <main className="flex-1 w-full h-[calc(100vh-3.5rem)] relative overflow-hidden">
        {activeTab === 'canvas' && (
          <CanvasView
            onOpenFile={(path) => setActiveFile(path)}
            onSyncStatusChange={setSyncStatus}
          />
        )}
        {activeTab === 'roadmap' && <RoadmapView />}
        {activeTab === 'kanban' && (
          <KanbanView onSyncStatusChange={setSyncStatus} />
        )}
      </main>

      {/* Slide-over Markdown & Image File Drawer */}
      <FileDrawer
        filePath={activeFile}
        onClose={() => setActiveFile(null)}
      />
    </div>
  );
};
