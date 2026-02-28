"""FFmpeg utility wrappers."""

import subprocess


def run_ffmpeg(args: list[str]) -> None:
    """Run ffmpeg with the provided argument list."""
    command = ["ffmpeg", *args]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
