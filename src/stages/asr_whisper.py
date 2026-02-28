"""ASR stage using Whisper."""

from pathlib import Path

import whisper


def transcribe(audio_path, out_txt_path, model_name="small", language="kn"):
    """Transcribe audio and save plain text to outputs/<run_id>/transcript.txt."""
    _ = language
    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio_path), language="kn")

    run_id = Path(str(out_txt_path)).parent.name
    transcript_path = Path("outputs") / run_id / "transcript.txt"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(result.get("text", "").strip(), encoding="utf-8")

    return transcript_path
