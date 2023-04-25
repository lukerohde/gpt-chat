import json
import redis
import os 
from typing import Any, Dict, Optional

class RedisQueueManager:
    def __init__(self, redis_url: Optional[str] = None):
        redis_env = os.getenv('REDIS_URL', f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT_NUMBER')}")
        self.redis_url = redis_url or redis_env
        self.redis = redis.StrictRedis.from_url(self.redis_url)

    def enqueue(self, queue_name: str, payload: Dict) -> None:
        self.redis.rpush(queue_name, json.dumps(payload))

    def dequeue(self, queue_name: str) -> Optional[Dict]:
        payload = self.redis.lpop(queue_name)
        return json.loads(payload) if payload else None

    def blocking_dequeue(self, queue_name: str) -> Dict:
        _, payload = self.redis.blpop(queue_name)
        return json.loads(payload)