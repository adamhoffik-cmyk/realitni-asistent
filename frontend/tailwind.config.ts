import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        matrix: {
          // Primární paleta
          bg: "#000000",
          green: "#00FF41",     // hlavní "matrix green"
          mid: "#008F11",       // tmavší zelená
          dark: "#003B00",      // nejtmavší zelená (pozadí prvků)
          glow: "#39FF14",      // extra glow variant
          dim: "#0A2F0A",       // nejtmavší bg tile
        },
        // Čitelný režim (readable) — Matrix estetika, ale vyšší kontrast
        readable: {
          bg: "#0A0F0A",
          green: "#A8FFB0",     // mnohem světlejší zelená
          mid: "#5FDD6F",
          dark: "#1E3F20",
          text: "#D0FFD8",
        },
      },
      fontFamily: {
        mono: [
          "JetBrains Mono",
          "Fira Code",
          "Consolas",
          "monospace",
        ],
      },
      boxShadow: {
        "matrix-glow": "0 0 10px rgba(0, 255, 65, 0.5), 0 0 20px rgba(0, 255, 65, 0.25)",
        "matrix-glow-strong": "0 0 15px rgba(0, 255, 65, 0.8), 0 0 30px rgba(0, 255, 65, 0.4)",
        "readable-glow": "0 0 8px rgba(168, 255, 176, 0.35)",
      },
      animation: {
        "pulse-green": "pulseGreen 2s ease-in-out infinite",
        "flicker": "flicker 3s linear infinite",
        "typewriter": "typewriter 2s steps(40) forwards",
      },
      keyframes: {
        pulseGreen: {
          "0%, 100%": { opacity: "1", textShadow: "0 0 10px #00FF41" },
          "50%": { opacity: "0.8", textShadow: "0 0 20px #00FF41" },
        },
        flicker: {
          "0%, 100%": { opacity: "1" },
          "50.5%": { opacity: "1" },
          "50%": { opacity: "0.9" },
        },
        typewriter: {
          from: { width: "0" },
          to: { width: "100%" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
