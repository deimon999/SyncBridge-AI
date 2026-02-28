"""Lip-sync stage using local Wav2Lip."""

from pathlib import Path
import subprocess
import sys


def run_wav2lip(face_video, audio, checkpoint, out_video):
    """Run Wav2Lip inference and save outputs/<run_id>/lipsynced.mp4."""
    wav2lip_repo = Path("Wav2Lip")
    checkpoint_path = Path(str(checkpoint)) if checkpoint else Path("checkpoints") / "wav2lip_gan.pth"

    if not wav2lip_repo.exists():
        raise FileNotFoundError("Missing ./Wav2Lip repository")
    if not checkpoint_path.exists():
        raise FileNotFoundError("Missing checkpoint: ./checkpoints/wav2lip_gan.pth")

    run_id = Path(str(out_video)).parent.name
    output_video = Path("outputs") / run_id / "lipsynced.mp4"
    output_video.parent.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "inference.py",
        "--checkpoint_path",
        str(checkpoint_path.resolve()),
        "--face",
        str(Path(str(face_video))),
        "--audio",
        str(Path(str(audio))),
        "--outfile",
        str(output_video.resolve()),
    ]

    subprocess.run(command, cwd=str(wav2lip_repo), check=True)
    return output_video
