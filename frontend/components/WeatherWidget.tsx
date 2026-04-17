"use client";

import { useEffect, useState } from "react";
import { endpoints, type Weather } from "@/lib/api";
import { weatherDescription } from "@/lib/weatherCodes";
import { Sunrise, Sunset, Wind, Droplets } from "lucide-react";

export function WeatherWidget() {
  const [data, setData] = useState<Weather | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = () => {
      endpoints
        .weather()
        .then((w) => !cancelled && setData(w))
        .catch((e) => !cancelled && setError(e.detail || "Chyba načtení"));
    };
    load();
    const t = setInterval(load, 15 * 60 * 1000); // refresh každých 15 min
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, []);

  if (error) {
    return (
      <div className="bg-matrix-tile p-4 rounded">
        <h3 className="text-matrix mb-2">☁ Počasí</h3>
        <p className="text-matrix-dim text-sm">⚠ {error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-matrix-tile p-4 rounded animate-pulse">
        <h3 className="text-matrix mb-2">☁ Počasí</h3>
        <p className="text-matrix-dim text-sm">Načítám…</p>
      </div>
    );
  }

  const desc = weatherDescription(data.current.weather_code, data.current.is_day);
  const sunrise = new Date(data.daily.sunrise).toLocaleTimeString("cs-CZ", {
    hour: "2-digit",
    minute: "2-digit",
  });
  const sunset = new Date(data.daily.sunset).toLocaleTimeString("cs-CZ", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="bg-matrix-tile p-4 rounded">
      <h3 className="text-matrix mb-3 flex items-center justify-between">
        <span>☁ Počasí — {data.location_name}</span>
        <span className="text-xs text-matrix-dim">
          {new Date(data.fetched_at).toLocaleTimeString("cs-CZ", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </h3>
      <div className="flex items-center gap-4 mb-4">
        <span className="text-5xl">{desc.icon}</span>
        <div>
          <p className="text-3xl text-matrix font-bold">
            {data.current.temperature_c.toFixed(1)}°C
          </p>
          <p className="text-matrix-dim text-sm">
            Pocitově {data.current.apparent_temperature_c.toFixed(1)}°C · {desc.label}
          </p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-matrix-dim mb-3">
        <span className="flex items-center gap-1.5">
          <Wind size={12} /> {data.current.wind_speed_kmh.toFixed(0)} km/h
        </span>
        <span className="flex items-center gap-1.5">
          <Droplets size={12} /> {data.current.precipitation_mm.toFixed(1)} mm
        </span>
        <span className="flex items-center gap-1.5">
          <Sunrise size={12} /> {sunrise}
        </span>
        <span className="flex items-center gap-1.5">
          <Sunset size={12} /> {sunset}
        </span>
      </div>
      <div>
        <p className="text-xs text-matrix-dim mb-1">Dalších 12 hodin:</p>
        <div className="flex gap-1 overflow-x-auto">
          {data.hourly.time.slice(0, 12).map((t, i) => {
            const d = weatherDescription(
              data.hourly.weather_code[i],
              new Date(t).getHours() >= 6 && new Date(t).getHours() <= 20
            );
            return (
              <div
                key={t}
                className="flex flex-col items-center min-w-[40px] text-xs"
                title={d.label}
              >
                <span className="text-matrix-dim">
                  {new Date(t).getHours()}h
                </span>
                <span>{d.icon}</span>
                <span className="text-matrix">
                  {data.hourly.temperature_c[i].toFixed(0)}°
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
