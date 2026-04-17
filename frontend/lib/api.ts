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

// ----- Notes / Memory -----
export interface Note {
  id: string;
  type: string;
  title: string | null;
  content: string;
  tags: string[] | null;
  source: string | null;
  sensitivity: string;
  created_at: string;
  updated_at: string;
}

export interface NoteIn {
  type?: string;
  title?: string | null;
  content: string;
  tags?: string[] | null;
  source?: string | null;
  sensitivity?: string;
  metadata?: Record<string, unknown> | null;
}

export interface MemorySearchHit {
  note: Note;
  score: number;
}

// ----- News -----
export interface NewsItem {
  id: string;
  url: string;
  source: string;
  title: string;
  summary: string | null;
  published_at: string | null;
  tags: string[] | null;
  is_favorite?: boolean;
}

// ----- Articles -----
export interface Article {
  id: string;
  slug: string;
  title: string;
  status: string;
  mode: string;
  content_md: string;
  meta_description: string | null;
  keywords: string[] | null;
  source_url: string | null;
  created_at: string;
  updated_at: string;
}

// ----- Favorites -----
export interface FavoriteNews {
  id: string;
  news_item_id: string;
  note: string | null;
  article_id: string | null;
  created_at: string;
  news: NewsItem | null;
}

export const endpoints = {
  health: () => api.get<HealthResponse>("/health"),
  skills: () => api.get<Skill[]>("/skills"),
  weather: () => api.get<Weather>("/weather"),
  notes: {
    list: (params?: {
      types?: string[];
      tags?: string[];
      limit?: number;
      offset?: number;
    }) => {
      const q = new URLSearchParams();
      params?.types?.forEach((t) => q.append("types", t));
      params?.tags?.forEach((t) => q.append("tags", t));
      if (params?.limit) q.set("limit", String(params.limit));
      if (params?.offset) q.set("offset", String(params.offset));
      const qs = q.toString();
      return api.get<Note[]>(`/notes${qs ? `?${qs}` : ""}`);
    },
    get: (id: string) => api.get<Note>(`/notes/${id}`),
    create: (body: NoteIn) => api.post<Note>("/notes", body),
    update: (id: string, body: NoteIn) => api.patch<Note>(`/notes/${id}`, body),
    delete: (id: string) => api.delete<void>(`/notes/${id}`),
    search: (query: string, types?: string[], limit = 10) =>
      api.post<MemorySearchHit[]>("/notes/search", { query, types, limit }),
  },
  news: {
    list: (limit = 10) => api.get<NewsItem[]>(`/news?limit=${limit}`),
    refresh: () => api.post<{ sources: Record<string, Record<string, number>> }>(
      "/news/refresh"
    ),
  },
  articles: {
    list: (status?: string) =>
      api.get<Article[]>(`/articles${status ? `?status=${status}` : ""}`),
    get: (id: string) => api.get<Article>(`/articles/${id}`),
    generate: (body: { source_url?: string; topic?: string; favorite_id?: string }) =>
      api.post<Article>("/articles/generate", body),
    update: (id: string, body: Partial<Article>) =>
      api.patch<Article>(`/articles/${id}`, body),
    delete: (id: string) => api.delete<void>(`/articles/${id}`),
  },
  favorites: {
    list: () => api.get<FavoriteNews[]>("/favorites"),
    add: (newsItemId: string, note?: string) =>
      api.post<FavoriteNews>("/favorites", {
        news_item_id: newsItemId,
        note: note || null,
      }),
    removeByNews: (newsItemId: string) =>
      api.delete<void>(`/favorites/news/${newsItemId}`),
    updateNote: (favoriteId: string, note: string) =>
      api.patch<FavoriteNews>(`/favorites/${favoriteId}`, { note }),
  },
};
