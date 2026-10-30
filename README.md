# Multimodal Attendance & Engagement Agent

An offline-first classroom intelligence **student project prototype**. It demonstrates video-based person detection, sustained track filtering, manual student identification, attendance export, and a basic room-level visual activity indicator.

## Features

- Upload a classroom recording from the browser.
- Detect people using OpenCV's built-in HOG person detector.
- Associate detections across sampled frames using bounding-box overlap (IoU).
- Keep tracks that meet a configurable sustained-presence threshold.
- Manually map a track to a registered student; no face recognition is used.
- Save timestamped session records locally and export attendance as CSV.
- Show a coarse frame-change/movement estimate for the room.

## Important limitations

This is a prototype, not a production attendance or engagement system.

- HOG detection is a classical computer-vision baseline. It can miss people, produce duplicate tracks, and struggle with occlusion, unusual camera angles, or crowded rooms.
- Track IDs are temporary visual tracks, **not student identities**. A teacher must manually assign each track.
- The activity indicator measures coarse frame-to-frame visual change. It does **not** infer attention, emotion, comprehension, or learning.
- This initial version does not yet implement audio analysis, per-student engagement scoring, live webcam processing, or automated teaching recommendations. Those are suitable future extensions.
- Validate attendance manually before using records for official purposes. Obtain appropriate consent and follow your institution's privacy rules before recording a class.

## Tech stack

- Python + FastAPI
- OpenCV + NumPy
- HTML, CSS, vanilla JavaScript
- JSON file storage (local prototype)

## Project structure

```text
multimodal-attendance-engagement-agent/
├── app/
│   ├── main.py
│   ├── data/
│   │   └── .gitkeep
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── requirements.txt
├── .gitignore
└── README.md
```

## Run locally

### 1. Install Python

Use Python 3.10 or newer. Check:

```bash
python --version
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the server

From the project root:

```bash
uvicorn app.main:app --reload
```

### 5. Open the dashboard

Visit <http://127.0.0.1:8000> in your browser.

API documentation is available at <http://127.0.0.1:8000/docs>.

## How to use

1. Add students to the Student Register.
2. Choose a classroom video and set the minimum sustained-presence duration.
3. Select **Analyze video** and wait for processing.
4. Review the detected tracks.
5. Manually assign each track to the correct student.
6. Export the attendance CSV.

Use a short, well-lit video with a stationary camera for the first test. For best results, choose a recording where people are visible from head to toe and are not heavily obstructed.

## GitHub upload

1. Create a new empty repository on GitHub.
2. Extract this project ZIP.
3. Open a terminal in the extracted project folder.
4. Run:

```bash
git init
git add .
git commit -m "Initial classroom attendance and engagement prototype"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL.

## Future improvements

- Add audio activity analysis using a local audio-processing pipeline.
- Improve tracking with a dedicated multi-object tracker.
- Add a live webcam mode.
- Add class-level interaction summaries and instructor-reviewed teaching suggestions.
- Add database storage, authentication, and configurable data-retention controls.
- Add tests and deployment configuration.
