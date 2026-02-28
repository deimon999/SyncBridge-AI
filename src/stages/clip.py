"""Video clipping stage."""

from pathlib import Path

from src.utils.ffmpeg import run_ffmpeg


def extract_clip(input_video, start, end, out_path) -> None:
    """Extract a clip from input video to outputs/<run_id>/clip.mp4."""
    output_file = Path("outputs") / str(out_path) / "clip.mp4"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    run_ffmpeg(
        [
            "-y",
            "-i",
            str(input_video),
            "-ss",
            str(start),
            "-to",
            str(end),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_file),
        ]
    )
