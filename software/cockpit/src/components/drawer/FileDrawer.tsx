import React, { useState, useEffect } from 'react';
import { X, Copy, Check, FileText, Image as ImageIcon, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

interface FileDrawerProps {
  filePath: string | null;
  onClose: () => void;
}

export const FileDrawer: React.FC<FileDrawerProps> = ({ filePath, onClose }) => {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!filePath) {
      setContent('');
      return;
    }

    const ext = filePath.split('.').pop()?.toLowerCase() || '';
    const isImage = ['png', 'jpg', 'jpeg', 'webp', 'svg'].includes(ext);

    if (isImage) {
      setLoading(false);
      return;
    }

    setLoading(true);
    api.fetchFile(filePath)
      .then((data) => {
        setContent(data.content || '');
        setLoading(false);
      })
      .catch((err) => {
        setContent(`Error loading file content: ${err.message}`);
        setLoading(false);
      });
  }, [filePath]);

  if (!filePath) return null;

  const ext = filePath.split('.').pop()?.toLowerCase() || '';
  const isImage = ['png', 'jpg', 'jpeg', 'webp', 'svg'].includes(ext);
  const filename = filePath.split('/').pop() || filePath;

  const handleCopyPath = () => {
    navigator.clipboard.writeText(filePath);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end bg-slate-900/30 backdrop-blur-xs transition-opacity animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-250">
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            {isImage ? (
              <ImageIcon className="w-4 h-4 text-amber-600 flex-shrink-0" />
            ) : (
              <FileText className="w-4 h-4 text-sky-600 flex-shrink-0" />
            )}
            <div className="min-w-0">
              <h3 className="font-bold text-sm text-slate-900 truncate" title={filename}>
                {filename}
              </h3>
              <p className="text-[11px] font-mono text-slate-400 truncate" title={filePath}>
                {filePath}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 flex-shrink-0">
            <button
              onClick={handleCopyPath}
              title="Copy relative file path"
              className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-200/70 rounded transition-colors"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
            </button>
            <button
              onClick={onClose}
              title="Close drawer"
              className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-200/70 rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Drawer Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center gap-2 text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin text-engineering-amber" />
              <span className="text-xs font-mono">Reading from disk...</span>
            </div>
          ) : isImage ? (
            <div className="flex flex-col items-center justify-center gap-4 py-8">
              <div className="border border-slate-200 rounded-lg p-2 bg-slate-50 shadow-inner max-w-full">
                <img
                  src={api.getFileImageUrl(filePath)}
                  alt={filename}
                  className="max-h-[70vh] object-contain rounded shadow"
                />
              </div>
              <span className="text-xs font-mono text-slate-400">High-Resolution Hardware/CAD 3D Render</span>
            </div>
          ) : (
            <div className="prose prose-slate max-w-none text-xs font-mono select-text whitespace-pre-wrap leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200">
              {content}
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="p-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>Read-only inspection buffer</span>
          <span>Workspace root linked</span>
        </div>
      </div>
    </div>
  );
};
