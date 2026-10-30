from __future__ import annotations

import csv
import io
import json
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "records.json"

app = FastAPI(
    title="Multimodal Attendance & Engagement Agent",
    description="Offline-first classroom attendance and session activity prototype.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def load_db() -> dict[str, Any]:
    if DB_PATH.exists():
        try:
            return json.loads(DB_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"students": [], "sessions": []}


def save_db(db: dict[str, Any]) -> None:
    DB_PATH.write_text(json.dumps(db, indent=2), encoding="utf-8")


class StudentIn(BaseModel):
    name: str
    roll_number: str = ""


class AssignIn(BaseModel):
    session_id: str
    track_id: int
    student_id: str


@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "local/offline prototype"}


@app.get("/api/students")
def get_students():
    return load_db()["students"]


@app.post("/api/students")
def add_student(payload: StudentIn):
    name = payload.name.strip()
    if not name:
        raise HTTPException(400, "Student name is required.")
    db = load_db()
    student = {
        "id": f"stu_{int(time.time() * 1000)}",
        "name": name,
        "roll_number": payload.roll_number.strip(),
    }
    db["students"].append(student)
    save_db(db)
    return student


@app.delete("/api/students/{student_id}")
def delete_student(student_id: str):
    db = load_db()
    db["students"] = [s for s in db["students"] if s["id"] != student_id]
    save_db(db)
    return {"deleted": True}


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    x1, y1 = max(ax1, bx1), max(ay1, by1)
    x2, y2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    return inter / max(area_a + area_b - inter, 1)


def process_video(path: Path, min_presence_seconds: float = 3.0):
    """Detect people with OpenCV's built-in HOG detector and associate boxes over time."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError("Could not open this video. Try MP4, AVI, or MOV.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if total_frames else 0
    sample_every = max(1, int(fps * 1.0))  # sample approximately once per second

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    tracks: dict[int, dict[str, Any]] = {}
    next_id = 1
    frame_index = 0
    sampled = 0
    motion_values = []
    previous_gray = None

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index % sample_every == 0:
            sampled += 1
            height, width = frame.shape[:2]
            scale = min(1.0, 960 / max(width, height))
            if scale < 1:
                frame = cv2.resize(frame, (int(width * scale), int(height * scale)))
            boxes, weights = hog.detectMultiScale(
                frame, winStride=(8, 8), padding=(8, 8), scale=1.05
            )
            detections = []
            for (x, y, w, h), weight in zip(boxes, weights):
                if float(weight) >= 0.25:
                    detections.append((int(x), int(y), int(x + w), int(y + h)))

            # Greedy IoU association keeps IDs stable for adjacent sampled frames.
            unmatched = set(tracks.keys())
            for box in detections:
                best_id, best_score = None, 0.15
                for tid in list(unmatched):
                    score = iou(box, tracks[tid]["last_box"])
                    if score > best_score:
                        best_id, best_score = tid, score
                timestamp = frame_index / fps
                if best_id is None:
                    tid = next_id
                    next_id += 1
                    tracks[tid] = {
                        "track_id": tid, "first_seen": timestamp,
                        "last_seen": timestamp, "last_box": box,
                        "detections": 1, "samples": [timestamp],
                    }
                else:
                    tid = best_id
                    unmatched.discard(tid)
                    tracks[tid]["last_seen"] = timestamp
                    tracks[tid]["last_box"] = box
                    tracks[tid]["detections"] += 1
                    tracks[tid]["samples"].append(timestamp)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if previous_gray is not None and previous_gray.shape == gray.shape:
                motion_values.append(float(cv2.absdiff(gray, previous_gray).mean()))
            previous_gray = gray
        frame_index += 1

    cap.release()
    results = []
    for tid, tr in tracks.items():
        observed = max(0.0, tr["last_seen"] - tr["first_seen"] + 1.0)
        if tr["detections"] >= 2 and observed >= min_presence_seconds:
            results.append({
                "track_id": tid,
                "first_seen": round(tr["first_seen"], 1),
                "last_seen": round(tr["last_seen"], 1),
                "observed_seconds": round(observed, 1),
                "detections": tr["detections"],
                "sustained_presence": True,
            })
    average_motion = sum(motion_values) / len(motion_values) if motion_values else 0
    # This is only a coarse room-level visual activity proxy, not an attention score.
    activity_label = "Higher movement" if average_motion > 8 else "Lower movement"
    return {
        "duration_seconds": round(duration, 1),
        "sampled_frames": sampled,
        "tracks": results,
        "visual_activity": {
            "average_frame_change": round(average_motion, 2),
            "label": activity_label,
            "note": "A room-level motion estimate; it does not measure attention or learning.",
        },
    }


@app.post("/api/sessions/process")
async def upload_and_process(
    video: UploadFile = File(...),
    min_presence_seconds: float = Form(3.0),
):
    suffix = Path(video.filename or "class.mp4").suffix.lower()
    if suffix not in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
        raise HTTPException(400, "Supported formats: MP4, AVI, MOV, MKV, WEBM.")
    if min_presence_seconds < 1 or min_presence_seconds > 60:
        raise HTTPException(400, "Minimum presence must be between 1 and 60 seconds.")
    temp_path = UPLOAD_DIR / f"upload_{int(time.time() * 1000)}{suffix}"
    try:
        with temp_path.open("wb") as out:
            shutil.copyfileobj(video.file, out)
        result = process_video(temp_path, min_presence_seconds)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    finally:
        await video.close()
        if temp_path.exists():
            temp_path.unlink()

    session_id = f"session_{int(time.time() * 1000)}"
    session = {
        "id": session_id,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "filename": video.filename,
        **result,
        "assignments": {},
    }
    db = load_db()
    db["sessions"].insert(0, session)
    save_db(db)
    return session


@app.post("/api/sessions/assign")
def assign_track(payload: AssignIn):
    db = load_db()
    session = next((s for s in db["sessions"] if s["id"] == payload.session_id), None)
    if not session:
        raise HTTPException(404, "Session not found.")
    student = next((s for s in db["students"] if s["id"] == payload.student_id), None)
    if not student:
        raise HTTPException(404, "Student not found.")
    track = next((t for t in session["tracks"] if t["track_id"] == payload.track_id), None)
    if not track:
        raise HTTPException(404, "Track not found.")
    session["assignments"][str(payload.track_id)] = payload.student_id
    track["student_name"] = student["name"]
    track["roll_number"] = student["roll_number"]
    track["attendance_status"] = "Present"
    save_db(db)
    return {"assigned": True, "track": track}


@app.get("/api/sessions")
def get_sessions():
    return load_db()["sessions"]


@app.get("/api/sessions/{session_id}/attendance.csv")
def attendance_csv(session_id: str):
    db = load_db()
    session = next((s for s in db["sessions"] if s["id"] == session_id), None)
    if not session:
        raise HTTPException(404, "Session not found.")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student", "Roll Number", "Track ID", "First Seen (s)", "Last Seen (s)", "Observed (s)", "Status"])
    for track in session["tracks"]:
        sid = session["assignments"].get(str(track["track_id"]))
        student = next((s for s in db["students"] if s["id"] == sid), None)
        writer.writerow([
            student["name"] if student else "Unidentified",
            student["roll_number"] if student else "",
            track["track_id"], track["first_seen"], track["last_seen"],
            track["observed_seconds"], "Present" if student else "Needs identification",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="attendance_{session_id}.csv"'},
    )


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    db = load_db()
    session = next((s for s in db["sessions"] if s["id"] == session_id), None)
    if not session:
        raise HTTPException(404, "Session not found.")
    return session
