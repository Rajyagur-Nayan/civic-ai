# Civ-AI: Smart Road Intelligence

AI-Driven Road Infrastructure Intelligence System for pothole detection, damage assessment, and repair planning.

## Features

- **Pothole Detection**: YOLOv8-based detection in images
- **Damage Assessment**: Calculate area, classify severity
- **Cost Estimation**: Workers, time, and repair costs
- **Modern UI**: Next.js frontend with dark theme
- **REST API**: FastAPI backend integration

## Tech Stack

### Frontend
- Next.js 16 (App Router)
- Tailwind CSS
- Framer Motion
- Axios

### Backend
- FastAPI
- Ultralytics YOLOv8
- OpenCV
- NumPy

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- API key for YOLOv8 model (optional for default model)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python run.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## API Usage

### POST /detect

```bash
curl -X POST http://localhost:8000/detect \
  -F "file=@road_image.jpg"
```

**Response:**
```json
{
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "area": 1.5,
      "severity": "medium",
      "workers": 2,
      "cost": 180.0,
      "time": 4
    }
  ],
  "total_potholes": 1,
  "total_cost": 180.0,
  "severity_distribution": {
    "small": 0,
    "medium": 1,
    "large": 0
  }
}
```

## Project Structure

```
civ-ai/
├── frontend/           # Next.js frontend
│   ├── app/
│   │   ├── page.tsx   # Landing page
│   │   ├── upload/   # Upload page
│   │   └── results/  # Results page
│   ├── components/    # Reusable components
│   └── services/     # API client
│
└── backend/           # FastAPI backend
    ├── app/
    │   ├── routes/  # API endpoints
    │   ├── services/# Business logic
    │   └── utils/  # Utilities
    └── models/       # YOLOv8 models
```

## Severity Classification

| Severity | Area (sq m) | Cost per sq m | Workers | Time (hrs) |
|----------|------------|---------------|---------|------------|
| Small    | < 0.5      | $150          | 1       | 2          |
| Medium   | 0.5 - 2.0  | $120          | 2       | 4          |
| Large   | > 2.0      | $100          | 4       | 8          |

## Testing

```bash
cd backend
python test_api.py
```

## Environment Variables

Backend (optional):
- `MODEL_PATH`: Custom YOLOv8 model path

Frontend connects to: `http://localhost:8000/detect`

## License

MIT