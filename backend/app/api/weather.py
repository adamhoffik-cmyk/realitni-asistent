"""Weather endpoint — volá Open-Meteo (zdarma, bez klíče)."""
from __future__ import annotations

from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.schemas import (
    WeatherCurrent,
    WeatherDaily,
    WeatherHourly,
    WeatherResponse,
)

router = APIRouter(prefix="/weather", tags=["weather"])

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


@router.get("", response_model=WeatherResponse)
async def get_weather() -> WeatherResponse:
    settings = get_settings()
    params = {
        "latitude": settings.weather_lat,
        "longitude": settings.weather_lon,
        "timezone": settings.app_timezone,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "precipitation",
            "weather_code",
            "is_day",
        ],
        "hourly": ["temperature_2m", "precipitation", "weather_code"],
        "daily": [
            "sunrise",
            "sunset",
            "temperature_2m_max",
            "temperature_2m_min",
        ],
        "forecast_hours": 12,
        "forecast_days": 1,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Open-Meteo error: {exc}") from exc

    data = resp.json()
    c = data["current"]
    h = data["hourly"]
    d = data["daily"]

    return WeatherResponse(
        location_name=settings.weather_location_name,
        current=WeatherCurrent(
            temperature_c=c["temperature_2m"],
            apparent_temperature_c=c["apparent_temperature"],
            humidity=c.get("relative_humidity_2m"),
            wind_speed_kmh=c["wind_speed_10m"],
            wind_direction_deg=c.get("wind_direction_10m"),
            precipitation_mm=c["precipitation"],
            weather_code=c["weather_code"],
            is_day=bool(c["is_day"]),
            time=datetime.fromisoformat(c["time"]),
        ),
        hourly=WeatherHourly(
            time=[datetime.fromisoformat(t) for t in h["time"]],
            temperature_c=h["temperature_2m"],
            precipitation_mm=h["precipitation"],
            weather_code=h["weather_code"],
        ),
        daily=WeatherDaily(
            sunrise=datetime.fromisoformat(d["sunrise"][0]),
            sunset=datetime.fromisoformat(d["sunset"][0]),
            temperature_max_c=d["temperature_2m_max"][0],
            temperature_min_c=d["temperature_2m_min"][0],
        ),
        fetched_at=datetime.now(timezone.utc),
    )
