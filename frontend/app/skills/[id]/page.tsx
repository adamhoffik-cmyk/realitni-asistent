"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { endpoints, type Skill } from "@/lib/api";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";

export default function SkillPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [skill, setSkill] = useState<Skill | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    endpoints
      .skills()
      .then((list) => {
        const found = list.find((s) => s.id === id);
        if (!found) setNotFound(true);
        else setSkill(found);
      })
      .catch(() => setNotFound(true));
  }, [id]);

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

        {notFound ? (
          <div className="bg-matrix-tile p-6 rounded">
            <h1 className="text-matrix text-xl mb-2">⚠ Skill nenalezen</h1>
            <p className="text-matrix-dim">
              Skill <code>{id}</code> v registry neexistuje nebo je disabled.
            </p>
          </div>
        ) : !skill ? (
          <p className="text-matrix-dim">Načítám…</p>
        ) : (
          <div>
            <h1 className="text-matrix text-2xl mb-2 tracking-wide">
              {skill.name}
            </h1>
            <p className="text-matrix-dim mb-6">{skill.description}</p>

            <div className="bg-matrix-tile p-6 rounded">
              <p className="text-matrix-dim italic">
                Skill UI je scaffold — konkrétní funkcionalita pro „{skill.name}"
                přijde v odpovídající fázi (Články: Fáze 3, Videa: Fáze 4).
              </p>
              <p className="text-matrix-dim italic mt-2">
                Zatím můžeš použít chat (Ctrl+K) — v tomto kontextu se AI
                přepne do režimu: <span className="text-matrix">{skill.id}</span>.
              </p>
            </div>
          </div>
        )}
      </main>

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        context={skill?.id || "home"}
      />
    </>
  );
}
