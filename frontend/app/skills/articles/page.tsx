"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  FileText,
  Loader2,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type Article } from "@/lib/api";

function ArticlesClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const prefilledSource = searchParams.get("source") || "";
  const favoriteId = searchParams.get("favorite_id") || undefined;

  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [sourceUrl, setSourceUrl] = useState(prefilledSource);
  const [topic, setTopic] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const result = await endpoints.articles.list();
      setArticles(result);
    } catch (e: any) {
      setError(e?.detail || "Chyba načtení");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  // Pokud přišla URL přes ?source= (z oblíbených), auto-trigger generate
  useEffect(() => {
    if (prefilledSource && !generating && articles.length >= 0) {
      // volitelně auto-generate — pro teď necháme uživatele kliknout
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prefilledSource]);

  const generate = async () => {
    if (!sourceUrl && !topic) return;
    setGenerating(true);
    setError(null);
    try {
      const article = await endpoints.articles.generate({
        source_url: sourceUrl || undefined,
        topic: topic || undefined,
        favorite_id: favoriteId,
      });
      router.push(`/skills/articles/${article.id}`);
    } catch (e: any) {
      setError(e?.detail || "Chyba generování");
      setGenerating(false);
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Smazat článek?")) return;
    try {
      await endpoints.articles.delete(id);
      setArticles((prev) => prev.filter((a) => a.id !== id));
    } catch (e: any) {
      alert(e?.detail || "Chyba");
    }
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
          <FileText size={22} /> Články
        </h1>

        {/* Generator panel */}
        <div className="bg-matrix-tile p-4 rounded mb-6">
          <h2 className="text-matrix mb-3 flex items-center gap-2">
            <Sparkles size={16} /> Generovat nový článek
          </h2>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-matrix-dim block mb-1">
                Režim B — Legalizace ze zdroje (URL)
              </label>
              <input
                type="url"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                placeholder="https://cizí-blog.cz/článek"
                className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm focus:outline-none focus:shadow-matrix-glow"
                disabled={generating}
              />
            </div>

            <div className="text-center text-xs text-matrix-dim">NEBO</div>

            <div>
              <label className="text-xs text-matrix-dim block mb-1">
                Režim A — Nové téma
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Např. 5 nejčastějších chyb při koupi nemovitosti"
                className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm focus:outline-none focus:shadow-matrix-glow"
                disabled={generating}
              />
            </div>

            <button
              onClick={generate}
              disabled={generating || (!sourceUrl && !topic)}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2 border border-matrix text-matrix rounded hover:shadow-matrix-glow transition disabled:opacity-30"
            >
              {generating ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Generuji
                  (~30–60 s)…
                </>
              ) : (
                <>
                  <Plus size={16} /> Vygenerovat draft
                </>
              )}
            </button>

            {error && (
              <p className="text-red-400 text-xs">⚠ {error}</p>
            )}
          </div>
        </div>

        {/* Seznam článků */}
        <h2 className="text-matrix text-lg mb-3 tracking-wider">
          ▢ Drafty a publikované
        </h2>

        {loading && <p className="text-matrix-dim">Načítám…</p>}
        {!loading && articles.length === 0 && (
          <p className="text-matrix-dim italic">
            Žádné články. Vygeneruj první výše, nebo přes srdíčko v
            Novinkách.
          </p>
        )}

        <div className="space-y-2">
          {articles.map((a) => (
            <Link
              key={a.id}
              href={`/skills/articles/${a.id}`}
              className="block bg-matrix-tile p-4 rounded hover:shadow-matrix-glow transition group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="text-matrix font-bold group-hover:text-matrix-glow">
                    {a.title}
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-matrix-dim mt-1">
                    <span
                      className={`px-2 py-0.5 border rounded ${
                        a.status === "published"
                          ? "border-green-400 text-green-400"
                          : "border-matrix-dim"
                      }`}
                    >
                      {a.status === "published" ? "publikováno" : "draft"}
                    </span>
                    <span>
                      {a.mode === "B_legalized" ? "Režim B (zdroj)" : "Režim A (téma)"}
                    </span>
                    <span>·</span>
                    <span>
                      {new Date(a.updated_at).toLocaleString("cs-CZ", {
                        day: "numeric",
                        month: "numeric",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    {a.source_url && (
                      <>
                        <span>·</span>
                        <span className="truncate max-w-[200px]">
                          {new URL(a.source_url).hostname}
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    remove(a.id);
                  }}
                  className="text-matrix-dim hover:text-red-400 p-1"
                  title="Smazat"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </Link>
          ))}
        </div>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="articles"
      />
    </>
  );
}

export default function ArticlesPage() {
  return (
    <Suspense fallback={<div className="p-8 text-matrix-dim">Načítám…</div>}>
      <ArticlesClient />
    </Suspense>
  );
}
