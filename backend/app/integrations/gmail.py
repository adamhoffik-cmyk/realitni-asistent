"""Gmail API wrapper — read, send, list, label."""
from __future__ import annotations

import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.google_oauth import get_credentials

logger = logging.getLogger(__name__)


async def _build_service(session: AsyncSession):
    creds = await get_credentials(session)
    if creds is None:
        raise RuntimeError("Google není přihlášený — projdi OAuth flow na /api/auth/google")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


async def get_profile(session: AsyncSession) -> dict[str, Any]:
    """Vrátí profil (emailAddress, messagesTotal, threadsTotal)."""
    service = await _build_service(session)
    return service.users().getProfile(userId="me").execute()


async def list_messages(
    session: AsyncSession,
    *,
    query: str = "in:inbox",
    max_results: int = 20,
    label_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """List messages (IDs only — pro plný obsah volej get_message).

    `query` je Gmail search syntax: `from:foo@bar.cz`, `is:unread`, `newer_than:7d`
    """
    service = await _build_service(session)
    req = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results,
    )
    if label_ids:
        req = service.users().messages().list(
            userId="me", q=query, maxResults=max_results, labelIds=label_ids
        )
    return req.execute().get("messages", [])


async def get_message(session: AsyncSession, msg_id: str) -> dict[str, Any]:
    """Plný content zprávy s headerem + body."""
    service = await _build_service(session)
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()
    return _parse_message(msg)


def _parse_message(msg: dict) -> dict[str, Any]:
    """Extrahuje subject, from, to, date, body z raw API response."""
    headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}

    # Body — rekurzivně najdi text/plain nebo text/html
    def extract_body(payload: dict) -> str:
        body = payload.get("body", {})
        if body.get("data"):
            try:
                return base64.urlsafe_b64decode(body["data"]).decode("utf-8", errors="replace")
            except Exception:
                return ""
        for part in payload.get("parts", []) or []:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        # Fallback: první text/html bez tagů (hrubě)
        for part in payload.get("parts", []) or []:
            if part.get("mimeType") == "text/html":
                data = part.get("body", {}).get("data")
                if data:
                    html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                    # jednoduché strip HTML — pro lepší použít bleach/html2text
                    import re
                    return re.sub(r"<[^>]+>", "", html)
        return ""

    return {
        "id": msg["id"],
        "thread_id": msg.get("threadId"),
        "snippet": msg.get("snippet", ""),
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "subject": headers.get("subject", "(bez předmětu)"),
        "date": headers.get("date", ""),
        "body": extract_body(msg.get("payload", {})),
        "label_ids": msg.get("labelIds", []),
        "is_unread": "UNREAD" in (msg.get("labelIds", []) or []),
    }


async def send_message(
    session: AsyncSession,
    *,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    reply_to_message_id: str | None = None,
    thread_id: str | None = None,
    html: bool = False,
) -> dict[str, Any]:
    """Odešle e-mail. Vrátí odeslanou zprávu (id + threadId)."""
    service = await _build_service(session)

    msg = MIMEMultipart("alternative") if html else MIMEText(body, "plain", "utf-8")
    if html:
        from email.mime.text import MIMEText as MT

        msg.attach(MT(body, "html", "utf-8"))

    msg["to"] = to
    msg["subject"] = subject
    if cc:
        msg["cc"] = ", ".join(cc)
    if bcc:
        msg["bcc"] = ", ".join(bcc)

    # Reply headers
    if reply_to_message_id:
        msg["In-Reply-To"] = reply_to_message_id
        msg["References"] = reply_to_message_id

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    request_body: dict[str, Any] = {"raw": raw}
    if thread_id:
        request_body["threadId"] = thread_id

    return service.users().messages().send(
        userId="me", body=request_body
    ).execute()


async def create_draft(
    session: AsyncSession,
    *,
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
) -> dict[str, Any]:
    """Vytvoří draft v Gmailu (neodešle — uživatel dokončí v Gmail UI)."""
    service = await _build_service(session)

    msg = MIMEText(body, "plain", "utf-8")
    msg["to"] = to
    msg["subject"] = subject
    if cc:
        msg["cc"] = ", ".join(cc)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()


async def mark_read(session: AsyncSession, msg_id: str) -> None:
    """Označí zprávu jako přečtenou (removeLabelIds: UNREAD)."""
    service = await _build_service(session)
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


async def list_labels(session: AsyncSession) -> list[dict[str, Any]]:
    service = await _build_service(session)
    return service.users().labels().list(userId="me").execute().get("labels", [])
