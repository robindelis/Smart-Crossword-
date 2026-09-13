import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { FileText, Image as ImageIcon, ExternalLink, Cpu, BookOpen, Layers } from 'lucide-react';
import { api } from '../../services/api';

const colorTopBorders: Record<string, string> = {
  '1': 'border-t-red-500',
  '2': 'border-t-orange-500',
  '3': 'border-t-amber-500',
  '4': 'border-t-emerald-500',
  '5': 'border-t-sky-500',
  '6': 'border-t-purple-500',
};

const domainIcons: Record<string, React.ReactNode> = {
  hardware: <Cpu className="w-3.5 h-3.5 text-sky-600" />,
  cad: <Layers className="w-3.5 h-3.5 text-red-600" />,
  docs: <BookOpen className="w-3.5 h-3.5 text-purple-600" />,
};

export const FileCardNode: React.FC<NodeProps> = memo(({ data, selected }) => {
  const filePath = (data.file as string) || '';
  const color = (data.color as string) || '5';
  const topBorder = colorTopBorders[color] || 'border-t-sky-500';

  const ext = filePath.split('.').pop()?.toLowerCase() || '';
  const isImage = ['png', 'jpg', 'jpeg', 'webp', 'svg'].includes(ext);
  const filename = filePath.split('/').pop() || filePath;
  const dirPath = filePath.substring(0, filePath.lastIndexOf('/')) || 'root';

  const onOpen = () => {
    if (data.onOpenFile && typeof data.onOpenFile === 'function') {
      data.onOpenFile(filePath);
    }
  };

  return (
    <div
      onClick={onOpen}
      className={`bg-white rounded-lg border border-slate-200 border-t-4 ${topBorder} shadow-sm hover:shadow-md transition-all duration-150 flex flex-col justify-between overflow-hidden cursor-pointer ${
        selected ? 'ring-2 ring-engineering-amber ring-offset-2 shadow-lg' : ''
      }`}
      style={{
        width: '100%',
        height: '100%',
      }}
    >
      {/* Handles on all 4 sides */}
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="target" position={Position.Left} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />

      {/* Header */}
      <div className="p-3 pb-2 border-b border-slate-100 flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 min-w-0">
          {isImage ? (
            <ImageIcon className="w-4 h-4 text-amber-600 flex-shrink-0" />
          ) : (
            domainIcons[dirPath.split('/')[0]] || <FileText className="w-4 h-4 text-slate-500 flex-shrink-0" />
          )}
          <span className="font-semibold text-xs text-slate-800 truncate" title={filename}>
            {filename}
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded uppercase flex-shrink-0">
          {ext}
        </span>
      </div>

      {/* Body Preview */}
      <div className="flex-1 p-2.5 overflow-hidden flex flex-col justify-center items-center bg-slate-50/50">
        {isImage ? (
          <div className="w-full h-full relative rounded overflow-hidden border border-slate-200 bg-white flex items-center justify-center group">
            <img
              src={api.getFileImageUrl(filePath)}
              alt={filename}
              className="max-w-full max-h-full object-contain p-1 transition-transform duration-200 group-hover:scale-105"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-slate-900/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <span className="bg-slate-900/80 text-white text-[10px] px-2 py-1 rounded flex items-center gap-1 shadow">
                <ExternalLink className="w-3 h-3" /> Inspect Render
              </span>
            </div>
          </div>
        ) : (
          <div className="w-full h-full flex flex-col justify-between p-2 text-slate-600">
            <div className="text-[11px] font-mono text-slate-500 line-clamp-3 leading-relaxed">
              Path: <span className="text-slate-800">{filePath}</span>
            </div>
            <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-200/60">
              <span className="text-[10px] text-slate-400 font-mono">Live Sync</span>
              <span className="inline-flex items-center gap-1 text-[10px] font-medium text-engineering-amber hover:underline">
                Read Markdown <ExternalLink className="w-3 h-3" />
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Breadcrumb */}
      <div className="px-3 py-1.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[9px] font-mono text-slate-400">
        <span className="truncate">{dirPath}/</span>
        <span>Obsidian Linked</span>
      </div>
    </div>
  );
});

FileCardNode.displayName = 'FileCardNode';
