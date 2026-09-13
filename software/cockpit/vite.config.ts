import { defineConfig, Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'node:path';

const REPO_ROOT = path.resolve(__dirname, '../../');
const CANVAS_FILE = path.join(REPO_ROOT, 'Project_Cockpit.canvas');
const TASKS_FILE = path.join(REPO_ROOT, 'docs/Project_Tasks.md');
const STATE_FILE = path.join(REPO_ROOT, 'docs/PROJECT_STATE.md');

function readJsonBody(req: any): Promise<any> {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk: any) => { body += chunk; });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        reject(err);
      }
    });
    req.on('error', reject);
  });
}

function parseTasksMarkdown(content: string) {
  const lines = content.split('\n');
  const sections: { backlog: any[]; inProgress: any[]; done: any[] } = {
    backlog: [],
    inProgress: [],
    done: [],
  };

  let currentSection: 'backlog' | 'inProgress' | 'done' | null = null;
  let currentParentTask: any = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed.includes('## 📋 Backlog')) {
      currentSection = 'backlog';
      currentParentTask = null;
      continue;
    } else if (trimmed.includes('## ⏳ In Progress')) {
      currentSection = 'inProgress';
      currentParentTask = null;
      continue;
    } else if (trimmed.includes('## ✅ Done')) {
      currentSection = 'done';
      currentParentTask = null;
      continue;
    }

    if (!currentSection) continue;

    // Check for task items
    const match = line.match(/^(\s*)-\s*\[([ xX])\]\s*(.*)$/);
    if (match) {
      const indent = match[1].length;
      const completed = match[2].toLowerCase() === 'x';
      const text = match[3];

      const taskObj = {
        id: `task-${currentSection}-${i}`,
        text,
        completed,
        subtasks: [] as any[],
      };

      if (indent >= 2 && currentParentTask) {
        currentParentTask.subtasks.push(taskObj);
      } else {
        sections[currentSection].push(taskObj);
        currentParentTask = taskObj;
      }
    }
  }

  return sections;
}

function serializeTasksMarkdown(sections: { backlog: any[]; inProgress: any[]; done: any[] }): string {
  let md = '# Project Tasks\n\n';

  md += '## 📋 Backlog\n\n';
  for (const t of sections.backlog) {
    md += `- [${t.completed ? 'x' : ' '}] ${t.text}\n`;
    if (t.subtasks) {
      for (const st of t.subtasks) {
        md += `  - [${st.completed ? 'x' : ' '}] ${st.text}\n`;
      }
    }
  }

  md += '\n## ⏳ In Progress (Phase 1: Hardware Bench Assembly & Testing)\n\n';
  for (const t of sections.inProgress) {
    md += `- [${t.completed ? 'x' : ' '}] ${t.text}\n`;
    if (t.subtasks) {
      for (const st of t.subtasks) {
        md += `  - [${st.completed ? 'x' : ' '}] ${st.text}\n`;
      }
    }
  }

  md += '\n## ✅ Done\n\n';
  for (const t of sections.done) {
    md += `- [${t.completed ? 'x' : ' '}] ${t.text}\n`;
    if (t.subtasks) {
      for (const st of t.subtasks) {
        md += `  - [${st.completed ? 'x' : ' '}] ${st.text}\n`;
      }
    }
  }

  return md;
}

function parseProjectStateMarkdown(content: string) {
  // Extract phase
  const phaseMatch = content.match(/\*\*Phase \d+: [^*]+\*\*/);
  const currentPhase = phaseMatch ? phaseMatch[0].replace(/\*\*/g, '') : 'Phase 1: Test Board and Game Engine';

  // Extract Decision table
  const decisions: any[] = [];
  const lines = content.split('\n');
  let inTable = false;

  for (const line of lines) {
    if (line.includes('| ID') && line.includes('Date') && line.includes('Topic') && line.includes('Decision')) {
      inTable = true;
      continue;
    }
    if (inTable) {
      if (line.trim().startsWith('| :--') || line.trim().startsWith('|:--')) continue;
      if (!line.trim().startsWith('|')) {
        if (decisions.length > 0) break; // Finished table
        continue;
      }
      const parts = line.split('|').map(s => s.trim()).filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      if (parts.length >= 4) {
        const id = parts[0].replace(/\*\*/g, '');
        const date = parts[1];
        const topic = parts[2];
        const reason = parts[3];
        decisions.push({ id, date, topic, reason });
      }
    }
  }

  // Extract roadmap tasks
  const roadmapStages = [
    {
      phase: "Phase 1: Test Board & Code",
      status: "active",
      milestones: [
        { name: "Team setup & rules", done: true },
        { name: "Kickstarter market plan", done: true },
        { name: "Game engine in C (WebAssembly & firmware)", done: true },
        { name: "Native Android companion prototype (Kotlin & Compose)", done: true },
        { name: "4x4 test circuit board (KiCad 10, zero-DRC)", done: true },
        { name: "1-page pre-launch website ($1 VIP pre-orders)", done: true },
        { name: "Bench driver code & JLCPCB manufacturing package", done: true },
        { name: "Hardware delivery & bench test", done: false, active: true },
      ]
    },
    {
      phase: "Phase 2: Full Board & Screen",
      status: "upcoming",
      milestones: [
        { name: "Full 15x15 circuit board (225 coil mux array)", done: false },
        { name: "Screen code & speaker setup (3.5\" LCD & I2S)", done: false },
      ]
    },
    {
      phase: "Phase 3: Phone App & Launch",
      status: "upcoming",
      milestones: [
        { name: "Phone app & server sync (MQTT / Firestore)", done: false },
        { name: "Kickstarter launch (750 VIP backers)", done: false },
      ]
    }
  ];

  return {
    currentPhase,
    roadmapStages,
    decisions,
  };
}

