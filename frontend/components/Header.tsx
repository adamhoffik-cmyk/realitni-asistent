"use client";

import { useEffect, useState } from "react";
import { useTheme } from "@/app/providers";
import { Eye, EyeOff, MessageSquare } from "lucide-react";

export function Header({ onOpenChat }: { onOpenChat: () => void }) {
  const { theme, toggle } = useTheme();
  const [now, setNow] = useState<Date>(new Date());

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const timeStr = now.toLocaleTimeString("cs-CZ", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  const dateStr = now.toLocaleDateString("cs-CZ", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-matrix backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={toggle}
          className="text-matrix-dim hover:text-matrix transition p-1"
          aria-label="Přepnout téma"
          title={theme === "matrix" ? "Čitelný režim" : "Matrix režim"}
        >
          {theme === "matrix" ? <Eye size={18} /> : <EyeOff size={18} />}
        </button>
        <h1 className="text-matrix text-lg font-bold tracking-wider animate-flicker">
          REALITNÍ ASISTENT
        </h1>
      </div>

      <div className="hidden sm:flex flex-col items-end text-xs">
        <span className="text-matrix font-mono">{timeStr}</span>
        <span className="text-matrix-dim">{dateStr}</span>
      </div>

      <button
        type="button"
        onClick={onOpenChat}
        className="text-matrix-dim hover:text-matrix transition p-2 border border-matrix rounded glow-on-hover"
        aria-label="Otevřít chat"
        title="Chat (Ctrl+K)"
      >
        <MessageSquare size={18} />
      </button>
    </header>
  );
}
