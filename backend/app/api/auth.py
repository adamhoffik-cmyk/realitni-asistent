"""Google OAuth authorization flow — start, callback, status, revoke."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.integrations import google_oauth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def google_authorize() -> RedirectResponse:
    """Začátek OAuth flow — přesměrování na Google consent screen."""
    try:
        url, state = google_oauth.build_authorization_url()
    except RuntimeError as exc:
        raise HTTPException(500, detail=str(exc))
    # state bys měl uložit do cookie pro CSRF protection; pro single-user
    # on-premise app to zatím zanedbáme
    return RedirectResponse(url=url, status_code=302)


@router.get("/google/callback", response_class=HTMLResponse)
async def google_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """OAuth callback — výměna code za tokeny, uložení."""
    if error:
        return HTMLResponse(
            f"<html><body style='background:#000;color:#00FF41;font-family:monospace;padding:2rem'>"
            f"<h1>⚠ OAuth chyba</h1><p>{error}</p>"
            f"<a href='/' style='color:#00FF41'>← Zpět</a></body></html>",
            status_code=400,
        )
    if not code:
        raise HTTPException(400, detail="Chybí authorization code")

    try:
        result = await google_oauth.exchange_code_for_tokens(code, state, session)
    except Exception as exc:
        logger.exception("OAuth exchange failed")
        return HTMLResponse(
            f"<html><body style='background:#000;color:#00FF41;font-family:monospace;padding:2rem'>"
            f"<h1>⚠ OAuth výměna selhala</h1><p>{exc}</p>"
            f"<a href='/' style='color:#00FF41'>← Zpět</a></body></html>",
            status_code=500,
        )

    return HTMLResponse(
        f"<html><body style='background:#000;color:#00FF41;font-family:monospace;padding:2rem'>"
        f"<h1>✓ Google připojen</h1>"
        f"<p>Scopes: {', '.join(result['scopes'] or [])}</p>"
        f"<p>Expires: {result['expires_at']}</p>"
        f"<p><a href='/' style='color:#00FF41'>← Zpět na home</a></p>"
        f"</body></html>"
    )


@router.get("/google/status")
async def google_status(session: AsyncSession = Depends(get_db)) -> dict:
    authorized = await google_oauth.is_authorized(session)
    return {"authorized": authorized, "service": "google"}


@router.post("/google/revoke")
async def google_revoke(session: AsyncSession = Depends(get_db)) -> dict:
    ok = await google_oauth.revoke(session)
    return {"revoked": ok}
