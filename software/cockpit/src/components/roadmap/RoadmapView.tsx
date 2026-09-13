import React, { useState, useEffect, useMemo } from 'react';
import { ProjectStateData, DecisionEntry } from '../../types/cockpit';
import { api } from '../../services/api';
import { CheckCircle2, Clock, Calendar, Search, ShieldCheck, RefreshCw } from 'lucide-react';

export const RoadmapView: React.FC = () => {
  const [state, setState] = useState<ProjectStateData | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedTopic, setSelectedTopic] = useState<string>('all');

  useEffect(() => {
    api.fetchState().then(data => {
      setState(data);
      setLoading(false);
    }).catch(err => {
      console.error('Failed to load state:', err);
      setLoading(false);
    });
  }, []);

  const filteredDecisions = useMemo(() => {
    if (!state?.decisions) return [];
    return state.decisions.filter(d => {
      const matchSearch = search.trim() === '' ||
        d.id.toLowerCase().includes(search.toLowerCase()) ||
        d.topic.toLowerCase().includes(search.toLowerCase()) ||
        d.reason.toLowerCase().includes(search.toLowerCase());

      const matchTopic = selectedTopic === 'all' || d.topic.toLowerCase().includes(selectedTopic.toLowerCase());
      return matchSearch && matchTopic;
    });
  }, [state, search, selectedTopic]);

  if (loading) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-canvas-bg gap-3">
        <RefreshCw className="w-6 h-6 text-engineering-amber animate-spin" />
        <span className="text-sm font-mono text-slate-500">Loading PROJECT_STATE.md...</span>
      </div>
    );
  }

  return (
    <div className="w-full h-full overflow-y-auto bg-canvas-bg p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Phase Header Banner */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                ACTIVE PHASE
              </span>
              <span className="text-xs font-mono text-slate-400">Target: Bench Assembly & Verification</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              {state?.currentPhase || 'Phase 1: Test Board and Game Engine'}
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-2xl">
              Focusing on 4x4 test grid verification, 13.56 MHz RFID multiplexing latency, and local C crossword referee engine.
            </p>
          </div>

          <div className="flex items-center gap-4 border-t md:border-t-0 md:border-l border-slate-100 pt-4 md:pt-0 md:pl-6">
            <div className="text-center">
              <div className="text-2xl font-mono font-bold text-slate-900">24</div>
              <div className="text-[11px] font-mono text-slate-500 uppercase">Decisions</div>
            </div>
            <div className="w-px h-8 bg-slate-200" />
            <div className="text-center">
              <div className="text-2xl font-mono font-bold text-emerald-600">88%</div>
              <div className="text-[11px] font-mono text-slate-500 uppercase">Phase 1 Done</div>
            </div>
          </div>
        </div>

        {/* Roadmap Stages Visual Gantt / Timeline */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-engineering-amber" />
              <h2 className="text-base font-bold text-slate-900">Project Roadmap & Milestones</h2>
            </div>
            <span className="text-xs font-mono text-slate-400">Updated from PROJECT_STATE.md</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {state?.roadmapStages.map((stage, idx) => (
              <div
                key={idx}
                className={`rounded-lg border p-4 flex flex-col justify-between transition-all ${
                  stage.status === 'active'
                    ? 'border-emerald-300 bg-emerald-50/20 shadow-sm'
                    : 'border-slate-200 bg-slate-50/40'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-mono font-bold text-slate-500">STAGE 0{idx + 1}</span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold uppercase ${
                        stage.status === 'active'
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : 'bg-slate-200/70 text-slate-600'
                      }`}
                    >
                      {stage.status}
                    </span>
                  </div>
                  <h3 className="font-semibold text-sm text-slate-900 mb-3">{stage.phase}</h3>

                  <div className="space-y-2">
                    {stage.milestones.map((m, mIdx) => (
                      <div key={mIdx} className="flex items-start gap-2 text-xs">
                        {m.done ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                        ) : m.active ? (
                          <Clock className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5 animate-spin" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border border-slate-300 flex-shrink-0 mt-0.5" />
                        )}
                        <span className={m.done ? 'text-slate-700' : m.active ? 'text-amber-900 font-medium' : 'text-slate-400'}>
                          {m.name}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between text-[11px] font-mono text-slate-500">
                  <span>{stage.milestones.filter(m => m.done).length} / {stage.milestones.length} Done</span>
                  <span className="font-semibold">
                    {Math.round((stage.milestones.filter(m => m.done).length / stage.milestones.length) * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Decisions Log Table */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-engineering-blue" />
                <h2 className="text-base font-bold text-slate-900">Architectural Decisions Log (ADL)</h2>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Every architectural choice, RF derivation, and component trade-off recorded chronologically.
              </p>
            </div>

            {/* Filter controls */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter decisions..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-engineering-amber w-52"
                />
              </div>

              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="text-xs border border-slate-200 rounded-md py-1.5 px-2.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-engineering-amber"
              >
                <option value="all">All Topics</option>
                <option value="sensor">Sensors & RFID</option>
                <option value="circuit">Circuit & KiCad</option>
                <option value="cad">CAD & Mechanics</option>
                <option value="android">Android & Software</option>
                <option value="sourcing">Sourcing & BOM</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-mono text-[11px] border-b border-slate-200 uppercase">
                <tr>
                  <th className="py-3 px-4 font-semibold w-24">ID</th>
                  <th className="py-3 px-4 font-semibold w-28">Date</th>
                  <th className="py-3 px-4 font-semibold w-48">Topic</th>
                  <th className="py-3 px-4 font-semibold">Decision & Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredDecisions.map((d: DecisionEntry) => (
                  <tr key={d.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      <span className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded border border-slate-200 text-[11px]">
                        {d.id}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-500 text-[11px]">{d.date}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800">{d.topic}</td>
                    <td className="py-3 px-4 text-slate-600 leading-relaxed font-sans">{d.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
