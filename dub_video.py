"""Entry point for Kannada→Hindi dubbing pipeline."""

import argparse

from src.pipeline import run_pipeline


def main() -> None:
    """Run the dubbing pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_video", default="Hygiene - Kannada.mp4")
    parser.add_argument("--start", default="00:00:15")
    parser.add_argument("--end", default="00:00:45")
    parser.add_argument("--run_id", default="run1")
    parser.add_argument("--whisper_model", default="small", choices=["base", "small", "medium", "large"])
    parser.add_argument("--wav2lip_checkpoint", default=None)
    parser.add_argument("--no_enhance", action="store_true")
    args = parser.parse_args()

    final_path = run_pipeline(
        input_video=args.input_video,
        start=args.start,
        end=args.end,
        run_id=args.run_id,
        whisper_model=args.whisper_model,
        wav2lip_checkpoint=args.wav2lip_checkpoint,
        enable_enhancement=not args.no_enhance,
    )
    print(f"Final dubbed video: {final_path}")


if __name__ == "__main__":
    main()
