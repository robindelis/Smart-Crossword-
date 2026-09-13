export type CanvasNodeType = 'group' | 'text' | 'file';

export interface ObsidianCanvasNode {
  id: string;
  type: CanvasNodeType;
  x: number;
  y: number;
  width: number;
  height: number;
  color?: string; // '1' | '2' | '3' | '4' | '5' | '6'
  label?: string; // for group nodes
  text?: string;  // for text nodes
  file?: string;  // for file nodes
}

export interface ObsidianCanvasEdge {
  id: string;
  fromNode: string;
  fromSide?: 'top' | 'right' | 'bottom' | 'left';
  toNode: string;
  toSide?: 'top' | 'right' | 'bottom' | 'left';
  label?: string;
  color?: string;
}

export interface ObsidianCanvasData {
  nodes: ObsidianCanvasNode[];
  edges: ObsidianCanvasEdge[];
}

export interface TaskItem {
  id: string;
  text: string;
  completed: boolean;
  subtasks?: TaskItem[];
}

export interface TaskBoardData {
  backlog: TaskItem[];
  inProgress: TaskItem[];
  done: TaskItem[];
}

export interface Milestone {
  name: string;
  done: boolean;
  active?: boolean;
}

export interface RoadmapStage {
  phase: string;
  status: 'active' | 'upcoming' | 'completed';
  milestones: Milestone[];
}

export interface DecisionEntry {
  id: string;
  date: string;
  topic: string;
  reason: string;
}

export interface ProjectStateData {
  currentPhase: string;
  roadmapStages: RoadmapStage[];
  decisions: DecisionEntry[];
}

export interface ActiveFilePreview {
  path: string;
  filename: string;
  content?: string;
  isImage?: boolean;
}
