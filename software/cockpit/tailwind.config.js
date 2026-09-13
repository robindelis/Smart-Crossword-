/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          bg: "#f8fafc",
          grid: "#e2e8f0",
          card: "#ffffff",
          border: "#cbd5e1",
        },
        engineering: {
          copper: "#b45309",
          slate: "#0f172a",
          muted: "#64748b",
          emerald: "#15803d",
          amber: "#d97706",
          blue: "#0284c7",
        },
        obsidian: {
          1: { text: "#b91c1c", bg: "#fef2f2", border: "#f87171", label: "CAD & Mechanics" },
          2: { text: "#c2410c", bg: "#fff7ed", border: "#fb923c", label: "Commercial & Launch" },
          3: { text: "#a16207", bg: "#fefce8", border: "#facc15", label: "Ideas & Backlog" },
          4: { text: "#047857", bg: "#ecfdf5", border: "#34d399", label: "Software & Lexicons" },
          5: { text: "#0369a1", bg: "#f0f9ff", border: "#38bdf8", label: "Hardware & RFID" },
          6: { text: "#6d28d9", bg: "#f5f3ff", border: "#a78bfa", label: "Tasks & State" },
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      }
    },
  },
  plugins: [],
};
