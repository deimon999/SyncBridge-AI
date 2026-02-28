"""Pipeline composition for Kannada→Hindi dubbing."""

from pathlib import Path

from src.stages.align_audio import align
from src.stages.asr_whisper import transcribe
from src.stages.clip import extract_clip
from src.stages.enhance_gfpgan import enhance
from src.stages.lipsync_wav2lip import run_wav2lip
from src.stages.normalize import normalize
from src.stages.translate_indictrans import translate_kn_hi
from src.stages.tts_xtts import synthesize
from src.utils.ffmpeg import run_ffmpeg


def _finalize_video(video_path: Path, audio_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(output_path),
        ]
    )
    return output_path


def run_pipeline(
    input_video: str,
    start: str,
    end: str,
    run_id: str,
    whisper_model: str = "small",
    wav2lip_checkpoint: str | None = None,
    enable_enhancement: bool = True,
) -> Path:
    """Run all dubbing stages and return final output path."""
    base_dir = Path("outputs") / run_id
    base_dir.mkdir(parents=True, exist_ok=True)

    extract_clip(input_video, start, end, run_id)
    normalize(run_id)

    clip_fixed = base_dir / "clip_fixed.mp4"
    audio_wav = base_dir / "audio.wav"
    transcript_txt = base_dir / "transcript.txt"
    hindi_txt = base_dir / "hindi.txt"
    hindi_raw_wav = base_dir / "hindi_raw.wav"
    hindi_aligned_wav = base_dir / "hindi_aligned.wav"
    lipsynced_mp4 = base_dir / "lipsynced.mp4"
    enhanced_mp4 = base_dir / "enhanced.mp4"
    final_mp4 = base_dir / "final.mp4"

    transcribe(audio_wav, transcript_txt, model_name=whisper_model, language="kn")
    translate_kn_hi(transcript_txt, hindi_txt)
    synthesize(hindi_txt, audio_wav, hindi_raw_wav)
    align(hindi_raw_wav, clip_fixed, hindi_aligned_wav)
    run_wav2lip(clip_fixed, hindi_aligned_wav, wav2lip_checkpoint, lipsynced_mp4)

    source_video = lipsynced_mp4
    if enable_enhancement:
        source_video = enhance(lipsynced_mp4, enhanced_mp4)

    return _finalize_video(source_video, hindi_aligned_wav, final_mp4)
