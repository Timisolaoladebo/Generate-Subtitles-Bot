# MP4 to SRT Subtitle Generator — Project Plan

## 1. Project Overview
A local-first, CPU-optimized web application that takes an MP4 video file, transcribes the audio with precise timestamps using `faster-whisper`, formats the output into standard `.srt` subtitle format, and allows instant playback and verification in an embedded browser video player.

---

## 2. Technical Stack
- **Backend**: Python, FastAPI, Uvicorn
- **Speech-to-Text Engine**: `faster-whisper` (CTranslate2, quantized `int8` for fast CPU execution)
- **Audio Processing**: `ffmpeg` (with `imageio-ffmpeg` as standalone fallback for Windows)
- **Frontend**: HTML5, Vanilla CSS (Modern dark mode / responsive UI), Vanilla JavaScript
- **Video & Subtitle Playback**: HTML5 `<video>` player with WebVTT/SRT `<track>` support for real-time in-browser preview

---

## 3. Project Directory Structure
```
Generate Subtitles/
├── .venv/                      # Python virtual environment (isolated dependencies)
├── plan.md                     # Project plan and progress tracker
├── requirements.txt            # Python dependencies
├── core/
│   ├── __init__.py
│   ├── audio.py                # Audio extraction from MP4 using FFmpeg
│   ├── transcriber.py          # faster-whisper speech-to-text with timestamps
│   └── srt_formatter.py        # Timestamp formatting & SRT file writer
├── web/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Clean, modern styling with dark mode
│   │   └── js/
│   │       └── app.js          # File upload, progress polling, player controller
│   └── templates/
│       └── index.html          # Main web dashboard interface
├── uploads/                    # Temporary storage for uploaded MP4s
├── outputs/                    # Generated .srt and .vtt files
└── app.py                      # FastAPI server entry point
```

---

## 4. Step-by-Step Implementation Plan

### Phase 1: Environment & Dependency Setup
- [x] **Step 1.1**: Create `requirements.txt` listing:
  - `fastapi`
  - `uvicorn[standard]`
  - `python-multipart` (for file uploads)
  - `faster-whisper`
  - `imageio-ffmpeg` (provides a portable static ffmpeg binary)
  - `jinja2`
- [x] **Step 1.2**: Set up Python virtual environment (`venv`).
- [x] **Step 1.3**: Install dependencies and verify `ffmpeg` and `faster-whisper` import cleanly.

---

### Phase 2: Core Processing Engine
- [x] **Step 2.1**: Implement `core/audio.py`
  - Locate system `ffmpeg` or `imageio-ffmpeg` binary.
  - Extract audio stream from MP4 to 16kHz mono `.wav` file.
- [x] **Step 2.2**: Implement `core/srt_formatter.py`
  - Convert float seconds into standard SRT timestamp format (`HH:MM:SS,mmm`).
  - Generate valid `.srt` file blocks:
    ```
    1
    00:00:01,200 --> 00:00:04,500
    Subtitle text here.
    ```
  - Also provide VTT formatting (`HH:MM:SS.mmm`) for HTML5 `<video>` `<track>` playback.
- [x] **Step 2.3**: Implement `core/transcriber.py`
  - Initialize `faster-whisper` WhisperModel (`tiny`, `base`, or `small`) on CPU with `compute_type="int8"`.
  - Process extracted audio and yield progress callbacks / segment data.
- [x] **Step 2.4**: Create a standalone CLI test script to verify MP4 $\rightarrow$ SRT pipeline on a test file.

---

### Phase 3: Backend API Service (`app.py`)
- [ ] **Step 3.1**: Initialize FastAPI application with static files and template mounting.
- [ ] **Step 3.2**: Implement `/api/upload` endpoint for receiving the MP4 file and model selection.
- [ ] **Step 3.3**: Implement background transcription job queue/manager with real-time status updates (progress percentage, current segment).
- [ ] **Step 3.4**: Implement `/api/status/{job_id}` endpoint (or Server-Sent Events / SSE).
- [ ] **Step 3.5**: Implement endpoints to serve video stream, download `.srt`, and serve `.vtt` for browser track preview.

---

### Phase 4: Frontend Web Dashboard
- [ ] **Step 4.1**: Build `templates/index.html`
  - Modern, responsive header and layout.
  - Drag-and-drop file upload zone with file info.
  - Model selector (e.g. `tiny` for speed, `base` for balance, `small` for high accuracy).
  - Language options (Auto-detect or specific language).
  - Progress bar with live status messages.
  - Split view / preview section with HTML5 Video Player and Subtitle Preview panel.
- [ ] **Step 4.2**: Design `static/css/style.css`
  - Sleek modern dark UI theme with typography, subtle gradients, and clean card containers.
  - Custom subtitle track styling for the video player.
- [ ] **Step 4.3**: Implement `static/js/app.js`
  - Upload handling with progress tracking.
  - Polling / SSE connection for transcription milestones.
  - Dynamic loading of the generated subtitle track onto the `<video>` element.
  - Download trigger for `.srt` file.

---

### Phase 5: End-to-End Testing & Verification
- [ ] **Step 5.1**: Start the local server (`uvicorn app:app --reload`).
- [ ] **Step 5.2**: Test with a sample MP4 video.
- [ ] **Step 5.3**: Verify subtitle synchronization, text accuracy, and file download in `.srt` format.
- [ ] **Step 5.4**: Add error handling for corrupted files, audio-less videos, or long transcripts.
