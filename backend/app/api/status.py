"""System status — unified health check endpoint pro UI widget.

Vrací strukturovaný list checků s celkovým overall statusem.
Používá se ve frontend `StatusWidget` + můžeš použít jako monitoring hook.
"""
from __future__ import annotations

import logging
import os
import shutil
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.config import get_settings
from app.db import get_db
from app.integrations import google_oauth
from app.models.db_models import OAuthToken

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["status"])

_START_TIME = time.time()


class CheckResult(BaseModel):
    id: str
    name: str
    status: Literal["ok", "warning", "error", "info"]
    message: str
    details: dict[str, Any] | None = None


class StatusResponse(BaseModel):
    overall: Literal["ok", "warning", "error"]
    checks: list[CheckResult]
    generated_at: datetime


async def _check_backend() -> CheckResult:
    uptime_sec = int(time.time() - _START_TIME)
    hours = uptime_sec // 3600
    mins = (uptime_sec % 3600) // 60
    if hours >= 24:
        uptime_str = f"{hours // 24} d {hours % 24} h"
    elif hours > 0:
        uptime_str = f"{hours} h {mins} m"
    else:
        uptime_str = f"{mins} m"
    return CheckResult(
        id="backend",
        name="Backend",
        status="ok",
        message=f"v{__version__} · uptime {uptime_str}",
        details={"uptime_sec": uptime_sec, "version": __version__},
    )


async def _check_database(session: AsyncSession) -> CheckResult:
    try:
        await session.execute(text("SELECT 1"))
        return CheckResult(
            id="database",
            name="Databáze",
            status="ok",
            message="SQLite OK",
        )
    except Exception as exc:  # noqa: BLE001
        return CheckResult(
            id="database",
            name="Databáze",
            status="error",
            message=str(exc),
        )


async def _check_chroma() -> CheckResult:
    try:
        from app.core.memory import get_memory_collection

        coll = get_memory_collection()
        count = coll.count()
        return CheckResult(
            id="chroma",
            name="Paměť (ChromaDB)",
            status="ok",
            message=f"{count} záznamů",
            details={"count": count},
        )
    except Exception as exc:  # noqa: BLE001
        return CheckResult(
            id="chroma",
            name="Paměť (ChromaDB)",
            status="warning",
            message=f"Selhalo: {exc}",
        )


async def _check_google_oauth(session: AsyncSession) -> CheckResult:
    """Google OAuth — authorized + access token expirace."""
    settings = get_settings()
    if not settings.google_client_id:
        return CheckResult(
            id="google_oauth",
            name="Google OAuth",
            status="warning",
            message="GOOGLE_CLIENT_ID nenastaveno — OAuth nelze použít",
        )

    row = (
        await session.execute(
            __import__("sqlalchemy").select(OAuthToken).where(
                OAuthToken.service == google_oauth.SERVICE_KEY
            )
        )
    ).scalar_one_or_none()
    if row is None or not row.access_token_enc:
        return CheckResult(
            id="google_oauth",
            name="Google OAuth",
            status="warning",
            message="Nepřihlášeno — klikni 'Připojit Google účet' v Kalendáři",
        )

    # Spočítat čas do expirace access tokenu
    now = datetime.now(timezone.utc)
    expires_at = row.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    token_age_days = (now - row.updated_at.replace(tzinfo=timezone.utc)).days if row.updated_at else 0

    # Refresh token warning — Testing mode má 7 dní
    # (nevíme přesný expire, ale tokenAge > 5 dní = blíží se to)
    if token_age_days >= 6:
        status = "warning"
        message = f"Token starý {token_age_days} d — obnov přihlášení (Testing mode limit ~7 d)"
    elif token_age_days >= 4:
        status = "info"
        message = f"Token starý {token_age_days} d (refresh token drží ~7 d v Testing módu)"
    else:
        # Access token — auto-refresh, jen pro info
        if expires_at:
            mins_to_expire = int((expires_at - now).total_seconds() / 60)
            if mins_to_expire < 0:
                message = "Access token expirovaný — při dalším volání se auto-obnoví"
            else:
                message = f"Přihlášen · access token zbývá {mins_to_expire} min (auto-refresh)"
        else:
            message = "Přihlášen"
        status = "ok"

    scope_list = (row.scope or "").split()
    has_calendar = any("calendar" in s for s in scope_list)
    has_gmail = any("gmail" in s for s in scope_list)
    has_drive = any("drive" in s for s in scope_list)

    return CheckResult(
        id="google_oauth",
        name="Google OAuth",
        status=status,
        message=message,
        details={
            "token_age_days": token_age_days,
            "has_calendar": has_calendar,
            "has_gmail": has_gmail,
            "has_drive": has_drive,
            "scopes_count": len(scope_list),
        },
    )


