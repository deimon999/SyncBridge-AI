"""Audio/video normalization stage."""

from pathlib import Path

from src.utils.ffmpeg import run_ffmpeg


def normalize(run_id) -> None:
    """Normalize clip video and extract mono 16k PCM audio."""
    base_dir = Path("outputs") / str(run_id)
    input_video = base_dir / "clip.mp4"
    fixed_video = base_dir / "clip_fixed.mp4"
    output_audio = base_dir / "audio.wav"

    base_dir.mkdir(parents=True, exist_ok=True)

    run_ffmpeg(
        [
            "-y",
            "-i",
            str(input_video),
            "-r",
            "25",
            "-c:v",
            "libx264",
            str(fixed_video),
        ]
    )

    run_ffmpeg(
        [
            "-y",
            "-i",
            str(fixed_video),
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(output_audio),
        ]
    )
