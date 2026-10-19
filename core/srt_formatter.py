from pathlib import Path
from typing import Any, Iterable


def format_timestamp(seconds: float, is_vtt: bool = False) -> str:
    """
    Convert seconds into subtitle timestamp format.
    SRT format:  HH:MM:SS,mmm (comma delimiter)
    VTT format:  HH:MM:SS.mmm (dot delimiter)
    """
    total_seconds = max(0.0, float(seconds))
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    secs = int(total_seconds % 60)
    millis = int(round((total_seconds - int(total_seconds)) * 1000))

    # Guard for rounding overflow (e.g., 999.6ms rounding up to 1000ms)
    if millis >= 1000:
        millis -= 1000
        secs += 1
        if secs >= 60:
            secs -= 60
            minutes += 1
            if minutes >= 60:
                minutes -= 60
                hours += 1

    sep = "." if is_vtt else ","
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{sep}{millis:03d}"


def segments_to_srt(segments: Iterable[Any], output_file: str | Path) -> Path:
    """
    Write segments into standard .srt format.
    Accepts segments with `start`, `end`, and `text` as attributes or dict keys.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        counter = 1
        for seg in segments:
            start = getattr(seg, "start", None) if hasattr(seg, "start") else seg.get("start", 0.0)
            end = getattr(seg, "end", None) if hasattr(seg, "end") else seg.get("end", 0.0)
            text = (getattr(seg, "text", None) if hasattr(seg, "text") else seg.get("text", "")).strip()

            if not text:
                continue

            start_str = format_timestamp(start, is_vtt=False)
            end_str = format_timestamp(end, is_vtt=False)

            f.write(f"{counter}\n{start_str} --> {end_str}\n{text}\n\n")
            counter += 1

    return output_path


def segments_to_vtt(segments: Iterable[Any], output_file: str | Path) -> Path:
    """
    Write segments into standard .vtt format for HTML5 browser video playback.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        counter = 1
        for seg in segments:
            start = getattr(seg, "start", None) if hasattr(seg, "start") else seg.get("start", 0.0)
            end = getattr(seg, "end", None) if hasattr(seg, "end") else seg.get("end", 0.0)
            text = (getattr(seg, "text", None) if hasattr(seg, "text") else seg.get("text", "")).strip()

            if not text:
                continue

            start_str = format_timestamp(start, is_vtt=True)
            end_str = format_timestamp(end, is_vtt=True)

            f.write(f"{counter}\n{start_str} --> {end_str}\n{text}\n\n")
            counter += 1

    return output_path
