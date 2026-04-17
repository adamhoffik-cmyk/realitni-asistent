"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ExternalLink,
  FileText,
  Heart,
  PenLine,
  Trash2,
} from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type FavoriteNews } from "@/lib/api";

export default function FavoritesPage() {
  const [items, setItems] = useState<FavoriteNews[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [noteDraft, setNoteDraft] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const result = await endpoints.favorites.list();
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
  }, []);

  const remove = async (fav: FavoriteNews) => {
    if (!confirm("Odebrat z oblíbených?")) return;
    try {
      await endpoints.favorites.removeByNews(fav.news_item_id);
      setItems((prev) => prev.filter((f) => f.id !== fav.id));
    } catch (e: any) {
      alert(e?.detail || "Chyba");
    }
  };

  const saveNote = async (fav: FavoriteNews) => {
    try {
      const updated = await endpoints.favorites.updateNote(fav.id, noteDraft);
      setItems((prev) => prev.map((f) => (f.id === fav.id ? updated : f)));
      setEditingNoteId(null);
    } catch (e: any) {
      alert(e?.detail || "Chyba uložení");
    }
  };

  const generateArticle = (fav: FavoriteNews) => {
    // Navigace na Skill Články se source URL přednastaveným
    if (!fav.news?.url) return;
    const url = encodeURIComponent(fav.news.url);
    window.location.href = `/skills/articles?source=${url}&favorite_id=${fav.id}`;
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
          <Heart className="text-red-400" size={22} /> Oblíbené novinky
        </h1>

        <p className="text-matrix-dim text-sm mb-4">
          Z těchto zdrojů můžeš jedním klikem vygenerovat vlastní článek přes
          Skill "Články".
        </p>

        {error && (
          <div className="bg-matrix-tile p-3 rounded border border-red-500/40 mb-4">
            <p className="text-matrix">⚠ {error}</p>
          </div>
        )}

        {loading && <p className="text-matrix-dim">Načítám…</p>}

        {!loading && items.length === 0 && (
          <p className="text-matrix-dim italic">
            Žádné oblíbené. Klikni na ♥ u novinky na home screen.
          </p>
        )}

        <div className="space-y-3">
          {items.map((fav) => (
            <div key={fav.id} className="bg-matrix-tile p-4 rounded">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex-1">
                  <h3 className="text-matrix font-bold">
                    {fav.news?.title || "(novinka smazána)"}
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-matrix-dim mt-1">
                    <span>{fav.news?.source}</span>
                    {fav.news?.published_at && (
                      <>
                        <span>·</span>
                        <span>
                          {new Date(fav.news.published_at).toLocaleString(
                            "cs-CZ",
                            {
                              day: "numeric",
                              month: "numeric",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            }
                          )}
                        </span>
                      </>
                    )}
                    <span>·</span>
                    <span>
                      přidáno{" "}
                      {new Date(fav.created_at).toLocaleDateString("cs-CZ")}
                    </span>
                  </div>
                </div>
                <div className="flex gap-1 shrink-0">
                  {fav.news?.url && (
                    <a
                      href={fav.news.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-matrix-dim hover:text-matrix p-1"
                      title="Otevřít zdroj"
                    >
                      <ExternalLink size={16} />
                    </a>
                  )}
                  <button
                    onClick={() => remove(fav)}
                    className="text-matrix-dim hover:text-red-400 p-1"
                    title="Odebrat"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {fav.news?.summary && (
                <p className="text-matrix-dim text-sm mt-2 mb-2 line-clamp-3">
                  {fav.news.summary.replace(/<[^>]*>/g, "")}
                </p>
              )}

              {/* Note */}
              <div className="mt-2">
                {editingNoteId === fav.id ? (
                  <div className="flex gap-2 items-end">
                    <textarea
                      value={noteDraft}
                      onChange={(e) => setNoteDraft(e.target.value)}
                      rows={2}
                      autoFocus
                      className="flex-1 bg-transparent border border-matrix rounded p-2 text-matrix text-xs resize-none focus:outline-none focus:shadow-matrix-glow"
                      placeholder="Tvoje poznámka k této novince…"
                    />
                    <div className="flex flex-col gap-1">
                      <button
                        onClick={() => saveNote(fav)}
                        className="px-2 py-1 border border-matrix text-matrix text-xs rounded hover:shadow-matrix-glow"
                      >
                        OK
                      </button>
                      <button
                        onClick={() => setEditingNoteId(null)}
                        className="px-2 py-1 border border-matrix-dim text-matrix-dim text-xs rounded"
                      >
                        Zrušit
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setEditingNoteId(fav.id);
                      setNoteDraft(fav.note || "");
                    }}
                    className="text-xs text-matrix-dim hover:text-matrix flex items-center gap-1"
                  >
                    <PenLine size={12} />
                    {fav.note ? (
                      <span className="italic">{fav.note}</span>
                    ) : (
                      <span>Přidat poznámku</span>
                    )}
                  </button>
                )}
              </div>

              {/* CTA: Generate article */}
              <div className="mt-3 pt-3 border-t border-matrix-dim/30 flex gap-2">
                {fav.article_id ? (
                  <Link
                    href={`/skills/articles/${fav.article_id}`}
                    className="inline-flex items-center gap-2 px-3 py-1 border border-matrix text-matrix text-xs rounded hover:shadow-matrix-glow"
                  >
                    <FileText size={14} /> Otevřít článek
                  </Link>
                ) : (
                  <button
                    onClick={() => generateArticle(fav)}
                    className="inline-flex items-center gap-2 px-3 py-1 border border-matrix text-matrix text-xs rounded hover:shadow-matrix-glow"
                  >
                    <PenLine size={14} /> ✍ Přetvořit na článek
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="favorites"
      />
    </>
  );
}
