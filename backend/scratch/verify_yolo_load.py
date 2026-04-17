import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path("c:/project folder/resume project/civic-ai/backend")
sys.path.append(str(backend_path))

try:
    from app.services.detection import get_model, get_model_path
    
    print(f"Target model path: {get_model_path()}")
    
    print("Loading model...")
    model = get_model()
    print("Model loaded successfully!")
    print(f"Model properties: {model.names}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
