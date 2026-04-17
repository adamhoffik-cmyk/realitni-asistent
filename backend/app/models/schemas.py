"""Pydantic schémata pro API (request/response DTOs)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ----- Health -----
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    env: str
    timestamp: datetime


# ----- Weather -----
class WeatherCurrent(BaseModel):
    temperature_c: float
    apparent_temperature_c: float
    humidity: int | None = None
    wind_speed_kmh: float
    wind_direction_deg: int | None = None
    precipitation_mm: float
    weather_code: int
    is_day: bool
    time: datetime


class WeatherHourly(BaseModel):
    time: list[datetime]
    temperature_c: list[float]
    precipitation_mm: list[float]
    weather_code: list[int]


class WeatherDaily(BaseModel):
    sunrise: datetime
    sunset: datetime
    temperature_max_c: float
    temperature_min_c: float


class WeatherResponse(BaseModel):
    location_name: str
    current: WeatherCurrent
    hourly: WeatherHourly
    daily: WeatherDaily
    fetched_at: datetime


# ----- Skills -----
class SkillOut(ORMBase):
    id: str
    name: str
    description: str | None
    icon: str | None
    version: str
    enabled: bool
    order_index: int
    usage_count: int
    last_used_at: datetime | None
    tile_data: dict[str, Any] | None = None


class SkillReorderPayload(BaseModel):
    order: list[str] = Field(..., description="IDs skillů v novém pořadí")


# ----- Chat -----
class ChatMessageIn(BaseModel):
    message: str
    session_id: str | None = None
    context: str | None = "home"  # home | articles | video-transcript | …


class ChatMessageOut(ORMBase):
    id: str
    session_id: str
    role: str
    content: str
    skill_id: str | None
    created_at: datetime


# ----- Notes / Memory -----
class NoteIn(BaseModel):
    type: str = "note"
    title: str | None = None
    content: str
    tags: list[str] | None = None
    source: str | None = None
    sensitivity: str = "internal"
    metadata: dict[str, Any] | None = None


class NoteOut(ORMBase):
    id: str
    type: str
    title: str | None
    content: str
    tags: list[str] | None
    source: str | None
    sensitivity: str
    created_at: datetime
    updated_at: datetime


class MemorySearchQuery(BaseModel):
    query: str
    types: list[str] | None = None
    limit: int = 10


class MemorySearchHit(BaseModel):
    note: NoteOut
    score: float


# ----- News -----
class NewsItemOut(ORMBase):
    id: str
    url: str
    source: str
    title: str
    summary: str | None
    published_at: datetime | None
    tags: list[str] | None
    is_favorite: bool = False


class FavoriteNewsIn(BaseModel):
    news_item_id: str
    note: str | None = None


class FavoriteNewsOut(ORMBase):
    id: str
    news_item_id: str
    note: str | None
    article_id: str | None
    created_at: datetime
    news: NewsItemOut | None = None


# ----- Briefing -----
class BriefingOut(ORMBase):
    id: str
    date: str
    content: str
    generated_at: datetime
