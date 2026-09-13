import React, { memo } from 'react';
import { NodeProps } from '@xyflow/react';

const colorStyles: Record<string, { border: string; bg: string; badge: string; text: string }> = {
  '1': { border: 'border-red-300', bg: 'bg-red-50/30', badge: 'bg-red-100 text-red-800 border-red-200', text: 'text-red-900' },
  '2': { border: 'border-orange-300', bg: 'bg-orange-50/30', badge: 'bg-orange-100 text-orange-800 border-orange-200', text: 'text-orange-900' },
  '3': { border: 'border-amber-300', bg: 'bg-amber-50/30', badge: 'bg-amber-100 text-amber-800 border-amber-200', text: 'text-amber-900' },
  '4': { border: 'border-emerald-300', bg: 'bg-emerald-50/30', badge: 'bg-emerald-100 text-emerald-800 border-emerald-200', text: 'text-emerald-900' },
  '5': { border: 'border-sky-300', bg: 'bg-sky-50/30', badge: 'bg-sky-100 text-sky-800 border-sky-200', text: 'text-sky-900' },
  '6': { border: 'border-purple-300', bg: 'bg-purple-50/30', badge: 'bg-purple-100 text-purple-800 border-purple-200', text: 'text-purple-900' },
};

export const GroupNode: React.FC<NodeProps> = memo(({ data, selected }) => {
  const color = (data.color as string) || '5';
  const style = colorStyles[color] || colorStyles['5'];
  const label = (data.label as string) || 'Section';

  return (
    <div
      className={`w-full h-full rounded-xl border-2 border-dashed ${style.border} ${style.bg} transition-all duration-150 pointer-events-none ${
        selected ? 'ring-2 ring-engineering-amber ring-offset-2' : ''
      }`}
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      <div className="p-4">
        <span
          className={`inline-flex items-center px-3 py-1 rounded-md text-xs font-mono font-semibold tracking-wide border shadow-sm ${style.badge}`}
        >
          {label.toUpperCase()}
        </span>
      </div>
    </div>
  );
});

GroupNode.displayName = 'GroupNode';
