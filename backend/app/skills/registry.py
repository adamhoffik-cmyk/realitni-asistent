"""Skill registry — objevuje, registruje a obsluhuje skilly."""
from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from datetime import datetime, timezone

from sqlalchemy import select

from app.db import session_scope
from app.models.db_models import Skill as SkillRow
from app.skills.base import BaseSkill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Singleton registry pro skilly."""

    _skills: dict[str, BaseSkill] = {}

    @classmethod
    def register(cls, skill: BaseSkill) -> None:
        if skill.manifest.id in cls._skills:
            logger.warning("Skill %s už registrovaný, přepisuji", skill.manifest.id)
        cls._skills[skill.manifest.id] = skill
        logger.info("Skill %s registrován", skill.manifest.id)

    @classmethod
    def get(cls, skill_id: str) -> BaseSkill | None:
        return cls._skills.get(skill_id)

    @classmethod
    def all(cls) -> list[BaseSkill]:
        return sorted(cls._skills.values(), key=lambda s: s.manifest.order_index)

    @classmethod
    async def bootstrap(cls) -> None:
        """Iteruje `app.skills.*`, instancuje BaseSkill subclassy, sync s DB."""
        import app.skills as skills_pkg

        for _, mod_name, _ in pkgutil.iter_modules(skills_pkg.__path__):
            if mod_name in {"base", "registry"}:
                continue
            module = importlib.import_module(f"app.skills.{mod_name}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj is BaseSkill:
                    continue
                if issubclass(obj, BaseSkill) and obj.__module__ == module.__name__:
                    instance = obj()
                    await instance.on_register()
                    cls.register(instance)

        await cls._sync_db()

    @classmethod
    async def _sync_db(cls) -> None:
        """Synchronizuje registr s tabulkou `skills`."""
        async with session_scope() as session:
            existing_rows = (await session.execute(select(SkillRow))).scalars().all()
            existing_by_id = {r.id: r for r in existing_rows}
            now = datetime.now(timezone.utc)

            for skill in cls._skills.values():
                m = skill.manifest
                row = existing_by_id.get(m.id)
                if row is None:
                    row = SkillRow(
                        id=m.id,
                        name=m.name,
                        description=m.description,
                        icon=m.icon,
                        version=m.version,
                        order_index=m.order_index,
                        enabled=True,
                        usage_count=0,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(row)
                    logger.info("Skill %s přidán do DB", m.id)
                else:
                    # aktualizace metadat (uživatel může ponechat enabled/order_index)
                    row.name = m.name
                    row.description = m.description
                    row.icon = m.icon
                    row.version = m.version
                    row.updated_at = now

            # Skilly v DB, ale ne v kódu — nastavit enabled=False, nesmazat
            for row in existing_rows:
                if row.id not in cls._skills:
                    row.enabled = False
                    logger.info("Skill %s v DB, ale ne v kódu → disable", row.id)