async def _check_claude_cli() -> CheckResult:
    """Claude Code CLI a plugin ceske-realitni-pravo."""
    import json as _json

    settings = get_settings()
    claude_bin = settings.claude_cli_path
    which = shutil.which(claude_bin) or shutil.which("claude")
    if not which:
        return CheckResult(
            id="claude_cli",
            name="Claude Code CLI",
            status="error",
            message="Binárka nenalezena — chat nebude fungovat",
        )

    home = os.environ.get("HOME", "/root")
    claude_json = Path(home) / ".claude.json"
    claude_dir = Path(home) / ".claude"
    marketplaces_dir = claude_dir / "plugins" / "marketplaces"
    known_marketplaces_json = claude_dir / "plugins" / "known_marketplaces.json"

    if not claude_json.exists():
        return CheckResult(
            id="claude_cli",
            name="Claude Code CLI",
            status="warning",
            message=f"Chybí {claude_json} — možná neprovedený login",
            details={"binary": which, "home": str(home)},
        )

    # Plugin detekce — zkusíme 3 způsoby
    plugin_found = False
    plugin_details: dict[str, Any] = {}

    # 1) Marketplace adresář (může mít různé jméno)
    if marketplaces_dir.exists():
        marketplaces = [d.name for d in marketplaces_dir.iterdir() if d.is_dir()]
        plugin_details["marketplaces"] = marketplaces
        # hledáme něco obsahující "realitni" nebo "legal" nebo "ceske"
        for mp_name in marketplaces:
            lower = mp_name.lower()
            if "realitni" in lower or "ceske" in lower:
                plugin_found = True
                plugin_details["matched_marketplace"] = mp_name
                break

    # 2) known_marketplaces.json
    if not plugin_found and known_marketplaces_json.exists():
        try:
            data = _json.loads(known_marketplaces_json.read_text(encoding="utf-8"))
            names = list(data.keys()) if isinstance(data, dict) else []
            plugin_details["known_marketplaces"] = names
            for name in names:
                if "realitni" in name.lower() or "ceske" in name.lower():
                    plugin_found = True
                    plugin_details["matched_in_known"] = name
                    break
        except Exception as exc:  # noqa: BLE001
            plugin_details["known_marketplaces_error"] = str(exc)

    # 3) .claude.json obsahuje zmínku o plugin legal
    if not plugin_found and claude_json.exists():
        try:
            content = claude_json.read_text(encoding="utf-8", errors="ignore")
            if '"legal"' in content or "realitni-asistent-local" in content:
                plugin_found = True
                plugin_details["found_in_claude_json"] = True
        except Exception:  # noqa: BLE001
            pass

    plugin_status = "aktivní ✓" if plugin_found else "nedetekovaný"
    status_level = "ok" if plugin_found else "info"

    return CheckResult(
        id="claude_cli",
        name="Claude Code CLI",
        status=status_level,
        message=f"CLI OK · plugin {plugin_status}",
        details={"binary": which, **plugin_details},
    )


