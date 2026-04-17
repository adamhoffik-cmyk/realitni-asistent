"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, ArrowRight, CheckCircle2, AlertCircle, Info, XCircle } from "lucide-react";
import { endpoints, type CheckResult, type StatusResponse } from "@/lib/api";

const ICONS: Record<string, typeof CheckCircle2> = {
  ok: CheckCircle2,
  warning: AlertCircle,
  error: XCircle,
  info: Info,
};

const COLORS: Record<string, string> = {
  ok: "text-matrix",
  warning: "text-yellow-400",
  error: "text-red-400",
  info: "text-matrix-dim",
};

export function StatusWidget() {
  const [data, setData] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      setData(await endpoints.status());
    } catch {
      /* silent — backend down rovnou vidíš jinde */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const t = setInterval(load, 60 * 1000); // refresh 1×/min
    return () => clearInterval(t);
  }, []);

  if (loading) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-2 flex items-center gap-2">
          <Activity size={16} /> Stav systému
        </h3>
        <p className="text-matrix-dim text-sm">Načítám…</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-2 flex items-center gap-2">
          <Activity size={16} /> Stav systému
        </h3>
        <p className="text-matrix-dim text-sm">—</p>
      </div>
    );
  }

  const overallIcon = ICONS[data.overall];
  const overallColor = COLORS[data.overall];
  const problems = data.checks.filter(
    (c) => c.status === "warning" || c.status === "error"
  );

  return (
    <div className="bg-matrix-tile p-4 rounded">
      <div className="flex items-center justify-between mb-3">
        <h3 className={`flex items-center gap-2 ${overallColor}`}>
          <Activity size={16} /> Stav systému
          {(() => {
            const Icon = overallIcon;
            return <Icon size={14} />;
          })()}
        </h3>
        <Link
          href="/status"
          className="text-xs text-matrix-dim hover:text-matrix flex items-center gap-1"
        >
          detail <ArrowRight size={12} />
        </Link>
      </div>

      {problems.length === 0 ? (
        <p className="text-matrix text-sm">✓ Vše v pořádku ({data.checks.length} komponent)</p>
      ) : (
        <div className="space-y-1">
          <p className="text-xs text-matrix-dim mb-1">
            Problémy ({problems.length}):
          </p>
          {problems.map((c) => {
            const Icon = ICONS[c.status];
            const color = COLORS[c.status];
            return (
              <div key={c.id} className="text-sm flex items-start gap-2">
                <Icon size={14} className={`${color} mt-0.5 shrink-0`} />
                <div className="flex-1 min-w-0">
                  <div className={`${color} font-medium`}>{c.name}</div>
                  <div className="text-xs text-matrix-dim">{c.message}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <p className="text-xs text-matrix-dim/60 mt-2">
        {new Date(data.generated_at).toLocaleTimeString("cs-CZ", {
          hour: "2-digit",
          minute: "2-digit",
        })}
        {" · "}
        {data.checks.length} checků
      </p>
    </div>
  );
}
