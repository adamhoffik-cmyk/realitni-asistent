"use client";

import { useEffect, useRef, useState } from "react";
import { RotateCcw, Send, X } from "lucide-react";
import { api } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

// Persistence — session ID per context (home, articles, nabor, …) aby se
// kontexty mezi sebou nemíchaly. Klíč: "chat_session:<context>".
const STORAGE_KEY = (ctx: string) => `chat_session:${ctx}`;

// Kolik posledních turnů z DB načíst při obnově (pro zobrazení).
// Backend sliding window Claude SDK je separátní — zůstává 20.
const DISPLAY_LOAD_LIMIT = 40;

interface BackendTurn {
  id: string;
  session_id: string;
  role: string;
  content: string;
  created_at: string;
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
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const stickToBottomRef = useRef<boolean>(true);

  // Load stored session + history při prvním otevření (nebo po context change).
  useEffect(() => {
    if (!open) return;
    let cancelled = false;

    const restore = async () => {
      try {
        // Cross-device sync: server rozhodne co je "aktivní session" pro
        // tento kontext (na základě posledních 24h activity).
        const current = await api.get<{ id: string | null }>(
          `/chat/sessions/current?context=${encodeURIComponent(context)}`
        );
        if (cancelled) return;

        if (!current.id) {
          // Žádná aktivní session — uklidíme UI a localStorage
          setSessionId(null);
          setMessages([]);
          try {
            localStorage.removeItem(STORAGE_KEY(context));
          } catch {
            /* ignore */
          }
          return;
        }

        const turns = await api.get<BackendTurn[]>(
          `/chat/sessions/${current.id}/turns`
        );
        if (cancelled) return;

        setSessionId(current.id);
        const recent = (turns || []).slice(-DISPLAY_LOAD_LIMIT);
        setMessages(
          recent
            .filter((t) => t.role === "user" || t.role === "assistant")
            .map((t) => ({
              id: t.id,
              role: t.role as "user" | "assistant",
              content: t.content,
            }))
        );

        try {
          localStorage.setItem(STORAGE_KEY(context), current.id);
        } catch {
          /* ignore */
        }
      } catch (e) {
        // Backend nedostupný → offline fallback na localStorage cache
        const storedId = localStorage.getItem(STORAGE_KEY(context));
        if (!storedId) return;
        try {
          const turns = await api.get<BackendTurn[]>(
            `/chat/sessions/${storedId}/turns`
          );
          if (cancelled) return;
          if (turns && turns.length > 0) {
            setSessionId(storedId);
            setMessages(
              turns
                .slice(-DISPLAY_LOAD_LIMIT)
                .filter((t) => t.role === "user" || t.role === "assistant")
                .map((t) => ({
                  id: t.id,
                  role: t.role as "user" | "assistant",
                  content: t.content,
                }))
            );
          }
        } catch {
          /* ignore */
        }
      }
    };

    restore();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, context]);

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
          // Persist session id per context
          try {
            localStorage.setItem(STORAGE_KEY(context), msg.data.id);
          } catch {
            /* ignore */
          }
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

  // Auto-scroll JEN pokud je uživatel u spodního kraje (do 60 px).
  // Když se uživatel posune nahoru, přestaneme za něj rolovat —
  // jakmile ručně scrolluje k dolní části, zase zapneme.
  useEffect(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const onScroll = () => {
      const nearBottom =
        el.scrollHeight - el.scrollTop - el.clientHeight < 60;
      stickToBottomRef.current = nearBottom;
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (stickToBottomRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
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
            {messages.length > 0 && (
              <span className="ml-2">· {messages.length} zpráv</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <button
              onClick={() => {
                if (!confirm("Začít novou konverzaci? Historie se zachová v paměti.")) return;
                localStorage.removeItem(STORAGE_KEY(context));
                setSessionId(null);
                setMessages([]);
                setTimeout(() => inputRef.current?.focus(), 50);
              }}
              className="text-matrix-dim hover:text-matrix p-1"
              title="Nový chat (aktuální konverzace zůstane uložená na serveru)"
            >
              <RotateCcw size={16} />
            </button>
          )}
          <button
            onClick={onClose}
            className="text-matrix-dim hover:text-matrix p-1"
            aria-label="Zavřít chat"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-3 space-y-3"
        style={{ overscrollBehavior: "contain" }}
      >
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
