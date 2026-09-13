import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  BackgroundVariant,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { GroupNode } from './GroupNode';
import { TextCardNode } from './TextCardNode';
import { FileCardNode } from './FileCardNode';
import { ObsidianCanvasData, ObsidianCanvasNode, ObsidianCanvasEdge } from '../../types/cockpit';
import { api } from '../../services/api';
import { Search, RotateCcw, CheckCircle2, RefreshCw } from 'lucide-react';

interface CanvasViewProps {
  onOpenFile: (filePath: string) => void;
  onSyncStatusChange: (status: 'idle' | 'saving' | 'saved' | 'error') => void;
}

const nodeTypes = {
  groupNode: GroupNode,
  textCardNode: TextCardNode,
  fileCardNode: FileCardNode,
};

export const CanvasView: React.FC<CanvasViewProps> = ({ onOpenFile, onSyncStatusChange }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDomain, setFilterDomain] = useState<string>('all');
  const [saveTimer, setSaveTimer] = useState<NodeJS.Timeout | null>(null);
  const rawCanvasRef = useRef<ObsidianCanvasData | null>(null);

  // Load canvas data from disk
  const loadCanvas = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.fetchCanvas();
      rawCanvasRef.current = data;

      // Map Obsidian nodes to ReactFlow nodes
      const rfNodes: Node[] = data.nodes.map((node: ObsidianCanvasNode) => {
        let type = 'textCardNode';
        let zIndex = 1;

        if (node.type === 'group') {
          type = 'groupNode';
          zIndex = -10;
        } else if (node.type === 'file') {
          type = 'fileCardNode';
          zIndex = 1;
        }

        return {
          id: node.id,
          type,
          position: { x: node.x, y: node.y },
          style: {
            width: node.width,
            height: node.height,
            zIndex,
          },
          data: {
            ...node,
            onOpenFile,
          },
          draggable: true,
          selectable: true,
        };
      });

      // Map Obsidian edges to ReactFlow edges
      const rfEdges: Edge[] = data.edges.map((edge: ObsidianCanvasEdge) => ({
        id: edge.id,
        source: edge.fromNode,
        target: edge.toNode,
        sourceHandle: edge.fromSide || 'bottom',
        targetHandle: edge.toSide || 'top',
        label: edge.label || '',
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 14,
          height: 14,
          color: '#64748b',
        },
        style: { stroke: '#64748b', strokeWidth: 1.5 },
      }));

      setNodes(rfNodes);
      setEdges(rfEdges);
      onSyncStatusChange('saved');
    } catch (err) {
      console.error('Failed to load canvas data:', err);
      onSyncStatusChange('error');
    } finally {
      setLoading(false);
    }
  }, [onOpenFile, onSyncStatusChange, setNodes, setEdges]);

  useEffect(() => {
    loadCanvas();
  }, [loadCanvas]);

  // Handle bidirectional save when node positions change
  const handleNodesChange = useCallback(
    (changes: any) => {
      onNodesChange(changes);

      // Check if any change was a position change
      const hasPositionChange = changes.some(
        (c: any) => c.type === 'position' && c.dragging === false
      );

      if (hasPositionChange && rawCanvasRef.current) {
        if (saveTimer) clearTimeout(saveTimer);
        onSyncStatusChange('saving');

        const timer = setTimeout(async () => {
          try {
            // Update node positions in rawCanvasRef
            setNodes((currentNodes) => {
              if (!rawCanvasRef.current) return currentNodes;

              const nodeMap = new Map(currentNodes.map((n) => [n.id, n]));
              const updatedObsidianNodes: ObsidianCanvasNode[] = rawCanvasRef.current.nodes.map(
                (origNode) => {
                  const rfNode = nodeMap.get(origNode.id);
                  if (rfNode) {
                    return {
                      ...origNode,
                      x: Math.round(rfNode.position.x),
                      y: Math.round(rfNode.position.y),
                    };
                  }
                  return origNode;
                }
              );

              const updatedCanvas: ObsidianCanvasData = {
                ...rawCanvasRef.current,
                nodes: updatedObsidianNodes,
              };

              // Send to disk API
              api.saveCanvas(updatedCanvas).then(() => {
                rawCanvasRef.current = updatedCanvas;
                onSyncStatusChange('saved');
              }).catch((e) => {
                console.error('Error auto-saving canvas:', e);
                onSyncStatusChange('error');
              });

              return currentNodes;
            });
          } catch (e) {
            console.error('Failed to serialize canvas:', e);
            onSyncStatusChange('error');
          }
        }, 800);

        setSaveTimer(timer);
      }
    },
    [onNodesChange, saveTimer, onSyncStatusChange, setNodes]
  );

  // Filtered nodes based on search or category
  const filteredNodes = useMemo(() => {
    if (!searchQuery && filterDomain === 'all') return nodes;

    return nodes.map((node) => {
      const label = (node.data.label as string) || '';
      const text = (node.data.text as string) || '';
      const file = (node.data.file as string) || '';
      const color = (node.data.color as string) || '';

      let matchDomain = true;
      if (filterDomain !== 'all') {
        matchDomain = color === filterDomain;
      }

      let matchQuery = true;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        matchQuery =
          label.toLowerCase().includes(q) ||
          text.toLowerCase().includes(q) ||
          file.toLowerCase().includes(q);
      }

      const isMatch = matchDomain && matchQuery;
      return {
        ...node,
        style: {
          ...node.style,
          opacity: isMatch || node.type === 'groupNode' ? 1 : 0.15,
        },
      };
    });
  }, [nodes, searchQuery, filterDomain]);

  if (loading) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-canvas-bg gap-3">
        <RefreshCw className="w-6 h-6 text-engineering-amber animate-spin" />
        <span className="text-sm font-mono text-slate-500">Loading Project_Cockpit.canvas...</span>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      <ReactFlow
        nodes={filteredNodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.1 }}
        minZoom={0.05}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.2 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1.2} color="#cbd5e1" />
        <Controls position="bottom-left" showInteractive={false} />
        <MiniMap
          position="bottom-right"
          nodeColor={(n) => {
            if (n.type === 'groupNode') return '#e2e8f0';
            const color = (n.data?.color as string) || '5';
            const colors: Record<string, string> = {
              '1': '#f87171',
              '2': '#fb923c',
              '3': '#facc15',
              '4': '#34d399',
              '5': '#38bdf8',
              '6': '#a78bfa',
            };
            return colors[color] || '#cbd5e1';
          }}
          className="rounded-lg shadow-sm overflow-hidden"
          zoomable
          pannable
        />

        {/* Top Floating Utility Filter Panel */}
        <Panel position="top-left" className="bg-white/95 backdrop-blur-sm p-2 rounded-lg border border-slate-200 shadow-md flex items-center gap-3">
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 pointer-events-none" />
            <input
              type="text"
              placeholder="Search cards, files, specs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1 text-xs border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-engineering-amber w-60"
            />
          </div>

          <div className="h-4 w-px bg-slate-200" />

          {/* Domain Filter Pills */}
          <div className="flex items-center gap-1 text-[11px] font-mono">
            <button
              onClick={() => setFilterDomain('all')}
              className={`px-2 py-0.5 rounded border transition-colors ${
                filterDomain === 'all'
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              ALL
            </button>
            <button
              onClick={() => setFilterDomain('5')}
              className={`px-2 py-0.5 rounded border transition-colors ${
                filterDomain === '5'
                  ? 'bg-sky-600 text-white border-sky-600'
                  : 'bg-sky-50 text-sky-700 border-sky-200 hover:bg-sky-100'
              }`}
            >
              HW / RF
            </button>
            <button
              onClick={() => setFilterDomain('1')}
              className={`px-2 py-0.5 rounded border transition-colors ${
                filterDomain === '1'
                  ? 'bg-red-600 text-white border-red-600'
                  : 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100'
              }`}
            >
              CAD
            </button>
            <button
              onClick={() => setFilterDomain('4')}
              className={`px-2 py-0.5 rounded border transition-colors ${
                filterDomain === '4'
                  ? 'bg-emerald-600 text-white border-emerald-600'
                  : 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100'
              }`}
            >
              SW / ANDROID
            </button>
            <button
              onClick={() => setFilterDomain('2')}
              className={`px-2 py-0.5 rounded border transition-colors ${
                filterDomain === '2'
                  ? 'bg-orange-600 text-white border-orange-600'
                  : 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100'
              }`}
            >
              COMMERCIAL
            </button>
          </div>

          <div className="h-4 w-px bg-slate-200" />

          <button
            onClick={loadCanvas}
            title="Reload from disk"
            className="p-1 hover:bg-slate-100 rounded text-slate-500 hover:text-slate-900"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </Panel>

        {/* Floating Metrics Badge */}
        <Panel position="top-right" className="bg-white/95 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm flex items-center gap-2 text-xs font-mono text-slate-600">
          <CheckCircle2 className="w-3.5 h-3.5 text-engineering-emerald" />
          <span>{nodes.length} Nodes</span>
          <span className="text-slate-300">•</span>
          <span>{edges.length} Edges</span>
        </Panel>
      </ReactFlow>
    </div>
  );
};
