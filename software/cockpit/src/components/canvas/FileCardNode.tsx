import React, { memo, useState, useEffect, useRef } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { FileText, Image as ImageIcon, ExternalLink, Cpu, BookOpen, Layers, Edit3, Check, Trash2, Eye } from 'lucide-react';
import { api } from '../../services/api';
import { marked } from 'marked';

// Configure marked
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

const domainIcons: Record<string, React.ReactNode> = {
  hardware: <Cpu className="w-3.5 h-3.5 text-sky-600" />,
  cad: <Layers className="w-3.5 h-3.5 text-red-600" />,
  docs: <BookOpen className="w-3.5 h-3.5 text-purple-600" />,
};

export const FileCardNode: React.FC<NodeProps> = memo(({ id, data, selected }) => {
  const filePath = (data.file as string) || '';
  const color = (data.color as string) || '5';
  const topBorder = colorTopBorders[color] || 'border-t-sky-500';

  const ext = filePath.split('.').pop()?.toLowerCase() || '';
  const isImage = ['png', 'jpg', 'jpeg', 'webp', 'svg'].includes(ext);
  const filename = filePath.split('/').pop() || filePath;
  const dirPath = filePath.substring(0, filePath.lastIndexOf('/')) || 'root';

  // Markdown content state
  const [content, setContent] = useState<string>((data.fileContent as string) || '');
  const [isEditing, setIsEditing] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
  const saveTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (data.fileContent) {
      setContent(data.fileContent as string);
    } else if (!isImage && filePath) {
      // Fallback fetch if not pre-attached
      api.fetchFile(filePath).then((res) => {
        if (res.content) setContent(res.content);
      }).catch(console.error);
    }
  }, [data.fileContent, isImage, filePath]);

  const handleContentChange = (newVal: string) => {
    setContent(newVal);
    setSaveStatus('saving');

    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(async () => {
      try {
        await api.saveFile(filePath, newVal);
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
      } catch (err) {
        console.error('Failed to auto-save file:', err);
        setSaveStatus('idle');
      }
    }, 800);
  };

  const handleOpenDrawer = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (data.onOpenFile && typeof data.onOpenFile === 'function') {
      data.onOpenFile(filePath);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (data.onDeleteNode && typeof data.onDeleteNode === 'function') {
      data.onDeleteNode(id);
    }
  };

  // Convert markdown to HTML safely
  const renderedHtml = React.useMemo(() => {
    if (!content) return '';
    try {
      return marked.parse(content) as string;
    } catch (e) {
      return content;
    }
  }, [content]);

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
      {/* React Flow Handles on all 4 sides */}
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="target" position={Position.Left} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />
      <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-slate-400 hover:bg-engineering-amber border-2 border-white" />

      {/* Card Header */}
      <div className="p-3 pb-2 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between gap-2 flex-shrink-0">
        <div className="flex items-center gap-1.5 min-w-0">
          {isImage ? (
            <ImageIcon className="w-4 h-4 text-amber-600 flex-shrink-0" />
          ) : (
            domainIcons[dirPath.split('/')[0]] || <FileText className="w-4 h-4 text-slate-500 flex-shrink-0" />
          )}
          <span className="font-semibold text-xs text-slate-800 truncate" title={filename}>
            {filename}
          </span>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-200/60 px-1 py-0.2 rounded uppercase">
            {ext}
          </span>
        </div>

        {/* Header Action Tools */}
        <div className="flex items-center gap-1 flex-shrink-0 nodrag">
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

          {!isImage && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(!isEditing);
              }}
              title={isEditing ? 'View rendered preview' : 'Edit markdown file'}
              className={`p-1 rounded transition-colors ${
                isEditing
                  ? 'bg-amber-100 text-amber-800 hover:bg-amber-200'
                  : 'text-slate-400 hover:text-slate-800 hover:bg-slate-200/60'
              }`}
            >
              {isEditing ? <Eye className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
            </button>
          )}

          <button
            onClick={handleOpenDrawer}
            title="Inspect in side drawer"
            className="p-1 text-slate-400 hover:text-slate-800 hover:bg-slate-200/60 rounded transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
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

      {/* Card Body */}
      <div className="flex-1 overflow-hidden relative">
        {isImage ? (
          <div
            onClick={handleOpenDrawer}
            className="w-full h-full relative p-2 bg-slate-50 flex items-center justify-center group cursor-pointer"
          >
            <img
              src={api.getFileImageUrl(filePath)}
              alt={filename}
              className="max-w-full max-h-full object-contain p-1 transition-transform duration-200 group-hover:scale-105"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-slate-900/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <span className="bg-slate-900/80 text-white text-[10px] px-2 py-1 rounded flex items-center gap-1 shadow">
                <ExternalLink className="w-3 h-3" /> Zoom Render
              </span>
            </div>
          </div>
        ) : isEditing ? (
          <div className="w-full h-full p-2 nodrag flex flex-col bg-slate-50">
            <textarea
              value={content}
              onChange={(e) => handleContentChange(e.target.value)}
              placeholder="Edit markdown..."
              className="w-full h-full p-2.5 font-mono text-xs text-slate-800 bg-white border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-amber-500/50 resize-none leading-relaxed select-text"
              onKeyDown={(e) => e.stopPropagation()}
            />
          </div>
        ) : (
          <div
            onDoubleClick={() => setIsEditing(true)}
            className="w-full h-full overflow-y-auto p-4 select-text font-sans text-xs text-slate-700 leading-relaxed space-y-2 prose prose-slate max-w-none prose-sm prose-headings:font-bold prose-headings:text-slate-900 prose-headings:border-b prose-headings:border-slate-100 prose-headings:pb-1 prose-code:bg-slate-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-[11px] prose-code:font-mono prose-table:border prose-table:border-slate-200 prose-th:bg-slate-100 prose-th:p-1.5 prose-td:p-1.5 prose-th:border prose-td:border prose-td:border-slate-200"
            dangerouslySetInnerHTML={{ __html: renderedHtml }}
          />
        )}
      </div>

      {/* Footer Breadcrumb */}
      <div className="px-3 py-1.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[9px] font-mono text-slate-400 flex-shrink-0">
        <span className="truncate">{dirPath}/</span>
        <span>{isEditing ? 'Editing Mode' : 'Double-click to edit'}</span>
      </div>
    </div>
  );
});

FileCardNode.displayName = 'FileCardNode';
