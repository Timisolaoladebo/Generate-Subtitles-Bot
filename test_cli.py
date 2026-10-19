import sys
from pathlib import Path
from core import process_video_to_subtitles


def progress_tracker(percentage: float, message: str):
    print(f"[{percentage:5.1f}%] {message}")


def main():
    if len(sys.argv) < 2:
        print("\n❌ Missing video path argument!")
        print("Usage: python test_cli.py <path_to_video.mp4> [model_name]")
        print("Models: tiny, base (default), small, medium")
        print('Example: python test_cli.py "C:\\path\\to\\my_video.mp4" tiny\n')
        return

    video_path = Path(sys.argv[1].strip('"\''))
    model_name = sys.argv[2] if len(sys.argv) > 2 else "base"

    if not video_path.exists():
        print(f"\n❌ Error: File not found at '{video_path}'\n")
        return

    print(f"\n🚀 Starting subtitle generation for: {video_path.name}")
    print(f"⚙️ Engine: faster-whisper on CPU (model: '{model_name}')\n")

    try:
        result = process_video_to_subtitles(
            video_path=video_path,
            output_dir="outputs",
            model_name=model_name,
            progress_callback=progress_tracker
        )

        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Subtitles generated.")
        print("=" * 50)
        print(f"📄 SRT File (for VLC/media players): {result['srt_path']}")
        print(f"📄 VTT File (for web browsers):       {result['vtt_path']}")
        print(f"⏱️ Video Duration:                   {result['metadata']['duration']}s")
        print(f"🌐 Detected Language:                 {result['metadata']['language'].upper()} ({result['metadata']['language_probability']*100:.1f}%)")
        print(f"🔢 Total Subtitle Blocks:             {result['segment_count']}")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n❌ Error during processing: {e}\n")


if __name__ == "__main__":
    main()
