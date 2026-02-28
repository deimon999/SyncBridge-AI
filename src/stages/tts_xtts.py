"""TTS stage using a fixed Hindi female neural voice (no speaker cloning)."""

import asyncio
import importlib
import subprocess
from pathlib import Path

from src.utils.ffmpeg import run_ffmpeg


VOICE = "hi-IN-SwaraNeural"
RATE_MIN = -40
RATE_MAX = 40


def _probe_duration_seconds(media_path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def _rate_to_edge_string(rate_percent):
    if rate_percent >= 0:
        return f"+{rate_percent}%"
    return f"{rate_percent}%"


async def _save_mp3(text, voice, rate_percent, out_mp3):
    edge_tts = importlib.import_module("edge_tts")
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=_rate_to_edge_string(rate_percent),
    )
    await communicate.save(str(out_mp3))


def _choose_rate_percent(ref_wav_path, synthesized_mp3_path):
    if not ref_wav_path:
        return 0

    reference = Path(str(ref_wav_path))
    if not reference.exists():
        return 0

    target_duration = _probe_duration_seconds(reference)
    current_duration = _probe_duration_seconds(synthesized_mp3_path)
    if target_duration <= 0 or current_duration <= 0:
        return 0

    rate = int(round(((current_duration / target_duration) - 1.0) * 100.0))
    return max(RATE_MIN, min(RATE_MAX, rate))


def synthesize(hindi_txt_path, ref_wav_path, out_wav_path):
    """Synthesize Hindi speech to outputs/<run_id>/hindi_raw.wav using a Hindi female neural voice."""
    try:
        importlib.import_module("edge_tts")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "edge-tts is required for Hindi neural TTS. Install it with `pip install edge-tts`."
        ) from exc

    text = Path(str(hindi_txt_path)).read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Hindi text is empty; cannot synthesize speech.")

    run_id = Path(str(out_wav_path)).parent.name
    output_wav = Path("outputs") / run_id / "hindi_raw.wav"
    output_wav.parent.mkdir(parents=True, exist_ok=True)

    temp_mp3 = output_wav.with_suffix(".tmp.mp3")
    asyncio.run(_save_mp3(text, VOICE, 0, temp_mp3))

    tuned_rate = _choose_rate_percent(ref_wav_path, temp_mp3)
    if tuned_rate != 0:
        asyncio.run(_save_mp3(text, VOICE, tuned_rate, temp_mp3))

    run_ffmpeg(
        [
            "-y",
            "-i",
            str(temp_mp3),
            "-ac",
            "1",
            "-ar",
            "24000",
            str(output_wav),
        ]
    )

    if temp_mp3.exists():
        temp_mp3.unlink()

    return output_wav
