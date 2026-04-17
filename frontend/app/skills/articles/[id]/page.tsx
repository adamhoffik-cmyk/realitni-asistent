"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Check, ExternalLink, Eye, Save, Trash2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type Article } from "@/lib/api";

type Mode = "edit" | "preview";

export default function ArticleDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ?? "";
  const router = useRouter();

  const [article, setArticle] = useState<Article | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [mode, setMode] = useState<Mode>("edit");
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string>("idle");
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    if (!id) return;
    endpoints.articles
      .get(id)
      .then((a) => {
        setArticle(a);
        setTitle(a.title);
        setContent(a.content_md);
      })
      .catch(() => setStatus("error"));
  }, [id]);

  const save = async (newStatus?: string) => {
    if (!article) return;
    setSaving(true);
    try {
      const updated = await endpoints.articles.update(article.id, {
        title,
        content_md: content,
        ...(newStatus && { status: newStatus }),
      });
      setArticle(updated);
      setStatus("saved");
      setTimeout(() => setStatus("idle"), 2000);
    } catch (e: any) {
      setStatus("error");
    } finally {
      setSaving(false);
    }
  };

  const publish = () => save("published");
  const unpublish = () => save("draft");

  const remove = async () => {
    if (!confirm("Smazat článek?")) return;
    if (!article) return;
    try {
      await endpoints.articles.delete(article.id);
      router.push("/skills/articles");
    } catch (e: any) {
      alert(e?.detail || "Chyba");
    }
  };

  if (!article && status !== "error") {
    return (
      <>
        <Header onOpenChat={() => setChatOpen(true)} />
        <main className="max-w-5xl mx-auto px-4 py-6">
          <p className="text-matrix-dim">Načítám…</p>
        </main>
      </>
    );
  }

  if (!article) {
    return (
      <>
        <Header onOpenChat={() => setChatOpen(true)} />
        <main className="max-w-5xl mx-auto px-4 py-6">
          <div className="bg-matrix-tile p-6 rounded">
            <h1 className="text-matrix text-xl mb-2">⚠ Článek nenalezen</h1>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />

      <main className="max-w-5xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <Link
            href="/skills/articles"
            className="inline-flex items-center gap-2 text-matrix-dim hover:text-matrix"
          >
            <ArrowLeft size={16} /> Zpět
          </Link>

          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setMode(mode === "edit" ? "preview" : "edit")}
              className="inline-flex items-center gap-1 px-3 py-1 border border-matrix-dim text-matrix-dim text-xs rounded hover:text-matrix hover:border-matrix"
            >
              <Eye size={14} /> {mode === "edit" ? "Náhled" : "Editovat"}
            </button>

            <button
              onClick={() => save()}
              disabled={saving}
              className="inline-flex items-center gap-1 px-3 py-1 border border-matrix text-matrix text-xs rounded hover:shadow-matrix-glow disabled:opacity-30"
            >
              <Save size={14} />
              {saving ? "Ukládám…" : status === "saved" ? "Uloženo ✓" : "Uložit"}
            </button>

            {article.status === "draft" ? (
              <button
                onClick={publish}
                className="inline-flex items-center gap-1 px-3 py-1 border border-green-400 text-green-400 text-xs rounded"
              >
                <Check size={14} /> Publikovat
              </button>
            ) : (
              <button
                onClick={unpublish}
                className="inline-flex items-center gap-1 px-3 py-1 border border-yellow-400 text-yellow-400 text-xs rounded"
              >
                Zpět na draft
              </button>
            )}

            <button
              onClick={remove}
              className="inline-flex items-center gap-1 px-3 py-1 border border-red-400 text-red-400 text-xs rounded"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="bg-matrix-tile p-3 rounded mb-4 text-xs text-matrix-dim flex flex-wrap gap-3">
          <span>
            Status:{" "}
            <span
              className={
                article.status === "published" ? "text-green-400" : "text-matrix"
              }
            >
              {article.status}
            </span>
          </span>
          <span>
            Režim: {article.mode === "B_legalized" ? "B (ze zdroje)" : "A (nové téma)"}
          </span>
          {article.source_url && (
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 hover:text-matrix"
            >
              <ExternalLink size={12} /> zdroj
            </a>
          )}
          <span>
            Upraveno: {new Date(article.updated_at).toLocaleString("cs-CZ")}
          </span>
        </div>

        {/* Title */}
        {mode === "edit" ? (
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-xl font-bold mb-3 focus:outline-none focus:shadow-matrix-glow"
          />
        ) : (
          <h1 className="text-matrix text-2xl font-bold mb-3 tracking-wide">
            {title}
          </h1>
        )}

        {/* Content */}
        {mode === "edit" ? (
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={25}
            className="w-full bg-transparent border border-matrix rounded p-3 text-matrix text-sm font-mono resize-y focus:outline-none focus:shadow-matrix-glow"
            placeholder="# Nadpis\n\nObsah článku v markdownu…"
          />
        ) : (
          <div className="bg-matrix-tile p-6 rounded prose-matrix">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        )}

        <p className="text-xs text-matrix-dim/50 mt-4">
          Tip: v editoru Markdown + GFM (tabulky, checkboxy). Uložit (Ctrl+S)
          není implementováno — klikni Uložit. Export na Drive přijde ve Fázi 3-B.
        </p>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="articles"
      />
    </>
  );
}
