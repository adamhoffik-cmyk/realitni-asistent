"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Search, Trash2 } from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type Note, type MemorySearchHit } from "@/lib/api";

type Mode = "list" | "search";

const TYPE_LABELS: Record<string, string> = {
  note: "Poznámka",
  fact: "Fakt",
  context: "Kontext",
  article: "Článek",
  transcript: "Transkript",
  person: "Osoba",
  property: "Nemovitost",
};

const TYPE_ICONS: Record<string, string> = {
  note: "✎",
  fact: "ⓘ",
  context: "📚",
  article: "📄",
  transcript: "🎥",
  person: "👤",
  property: "🏠",
};

export default function MemoryPage() {
  const [mode, setMode] = useState<Mode>("list");
  const [notes, setNotes] = useState<Note[]>([]);
  const [hits, setHits] = useState<MemorySearchHit[]>([]);
  const [query, setQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);

  const loadList = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await endpoints.notes.list({
        types: filterType ? [filterType] : undefined,
        limit: 100,
      });
      setNotes(result);
    } catch (e: any) {
      setError(e?.detail || "Chyba načtení");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mode === "list") loadList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, filterType]);

  const doSearch = async () => {
    if (!query.trim()) return;
    setMode("search");
    setLoading(true);
    setError(null);
    try {
      const result = await endpoints.notes.search(
        query.trim(),
        filterType ? [filterType] : undefined,
        20
      );
      setHits(result);
    } catch (e: any) {
      setError(e?.detail || "Chyba hledání");
    } finally {
      setLoading(false);
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Opravdu smazat poznámku?")) return;
    try {
      await endpoints.notes.delete(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
      setHits((prev) => prev.filter((h) => h.note.id !== id));
    } catch (e: any) {
      alert(e?.detail || "Chyba smazání");
    }
  };

  const displayed =
    mode === "search"
      ? hits.map((h) => ({ note: h.note, score: h.score }))
      : notes.map((n) => ({ note: n, score: null }));

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

        <h1 className="text-matrix text-2xl mb-4 tracking-wide">
          📚 Paměť
        </h1>

        {/* Ovládání */}
        <div className="bg-matrix-tile p-4 rounded mb-4 space-y-3">
          <div className="flex gap-2 flex-wrap">
            <div className="flex-1 min-w-[200px] relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && doSearch()}
                placeholder="Sémantické hledání… (Enter)"
                className="w-full bg-transparent border border-matrix rounded px-3 py-2 pl-9 text-matrix placeholder:text-matrix-dim/50 text-sm focus:outline-none focus:shadow-matrix-glow"
              />
              <Search
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-matrix-dim"
              />
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-matrix-bg border border-matrix rounded px-3 py-2 text-matrix text-sm"
            >
              <option value="">Všechny typy</option>
              {Object.entries(TYPE_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
            <button
              onClick={doSearch}
              disabled={!query.trim()}
              className="px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow transition disabled:opacity-30"
            >
              Hledat
            </button>
            {mode === "search" && (
              <button
                onClick={() => {
                  setMode("list");
                  setQuery("");
                }}
                className="px-3 py-2 border border-matrix-dim text-matrix-dim text-sm rounded hover:text-matrix"
              >
                Zpět na seznam
              </button>
            )}
          </div>

          <p className="text-xs text-matrix-dim">
            {mode === "list"
              ? `${notes.length} záznam${notes.length === 1 ? "" : notes.length < 5 ? "y" : "ů"}`
              : `${hits.length} výsledků pro "${query}"`}
          </p>
        </div>

        {error && (
          <div className="bg-matrix-tile p-3 rounded border border-red-500/40 mb-4">
            <p className="text-matrix">⚠ {error}</p>
          </div>
        )}

        {loading && <p className="text-matrix-dim">Načítám…</p>}

        {!loading && displayed.length === 0 && (
          <p className="text-matrix-dim italic">
            {mode === "search"
              ? "Nic jsem nenašel."
              : "Zatím žádné poznámky — zadej něco přes Rychlou poznámku na home screen."}
          </p>
        )}

        <div className="space-y-3">
          {displayed.map(({ note, score }) => (
            <div key={note.id} className="bg-matrix-tile p-4 rounded">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {TYPE_ICONS[note.type] || "▢"}
                  </span>
                  <span className="text-matrix-dim text-xs uppercase tracking-wider">
                    {TYPE_LABELS[note.type] || note.type}
                  </span>
                  {note.sensitivity === "client_pii" && (
                    <span className="text-xs text-yellow-400">🔒 PII</span>
                  )}
                  {score !== null && (
                    <span className="text-xs text-matrix-dim">
                      relevance {(score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <button
                  onClick={() => remove(note.id)}
                  className="text-matrix-dim hover:text-red-400 transition"
                  title="Smazat"
                >
                  <Trash2 size={14} />
                </button>
              </div>
              {note.title && (
                <h3 className="text-matrix font-bold mb-1">{note.title}</h3>
              )}
              <p className="text-matrix-dim text-sm whitespace-pre-wrap">
                {note.content}
              </p>
              {note.tags && note.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {note.tags.map((t) => (
                    <span
                      key={t}
                      className="text-xs px-2 py-0.5 border border-matrix-dim text-matrix-dim rounded"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
              <p className="text-xs text-matrix-dim/60 mt-2">
                {new Date(note.updated_at).toLocaleString("cs-CZ")}
                {note.source && ` · zdroj: ${note.source}`}
              </p>
            </div>
          ))}
        </div>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="memory"
      />
    </>
  );
}
