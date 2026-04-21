import uvicorn
import os
from dotenv import load_dotenv

# Load env in case it's run directly
load_dotenv()

if __name__ == "__main__":
    # Prioritize environment variables (like Render's $PORT)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger_msg = f"Starting Civ-AI Backend on {host}:{port}"
    print(logger_msg)
    
    uvicorn.run(
        "app.main:app", 
        host=host, 
        port=port, 
        reload=True, 
        reload_dirs=["app"], # Only watch 'app' folder, ignoring 'output'
        log_level="info"
    )
