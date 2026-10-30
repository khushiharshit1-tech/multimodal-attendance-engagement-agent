
# Multimodal Attendance & Engagement Agent

A privacy-conscious classroom analytics dashboard designed to simplify attendance tracking and provide basic insights into classroom activity.

## Overview

Traditional attendance systems focus mainly on recording whether a student is present or absent. This project aims to go beyond basic attendance by combining computer vision, sustained person tracking, and classroom activity analysis.

The system processes uploaded classroom videos, detects people, tracks their presence over time, and allows the teacher to manually associate detected tracks with registered students.

## Key Features

- **Student Management:** Add and remove student records.
- **Person Detection:** Detect people in uploaded classroom videos using OpenCV.
- **Sustained Presence Tracking:** Track detected people across sampled video frames.
- **Manual Student Identification:** Assign detected person tracks to registered students.
- **Attendance Management:** Record student presence after identification.
- **Session History:** View previously processed classroom sessions.
- **CSV Export:** Export attendance records.
- **Activity Estimation:** Display a basic room-level visual activity estimate.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | Web framework and API development |
| OpenCV | Video processing and person detection |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Frontend functionality |
| Uvicorn | ASGI server |

## Project Structure

```text
multimodal-attendance-engagement-agent/
│
├── app/
│   ├── main.py
│   ├── static/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   ├── data/
│   └── __init__.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/khushiharshit1-tech/multimodal-attendance-engagement-agent.git
```

### 2. Open the project directory

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
7. View attendance and export session records as CSV.

## Current Limitations

- The system currently processes uploaded videos rather than providing live webcam tracking.
- Student identification is manual; the system does not perform facial recognition.
- Visual activity is a basic room-level movement estimate, not a direct measurement of student attention or learning.
- Audio activity analysis and AI-driven teaching suggestions are planned extensions, not currently implemented features.

## Future Scope

- Real-time classroom monitoring.
- Audio activity analysis.
- Improved multi-person tracking.
- Engagement trend visualization.
- AI-assisted teaching suggestions.
- Session analytics and reporting.
- Local database integration.

## Privacy

The application is designed around local video processing and local data storage. Use classroom recordings only with appropriate permission and consent. Avoid uploading personal student information or classroom recordings to public repositories.

## Author

**Khushi Jain**

GitHub: [@khushiharshit1-tech](https://github.com/khushiharshit1-tech)

---

*Developed as an academic project exploring computer vision, classroom analytics, and intelligent attendance management.*

