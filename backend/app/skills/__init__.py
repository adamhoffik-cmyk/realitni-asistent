"""Skill pluginy. Každý skill = samostatný modul importovaný zde.

Přidání nového skillu: vytvoř soubor `<nazev>.py`, definuj třídu dědící z BaseSkill,
přidej import níže. Registry při startu aplikace skill automaticky zaregistruje.
"""

from app.skills import articles, demo, nabor, sfera, video_transcript  # noqa: F401
