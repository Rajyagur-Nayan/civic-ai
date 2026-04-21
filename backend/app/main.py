import logging
import matplotlib
matplotlib.use("Agg")
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import detect, video
from fastapi.staticfiles import StaticFiles
import os
import mimetypes
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Ensure .mp4 is correctly served for all browsers
mimetypes.add_type('video/mp4', '.mp4')

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


from pathlib import Path

# Base directory (backend root)
BASE_DIR = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Civ-AI Backend starting up... (YOLO model loaded globally)")
    yield
    logger.info("Civ-AI Backend shutting down...")


# Get version from .env (fallback to 1.0.0)
BACKEND_VERSION = os.getenv("PYTHON_VERSION", "1.0.0")

app = FastAPI(
    title="Civ-AI API",
    description="AI-Driven Road Infrastructure Intelligence System",
    version=BACKEND_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect.router, prefix="/detect", tags=["Detection"])
app.include_router(video.router, prefix="/detect/video", tags=["Video Detection"])

# Initialize base infrastructure directories
directories = [
    BASE_DIR / "uploads",
    BASE_DIR / "output",
    BASE_DIR / "temp"
]

for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured directory exists: {directory}")

# Mount static files for job results and artifacts
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


@app.get("/")
async def root():
    return {"message": "Civ-AI API - Road Infrastructure Intelligence"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
