import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
print(f"Connecting to: {REDIS_URL}")

try:
    r = redis.from_url(REDIS_URL)
    r.ping()
    print("Success: Connected to Redis!")
except Exception as e:
    print(f"Error: Could not connect to Redis. {e}")
