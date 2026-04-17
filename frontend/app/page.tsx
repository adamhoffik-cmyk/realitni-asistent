"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Database, Heart, Users, Target } from "lucide-react";
import { Header } from "@/components/Header";
import { WeatherWidget } from "@/components/WeatherWidget";
import { CalendarWidget } from "@/components/CalendarWidget";
import { NewsWidget } from "@/components/NewsWidget";
import { SkillTile } from "@/components/SkillTile";
import { QuickNote } from "@/components/QuickNote";
import { RecentNotesWidget } from "@/components/RecentNotesWidget";
import { ChatPanel } from "@/components/ChatPanel";
import { endpoints, type Skill } from "@/lib/api";

export default function HomePage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [chatOpen, setChatOpen] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    endpoints
      .skills()
      .then(setSkills)
      .catch((e) =>
        setLoadError(e.detail || "Backend nedostupný — spustil jsi ho?")
      );
  }, []);

  // Ctrl+K pro otevření chatu
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setChatOpen((o) => !o);
      }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  return (
    <>
      <Header onOpenChat={() => setChatOpen(true)} />

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {loadError && (
          <div className="bg-matrix-tile p-4 rounded border border-red-500/50">
            <p className="text-matrix">⚠ {loadError}</p>
            <p className="text-matrix-dim text-xs mt-1">
              Zkus: <code>docker compose up -d</code>
            </p>
          </div>
        )}

        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          <WeatherWidget />

          <CalendarWidget />

          <PlaceholderTile
            title="☀ Ranní briefing"
            subtitle="Automatický souhrn v 7:00 — Fáze 5"
          />

          <QuickNote />

          <RecentNotesWidget />

          <NewsWidget />
        </div>

        <section className="flex gap-3 flex-wrap">
          <Link
            href="/memory"
            className="inline-flex items-center gap-2 px-4 py-2 border border-matrix text-matrix rounded hover:shadow-matrix-glow transition"
          >
            <Database size={16} /> Paměť
          </Link>
          <Link
            href="/favorites"
            className="inline-flex items-center gap-2 px-4 py-2 border border-matrix text-matrix rounded hover:shadow-matrix-glow transition"
          >
            <Heart size={16} /> Oblíbené
          </Link>
          <Link
            href="/skills/nabor"
            className="inline-flex items-center gap-2 px-4 py-2 border border-matrix text-matrix rounded hover:shadow-matrix-glow transition"
          >
            <Target size={16} /> Nábor
          </Link>
          <Link
            href="/skills/sfera"
            className="inline-flex items-center gap-2 px-4 py-2 border border-matrix text-matrix rounded hover:shadow-matrix-glow transition"
          >
            <Users size={16} /> Sféra vlivu
          </Link>
        </section>

        <section>
          <h2 className="text-matrix text-lg mb-3 tracking-wider">
            ▢ SKILLY
          </h2>
          {skills.length === 0 && !loadError ? (
            <p className="text-matrix-dim text-sm">Načítám skilly…</p>
          ) : (
            <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
              {skills
                .filter((s) => s.enabled)
                .map((s) => (
                  <SkillTile key={s.id} skill={s} />
                ))}
            </div>
          )}
        </section>

        <footer className="text-center text-xs text-matrix-dim/50 pt-8">
          Realitní Asistent · Fáze 1 MVP · {new Date().getFullYear()}
        </footer>
      </main>

      {/* Plovoucí chat trigger pro mobil */}
      <button
        onClick={() => setChatOpen(true)}
        className="sm:hidden fixed bottom-4 right-4 w-14 h-14 bg-matrix-bg border border-matrix rounded-full text-matrix shadow-matrix-glow z-40"
        aria-label="Otevřít chat"
      >
        💬
      </button>

      <ChatPanel open={chatOpen} onClose={() => setChatOpen(false)} />
    </>
  );
}

function PlaceholderTile({
  title,
  subtitle,
  className = "",
}: {
  title: string;
  subtitle: string;
  className?: string;
}) {
  return (
    <div className={`bg-matrix-tile p-4 rounded opacity-60 ${className}`}>
      <h3 className="text-matrix mb-2">{title}</h3>
      <p className="text-matrix-dim text-xs italic">{subtitle}</p>
    </div>
  );
}
