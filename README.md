# Civ-AI: Smart Road Intelligence System

[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js-000000?style=flat-square&logo=next.js)](https://nextjs.org)
[![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-FF2D20?style=flat-square&logo=ultralytics)](https://github.com/ultralytics/ultralytics)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**Civ-AI** is a state-of-the-art, AI-driven road infrastructure intelligence system. It leverages computer vision to automate pothole detection, damage assessment, repair estimation, and reporting, helping municipalities and road authorities optimize maintenance workflows.

---

## 🚀 Key Capabilities

### 🛠 Unified Detection Pipeline
A single, robust endpoint (`/detect`) that intelligently handles both **Image** and **Video** uploads. The system automatically detects file types and routes them through the appropriate processing engine.

### 📹 Video Intelligence
*   **SSIM-Based Deduplication**: Advanced frame extraction using Structural Similarity Index (SSIM) to filter out redundant frames and optimize processing speed.
*   **Centroid Tracking**: Intelligent pothole tracking across frames to prevent duplicate counts and ensure accurate reporting.
*   **Processed Output**: Generates an annotated video with detection overlays for visual verification.

### 📊 Automated PDF Reporting
Generates professional, data-rich PDF reports automatically after video analysis.
*   **Statistical Breakdown**: Total potholes, severity distribution (Small, Medium, Large).
*   **Repair Estimation**: Automated cost and labor estimation based on detected damage area.
*   **Visual Evidence**: High-resolution sample images of detected potholes included in the report.

### 🏗 Modern UI/UX
*   **Glassmorphic Design**: A premium Next.js dashboard with a sleek dark theme.
*   **Real-time Visualization**: Interactive charts and data visualizations for infrastructure health.

---

## 🛠 Tech Stack

### Backend (Intelligence Layer)
- **FastAPI**: High-performance Python API framework.
- **YOLOv8**: Real-time object detection model for infrastructure damage.
- **OpenCV & Scikit-Image**: Image processing and similarity analysis.
- **ReportLab**: PDF document generation engine.

### Frontend (User Interface)
- **Next.js (App Router)**: Modern React framework.
- **Tailwind CSS**: Utility-first styling for a sleek, responsive UI.
- **Framer Motion**: Smooth micro-animations and transitions.
- **Axios**: Robust API communication.

---

## 🏁 Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python run.py
```
*API will be available at `http://localhost:8000`*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*UI will be available at `http://localhost:3000`*

---

## 🔌 API Reference

### Unified Detection
`POST /detect`

Handles both images and videos. Upload a file as `multipart/form-data`.

**Request:**
```bash
curl -X POST http://localhost:8000/detect \
  -F "file=@road_data.mp4"
```

**Response (Video):**
```json
{
  "total_potholes": 12,
  "total_cost": 2150.50,
  "severity_distribution": {
    "small": 5,
    "medium": 4,
    "large": 3
  },
  "processed_url": "/output/output_video.mp4",
  "report_url": "/output/reports/report_20240420_123456.pdf"
}
```

---

## 📐 Severity & Estimation Logic

| Severity | Area (sq m) | Cost/m² | Workers | Time (hrs) |
| :--- | :--- | :--- | :--- | :--- |
| **Small** | < 0.5 | $150 | 1 | 2 |
| **Medium** | 0.5 - 2.0 | $120 | 2 | 4 |
| **Large** | > 2.0 | $100 | 4 | 8 |

---

## 📁 Project Structure

```text
civ-ai/
├── frontend/           # Next.js Application
│   ├── app/            # App Router pages
│   ├── components/     # UI Component library
│   └── services/       # API integration layer
│
├── backend/            # FastAPI Application
│   ├── app/
│   │   ├── routes/     # Detection & Video endpoints
│   │   ├── services/   # AI, Tracking, and PDF logic
│   │   └── utils/      # General utilities
│   ├── output/         # Processed artifacts (Videos, Reports)
│   └── models/         # Pre-trained YOLOv8 models
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.