function projectCockpitPlugin(): Plugin {
  return {
    name: 'project-cockpit-api',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        const urlObj = new URL(req.url || '/', `http://${req.headers.host}`);
        const pathname = urlObj.pathname;

        try {
          if (pathname === '/api/canvas') {
            if (req.method === 'GET' || req.method === 'HEAD') {
              const rawData = fs.readFileSync(CANVAS_FILE, 'utf-8');
              const canvasData = JSON.parse(rawData);

              // Attach markdown file contents directly for fast rendering
              if (canvasData.nodes && Array.isArray(canvasData.nodes)) {
                for (const node of canvasData.nodes) {
                  if (node.type === 'file' && node.file) {
                    const absPath = path.join(REPO_ROOT, node.file);
                    const ext = path.extname(node.file).toLowerCase();
                    if (['.md', '.txt', '.loom'].includes(ext) && fs.existsSync(absPath)) {
                      try {
                        node.fileContent = fs.readFileSync(absPath, 'utf-8');
                      } catch (e) {
                        console.error('Error reading file for node:', node.file, e);
                      }
                    }
                  }
                }
              }

              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(canvasData));
              return;
            } else if (req.method === 'PUT') {
              const body = await readJsonBody(req);
              // Clean fileContent before saving to Project_Cockpit.canvas so it stays pure
              if (body.nodes && Array.isArray(body.nodes)) {
                body.nodes = body.nodes.map((n: any) => {
                  const copy = { ...n };
                  delete copy.fileContent;
                  return copy;
                });
              }
              fs.writeFileSync(CANVAS_FILE, JSON.stringify(body, null, 2), 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true, timestamp: Date.now() }));
              return;
            }
          }

          if (pathname === '/api/tasks') {
            if (req.method === 'GET' || req.method === 'HEAD') {
              const content = fs.readFileSync(TASKS_FILE, 'utf-8');
              const tasks = parseTasksMarkdown(content);
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(tasks));
              return;
            } else if (req.method === 'PUT') {
              const body = await readJsonBody(req);
              const md = serializeTasksMarkdown(body);
              fs.writeFileSync(TASKS_FILE, md, 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true, timestamp: Date.now() }));
              return;
            }
          }

          if (pathname === '/api/state') {
            if (req.method === 'GET' || req.method === 'HEAD') {
              const content = fs.readFileSync(STATE_FILE, 'utf-8');
              const state = parseProjectStateMarkdown(content);
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(state));
              return;
            }
          }

          if (pathname === '/api/file') {
            if (req.method === 'GET' || req.method === 'HEAD') {
              const filePathQuery = urlObj.searchParams.get('path');
              if (!filePathQuery) {
                res.statusCode = 400;
                res.end(JSON.stringify({ error: 'Missing path parameter' }));
                return;
              }

              // Prevent path traversal outside repository
              const targetPath = path.resolve(REPO_ROOT, filePathQuery.replace(/^\/+/, ''));
              if (!targetPath.startsWith(REPO_ROOT)) {
                res.statusCode = 403;
                res.end(JSON.stringify({ error: 'Forbidden path' }));
                return;
              }

              if (!fs.existsSync(targetPath)) {
                res.statusCode = 404;
                res.end(JSON.stringify({ error: 'File not found' }));
                return;
              }

              const ext = path.extname(targetPath).toLowerCase();
              if (['.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif'].includes(ext)) {
                const mimeTypes: Record<string, string> = {
                  '.png': 'image/png',
                  '.jpg': 'image/jpeg',
                  '.jpeg': 'image/jpeg',
                  '.webp': 'image/webp',
                  '.svg': 'image/svg+xml',
                  '.gif': 'image/gif',
                };
                res.setHeader('Content-Type', mimeTypes[ext] || 'application/octet-stream');
                const stream = fs.createReadStream(targetPath);
                stream.pipe(res);
                return;
              }

              // Text or markdown file
              const content = fs.readFileSync(targetPath, 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                path: filePathQuery,
                filename: path.basename(targetPath),
                content,
              }));
              return;
            } else if (req.method === 'PUT') {
              const body = await readJsonBody(req);
              const filePath = body.path;
              if (!filePath) {
                res.statusCode = 400;
                res.end(JSON.stringify({ error: 'Missing path in request body' }));
                return;
              }

              const targetPath = path.resolve(REPO_ROOT, filePath.replace(/^\/+/, ''));
              if (!targetPath.startsWith(REPO_ROOT)) {
                res.statusCode = 403;
                res.end(JSON.stringify({ error: 'Forbidden path' }));
                return;
              }

              fs.writeFileSync(targetPath, body.content ?? '', 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true, timestamp: Date.now() }));
              return;
            }
          }
        } catch (err: any) {
          console.error('[API Error]:', err);
          res.statusCode = 500;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ error: err.message || 'Internal server error' }));
          return;
        }

        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [
    react(),
    projectCockpitPlugin(),
  ],
  server: {
    port: 5173,
    host: true,
  },
});
