
# Multimodal Attendance & Engagement Agent

An offline-first classroom intelligence student project prototype. It demonstrates video-based person detection, sustained tracking, manual student identification, attendance management, and basic classroom activity estimation.

## Features

- Upload classroom recordings through the browser.
- Detect people using OpenCV's HOG person detector.
- Track detected people across sampled video frames.
- Filter tracks using a sustained-presence threshold.
- Manually assign detected tracks to registered students.
- Manage student records and attendance.
- View previous classroom sessions.
- Export attendance records as CSV.
- Display a basic room-level visual activity indicator.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | Web framework and API |
| OpenCV | Video processing and person detection |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Frontend functionality |
| Uvicorn | Application server |

## Project Structure

```text
multimodal-attendance-engagement-agent/
├── app/
│   ├── main.py
│   ├── __init__.py
│   ├── data/
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/khushiharshit1-tech/multimodal-attendance-engagement-agent.git
```

### 2. Open the project folder

```bash
cd multimodal-attendance-engagement-agent
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Start the application

```bash
uvicorn app.main:app --reload
```

### 7. Open the dashboard

Visit:

http://127.0.0.1:8000

## How It Works

1. Register students through the dashboard.
2. Upload a classroom video.
3. The system processes sampled video frames.
4. Detected people are tracked across frames.
5. Tracks meeting the sustained-presence threshold are displayed.
6. Manually assign detected tracks to registered students.
7. View attendance and export records as CSV.

## Current Limitations

- The system processes uploaded videos rather than live webcam footage.
- Student identification is manual; facial recognition is not used.
- Visual activity is a basic room-level movement estimate, not a direct measurement of attention or learning.
- Audio analysis and AI-driven teaching suggestions are planned extensions, not currently implemented features.
- Detection and tracking may be affected by occlusion, crowded rooms, and camera angles.

## Future Scope

- Real-time classroom monitoring.
- Audio activity analysis.
- Improved multi-person tracking.
- Engagement trend visualization.
- AI-assisted teaching suggestions.
- Session analytics and reporting.
- Local database integration.

## Privacy

The application is designed for local video processing and local data storage. Use classroom recordings only with appropriate permission and consent. Do not upload private student information or classroom recordings to a public repository.

## Author

**Khushi Jain**

GitHub: https://github.com/khushiharshit1-tech

---

Developed as an academic project exploring computer vision, classroom analytics, and intelligent attendance management.
