"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Reply, Send, Sparkles } from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type GmailMessage } from "@/lib/api";

export default function MailDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ?? "";

  const [msg, setMsg] = useState<GmailMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);

  // Reply state
  const [replyOpen, setReplyOpen] = useState(false);
  const [replyBody, setReplyBody] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (!id) return;
    endpoints.gmail
      .get(id)
      .then((m) => {
        setMsg(m);
        // auto mark as read
        if (m.is_unread) {
          endpoints.gmail.markRead(id).catch(() => {});
        }
      })
      .catch((e: any) => setError(e?.detail || "Zprávu se nepodařilo načíst"));
  }, [id]);

  const extractEmail = (s: string): string => {
    const m = s.match(/<([^>]+)>/);
    return m ? m[1] : s.trim();
  };

  const sendReply = async () => {
    if (!msg || !replyBody.trim()) return;
    setSending(true);
    try {
      await endpoints.gmail.send({
        to: extractEmail(msg.sender),
        subject: msg.subject.startsWith("Re:")
          ? msg.subject
          : `Re: ${msg.subject}`,
        body: replyBody,
        thread_id: msg.thread_id || undefined,
      });
      alert("✓ Odpověď odeslána");
      setReplyBody("");
      setReplyOpen(false);
    } catch (e: any) {
      alert(e?.detail || "Odeslání selhalo");
    } finally {
      setSending(false);
    }
  };

  if (error) {
    return (
      <>
        <Header onOpenChat={() => setChatOpen(true)} />
        <main className="max-w-4xl mx-auto px-4 py-6">
          <p className="text-matrix">⚠ {error}</p>
          <Link href="/mail" className="text-matrix-dim hover:text-matrix mt-4 inline-block">
            ← Zpět do Gmail
          </Link>
        </main>
      </>
    );
  }

  if (!msg) {
    return (
      <>
        <Header onOpenChat={() => setChatOpen(true)} />
        <main className="max-w-4xl mx-auto px-4 py-6">
          <p className="text-matrix-dim">Načítám…</p>
        </main>
      </>
    );
  }

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />

      <main className="max-w-4xl mx-auto px-4 py-6">
        <Link
          href="/mail"
          className="inline-flex items-center gap-2 text-matrix-dim hover:text-matrix mb-4"
        >
          <ArrowLeft size={16} /> Zpět
        </Link>

        <div className="bg-matrix-tile p-5 rounded">
          <h1 className="text-matrix text-xl font-bold mb-3">{msg.subject}</h1>

          <div className="text-xs text-matrix-dim space-y-1 mb-4 border-b border-matrix-dim/30 pb-3">
            <div>
              <span className="opacity-70">Od:</span> {msg.sender}
            </div>
            <div>
              <span className="opacity-70">Komu:</span> {msg.to}
            </div>
            <div>
              <span className="opacity-70">Datum:</span> {msg.date}
            </div>
          </div>

          <pre className="text-matrix text-sm whitespace-pre-wrap font-mono leading-relaxed max-h-[500px] overflow-y-auto">
            {msg.body || msg.snippet}
          </pre>
        </div>

        {/* Reply */}
        <div className="mt-4">
          <button
            onClick={() => setReplyOpen(!replyOpen)}
            className="inline-flex items-center gap-2 px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow"
          >
            <Reply size={14} /> {replyOpen ? "Zavřít odpověď" : "Odpovědět"}
          </button>

          {replyOpen && (
            <div className="bg-matrix-tile p-4 rounded mt-3 space-y-2">
              <div className="text-xs text-matrix-dim">
                Komu: {extractEmail(msg.sender)} · Předmět:{" "}
                {msg.subject.startsWith("Re:") ? msg.subject : `Re: ${msg.subject}`}
              </div>
              <textarea
                placeholder="Tělo odpovědi… Pro AI návrh otevři chat (ikona vpravo nahoře) a napiš 'Navrhni odpověď'."
                value={replyBody}
                onChange={(e) => setReplyBody(e.target.value)}
                rows={8}
                className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm resize-y"
              />
              <div className="flex gap-2">
                <button
                  onClick={sendReply}
                  disabled={sending || !replyBody.trim()}
                  className="inline-flex items-center gap-2 px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow disabled:opacity-30"
                >
                  <Send size={14} /> {sending ? "Odesílám…" : "Odeslat"}
                </button>
              </div>
            </div>
          )}
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
