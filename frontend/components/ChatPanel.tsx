"use client";

import { useEffect, useRef, useState } from "react";
import { Send, X } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function ChatPanel({
  open,
  onClose,
  context = "home",
}: {
  open: boolean;
  onClose: () => void;
  context?: string;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Autofocus při otevření + po odeslání zprávy
  useEffect(() => {
    if (open) {
      const t = setTimeout(() => inputRef.current?.focus(), 50);
      return () => clearTimeout(t);
    }
  }, [open]);

  useEffect(() => {
    if (!streaming && open) {
      inputRef.current?.focus();
    }
  }, [streaming, open]);

  useEffect(() => {
    if (!open) return;
    const wsBase =
      process.env.NEXT_PUBLIC_WS_BASE_URL ||
      (typeof window !== "undefined"
        ? window.location.origin.replace(/^http/, "ws")
        : "ws://localhost:8000");
    const ws = new WebSocket(`${wsBase}/api/chat/ws`);
    wsRef.current = ws;

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "session") {
          setSessionId(msg.data.id);
        } else if (msg.type === "token") {
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.role === "assistant") {
              return [
                ...prev.slice(0, -1),
                { ...last, content: last.content + msg.data },
              ];
            }
            return [
              ...prev,
              { id: crypto.randomUUID(), role: "assistant", content: msg.data },
            ];
          });
        } else if (msg.type === "done") {
          setStreaming(false);
        } else if (msg.type === "error") {
          setMessages((p) => [
            ...p,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: `⚠ ${msg.data}`,
            },
          ]);
          setStreaming(false);
        }
      } catch (e) {
        console.error("WS parse error", e);
      }
    };

    ws.onclose = () => {
      wsRef.current = null;
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [open]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = () => {
    if (!input.trim() || !wsRef.current || streaming) return;
    const msg = input.trim();
    setMessages((p) => [
      ...p,
      { id: crypto.randomUUID(), role: "user", content: msg },
    ]);
    setStreaming(true);
    wsRef.current.send(
      JSON.stringify({
        message: msg,
        session_id: sessionId,
        context,
      })
    );
    setInput("");
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 sm:inset-auto sm:bottom-4 sm:right-4 sm:w-[420px] sm:h-[600px] bg-matrix-bg border border-matrix rounded z-50 flex flex-col shadow-matrix-glow-strong">
      <div className="flex items-center justify-between px-4 py-3 border-b border-matrix">
        <div>
          <h2 className="text-matrix font-bold">● Chat</h2>
          <p className="text-xs text-matrix-dim">
            🟢 Režim: {context === "home" ? "obecný" : context}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-matrix-dim hover:text-matrix"
          aria-label="Zavřít chat"
        >
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 && (
          <p className="text-matrix-dim text-xs italic text-center mt-8">
            Napiš cokoliv a AI odpoví.<br />
            (Backend je ve Fázi 1 STUB — odpoví echo. Reálná AI přijde brzy.)
          </p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`text-sm ${
              m.role === "user" ? "text-matrix" : "text-matrix-dim"
            }`}
          >
            <span className="text-xs text-matrix-dim">
              {m.role === "user" ? "▸ ty" : "◂ asistent"}
            </span>
            <div className="prose-matrix whitespace-pre-wrap">{m.content}</div>
          </div>
        ))}
        {streaming && (
          <div className="text-xs text-matrix-dim cursor-blink">◂</div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-matrix p-3">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            autoFocus
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Napiš zprávu… (Enter = odeslat, Shift+Enter = nový řádek)"
            rows={2}
            className="flex-1 bg-transparent border border-matrix rounded p-2 text-matrix placeholder:text-matrix-dim/50 text-sm resize-none focus:outline-none focus:shadow-matrix-glow"
            disabled={streaming}
          />
          <button
            type="button"
            onClick={send}
            disabled={!input.trim() || streaming}
            className="shrink-0 px-3 py-3 border border-matrix text-matrix rounded hover:shadow-matrix-glow transition disabled:opacity-30 disabled:cursor-not-allowed"
            aria-label="Odeslat"
            title="Odeslat (Enter)"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
