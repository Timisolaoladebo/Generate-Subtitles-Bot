"""Core processing package for audio extraction, transcription, and subtitle formatting."""

import os
from pathlib import Path
from typing import Callable, Any, Optional

try:
    from .audio import extract_audio, get_ffmpeg_binary
    from .srt_formatter import segments_to_srt, segments_to_vtt, format_timestamp
    from .transcriber import transcribe_audio, get_model
except (ImportError, ValueError):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from audio import extract_audio, get_ffmpeg_binary
    from srt_formatter import segments_to_srt, segments_to_vtt, format_timestamp
    from transcriber import transcribe_audio, get_model


def process_video_to_subtitles(
    video_path: str | Path,
    output_dir: str | Path,
    model_name: str = "base",
    language: Optional[str] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    keep_audio: bool = False
) -> dict[str, Any]:
    """
    Complete end-to-end processing pipeline:
      1. Extracts 16kHz WAV audio from MP4.
      2. Transcribes speech into timestamped segments using faster-whisper.
      3. Generates both .srt (desktop players) and .vtt (web preview) files.
      4. Optionally cleans up intermediate .wav audio.

    Returns:
      Dictionary with paths to generated files and metadata.
    """
    video_path = Path(video_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    base_name = video_path.stem
    temp_wav_path = output_dir / f"{base_name}_temp.wav"
    srt_path = output_dir / f"{base_name}.srt"
    vtt_path = output_dir / f"{base_name}.vtt"

    # Step 1: Extract Audio
    if progress_callback:
        progress_callback(5.0, "Extracting audio from video...")
    extract_audio(video_path, temp_wav_path)

    # Step 2: Transcribe
    if progress_callback:
        progress_callback(10.0, f"Loading Whisper ({model_name}) model...")

    def wrapped_progress(pct: float, current_text: str):
        if progress_callback:
            # Map transcription progress to 10% - 90% range
            scaled_pct = 10.0 + (pct * 0.8)
            progress_callback(round(scaled_pct, 1), current_text)

    segments, metadata = transcribe_audio(
        audio_path=temp_wav_path,
        model_name=model_name,
        language=language,
        progress_callback=wrapped_progress
    )

    # Step 3: Format and write subtitle files
    if progress_callback:
        progress_callback(95.0, "Formatting SRT and VTT subtitle files...")

    segments_to_srt(segments, srt_path)
    segments_to_vtt(segments, vtt_path)

    # Step 4: Clean up temporary WAV if not needed
    if not keep_audio and temp_wav_path.exists():
        try:
            os.remove(temp_wav_path)
        except OSError:
            pass

    if progress_callback:
        progress_callback(100.0, "Complete! Subtitles generated.")

    return {
        "status": "success",
        "video_path": str(video_path),
        "srt_path": str(srt_path),
        "vtt_path": str(vtt_path),
        "srt_filename": srt_path.name,
        "vtt_filename": vtt_path.name,
        "segment_count": len(segments),
        "metadata": metadata
    }


__all__ = [
    "process_video_to_subtitles",
    "extract_audio",
    "get_ffmpeg_binary",
    "segments_to_srt",
    "segments_to_vtt",
    "format_timestamp",
    "transcribe_audio",
    "get_model"
]
