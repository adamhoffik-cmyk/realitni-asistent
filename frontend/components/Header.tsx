"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MessageSquare } from "lucide-react";

export function Header({ onOpenChat }: { onOpenChat: () => void }) {
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
      <Link
        href="/"
        className="text-matrix text-lg font-bold tracking-wider animate-flicker hover:text-matrix-glow transition no-underline"
        title="Domů"
      >
        REALITNÍ ASISTENT
      </Link>

      <div className="hidden sm:flex flex-col items-end">
        <span className="text-matrix font-mono text-2xl lg:text-3xl font-bold tracking-wider">
          {timeStr}
        </span>
        <span className="text-matrix-dim text-sm lg:text-base">{dateStr}</span>
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
