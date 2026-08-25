import redis
import os
import sys

from dotenv import load_dotenv

load_dotenv()

try:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("❌ Error: REDIS_URL environment variable not set")
        sys.exit(1)
    
    print(f"Connecting to Redis: {redis_url}")
    r = redis.from_url(redis_url)
    r.ping()
    
    r.flushdb()
    print("✅ Cache flushed successfully!")
    
except Exception as e:
    print(f"❌ Error flushing cache: {e}")
    sys.exit(1)
