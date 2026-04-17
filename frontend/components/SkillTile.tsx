"use client";

import Link from "next/link";
import type { Skill } from "@/lib/api";

export function SkillTile({ skill }: { skill: Skill }) {
  return (
    <Link
      href={`/skills/${skill.id}`}
      className="bg-matrix-tile p-4 rounded flex flex-col gap-2 no-underline"
    >
      <div className="flex items-start justify-between">
        <span className="text-2xl">{iconFallback(skill.icon)}</span>
        <span className="text-xs text-matrix-dim">
          {skill.usage_count}× použito
        </span>
      </div>
      <h3 className="text-matrix font-bold glow-on-hover">{skill.name}</h3>
      <p className="text-matrix-dim text-xs flex-1">{skill.description}</p>
      {skill.tile_data && Object.keys(skill.tile_data).length > 0 && (
        <div className="text-xs text-matrix mt-2 pt-2 border-t border-matrix">
          {Object.entries(skill.tile_data).map(([k, v]) => (
            <div key={k} className="flex justify-between">
              <span className="text-matrix-dim">{k}:</span>
              <span>{String(v)}</span>
            </div>
          ))}
        </div>
      )}
    </Link>
  );
}

/**
 * Fallback ikona, dokud nepřipojíme PNG z marketing material 2026/ikony/.
 * Později: <Image src={`/icons/${skill.icon}.png`} .../>
 */
function iconFallback(icon: string | null): string {
  const map: Record<string, string> = {
    award: "🏆",
    document: "📄",
    "media-video": "🎥",
    budget_price: "💰",
    contact: "👥",
    search: "🔍",
    calendar: "📅",
    newsletter: "📰",
  };
  if (icon && map[icon]) return map[icon];
  return "▢";
}
