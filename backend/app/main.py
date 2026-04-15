import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import detect

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Civ-AI Backend starting up...")
    yield
    logger.info("Civ-AI Backend shutting down...")


app = FastAPI(
    title="Civ-AI API",
    description="AI-Driven Road Infrastructure Intelligence System",
    version="1.0.0",
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


@app.get("/")
async def root():
    return {"message": "Civ-AI API - Road Infrastructure Intelligence"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
