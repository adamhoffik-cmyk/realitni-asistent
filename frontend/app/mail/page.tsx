"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Edit3,
  Inbox,
  Mail,
  RefreshCw,
  Search,
  Send,
} from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type GmailMessage } from "@/lib/api";

const PRESETS = [
  { label: "📥 Nepřečtené", query: "in:inbox is:unread" },
  { label: "📬 Inbox", query: "in:inbox" },
  { label: "⭐ Hvězdičky", query: "is:starred" },
  { label: "🔔 Posledních 7 dní", query: "newer_than:7d" },
  { label: "📤 Odeslané", query: "in:sent" },
];

export default function MailPage() {
  const [messages, setMessages] = useState<GmailMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("in:inbox is:unread");
  const [customQuery, setCustomQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [composeOpen, setComposeOpen] = useState(false);

  // Compose form
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);

  const load = async (q: string) => {
    setLoading(true);
    setError(null);
    try {
      const msgs = await endpoints.gmail.messages({
        query: q,
        max_results: 30,
        full: true,
      });
      setMessages(msgs);
    } catch (e: any) {
      setError(e?.detail || "Chyba načtení");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(query);
  }, [query]);

  const send = async () => {
    if (!to || !subject || !body) {
      alert("Vyplň To + Subject + Body");
      return;
    }
    setSending(true);
    try {
      await endpoints.gmail.send({ to, subject, body });
      alert("✓ Odesláno");
      setTo("");
      setSubject("");
      setBody("");
      setComposeOpen(false);
    } catch (e: any) {
      alert(e?.detail || "Odeslání selhalo");
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />

      <main className="max-w-6xl mx-auto px-4 py-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-matrix-dim hover:text-matrix mb-4"
        >
          <ArrowLeft size={16} /> Zpět
        </Link>

        <div className="flex items-center justify-between mb-4">
          <h1 className="text-matrix text-2xl tracking-wide flex items-center gap-2">
            <Mail size={22} /> Gmail
          </h1>
          <button
            onClick={() => setComposeOpen(!composeOpen)}
            className="inline-flex items-center gap-2 px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow"
          >
            <Edit3 size={14} /> Nový e-mail
          </button>
        </div>

        {/* Compose panel */}
        {composeOpen && (
          <div className="bg-matrix-tile p-4 rounded mb-4 space-y-2">
            <input
              type="email"
              placeholder="Komu *"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm"
            />
            <input
              type="text"
              placeholder="Předmět *"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm"
            />
            <textarea
              placeholder="Tělo zprávy… (můžeš požádat AI v chatu o vygenerování)"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={8}
              className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm resize-y"
            />
            <div className="flex gap-2">
              <button
                onClick={send}
                disabled={sending || !to || !subject || !body}
                className="inline-flex items-center gap-2 px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow disabled:opacity-30"
              >
                <Send size={14} /> {sending ? "Odesílám…" : "Odeslat"}
              </button>
              <button
                onClick={() => setComposeOpen(false)}
                className="px-3 py-2 border border-matrix-dim text-matrix-dim text-sm rounded"
              >
                Zrušit
              </button>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mb-3">
          {PRESETS.map((p) => (
            <button
              key={p.query}
              onClick={() => setQuery(p.query)}
              className={`px-3 py-1 border text-xs rounded transition ${
                query === p.query
                  ? "border-matrix text-matrix shadow-matrix-glow"
                  : "border-matrix-dim text-matrix-dim hover:border-matrix hover:text-matrix"
              }`}
            >
              {p.label}
            </button>
          ))}
          <div className="flex-1 min-w-[200px] relative">
            <input
              type="text"
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && customQuery.trim() && setQuery(customQuery.trim())
              }
              placeholder='Vlastní Gmail query, např. "from:klient@example.cz"'
              className="w-full bg-transparent border border-matrix rounded px-3 py-1 pl-8 text-matrix placeholder:text-matrix-dim/50 text-xs"
            />
            <Search
              size={12}
              className="absolute left-2.5 top-1/2 -translate-y-1/2 text-matrix-dim"
            />
          </div>
          <button
            onClick={() => load(query)}
            className="text-matrix-dim hover:text-matrix"
            title="Obnovit"
          >
            <RefreshCw size={14} />
          </button>
        </div>

        {error && (
          <div className="bg-matrix-tile p-3 rounded border border-red-500/40 mb-4">
            <p className="text-matrix">⚠ {error}</p>
          </div>
        )}

        {loading && <p className="text-matrix-dim">Načítám…</p>}

        {!loading && messages.length === 0 && !error && (
          <p className="text-matrix-dim italic">Žádné zprávy v tomto filtru.</p>
        )}

        {/* Messages list */}
        <div className="space-y-1">
          {messages.map((m) => (
            <Link
              key={m.id}
              href={`/mail/${m.id}`}
              className={`block bg-matrix-tile p-3 rounded hover:shadow-matrix-glow transition ${
                m.is_unread ? "" : "opacity-70"
              }`}
            >
              <div className="flex items-start gap-3">
                <Inbox
                  size={14}
                  className={m.is_unread ? "text-matrix mt-1" : "text-matrix-dim mt-1"}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`text-sm ${
                        m.is_unread ? "text-matrix font-bold" : "text-matrix-dim"
                      }`}
                    >
                      {m.sender.replace(/<.+>/, "").trim() || m.sender}
                    </span>
                    <span className="text-xs text-matrix-dim">
                      {m.date.slice(0, 25)}
                    </span>
                  </div>
                  <div
                    className={`text-sm truncate ${
                      m.is_unread ? "text-matrix" : "text-matrix-dim"
                    }`}
                  >
                    {m.subject}
                  </div>
                  {m.snippet && (
                    <div className="text-xs text-matrix-dim/80 truncate mt-0.5">
                      {m.snippet}
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="mail"
      />
    </>
  );
}
