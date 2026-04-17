"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, ExternalLink, Mail, RefreshCw } from "lucide-react";
import { endpoints, type GmailMessage } from "@/lib/api";

/** Malý widget: posledních 5 unread e-mailů v inboxu. */
export function GmailWidget() {
  const [authorized, setAuthorized] = useState<boolean | null>(null);
  const [messages, setMessages] = useState<GmailMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const status = await endpoints.calendar.authStatus();
      setAuthorized(status.authorized);
      if (!status.authorized) return;
      const msgs = await endpoints.gmail.messages({
        query: "in:inbox is:unread",
        max_results: 5,
        full: true,
      });
      setMessages(msgs);
      setError(null);
    } catch (e: any) {
      setError(e?.detail || "Chyba");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 5 * 60 * 1000);
    return () => clearInterval(t);
  }, []);

  const manualRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-2 flex items-center gap-2">
          <Mail size={16} /> Gmail
        </h3>
        <p className="text-matrix-dim text-sm">Načítám…</p>
      </div>
    );
  }

  if (authorized === false) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-2 flex items-center gap-2">
          <Mail size={16} /> Gmail
        </h3>
        <p className="text-matrix-dim text-sm">
          Nepřihlášeno. Klikni v Kalendář widgetu na "Připojit Google účet".
        </p>
      </div>
    );
  }

  return (
    <div className="bg-matrix-tile p-4 rounded">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-matrix flex items-center gap-2">
          <Mail size={16} /> Gmail — nepřečtené
        </h3>
        <div className="flex items-center gap-2">
          <Link
            href="/mail"
            className="text-xs text-matrix-dim hover:text-matrix flex items-center gap-1"
          >
            vše <ArrowRight size={12} />
          </Link>
          <button
            onClick={manualRefresh}
            disabled={refreshing}
            className="text-matrix-dim hover:text-matrix"
            title="Načíst znovu"
          >
            <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {error && <p className="text-matrix-dim text-xs">⚠ {error}</p>}

      {!error && messages.length === 0 && (
        <p className="text-matrix-dim text-xs italic">
          Žádné nepřečtené. 💚
        </p>
      )}

      <ul className="space-y-2 max-h-80 overflow-y-auto">
        {messages.map((m) => (
          <li
            key={m.id}
            className="text-sm border-l-2 border-matrix-dim/30 pl-2"
          >
            <Link href={`/mail/${m.id}`} className="block">
              <div className="text-matrix font-medium line-clamp-1">
                {m.subject}
              </div>
              <div className="text-xs text-matrix-dim line-clamp-1">
                {m.sender.replace(/<.+>/, "").trim() || m.sender}
              </div>
              {m.snippet && (
                <div className="text-xs text-matrix-dim/80 line-clamp-1 mt-0.5">
                  {m.snippet}
                </div>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
