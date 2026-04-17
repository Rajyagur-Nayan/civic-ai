import os
import torch
import logging
from ultralytics import YOLO
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_model():
    """
    Train a YOLOv8 model for Pothole Detection
    """
    # 1. Configuration
    # ----------------
    project_root = Path(__file__).parent
    dataset_config = project_root / "datasets" / "data.yaml"
    
    # Path to the base model weights
    # We'll check the backend folder first, then local, then download if needed
    model_weights = project_root / "backend" / "yolov8n.pt"
    if not model_weights.exists():
        model_weights = "yolov8n.pt" # Falls back to downloading from Ultralytics
    
    # Training Parameters
    params = {
        "data": str(dataset_config),
        "epochs": 100,           # Sufficient for fine-tuning
        "imgsz": 640,            # Standard YOLOv8 size
        "batch": 16,             # Adjust based on GPU memory
        "name": "pothole_model", # Name of the experiment
        "project": str(project_root / "runs"), # Explicitly set save directory
        "patience": 20,          # Early stopping patience
        "device": 0 if torch.cuda.is_available() else "cpu", # Use GPU if available
        "exist_ok": True         # Overwrite existing result folder
    }

    # 2. Check for Requirements
    # --------------------------
    if not dataset_config.exists():
        logger.error(f"Dataset config not found at {dataset_config}")
        logger.info("Please run prepare_dataset.py first or ensure the datasets folder exists.")
        return

    logger.info(f"Using device: {params['device']}")
    if params['device'] == "cpu":
        logger.warning("CUDA not found. Training on CPU will be VERY slow.")

    # 3. Load and Train
    # -----------------
    try:
        logger.info(f"Loading model: {model_weights}")
        model = YOLO(model_weights)

        logger.info("Starting training...")
        results = model.train(**params)
        
        logger.info("Training complete!")
        
        # 4. Save and Validate
        # --------------------
        # The best model is usually saved automatically in runs/detect/pothole_model/weights/best.pt
        best_model_path = project_root / "runs" / "detect" / params["name"] / "weights" / "best.pt"
        
        if best_model_path.exists():
            logger.info(f"Best model saved to: {best_model_path}")
            
            # Optional: Copy to backend for easy access by the API
            backend_model_dir = project_root / "backend" / "models"
            backend_model_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            target_path = backend_model_dir / "pothole_best.pt"
            shutil.copy(best_model_path, target_path)
            logger.info(f"Model also copied to API directory: {target_path}")
        
    except Exception as e:
        logger.error(f"An error occurred during training: {e}")

if __name__ == "__main__":
    train_model()
