import React, { memo, useState, useEffect, useRef } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Edit3, Check, Trash2, Eye } from 'lucide-react';
import { marked } from 'marked';

marked.setOptions({
  gfm: true,
  breaks: true,
});

const colorTopBorders: Record<string, string> = {
  '1': 'border-t-red-500',
  '2': 'border-t-orange-500',
  '3': 'border-t-amber-500',
  '4': 'border-t-emerald-500',
  '5': 'border-t-sky-500',
  '6': 'border-t-purple-500',
};

const colorBadges: Record<string, string> = {
  '1': 'bg-red-50 text-red-700 border-red-200',
  '2': 'bg-orange-50 text-orange-700 border-orange-200',
  '3': 'bg-amber-50 text-amber-700 border-amber-200',
  '4': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  '5': 'bg-sky-50 text-sky-700 border-sky-200',
  '6': 'bg-purple-50 text-purple-700 border-purple-200',
};

export const TextCardNode: React.FC<NodeProps> = memo(({ id, data, selected }) => {
  const color = (data.color as string) || '5';
  const initialText = (data.text as string) || '';
  const topBorder = colorTopBorders[color] || 'border-t-sky-500';
  const badgeStyle = colorBadges[color] || colorBadges['5'];

  const [text, setText] = useState(initialText);
  const [isEditing, setIsEditing] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setText((data.text as string) || '');
  }, [data.text]);

  const handleTextChange = (val: string) => {
    setText(val);
    setSaveStatus('saving');

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      if (data.onTextChange && typeof data.onTextChange === 'function') {
        data.onTextChange(id, val);
      }
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 1500);
    }, 600);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (data.onDeleteNode && typeof data.onDeleteNode === 'function') {
      data.onDeleteNode(id);
    }
  };

  const renderedHtml = React.useMemo(() => {
    if (!text) return '';
    try {
      return marked.parse(text) as string;
    } catch (e) {
      return text;
    }
  }, [text]);

  return (
    <div
      className={`bg-white rounded-lg border border-slate-200 border-t-4 ${topBorder} shadow-sm hover:shadow-md transition-all duration-150 flex flex-col justify-between overflow-hidden ${
        selected ? 'ring-2 ring-engineering-amber ring-offset-2 shadow-lg' : ''
      }`}
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {/* React Flow Handles */}
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="target" position={Position.Left} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />

      {/* Header with Tools */}
      <div className="px-3 py-1.5 border-b border-slate-100 bg-slate-50 flex items-center justify-between gap-2 flex-shrink-0">
        <span className={`px-1.5 py-0.5 rounded border ${badgeStyle} text-[9px] font-mono font-semibold`}>
          NOTE CARD
        </span>

        <div className="flex items-center gap-1 nodrag">
          {saveStatus === 'saving' && (
            <span className="text-[10px] font-mono text-amber-600 font-medium animate-pulse mr-1">
              Saving...
            </span>
          )}
          {saveStatus === 'saved' && (
            <span className="text-[10px] font-mono text-emerald-600 font-medium flex items-center gap-0.5 mr-1">
              <Check className="w-3 h-3" /> Saved
            </span>
          )}

          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsEditing(!isEditing);
            }}
            title={isEditing ? 'Preview markdown' : 'Edit note'}
            className={`p-1 rounded transition-colors ${
              isEditing
                ? 'bg-amber-100 text-amber-800 hover:bg-amber-200'
                : 'text-slate-400 hover:text-slate-800 hover:bg-slate-200/60'
            }`}
          >
            {isEditing ? <Eye className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
          </button>

          <button
            onClick={handleDelete}
            title="Delete card (or press Delete key)"
            className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {isEditing ? (
          <div className="w-full h-full p-2 nodrag bg-slate-50 flex flex-col">
            <textarea
              value={text}
              onChange={(e) => handleTextChange(e.target.value)}
              placeholder="Edit note markdown..."
              className="w-full h-full p-2.5 font-mono text-xs text-slate-800 bg-white border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-amber-500/50 resize-none leading-relaxed select-text"
              onKeyDown={(e) => e.stopPropagation()}
            />
          </div>
        ) : (
          <div
            onDoubleClick={() => setIsEditing(true)}
            className="w-full h-full overflow-y-auto p-4 select-text font-sans text-xs text-slate-700 leading-relaxed space-y-2 prose prose-slate max-w-none prose-sm prose-headings:font-bold prose-headings:text-slate-900 prose-headings:border-b prose-headings:border-slate-100 prose-headings:pb-1 prose-code:bg-slate-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-[11px] prose-code:font-mono"
            dangerouslySetInnerHTML={{ __html: renderedHtml }}
          />
        )}
      </div>

      {/* Footer Tag */}
      <div className="px-3 py-1 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[9px] text-slate-400 font-mono flex-shrink-0">
        <span>{isEditing ? 'Editing Mode' : 'Double-click to edit'}</span>
        <span>ID: {id.substring(0, 8)}</span>
      </div>
    </div>
  );
});

TextCardNode.displayName = 'TextCardNode';
