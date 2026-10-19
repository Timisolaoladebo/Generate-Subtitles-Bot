# pyrefly: ignore[missing-import]
import os
import shutil
import subprocess
from pathlib import Path
import imageio_ffmpeg


def get_ffmpeg_binary() -> str:
    """Return path to ffmpeg binary (system ffmpeg if available, otherwise imageio-ffmpeg)."""
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def extract_audio(video_path: str | Path, output_wav_path: str | Path) -> Path:
    """
    Extract audio from video file to 16kHz mono 16-bit PCM WAV.
    This format is optimal for Whisper speech recognition.
    """
    video_path = Path(video_path)
    output_wav_path = Path(output_wav_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = get_ffmpeg_binary()

    # -y: overwrite output
    # -vn: disable video recording
    # -acodec pcm_s16le: 16-bit PCM
    # -ar 16000: 16kHz sampling rate
    # -ac 1: mono channel
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_wav_path)
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed:\n{result.stderr}")

    return output_wav_path
