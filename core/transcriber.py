import os
# Silence Windows HuggingFace symlinks warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# PyAV compatibility patch for newer av versions (handles metadata_errors removal)
try:
    import av
    _orig_av_open = av.open
    def _patched_av_open(*args, metadata_errors=None, **kwargs):
        return _orig_av_open(*args, **kwargs)
    av.open = _patched_av_open
except Exception:
    pass

from pathlib import Path
from typing import Callable, Any, Optional
from faster_whisper import WhisperModel

# Global model cache to avoid reloading models on repeated requests
_MODEL_CACHE: dict[str, WhisperModel] = {}


def get_model(model_name: str = "base", device: str = "cpu", compute_type: str = "int8") -> WhisperModel:
    """Retrieve or load a WhisperModel instance cached in memory."""
    cache_key = f"{model_name}_{device}_{compute_type}"
    if cache_key not in _MODEL_CACHE:
        _MODEL_CACHE[cache_key] = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type
        )
    return _MODEL_CACHE[cache_key]


def transcribe_audio(
    audio_path: str | Path,
    model_name: str = "base",
    language: Optional[str] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Transcribe audio file into timestamped segments.
    Returns:
      (segments_list, metadata_dict)
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = get_model(model_name=model_name, device="cpu", compute_type="int8")

    # vad_filter=True filters out non-speech segments
    segments_gen, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )

    total_duration = info.duration if info.duration else 0.0
    collected_segments: list[dict[str, Any]] = []

    for seg in segments_gen:
        seg_dict = {
            "id": seg.id,
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
            "words": [
                {"start": w.start, "end": w.end, "word": w.word}
                for w in (seg.words or [])
            ] if hasattr(seg, "words") and seg.words else []
        }
        collected_segments.append(seg_dict)

        if progress_callback and total_duration > 0:
            pct = min(100.0, round((seg.end / total_duration) * 100.0, 1))
            progress_callback(pct, seg_dict["text"])

    metadata = {
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(total_duration, 2)
    }

    return collected_segments, metadata
