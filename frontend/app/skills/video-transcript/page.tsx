"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ExternalLink,
  Film,
  Loader2,
  Plus,
  Trash2,
} from "lucide-react";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type VideoScript } from "@/lib/api";

export default function VideosPage() {
  const [videos, setVideos] = useState<VideoScript[]>([]);
  const [loading, setLoading] = useState(true);
  const [url, setUrl] = useState("");
  const [transcribing, setTranscribing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setVideos(await endpoints.videos.list());
    } catch (e: any) {
      setError(e?.detail || "Chyba načtení");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const transcribe = async () => {
    if (!url.trim()) return;
    setTranscribing(true);
    setError(null);
    try {
      const video = await endpoints.videos.transcribe(url.trim());
      setUrl("");
      await load();
      window.location.href = `/skills/video-transcript/${video.id}`;
    } catch (e: any) {
      setError(e?.detail || "Chyba transkripce");
    } finally {
      setTranscribing(false);
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Smazat transkript + scénář?")) return;
    try {
      await endpoints.videos.delete(id);
      setVideos((prev) => prev.filter((v) => v.id !== id));
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
          <Film size={22} /> Video → Scénář
        </h1>

        {/* Transcribe panel */}
        <div className="bg-matrix-tile p-4 rounded mb-6">
          <h2 className="text-matrix mb-3">Transkribovat cizí video</h2>

          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="URL (Instagram Reel, Facebook, TikTok, YouTube, X)"
            className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm focus:outline-none focus:shadow-matrix-glow mb-2"
            disabled={transcribing}
          />

          <button
            onClick={transcribe}
            disabled={transcribing || !url.trim()}
            className="inline-flex items-center gap-2 px-4 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow transition disabled:opacity-30"
          >
            {transcribing ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Stahuji + transkribuji
                (~1–3 min)…
              </>
            ) : (
              <>
                <Plus size={16} /> Transkribovat
              </>
            )}
          </button>

          {error && <p className="text-red-400 text-xs mt-2">⚠ {error}</p>}

          <p className="text-xs text-matrix-dim/70 mt-3">
            Tip: Pro Instagram a Facebook videa může být potřeba nastavit
            cookies — pokud selže "Sign in", nastav YT_DLP_COOKIES v .env.
          </p>
        </div>

        {/* List */}
        <h2 className="text-matrix text-lg mb-3 tracking-wider">
          ▢ Transkripty a scénáře
        </h2>

        {loading && <p className="text-matrix-dim">Načítám…</p>}
        {!loading && videos.length === 0 && (
          <p className="text-matrix-dim italic">
            Žádné. Vlož URL výše.
          </p>
        )}

        <div className="space-y-2">
          {videos.map((v) => (
            <Link
              key={v.id}
              href={`/skills/video-transcript/${v.id}`}
              className="block bg-matrix-tile p-4 rounded hover:shadow-matrix-glow transition group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-matrix group-hover:text-matrix-glow truncate">
                    {v.source_url}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-matrix-dim mt-1">
                    <span>
                      {v.duration_sec ? `${v.duration_sec}s` : ""}
                    </span>
                    <span>
                      {new Date(v.created_at).toLocaleString("cs-CZ", {
                        day: "numeric",
                        month: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    {v.script_md && (
                      <span className="text-green-400">✓ scénář</span>
                    )}
                  </div>
                </div>
                <div className="flex gap-1 shrink-0">
                  <a
                    href={v.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-matrix-dim hover:text-matrix p-1"
                  >
                    <ExternalLink size={14} />
                  </a>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      remove(v.id);
                    }}
                    className="text-matrix-dim hover:text-red-400 p-1"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context="video-transcript"
      />
    </>
  );
}
