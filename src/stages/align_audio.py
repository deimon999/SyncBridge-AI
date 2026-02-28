"""Audio alignment stage using ffprobe/ffmpeg."""

from pathlib import Path
import shutil
import subprocess

from src.utils.ffmpeg import run_ffmpeg


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


def align(hindi_raw_wav_path, clip_fixed_mp4_path, out_wav_path):
    """Align Hindi raw audio duration to clip video duration and save hindi_aligned.wav."""
    input_audio = Path(str(hindi_raw_wav_path))
    input_video = Path(str(clip_fixed_mp4_path))

    run_id = Path(str(out_wav_path)).parent.name
    output_audio = Path("outputs") / run_id / "hindi_aligned.wav"
    output_audio.parent.mkdir(parents=True, exist_ok=True)

    audio_duration = _probe_duration_seconds(input_audio)
    video_duration = _probe_duration_seconds(input_video)
    diff = audio_duration - video_duration

    print(f"hindi_raw.wav duration: {audio_duration:.3f}s")
    print(f"clip_fixed.mp4 duration: {video_duration:.3f}s")

    if abs(diff) > 0.05 and audio_duration > 0 and video_duration > 0:
        factor = audio_duration / video_duration
        factor = max(0.95, min(1.08, factor))
        print(f"chosen atempo factor: {factor:.4f}")
        run_ffmpeg(
            [
                "-y",
                "-i",
                str(input_audio),
                "-filter:a",
                f"atempo={factor:.6f}",
                str(output_audio),
            ]
        )
    else:
        print("chosen atempo factor: 1.0000")
        shutil.copyfile(input_audio, output_audio)

    return output_audio
