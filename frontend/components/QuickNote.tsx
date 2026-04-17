"use client";

import { useState } from "react";

export function QuickNote() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">(
    "idle"
  );

  const save = async () => {
    if (!text.trim()) return;
    setStatus("saving");
    // TODO Fáze 2: volat /api/notes
    // Zatím simulujeme uložení s timeoutem, abychom viděli flow
    await new Promise((r) => setTimeout(r, 500));
    setStatus("saved");
    setText("");
    setTimeout(() => setStatus("idle"), 2000);
  };

  return (
    <div className="bg-matrix-tile p-4 rounded">
      <h3 className="text-matrix mb-3">✎ Rychlá poznámka</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Co si chceš zapamatovat?"
        rows={3}
        className="w-full bg-transparent border border-matrix rounded p-2 text-matrix placeholder:text-matrix-dim/50 text-sm focus:outline-none focus:shadow-matrix-glow resize-none"
      />
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-matrix-dim">
          {status === "saving" && "Ukládám…"}
          {status === "saved" && "✓ Zapamatováno"}
          {status === "error" && "⚠ Chyba"}
        </span>
        <button
          onClick={save}
          disabled={!text.trim() || status === "saving"}
          className="px-3 py-1 border border-matrix text-matrix text-xs rounded hover:shadow-matrix-glow transition disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Uložit
        </button>
      </div>
      <p className="text-xs text-matrix-dim/60 mt-2 italic">
        Poznámka: full backend napojení přijde ve Fázi 2 (paměť + ChromaDB).
      </p>
    </div>
  );
}
