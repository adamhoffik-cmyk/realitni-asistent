"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Plus, Target, Trash2 } from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { api } from "@/lib/api";

interface Activity {
  id: string;
  date: string;
  activity_type: string;
  count: number;
  notes: string | null;
  outcome: string | null;
  created_at: string;
}

interface Stats {
  days: number;
  by_type: Record<string, number>;
  targets_weekly: Record<string, number>;
}

const TYPE_LABELS: Record<string, string> = {
  dopis: "📮 Dopisy majitelům",
  cold_call: "📞 Cold cally",
  setkani: "🤝 Osobní setkání",
  schuzka: "📅 Schůzky",
  sfera_vlivu: "💬 Kontakt sféra vlivu",
  jiny: "▢ Jiné",
};

export default function NaborPage() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);

  // Quick log form
  const [type, setType] = useState("dopis");
  const [count, setCount] = useState(1);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [acts, st] = await Promise.all([
        api.get<Activity[]>("/nabor/activities?limit=50"),
        api.get<Stats>("/nabor/stats?days=7"),
      ]);
      setActivities(acts);
      setStats(st);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const log = async () => {
    if (!count || saving) return;
    setSaving(true);
    try {
      const today = new Date().toISOString().slice(0, 10);
      await api.post<Activity>("/nabor/activities", {
        date: today,
        activity_type: type,
        count,
        notes: notes || null,
      });
      setCount(1);
      setNotes("");
      await load();
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Smazat záznam?")) return;
    await api.delete(`/nabor/activities/${id}`);
    setActivities((prev) => prev.filter((a) => a.id !== id));
  };

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />

      <main className="max-w-5xl mx-auto px-4 py-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-matrix-dim hover:text-matrix mb-4"
        >
          <ArrowLeft size={16} /> Zpět
        </Link>

        <h1 className="text-matrix text-2xl mb-4 tracking-wide flex items-center gap-2">
          <Target size={22} /> Nábor — tracker aktivit
        </h1>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            {Object.entries(TYPE_LABELS).map(([key, label]) => {
              const done = stats.by_type[key] || 0;
              const target = stats.targets_weekly[key] || 0;
              return (
                <div key={key} className="bg-matrix-tile p-3 rounded">
                  <div className="text-xs text-matrix-dim truncate">{label}</div>
                  <div className="text-2xl text-matrix font-bold">{done}</div>
                  {target > 0 && (
                    <div className="text-xs text-matrix-dim">
                      za 7 dní · cíl {target}/týden
                      <div className="w-full bg-matrix-dark rounded-full h-1 mt-1">
                        <div
                          className="bg-matrix-green h-1 rounded-full"
                          style={{ width: `${Math.min(100, (done / target) * 100)}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Quick log */}
        <div className="bg-matrix-tile p-4 rounded mb-6">
          <h2 className="text-matrix mb-3">+ Zaznamenat aktivitu</h2>
          <div className="grid gap-2 md:grid-cols-4">
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="bg-matrix-bg border border-matrix rounded px-2 py-2 text-matrix text-sm"
            >
              {Object.entries(TYPE_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
            <input
              type="number"
              value={count}
              min={1}
              onChange={(e) => setCount(parseInt(e.target.value || "1"))}
              className="bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm"
              placeholder="Počet"
            />
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Poznámka (volitelné)"
              className="bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm md:col-span-1"
            />
            <button
              onClick={log}
              disabled={saving}
              className="inline-flex items-center justify-center gap-1 px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow disabled:opacity-30"
            >
              <Plus size={14} /> Přidat
            </button>
          </div>
        </div>

        {/* Recent log */}
        <h2 className="text-matrix text-lg mb-3 tracking-wider">
          ▢ Poslední záznamy
        </h2>
        {loading && <p className="text-matrix-dim">Načítám…</p>}
        {!loading && activities.length === 0 && (
          <p className="text-matrix-dim italic">
            Zatím nic. Začni třeba "10 dopisů" dnes.
          </p>
        )}

        <div className="space-y-1">
          {activities.map((a) => (
            <div
              key={a.id}
              className="bg-matrix-tile p-2 rounded flex items-center gap-3 text-sm"
            >
              <span className="text-matrix-dim text-xs w-20">{a.date}</span>
              <span className="flex-1">
                <span className="text-matrix">
                  {TYPE_LABELS[a.activity_type] || a.activity_type}
                </span>
                {" · "}
                <span className="text-matrix">×{a.count}</span>
                {a.notes && (
                  <span className="text-matrix-dim"> — {a.notes}</span>
                )}
              </span>
              <button
                onClick={() => remove(a.id)}
                className="text-matrix-dim hover:text-red-400"
              >
                <Trash2 size={12} />
              </button>
            </div>
          ))}
        </div>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="nabor"
      />
    </>
  );
}
