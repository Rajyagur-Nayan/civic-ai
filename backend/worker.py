import os
import redis
from rq import Worker, Queue, Connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QUEUES = ['default']

def run_worker():
    """
    Connect to Redis and start the RQ worker.
    """
    print(f"[*] Starting RQ Worker connecting to {REDIS_URL}")
    try:
        conn = redis.from_url(REDIS_URL)
        with Connection(conn):
            worker = Worker(list(map(Queue, QUEUES)))
            worker.work()
    except Exception as e:
        print(f"[!] Worker Error: {e}")

if __name__ == '__main__':
    run_worker()
