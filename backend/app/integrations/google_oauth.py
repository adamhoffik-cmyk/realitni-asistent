"""Google OAuth 2.0 flow — authorize, callback, refresh.

Tokeny se ukládají šifrovaně do `oauth_tokens` tabulky.
Jeden tuple = jeden "service" klíč (google_calendar + google_drive mají
shodné credentials, ale různé scopes — v praxi je unifikujeme do 'google').
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.db_models import OAuthToken
from app.security.encryption import decrypt, encrypt

logger = logging.getLogger(__name__)

SERVICE_KEY = "google"  # unifikované — scopes zahrnují calendar i drive

# In-memory store pro PKCE code_verifier mezi /auth/google (authorize) a /callback.
# Google OAuth vyžaduje PKCE — při authorize se vygeneruje verifier, uloží se
# pod 'state' klíčem, a při callbacku se použije stejný. Flow trvá < 60 s,
# single-user app → in-memory dict stačí.
_pending_verifiers: dict[str, tuple[str, float]] = {}


def _cleanup_pending() -> None:
    """Smaže verifiers starší než 10 min (safety — nebrání memory leak)."""
    import time as _t

    now = _t.time()
    expired = [k for k, (_, ts) in _pending_verifiers.items() if now - ts > 600]
    for k in expired:
        _pending_verifiers.pop(k, None)


def _flow_from_settings() -> Flow:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID a GOOGLE_CLIENT_SECRET nejsou nastavené v .env. "
            "Vytvoř OAuth klienta v Google Cloud Console — viz docs/GOOGLE_OAUTH_SETUP.md"
        )
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=settings.google_scopes_list,
        redirect_uri=settings.google_redirect_uri,
    )


def build_authorization_url() -> tuple[str, str]:
    """Vrátí (authorize_url, state). Uloží PKCE code_verifier pro callback."""
    import time as _t

    _cleanup_pending()
    flow = _flow_from_settings()
    authorization_url, state = flow.authorization_url(
        access_type="offline",  # refresh token
        include_granted_scopes="true",
        prompt="consent",  # vynucuje refresh token i při re-auth
    )
    # Google OAuth vyžaduje PKCE — uložíme code_verifier pod state klíčem,
    # aby ho callback (v nové Flow instanci) mohl načíst
    verifier = getattr(flow, "code_verifier", None)
    if verifier:
        _pending_verifiers[state] = (verifier, _t.time())
        logger.debug("OAuth state=%s verifier uložen", state[:8])
    return authorization_url, state


async def exchange_code_for_tokens(
    code: str, state: str | None, session: AsyncSession
) -> dict[str, Any]:
    """Vymění authorization code za tokeny a uloží šifrovaně."""
    flow = _flow_from_settings()

    # Načti PKCE verifier z původní authorize response
    if state and state in _pending_verifiers:
        verifier, _ts = _pending_verifiers.pop(state)
        flow.code_verifier = verifier
        logger.debug("OAuth state=%s verifier obnoven", state[:8])
    else:
        logger.warning(
            "OAuth state=%s verifier NENALEZEN — PKCE selže, pokud ho Google vyžaduje",
            (state or "")[:8],
        )

    flow.fetch_token(code=code)
    credentials = flow.credentials

    access_enc = encrypt(credentials.token)
    refresh_enc = encrypt(credentials.refresh_token or "")
    expires_at = credentials.expiry.replace(tzinfo=timezone.utc) if credentials.expiry else None

    # Upsert
    existing = (
        await session.execute(select(OAuthToken).where(OAuthToken.service == SERVICE_KEY))
    ).scalar_one_or_none()
    if existing is None:
        row = OAuthToken(
            service=SERVICE_KEY,
            access_token_enc=access_enc,
            refresh_token_enc=refresh_enc,
            expires_at=expires_at,
            scope=" ".join(credentials.scopes or []),
        )
        session.add(row)
    else:
        existing.access_token_enc = access_enc
        if refresh_enc:
            existing.refresh_token_enc = refresh_enc
        existing.expires_at = expires_at
        existing.scope = " ".join(credentials.scopes or [])

    await session.commit()
    logger.info("Google OAuth: tokens uloženy, scopes=%s", credentials.scopes)

    return {
        "scopes": credentials.scopes,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


async def get_credentials(session: AsyncSession) -> Credentials | None:
    """Načte credentials ze SQLite, refreshne pokud expirované.

    Vrátí None, pokud uživatel ještě neprovedl OAuth flow.
    """
    settings = get_settings()
    row = (
        await session.execute(select(OAuthToken).where(OAuthToken.service == SERVICE_KEY))
    ).scalar_one_or_none()
    if row is None or not row.access_token_enc:
        return None

    access_token = decrypt(row.access_token_enc)
    refresh_token = decrypt(row.refresh_token_enc) if row.refresh_token_enc else None

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=(row.scope or "").split() if row.scope else None,
        expiry=row.expires_at.replace(tzinfo=None) if row.expires_at else None,
    )

    # Refresh pokud expirované
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleRequest())
            # Uložit nový access token
            row.access_token_enc = encrypt(creds.token)
            if creds.expiry:
                row.expires_at = creds.expiry.replace(tzinfo=timezone.utc)
            await session.commit()
            logger.info("Google OAuth: access token refreshed")
        except Exception as exc:  # noqa: BLE001
            logger.error("Token refresh failed: %s", exc)
            return None

    return creds


async def revoke(session: AsyncSession) -> bool:
    """Smaže tokeny z DB (revocation flow pojedeme volitelně)."""
    row = (
        await session.execute(select(OAuthToken).where(OAuthToken.service == SERVICE_KEY))
    ).scalar_one_or_none()
    if row is None:
        return False
    await session.delete(row)
    await session.commit()
    return True


async def is_authorized(session: AsyncSession) -> bool:
    creds = await get_credentials(session)
    return creds is not None and creds.valid
