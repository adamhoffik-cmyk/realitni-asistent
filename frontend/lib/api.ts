/**
 * Minimal API klient — fetch wrapper proti backend.
 * Rewrites v next.config.js routuje /api/* na backend.
 */

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export interface ApiError {
  status: number;
  detail: string;
}

async function request<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const url = `${BASE}/api${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw { status: res.status, detail } as ApiError;
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

// ----- Typed endpointy -----
export interface HealthResponse {
  status: string;
  version: string;
  env: string;
  timestamp: string;
}

export interface Skill {
  id: string;
  name: string;
  description: string | null;
  icon: string | null;
  version: string;
  enabled: boolean;
  order_index: number;
  usage_count: number;
  last_used_at: string | null;
  tile_data: Record<string, unknown> | null;
}

export interface Weather {
  location_name: string;
  current: {
    temperature_c: number;
    apparent_temperature_c: number;
    humidity: number | null;
    wind_speed_kmh: number;
    precipitation_mm: number;
    weather_code: number;
    is_day: boolean;
    time: string;
  };
  hourly: {
    time: string[];
    temperature_c: number[];
    precipitation_mm: number[];
    weather_code: number[];
  };
  daily: {
    sunrise: string;
    sunset: string;
    temperature_max_c: number;
    temperature_min_c: number;
  };
  fetched_at: string;
}

export const endpoints = {
  health: () => api.get<HealthResponse>("/health"),
  skills: () => api.get<Skill[]>("/skills"),
  weather: () => api.get<Weather>("/weather"),
};
