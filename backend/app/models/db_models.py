"""SQLAlchemy ORM modely.

Odpovídá schématu popsanému v ARCHITECTURE.md, sekce 5.
Všechny ID jsou UUID stringy (str). Timestamps jsou UTC ISO stringy uložené jako DATETIME.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Settings — klíč-hodnota KV store (jeden uživatel)
# --------------------------------------------------------------------------- #
class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )


# --------------------------------------------------------------------------- #
# Skill registry
# --------------------------------------------------------------------------- #
class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(128), nullable=True)
    version: Mapped[str] = mapped_column(String(32), default="0.1.0")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    order_index: Mapped[int] = mapped_column(Integer, default=100)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )


# --------------------------------------------------------------------------- #
# Chat — krátkodobá paměť
# --------------------------------------------------------------------------- #
class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    context: Mapped[str | None] = mapped_column(String(64), nullable=True)  # "home" | "articles" | …
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )

    turns: Mapped[list["ConversationTurn"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="ConversationTurn.created_at"
    )


class ConversationTurn(Base):
    __tablename__ = "conversation_turns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user | assistant | tool | system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skill_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tool_calls: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    session: Mapped[ConversationSession] = relationship(back_populates="turns")


# --------------------------------------------------------------------------- #
# Dlouhodobá paměť (poznámky, fakta, …)
# --------------------------------------------------------------------------- #
class Note(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    # note | fact | context | article | transcript | person | property
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sensitivity: Mapped[str] = mapped_column(String(16), default="internal")
    # public | internal | client_pii
    chroma_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )


# --------------------------------------------------------------------------- #
# Kalendář (cache z Google Calendar)
# --------------------------------------------------------------------------- #
class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # interní ID
    google_event_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    summary: Mapped[str] = mapped_column(String(512), nullable=False)
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    attendees: Mapped[list | None] = mapped_column(JSON, nullable=True)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)


# --------------------------------------------------------------------------- #
# Novinky (aggregátor)
# --------------------------------------------------------------------------- #
class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    url: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)


# --------------------------------------------------------------------------- #
# Oblíbené novinky (pro workflow News → Article)
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Nábor activities tracker
# --------------------------------------------------------------------------- #
class NaborActivity(Base):
    __tablename__ = "nabor_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    date: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    activity_type: Mapped[str] = mapped_column(String(32))
    # dopis | cold_call | setkani | schuzka | sfera_vlivu | jiny
    count: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # ne_zajem | mozna_pozdeji | schuzka_dohodnuta | zakazka_podepsana | other
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)


# --------------------------------------------------------------------------- #
# Sféra vlivu — evidence osob pro pravidelný kontakt (3× ročně)
# --------------------------------------------------------------------------- #
class SpheraPerson(Base):
    __tablename__ = "sfera_persons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    full_name: Mapped[str] = mapped_column(String(256), index=True)
    phone_enc: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    email_enc: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    relationship: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # rodina | pritel | byvaly_klient | znamy | kolega | jiny
    last_contact_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_contact_channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # phone | email | personal | whatsapp | sms
    target_interval_months: Mapped[int] = mapped_column(Integer, default=4)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )


class FavoriteNews(Base):
    __tablename__ = "favorite_news"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    news_item_id: Mapped[str] = mapped_column(
        ForeignKey("news_items.id", ondelete="CASCADE"), unique=True, index=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)  # uživatelská poznámka
    # Pokud uživatel vygeneruje článek z této novinky, odkaz na něj:
    article_id: Mapped[str | None] = mapped_column(
        ForeignKey("articles.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    news: Mapped["NewsItem"] = relationship(lazy="joined")


# --------------------------------------------------------------------------- #
# Ranní briefingy (historie)
# --------------------------------------------------------------------------- #
class Briefing(Base):
    __tablename__ = "briefings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    date: Mapped[str] = mapped_column(String(10), unique=True, index=True)  # YYYY-MM-DD
    content: Mapped[str] = mapped_column(Text, nullable=False)  # markdown
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)


# --------------------------------------------------------------------------- #
# Articles (Skill 1)
# --------------------------------------------------------------------------- #
class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    slug: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="draft")  # draft | published
    mode: Mapped[str] = mapped_column(String(16), default="A_new")  # A_new | B_legalized
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    meta_description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    stylebook_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    exported_to_drive_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )


# --------------------------------------------------------------------------- #
# VideoScripts (Skill 2)
# --------------------------------------------------------------------------- #
class VideoScript(Base):
    __tablename__ = "video_scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    transcript_md: Mapped[str] = mapped_column(Text, nullable=False)
    script_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)


# --------------------------------------------------------------------------- #
# OAuth tokens (šifrované)
# --------------------------------------------------------------------------- #
class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    service: Mapped[str] = mapped_column(String(64), primary_key=True)
    # "google_calendar" | "google_drive"
    access_token_enc: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    refresh_token_enc: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )


# Unique constraint — článek může mít stejný slug jen jednou (už je unique=True, ponechávám
# explicit jako dokumentační příklad pro budoucí indexy).
__all__ = [
    "Article",
    "Briefing",
    "CalendarEvent",
    "ConversationSession",
    "ConversationTurn",
    "FavoriteNews",
    "NaborActivity",
    "NewsItem",
    "Note",
    "OAuthToken",
    "Setting",
    "Skill",
    "SpheraPerson",
    "VideoScript",
]
