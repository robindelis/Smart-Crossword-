import { ObsidianCanvasData, TaskBoardData, ProjectStateData } from '../types/cockpit';

export const api = {
  async fetchCanvas(): Promise<ObsidianCanvasData> {
    const res = await fetch('/api/canvas');
    if (!res.ok) throw new Error(`Failed to load canvas: ${res.statusText}`);
    return res.json();
  },

  async saveCanvas(data: ObsidianCanvasData): Promise<void> {
    const res = await fetch('/api/canvas', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to save canvas: ${res.statusText}`);
  },

  async fetchTasks(): Promise<TaskBoardData> {
    const res = await fetch('/api/tasks');
    if (!res.ok) throw new Error(`Failed to load tasks: ${res.statusText}`);
    return res.json();
  },

  async saveTasks(data: TaskBoardData): Promise<void> {
    const res = await fetch('/api/tasks', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to save tasks: ${res.statusText}`);
  },

  async fetchState(): Promise<ProjectStateData> {
    const res = await fetch('/api/state');
    if (!res.ok) throw new Error(`Failed to load project state: ${res.statusText}`);
    return res.json();
  },

  async fetchFile(filePath: string): Promise<{ filename: string; content?: string; isImage?: boolean }> {
    const ext = filePath.split('.').pop()?.toLowerCase() || '';
    const isImage = ['png', 'jpg', 'jpeg', 'webp', 'svg', 'gif'].includes(ext);

    if (isImage) {
      return {
        filename: filePath.split('/').pop() || filePath,
        isImage: true,
      };
    }

    const res = await fetch(`/api/file?path=${encodeURIComponent(filePath)}`);
    if (!res.ok) throw new Error(`Failed to load file: ${res.statusText}`);
    return res.json();
  },

  getFileImageUrl(filePath: string): string {
    return `/api/file?path=${encodeURIComponent(filePath)}`;
  }
};