async def _check_disk() -> CheckResult:
    """Volné místo v data/ adresáři."""
    try:
        settings = get_settings()
        target = Path(settings.chroma_persist_dir).resolve()
        if not target.exists():
            target = Path("/app/data")
        if not target.exists():
            target = Path("/")

        stat = os.statvfs(target)
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        used_pct = int(((total_gb - free_gb) / total_gb) * 100) if total_gb else 0

        if used_pct >= 90:
            status = "error"
        elif used_pct >= 75:
            status = "warning"
        else:
            status = "ok"

        return CheckResult(
            id="disk",
            name="Disk",
            status=status,
            message=f"{used_pct}% obsazeno · {free_gb:.1f} GB volné z {total_gb:.1f} GB",
            details={
                "free_gb": round(free_gb, 1),
                "total_gb": round(total_gb, 1),
                "used_pct": used_pct,
            },
        )
    except Exception as exc:  # noqa: BLE001
        return CheckResult(
            id="disk",
            name="Disk",
            status="warning",
            message=f"Nelze zjistit: {exc}",
        )


async def _check_ssl_cert() -> CheckResult:
    """Zjistí expiraci Let's Encrypt certifikátu pro doménu."""
    settings = get_settings()
    domain_env = os.environ.get("CADDY_DOMAIN", "")
    if not domain_env:
        return CheckResult(
            id="ssl_cert",
            name="SSL certifikát",
            status="info",
            message="CADDY_DOMAIN není v env — nelze ověřit",
        )

    try:
        import socket

        ctx = ssl.create_default_context()
        with socket.create_connection((domain_env, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain_env) as ssock:
                cert = ssock.getpeercert()

        not_after = cert.get("notAfter")
        if not not_after:
            return CheckResult(
                id="ssl_cert",
                name="SSL certifikát",
                status="warning",
                message="Nelze načíst expiraci",
            )
        expire_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
        days_left = (expire_dt - datetime.utcnow()).days

        if days_left < 7:
            status = "error"
        elif days_left < 20:
            status = "warning"
        else:
            status = "ok"

        return CheckResult(
            id="ssl_cert",
            name="SSL certifikát",
            status=status,
            message=f"Vyprší za {days_left} dní (Caddy auto-obnovuje ~30 dní před)",
            details={
                "expires_at": expire_dt.isoformat(),
                "days_left": days_left,
            },
        )
    except Exception as exc:  # noqa: BLE001
        return CheckResult(
            id="ssl_cert",
            name="SSL certifikát",
            status="info",
            message=f"Nelze ověřit: {exc}",
        )


async def _check_scheduler() -> CheckResult:
    from app.scheduler.startup import get_scheduler

    sched = get_scheduler()
    if sched is None or not sched.running:
        return CheckResult(
            id="scheduler",
            name="Scheduler",
            status="warning",
            message="Neběží — ranní briefing + news fetch nefungují",
        )
    jobs = sched.get_jobs()
    return CheckResult(
        id="scheduler",
        name="Scheduler",
        status="ok",
        message=f"{len(jobs)} joby aktivní",
        details={"job_ids": [j.id for j in jobs]},
    )


@router.get("", response_model=StatusResponse)
async def get_status(session: AsyncSession = Depends(get_db)) -> StatusResponse:
    """Komplexní health check pro UI Status widget."""
    checks: list[CheckResult] = []
    checks.append(await _check_backend())
    checks.append(await _check_database(session))
    checks.append(await _check_chroma())
    checks.append(await _check_google_oauth(session))
    checks.append(await _check_claude_cli())
    checks.append(await _check_scheduler())
    checks.append(await _check_disk())
    checks.append(await _check_ssl_cert())

    # Overall status = nejhorší
    if any(c.status == "error" for c in checks):
        overall = "error"
    elif any(c.status == "warning" for c in checks):
        overall = "warning"
    else:
        overall = "ok"

    return StatusResponse(
        overall=overall,
        checks=checks,
        generated_at=datetime.now(timezone.utc),
    )
