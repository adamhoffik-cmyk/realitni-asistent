"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, StickyNote } from "lucide-react";
import { endpoints, type Note } from "@/lib/api";

export function RecentNotesWidget() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const result = await endpoints.notes.list({
        types: ["note"],
        limit: 3,
      });
      setNotes(result);
    } catch {
      /* silent */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // Auto-refresh — po uložení Rychlé poznámky ať widget ukáže nový obsah
    const t = setInterval(load, 30 * 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="bg-matrix-tile p-4 rounded">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-matrix flex items-center gap-2">
          <StickyNote size={16} /> Poslední poznámky
        </h3>
        <Link
          href="/memory"
          className="text-xs text-matrix-dim hover:text-matrix flex items-center gap-1"
        >
          vše <ArrowRight size={12} />
        </Link>
      </div>

      {loading && <p className="text-matrix-dim text-xs">Načítám…</p>}

      {!loading && notes.length === 0 && (
        <p className="text-matrix-dim text-xs italic">
          Zatím nic. Zapiš první poznámku přes Rychlou poznámku vlevo.
        </p>
      )}

      <ul className="space-y-2">
        {notes.map((n) => (
          <li
            key={n.id}
            className="text-sm border-l-2 border-matrix-dim/30 pl-2"
          >
            <Link href={`/memory`} className="block hover:text-matrix-glow transition">
              <div className="text-matrix line-clamp-2">
                {n.content.slice(0, 160)}
                {n.content.length > 160 ? "…" : ""}
              </div>
              <div className="text-xs text-matrix-dim mt-1">
                {new Date(n.created_at).toLocaleString("cs-CZ", {
                  day: "numeric",
                  month: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
                {n.tags && n.tags.length > 0 && (
                  <>
                    {" · "}
                    {n.tags.slice(0, 2).join(", ")}
                  </>
                )}
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
