import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';

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

function formatSimpleMarkdown(text: string) {
  if (!text) return null;

  const lines = text.split('\n');
  return (
    <div className="space-y-1.5 text-slate-700 text-xs leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (trimmed.startsWith('## ')) {
          return (
            <h3 key={idx} className="font-semibold text-sm text-slate-900 border-b border-slate-100 pb-1 mb-2">
              {trimmed.replace('## ', '')}
            </h3>
          );
        }
        if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
          const item = trimmed.substring(2);
          return (
            <div key={idx} className="flex items-start gap-1.5 pl-1">
              <span className="text-slate-400 mt-0.5">•</span>
              <span className="flex-1" dangerouslySetInnerHTML={{
                __html: item
                  .replace(/\*\*([^*]+)\*\*/g, '<strong class="text-slate-900 font-semibold">$1</strong>')
                  .replace(/`([^`]+)`/g, '<code class="bg-slate-100 px-1 py-0.5 rounded text-[11px] font-mono text-slate-800">$1</code>')
                  .replace(/\$([^$]+)\$/g, '<span class="font-mono text-[11px] text-amber-800 font-medium">$1</span>')
              }} />
            </div>
          );
        }
        if (!trimmed) {
          return <div key={idx} className="h-1" />;
        }
        return (
          <p key={idx} dangerouslySetInnerHTML={{
            __html: trimmed
              .replace(/\*\*([^*]+)\*\*/g, '<strong class="text-slate-900 font-semibold">$1</strong>')
              .replace(/`([^`]+)`/g, '<code class="bg-slate-100 px-1 py-0.5 rounded text-[11px] font-mono text-slate-800">$1</code>')
              .replace(/\$([^$]+)\$/g, '<span class="font-mono text-[11px] text-amber-800 font-medium">$1</span>')
          }} />
        );
      })}
    </div>
  );
}

export const TextCardNode: React.FC<NodeProps> = memo(({ data, selected }) => {
  const color = (data.color as string) || '5';
  const text = (data.text as string) || '';
  const topBorder = colorTopBorders[color] || 'border-t-sky-500';
  const badgeStyle = colorBadges[color] || colorBadges['5'];

  return (
    <div
      className={`bg-white rounded-lg border border-slate-200 border-t-4 ${topBorder} shadow-sm hover:shadow-md transition-all duration-150 p-3.5 flex flex-col justify-between overflow-hidden cursor-pointer ${
        selected ? 'ring-2 ring-engineering-amber ring-offset-2 shadow-lg' : ''
      }`}
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {/* Handles */}
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="target" position={Position.Left} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />

      {/* Content */}
      <div className="overflow-y-auto pr-1 flex-1 select-text">
        {formatSimpleMarkdown(text)}
      </div>

      {/* Card Footer Tag */}
      <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 font-mono">
        <span className={`px-1.5 py-0.5 rounded border ${badgeStyle} text-[9px]`}>
          NOTE CARD
        </span>
        <span>ID: {(data.id as string)?.substring(0, 8)}</span>
      </div>
    </div>
  );
});

TextCardNode.displayName = 'TextCardNode';
