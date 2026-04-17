"use client";

import { useState } from "react";
import { endpoints } from "@/lib/api";

export function QuickNote() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">(
    "idle"
  );
  const [errorMsg, setErrorMsg] = useState<string>("");

  const save = async () => {
    if (!text.trim()) return;
    setStatus("saving");
    setErrorMsg("");
    try {
      await endpoints.notes.create({
        type: "note",
        content: text.trim(),
        sensitivity: "internal",
      });
      setStatus("saved");
      setText("");
      setTimeout(() => setStatus("idle"), 2500);
    } catch (e: any) {
      setStatus("error");
      setErrorMsg(e?.detail || "Chyba uložení");
      setTimeout(() => setStatus("idle"), 4000);
    }
  };

  return (
    <div className="bg-matrix-tile p-4 rounded">
      <h3 className="text-matrix mb-3">✎ Rychlá poznámka</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            save();
          }
        }}
        placeholder="Co si chceš zapamatovat? (Ctrl+Enter pro odeslání)"
        rows={3}
        className="w-full bg-transparent border border-matrix rounded p-2 text-matrix placeholder:text-matrix-dim/50 text-sm focus:outline-none focus:shadow-matrix-glow resize-none"
        disabled={status === "saving"}
      />
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-matrix-dim">
          {status === "saving" && "Ukládám…"}
          {status === "saved" && "✓ Zapamatováno"}
          {status === "error" && `⚠ ${errorMsg}`}
        </span>
        <button
          onClick={save}
          disabled={!text.trim() || status === "saving"}
          className="px-3 py-1 border border-matrix text-matrix text-xs rounded hover:shadow-matrix-glow transition disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Uložit
        </button>
      </div>
    </div>
  );
}
