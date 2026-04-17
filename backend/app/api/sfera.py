"""Sféra vlivu API — evidence osob + automatické reminders."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db import get_db
from app.models.db_models import SpheraPerson
from app.security.encryption import decrypt, encrypt

router = APIRouter(prefix="/sfera", tags=["sfera"])


class PersonIn(BaseModel):
    full_name: str
    phone: str | None = None
    email: str | None = None
    relationship: str | None = None  # rodina|pritel|byvaly_klient|znamy|kolega|jiny
    target_interval_months: int = 4
    notes: str | None = None


class PersonOut(BaseModel):
    id: str
    full_name: str
    phone: str | None  # dešifrované pro UI (pozor: sensitivity)
    email: str | None
    relationship: str | None
    last_contact_at: datetime | None
    last_contact_channel: str | None
    target_interval_months: int
    notes: str | None
    days_since_last_contact: int | None = None
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime


def _to_out(row: SpheraPerson) -> PersonOut:
    phone = decrypt(row.phone_enc) if row.phone_enc else None
    email = decrypt(row.email_enc) if row.email_enc else None
    days_since: int | None = None
    is_overdue = False
    if row.last_contact_at is not None:
        delta = datetime.now(timezone.utc) - row.last_contact_at
        days_since = delta.days
        # Overdue = uplynul target interval
        target_days = row.target_interval_months * 30
        is_overdue = days_since > target_days
    else:
        is_overdue = True  # never contacted

    return PersonOut(
        id=row.id,
        full_name=row.full_name,
        phone=phone,
        email=email,
        relationship=row.relationship,
        last_contact_at=row.last_contact_at,
        last_contact_channel=row.last_contact_channel,
        target_interval_months=row.target_interval_months,
        notes=row.notes,
        days_since_last_contact=days_since,
        is_overdue=is_overdue,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.post("/persons", response_model=PersonOut, status_code=201)
async def create_person(
    payload: PersonIn, session: AsyncSession = Depends(get_db)
) -> PersonOut:
    row = SpheraPerson(
        full_name=payload.full_name,
        phone_enc=encrypt(payload.phone) if payload.phone else None,
        email_enc=encrypt(payload.email) if payload.email else None,
        relationship=payload.relationship,
        target_interval_months=payload.target_interval_months,
        notes=payload.notes,
    )
    session.add(row)
    await session.commit()
    return _to_out(row)


@router.get("/persons", response_model=list[PersonOut])
async def list_persons(
    overdue_only: bool = Query(False),
    session: AsyncSession = Depends(get_db),
) -> list[PersonOut]:
    rows = list(
        (await session.execute(select(SpheraPerson).order_by(SpheraPerson.full_name)))
        .scalars()
        .all()
    )
    outputs = [_to_out(r) for r in rows]
    if overdue_only:
        outputs = [o for o in outputs if o.is_overdue]
    return outputs


@router.patch("/persons/{person_id}", response_model=PersonOut)
async def update_person(
    person_id: str,
    payload: dict = Body(...),
    session: AsyncSession = Depends(get_db),
) -> PersonOut:
    row = (
        await session.execute(select(SpheraPerson).where(SpheraPerson.id == person_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404)

    if "full_name" in payload:
        row.full_name = payload["full_name"]
    if "phone" in payload:
        row.phone_enc = encrypt(payload["phone"]) if payload["phone"] else None
    if "email" in payload:
        row.email_enc = encrypt(payload["email"]) if payload["email"] else None
    if "relationship" in payload:
        row.relationship = payload["relationship"]
    if "target_interval_months" in payload:
        row.target_interval_months = int(payload["target_interval_months"])
    if "notes" in payload:
        row.notes = payload["notes"]

    await session.commit()
    return _to_out(row)


@router.post("/persons/{person_id}/contact")
async def log_contact(
    person_id: str,
    payload: dict = Body(default={}),
    session: AsyncSession = Depends(get_db),
) -> PersonOut:
    """Zaznamenej, že jsi dnes kontaktoval osobu."""
    row = (
        await session.execute(select(SpheraPerson).where(SpheraPerson.id == person_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404)
    row.last_contact_at = datetime.now(timezone.utc)
    row.last_contact_channel = payload.get("channel", "phone")
    await session.commit()
    return _to_out(row)


@router.delete("/persons/{person_id}", status_code=204)
async def delete_person(
    person_id: str, session: AsyncSession = Depends(get_db)
) -> None:
    row = (
        await session.execute(select(SpheraPerson).where(SpheraPerson.id == person_id))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404)
    await session.delete(row)
    await session.commit()
