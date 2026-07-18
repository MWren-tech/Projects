import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0a0d12",
        surface: "#12161d",
        "surface-2": "#1a1f29",
        border: "#2a313d",
        muted: "#9aa6b6",        // ~5.3:1 on bg — passes WCAG AA for body text
        "muted-strong": "#b8c2d0",
        fg: "#e7ecf3",
        ring: "#69d2ff",
        accent: "#3ee6a0",        // electric mint — primary accent
        "accent-dim": "#1f8f63",
        gold: "#f5c451",
        danger: "#ff5d6c",
        warn: "#ffb454",
        info: "#5aa9ff",
        // position colours
        gk: "#f5c451",
        def: "#5aa9ff",
        mid: "#3ee6a0",
        fwd: "#ff7a8a",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      borderRadius: { xl: "0.9rem", "2xl": "1.25rem" },
      boxShadow: {
        card: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(62,230,160,0.25), 0 0 24px -6px rgba(62,230,160,0.35)",
      },
    },
  },
  plugins: [],
};

export default config;
