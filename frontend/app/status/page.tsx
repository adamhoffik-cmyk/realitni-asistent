"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Info,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type StatusResponse } from "@/lib/api";

const ICONS = {
  ok: CheckCircle2,
  warning: AlertCircle,
  error: XCircle,
  info: Info,
} as const;

const COLORS = {
  ok: "text-matrix border-matrix",
  warning: "text-yellow-400 border-yellow-400/60",
  error: "text-red-400 border-red-400/60",
  info: "text-matrix-dim border-matrix-dim",
} as const;

export default function StatusPage() {
  const [data, setData] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    setRefreshing(true);
    try {
      setData(await endpoints.status());
      setError(null);
    } catch (e: any) {
      setError(e?.detail || "Backend nedostupný");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 30 * 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />
      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-matrix-dim hover:text-matrix"
          >
            <ArrowLeft size={16} /> Zpět
          </Link>
          <button
            onClick={load}
            disabled={refreshing}
            className="text-matrix-dim hover:text-matrix"
            title="Obnovit"
          >
            <RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />
          </button>
        </div>

        <h1 className="text-matrix text-2xl mb-4 tracking-wide flex items-center gap-2">
          <Activity size={22} /> Stav systému
        </h1>

        {error && (
          <div className="bg-matrix-tile p-4 rounded border border-red-500/60 mb-4">
            <p className="text-red-400">⚠ {error}</p>
          </div>
        )}

        {loading && <p className="text-matrix-dim">Načítám…</p>}

        {data && (
          <>
            {/* Overall */}
            <div
              className={`p-4 rounded mb-4 border-2 ${COLORS[data.overall]}`}
            >
              <div className="flex items-center gap-3">
                {(() => {
                  const Icon = ICONS[data.overall];
                  return <Icon size={28} />;
                })()}
                <div>
                  <div className="text-lg font-bold">
                    {data.overall === "ok" && "Vše v pořádku"}
                    {data.overall === "warning" && "Pozor — některé komponenty mají problém"}
                    {data.overall === "error" && "Kritická chyba"}
                  </div>
                  <div className="text-xs opacity-70">
                    {data.checks.length} komponent zkontrolováno ·{" "}
                    {new Date(data.generated_at).toLocaleString("cs-CZ")}
                  </div>
                </div>
              </div>
            </div>

            {/* Details */}
            <div className="space-y-2">
              {data.checks.map((c) => {
                const Icon = ICONS[c.status];
                const color = COLORS[c.status];
                return (
                  <div
                    key={c.id}
                    className={`bg-matrix-tile p-3 rounded border ${color}`}
                  >
                    <div className="flex items-start gap-3">
                      <Icon size={18} className="shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <div className="font-bold">{c.name}</div>
                        <div className="text-sm opacity-90">{c.message}</div>
                        {c.details && Object.keys(c.details).length > 0 && (
                          <details className="mt-2">
                            <summary className="text-xs text-matrix-dim cursor-pointer hover:text-matrix">
                              detail
                            </summary>
                            <pre className="text-xs text-matrix-dim mt-1 overflow-x-auto">
                              {JSON.stringify(c.details, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <p className="text-xs text-matrix-dim/60 mt-6 text-center">
              Automaticky se obnovuje každých 30 s
            </p>
          </>
        )}
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="status"
      />
    </>
  );
}
