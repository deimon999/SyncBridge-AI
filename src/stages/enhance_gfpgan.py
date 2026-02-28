"""Face enhancement stage with GFPGAN fallback."""

from pathlib import Path
import shutil
import subprocess
import sys


def _run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True)


def enhance(in_video, out_video):
    """Try GFPGAN+RealESRGAN enhancement; on failure copy input video."""
    input_video = Path(str(in_video))
    output_video = Path(str(out_video))
    output_video.parent.mkdir(parents=True, exist_ok=True)

    gfpgan_script = Path("GFPGAN") / "inference_gfpgan.py"

    try:
        if not gfpgan_script.exists():
            raise FileNotFoundError("Missing GFPGAN/inference_gfpgan.py")

        temp_dir = output_video.parent / "_gfpgan_tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        command = [
            sys.executable,
            str(gfpgan_script),
            "-i",
            str(input_video),
            "-o",
            str(temp_dir),
            "-v",
            "1.4",
            "-bg_upsampler",
            "realesrgan",
            "-face_upsample",
        ]
        _run(command)

        enhanced_video = temp_dir / input_video.name
        if not enhanced_video.exists():
            raise FileNotFoundError("GFPGAN output video not found")

        _run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(enhanced_video),
                "-i",
                str(input_video),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0?",
                "-c:v",
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "17",
                "-c:a",
                "copy",
                "-shortest",
                str(output_video),
            ]
        )
    except Exception:
        shutil.copyfile(input_video, output_video)

    return output_video
