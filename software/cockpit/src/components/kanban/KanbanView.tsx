import React, { useState, useEffect, useCallback, useRef } from 'react';
import { TaskBoardData, TaskItem } from '../../types/cockpit';
import { api } from '../../services/api';
import { CheckSquare, Square, ArrowRight, ArrowLeft, Search, RefreshCw } from 'lucide-react';

interface KanbanViewProps {
  onSyncStatusChange: (status: 'idle' | 'saving' | 'saved' | 'error') => void;
}

export const KanbanView: React.FC<KanbanViewProps> = ({ onSyncStatusChange }) => {
  const [board, setBoard] = useState<TaskBoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [saveTimer, setSaveTimer] = useState<NodeJS.Timeout | null>(null);
  const rawBoardRef = useRef<TaskBoardData | null>(null);

  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.fetchTasks();
      setBoard(data);
      rawBoardRef.current = data;
      onSyncStatusChange('saved');
    } catch (err) {
      console.error('Failed to load tasks:', err);
      onSyncStatusChange('error');
    } finally {
      setLoading(false);
    }
  }, [onSyncStatusChange]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  // Debounced auto-save function
  const triggerAutoSave = useCallback(
    (newBoard: TaskBoardData) => {
      setBoard(newBoard);
      rawBoardRef.current = newBoard;
      onSyncStatusChange('saving');

      if (saveTimer) clearTimeout(saveTimer);

      const timer = setTimeout(async () => {
        try {
          await api.saveTasks(newBoard);
          onSyncStatusChange('saved');
        } catch (err) {
          console.error('Failed to save tasks to docs/Project_Tasks.md:', err);
          onSyncStatusChange('error');
        }
      }, 600);

      setSaveTimer(timer);
    },
    [saveTimer, onSyncStatusChange]
  );

  // Move task between columns
  const moveTask = (
    fromCol: 'backlog' | 'inProgress' | 'done',
    toCol: 'backlog' | 'inProgress' | 'done',
    taskIndex: number
  ) => {
    if (!board) return;

    const sourceList = [...board[fromCol]];
    const targetList = [...board[toCol]];

    const [moved] = sourceList.splice(taskIndex, 1);
    // Adjust completion state if moved to/from done
    if (toCol === 'done') {
      moved.completed = true;
      if (moved.subtasks) moved.subtasks.forEach(st => st.completed = true);
    } else if (fromCol === 'done') {
      moved.completed = false;
    }

    targetList.push(moved);

    const updated: TaskBoardData = {
      ...board,
      [fromCol]: sourceList,
      [toCol]: targetList,
    };

    triggerAutoSave(updated);
  };

  // Toggle main task completed
  const toggleTask = (col: 'backlog' | 'inProgress' | 'done', index: number) => {
    if (!board) return;
    const list = [...board[col]];
    const item = { ...list[index] };
    item.completed = !item.completed;
    if (item.subtasks) {
      item.subtasks = item.subtasks.map(st => ({ ...st, completed: item.completed }));
    }
    list[index] = item;

    const updated: TaskBoardData = {
      ...board,
      [col]: list,
    };
    triggerAutoSave(updated);
  };

  // Toggle subtask completed
  const toggleSubtask = (
    col: 'backlog' | 'inProgress' | 'done',
    parentIndex: number,
    subIndex: number
  ) => {
    if (!board) return;
    const list = [...board[col]];
    const parent = { ...list[parentIndex] };
    if (!parent.subtasks) return;

    const subtasks = [...parent.subtasks];
    subtasks[subIndex] = {
      ...subtasks[subIndex],
      completed: !subtasks[subIndex].completed,
    };
    parent.subtasks = subtasks;
    list[parentIndex] = parent;

    const updated: TaskBoardData = {
      ...board,
      [col]: list,
    };
    triggerAutoSave(updated);
  };

  if (loading || !board) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-canvas-bg gap-3">
        <RefreshCw className="w-6 h-6 text-engineering-amber animate-spin" />
        <span className="text-sm font-mono text-slate-500">Loading docs/Project_Tasks.md...</span>
      </div>
    );
  }

  const columns: {
    key: 'backlog' | 'inProgress' | 'done';
    title: string;
    icon: string;
    badgeColor: string;
    items: TaskItem[];
  }[] = [
    {
      key: 'backlog',
      title: 'Backlog',
      icon: '📋',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-200',
      items: board.backlog,
    },
    {
      key: 'inProgress',
      title: 'In Progress (Phase 1 Bench)',
      icon: '⏳',
      badgeColor: 'bg-sky-100 text-sky-800 border-sky-200',
      items: board.inProgress,
    },
    {
      key: 'done',
      title: 'Completed Milestones',
      icon: '✅',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      items: board.done,
    },
  ];

  return (
    <div className="w-full h-full flex flex-col bg-canvas-bg overflow-hidden p-6 space-y-4">
      {/* Top Utility Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Project Tasks Kanban</h2>
          <p className="text-xs text-slate-500">
            Interactive task board synchronized live with <code className="bg-slate-100 px-1 py-0.5 rounded text-[11px] font-mono">docs/Project_Tasks.md</code>.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-engineering-amber w-60"
            />
          </div>

          <button
            onClick={loadTasks}
            title="Reload from disk"
            className="p-1.5 hover:bg-slate-200/60 rounded text-slate-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Columns Container */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6 min-h-0">
        {columns.map((col) => {
          const filteredItems = col.items.filter(item =>
            search.trim() === '' || item.text.toLowerCase().includes(search.toLowerCase())
          );

          return (
            <div
              key={col.key}
              className="kanban-column flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
            >
              {/* Column Header */}
              <div className="p-3.5 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-base">{col.icon}</span>
                  <h3 className="font-semibold text-xs text-slate-900">{col.title}</h3>
                </div>
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${col.badgeColor}`}>
                  {filteredItems.length}
                </span>
              </div>

              {/* Task Cards List */}
              <div className="flex-1 p-3 overflow-y-auto space-y-2.5">
                {filteredItems.map((item, idx) => (
                  <div
                    key={item.id}
                    className={`p-3 rounded-lg border transition-all ${
                      item.completed
                        ? 'bg-slate-50/70 border-slate-200 text-slate-500'
                        : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm hover:shadow'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2 flex-1">
                        <button
                          onClick={() => toggleTask(col.key, idx)}
                          className="mt-0.5 text-slate-400 hover:text-emerald-600 flex-shrink-0"
                        >
                          {item.completed ? (
                            <CheckSquare className="w-4 h-4 text-emerald-600" />
                          ) : (
                            <Square className="w-4 h-4" />
                          )}
                        </button>
                        <span
                          className={`text-xs leading-snug break-words ${
                            item.completed ? 'line-through text-slate-400' : 'text-slate-800'
                          }`}
                        >
                          {item.text}
                        </span>
                      </div>

                      {/* Movement arrows */}
                      <div className="flex items-center gap-1 flex-shrink-0">
                        {col.key !== 'backlog' && (
                          <button
                            onClick={() => moveTask(col.key, col.key === 'done' ? 'inProgress' : 'backlog', idx)}
                            title="Move left"
                            className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-700"
                          >
                            <ArrowLeft className="w-3.5 h-3.5" />
                          </button>
                        )}
                        {col.key !== 'done' && (
                          <button
                            onClick={() => moveTask(col.key, col.key === 'backlog' ? 'inProgress' : 'done', idx)}
                            title="Move right"
                            className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-700"
                          >
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Subtasks */}
                    {item.subtasks && item.subtasks.length > 0 && (
                      <div className="mt-2.5 pt-2 border-t border-slate-100 pl-4 space-y-1.5">
                        {item.subtasks.map((st, sIdx) => (
                          <div key={st.id} className="flex items-start gap-2 text-[11px]">
                            <button
                              onClick={() => toggleSubtask(col.key, idx, sIdx)}
                              className="mt-0.5 text-slate-400 hover:text-emerald-600 flex-shrink-0"
                            >
                              {st.completed ? (
                                <CheckSquare className="w-3.5 h-3.5 text-emerald-600" />
                              ) : (
                                <Square className="w-3.5 h-3.5" />
                              )}
                            </button>
                            <span
                              className={`leading-tight ${
                                st.completed ? 'line-through text-slate-400' : 'text-slate-600'
                              }`}
                            >
                              {st.text}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
