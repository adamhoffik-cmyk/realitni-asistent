"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Heart, RefreshCw } from "lucide-react";
import { endpoints, type NewsItem } from "@/lib/api";

export function NewsWidget() {
  const [items, setItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const load = async () => {
    try {
      const result = await endpoints.news.list(10);
      setItems(result);
      setError(null);
    } catch (e: any) {
      setError(e?.detail || "Chyba načtení");
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
    try {
      await endpoints.news.refresh();
      await load();
    } catch (e: any) {
      setError(e?.detail || "Chyba refresh");
    } finally {
      setRefreshing(false);
    }
  };

  const toggleFavorite = async (item: NewsItem) => {
    setTogglingId(item.id);
    // Optimistic update
    setItems((prev) =>
      prev.map((n) =>
        n.id === item.id ? { ...n, is_favorite: !n.is_favorite } : n
      )
    );
    try {
      if (item.is_favorite) {
        await endpoints.favorites.removeByNews(item.id);
      } else {
        await endpoints.favorites.add(item.id);
      }
    } catch (e: any) {
      // Revert
      setItems((prev) =>
        prev.map((n) =>
          n.id === item.id ? { ...n, is_favorite: item.is_favorite } : n
        )
      );
    } finally {
      setTogglingId(null);
    }
  };

  return (
    <div className="bg-matrix-tile p-4 rounded md:col-span-2">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-matrix">📰 Novinky</h3>
        <div className="flex items-center gap-3">
          <Link
            href="/favorites"
            className="text-xs text-matrix-dim hover:text-matrix flex items-center gap-1"
            title="Oblíbené novinky"
          >
            <Heart size={12} /> oblíbené
          </Link>
          <button
            onClick={manualRefresh}
            disabled={refreshing}
            className="text-matrix-dim hover:text-matrix disabled:animate-spin"
            title="Ručně načíst nejnovější"
          >
            <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {loading && <p className="text-matrix-dim text-sm">Načítám…</p>}
      {error && !loading && (
        <p className="text-matrix-dim text-sm">⚠ {error}</p>
      )}

      {!loading && items.length === 0 && !error && (
        <p className="text-matrix-dim text-xs italic">
          Zatím žádné. Klikni na ⟳ nebo počkej na scheduler (každé 2 hod).
        </p>
      )}

      <ul className="space-y-2 max-h-80 overflow-y-auto">
        {items.map((n) => (
          <li
            key={n.id}
            className="text-sm border-l-2 border-matrix-dim/30 pl-2 flex gap-2 items-start"
          >
            <button
              onClick={() => toggleFavorite(n)}
              disabled={togglingId === n.id}
              className={`shrink-0 mt-0.5 transition ${
                n.is_favorite
                  ? "text-red-400"
                  : "text-matrix-dim hover:text-red-400"
              } disabled:opacity-50`}
              title={n.is_favorite ? "Odebrat z oblíbených" : "Přidat k oblíbeným"}
            >
              <Heart
                size={14}
                fill={n.is_favorite ? "currentColor" : "none"}
              />
            </button>
            <div className="flex-1">
              <a
                href={n.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-matrix hover:text-matrix-glow transition"
              >
                {n.title}
              </a>
              <div className="flex items-center gap-2 text-xs text-matrix-dim mt-0.5">
                <span>{n.source}</span>
                {n.published_at && (
                  <>
                    <span>·</span>
                    <span>
                      {new Date(n.published_at).toLocaleDateString("cs-CZ", {
                        day: "numeric",
                        month: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
