"use client";

import { useEffect, useState } from "react";
import { Calendar as CalIcon, ExternalLink, LogIn, MapPin } from "lucide-react";
import { endpoints, type CalendarEvent } from "@/lib/api";

export function CalendarWidget() {
  const [authorized, setAuthorized] = useState<boolean | null>(null);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    endpoints.calendar
      .authStatus()
      .then((s) => {
        setAuthorized(s.authorized);
        if (s.authorized) {
          return endpoints.calendar.events(14);
        }
        return [];
      })
      .then(setEvents)
      .catch((e) => setError(e?.detail || "Chyba"))
      .finally(() => setLoading(false));
  }, []);

  const connect = () => {
    // OAuth flow musí jít přes prohlížeč (redirect na Google)
    // BasicAuth přes Caddy bude vyžadovat login ještě jednou — akceptovatelné
    window.location.href = "/api/auth/google";
  };

  if (loading) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-2 flex items-center gap-2">
          <CalIcon size={16} /> Kalendář
        </h3>
        <p className="text-matrix-dim text-sm">Načítám…</p>
      </div>
    );
  }

  if (authorized === false) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-3 flex items-center gap-2">
          <CalIcon size={16} /> Kalendář
        </h3>
        <p className="text-matrix-dim text-sm mb-3">
          Google Calendar zatím není propojený.
        </p>
        <button
          onClick={connect}
          className="inline-flex items-center gap-2 px-3 py-2 border border-matrix text-matrix text-sm rounded hover:shadow-matrix-glow transition"
        >
          <LogIn size={14} /> Připojit Google účet
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-2 flex items-center gap-2">
          <CalIcon size={16} /> Kalendář
        </h3>
        <p className="text-matrix-dim text-sm">⚠ {error}</p>
      </div>
    );
  }

  return (
    <div className="bg-matrix-tile p-4 rounded">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-matrix flex items-center gap-2">
          <CalIcon size={16} /> Kalendář — 14 dní
        </h3>
        <a
          href="https://calendar.google.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-matrix-dim hover:text-matrix"
          title="Otevřít Google Calendar"
        >
          <ExternalLink size={14} />
        </a>
      </div>

      {events.length === 0 && (
        <p className="text-matrix-dim text-xs italic">Žádné blížící se události.</p>
      )}

      <ul className="space-y-2 max-h-80 overflow-y-auto">
        {events.map((ev) => (
          <li
            key={ev.id}
            className="text-sm border-l-2 border-matrix-dim/30 pl-2"
          >
            <div className="text-matrix">{ev.summary}</div>
            {ev.start && (
              <div className="text-xs text-matrix-dim">
                {new Date(ev.start).toLocaleString("cs-CZ", {
                  weekday: "short",
                  day: "numeric",
                  month: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
                {ev.end && (
                  <>
                    {" – "}
                    {new Date(ev.end).toLocaleTimeString("cs-CZ", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </>
                )}
              </div>
            )}
            {ev.location && (
              <div className="text-xs text-matrix-dim flex items-center gap-1 mt-0.5">
                <MapPin size={10} /> {ev.location}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
