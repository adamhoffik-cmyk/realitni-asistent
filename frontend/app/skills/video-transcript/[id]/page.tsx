"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Loader2, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type VideoScript } from "@/lib/api";

const FORMATS = [
  { value: "reel_30s", label: "IG Reel 30s" },
  { value: "reel_60s", label: "IG Reel 60s" },
  { value: "tiktok", label: "TikTok 30-60s" },
  { value: "fb_post", label: "FB post + video 90s" },
];

export default function VideoDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ?? "";

  const [video, setVideo] = useState<VideoScript | null>(null);
  const [generating, setGenerating] = useState(false);
  const [format, setFormat] = useState("reel_60s");
  const [angle, setAngle] = useState("");
  const [chatOpen, setChatOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    endpoints.videos.get(id).then(setVideo).catch(() => setError("Nenalezeno"));
  }, [id]);

  const gen = async () => {
    if (!video) return;
    setGenerating(true);
    setError(null);
    try {
      const updated = await endpoints.videos.generateScript(video.id, {
        format,
        angle: angle || undefined,
      });
      setVideo(updated);
    } catch (e: any) {
      setError(e?.detail || "Chyba generování");
    } finally {
      setGenerating(false);
    }
  };

  if (error && !video) {
    return (
      <>
        <Header onOpenChat={() => setChatOpen(true)} />
        <main className="max-w-5xl mx-auto px-4 py-6">
          <p className="text-matrix">⚠ {error}</p>
        </main>
      </>
    );
  }

  if (!video) {
    return (
      <>
        <Header onOpenChat={() => setChatOpen(true)} />
        <main className="max-w-5xl mx-auto px-4 py-6">
          <p className="text-matrix-dim">Načítám…</p>
        </main>
      </>
    );
  }

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />

      <main className="max-w-6xl mx-auto px-4 py-6">
        <Link
          href="/skills/video-transcript"
          className="inline-flex items-center gap-2 text-matrix-dim hover:text-matrix mb-4"
        >
          <ArrowLeft size={16} /> Zpět
        </Link>

        <div className="mb-4">
          <a
            href={video.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-matrix hover:text-matrix-glow text-sm break-all"
          >
            {video.source_url}
          </a>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {/* Transkript */}
          <div className="bg-matrix-tile p-4 rounded">
            <h2 className="text-matrix mb-3">📝 Transkript</h2>
            <div className="prose-matrix max-h-[600px] overflow-y-auto text-sm">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {video.transcript_md}
              </ReactMarkdown>
            </div>
          </div>

          {/* Scénář */}
          <div className="bg-matrix-tile p-4 rounded">
            <h2 className="text-matrix mb-3 flex items-center gap-2">
              <Sparkles size={16} /> Scénář pro tvé video
            </h2>

            {!video.script_md && (
              <>
                <div className="space-y-2 mb-3">
                  <label className="text-xs text-matrix-dim block">Formát</label>
                  <select
                    value={format}
                    onChange={(e) => setFormat(e.target.value)}
                    className="w-full bg-matrix-bg border border-matrix rounded px-3 py-2 text-matrix text-sm"
                  >
                    {FORMATS.map((f) => (
                      <option key={f.value} value={f.value}>
                        {f.label}
                      </option>
                    ))}
                  </select>

                  <label className="text-xs text-matrix-dim block mt-2">
                    Volitelný vlastní úhel (co chceš zdůraznit)
                  </label>
                  <input
                    type="text"
                    value={angle}
                    onChange={(e) => setAngle(e.target.value)}
                    placeholder="např. „zaměř se na aspekt hypoték"
                    className="w-full bg-transparent border border-matrix rounded px-3 py-2 text-matrix text-sm"
                  />
                </div>

                <button
                  onClick={gen}
                  disabled={generating}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow transition disabled:opacity-30"
                >
                  {generating ? (
                    <>
                      <Loader2 size={14} className="animate-spin" /> Claude
                      píše scénář…
                    </>
                  ) : (
                    <>
                      <Sparkles size={14} /> Vygenerovat scénář
                    </>
                  )}
                </button>

                {error && <p className="text-red-400 text-xs mt-2">⚠ {error}</p>}
              </>
            )}

            {video.script_md && (
              <>
                <div className="prose-matrix max-h-[600px] overflow-y-auto text-sm">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {video.script_md}
                  </ReactMarkdown>
                </div>
                <button
                  onClick={gen}
                  disabled={generating}
                  className="mt-3 text-xs text-matrix-dim hover:text-matrix"
                >
                  Regenerovat scénář
                </button>
              </>
            )}
          </div>
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
