"""yt-dlp + ffmpeg + faster-whisper → transkript videa z URL.

Podporuje Instagram Reels, Facebook Watch, TikTok, YouTube, Twitter/X.
Pro IG/FB je někdy potřeba cookies — nastav přes YT_DLP_COOKIES env var.
"""
from __future__ import annotations

import logging
import shutil
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TranscribeResult:
    text: str
    language: str
    duration_sec: float
    source_title: str | None
    source_duration: int | None
    segments: list[dict]  # [{start, end, text}]


@lru_cache
def get_whisper_model():
    """Lazy-load Whisper model (~244 MB small, ~769 MB medium)."""
    from faster_whisper import WhisperModel

    settings = get_settings()
    logger.info(
        "Načítám Whisper model: %s (device=%s, compute=%s)",
        settings.whisper_model,
        settings.whisper_device,
        settings.whisper_compute_type,
    )
    return WhisperModel(
        settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )


async def download_audio(url: str, work_dir: Path) -> tuple[Path, dict]:
    """Stáhne video/audio přes yt-dlp.

    Vrátí (audio_path, info_dict). Audio je WAV 16 kHz mono (optimální pro Whisper).
    """
    import asyncio

    import yt_dlp

    output_template = str(work_dir / "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }
        ],
        "postprocessor_args": ["-ar", "16000", "-ac", "1"],  # 16kHz mono
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }

    # Volitelné cookies (IG/FB často vyžaduje)
    settings = get_settings()
    cookies_path = getattr(settings, "yt_dlp_cookies", None)
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path

    def _run() -> dict:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, _run)

    audio_path = work_dir / "audio.wav"
    if not audio_path.exists():
        # Někdy yt-dlp vytvoří .m4a → převod ffmpeg
        for ext in ("m4a", "mp3", "ogg", "webm"):
            candidate = work_dir / f"audio.{ext}"
            if candidate.exists():
                audio_path = candidate
                break
    if not audio_path.exists():
        raise RuntimeError("yt-dlp audio extract failed — soubor neexistuje")

    return audio_path, info


async def transcribe_url(url: str) -> TranscribeResult:
    """Komplet pipeline — URL → audio → Whisper → transkript."""
    import asyncio

    with tempfile.TemporaryDirectory(prefix="asistent_whisper_") as tmp:
        tmp_dir = Path(tmp)

        audio_path, info = await download_audio(url, tmp_dir)
        logger.info("Audio: %s (%s bytes)", audio_path.name, audio_path.stat().st_size)

        model = get_whisper_model()

        def _transcribe():
            segments_gen, info_w = model.transcribe(
                str(audio_path),
                language="cs",
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )
            segs = [
                {"start": s.start, "end": s.end, "text": s.text.strip()}
                for s in segments_gen
            ]
            return segs, info_w

        loop = asyncio.get_event_loop()
        segments, winfo = await loop.run_in_executor(None, _transcribe)

        full_text = "\n".join(s["text"] for s in segments if s["text"].strip())

        return TranscribeResult(
            text=full_text,
            language=winfo.language,
            duration_sec=winfo.duration,
            source_title=info.get("title"),
            source_duration=info.get("duration"),
            segments=segments,
        )
