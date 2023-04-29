import json
import aioredis
import redis
import os
import asyncio
from typing import Any, Dict, Optional

class RedisQueueManager:
    def __init__(self, redis_url: Optional[str] = None):
        redis_env = os.getenv('REDIS_URL', f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT_NUMBER')}")
        self.redis_url = redis_url or redis_env
        self.redis = redis.StrictRedis.from_url(self.redis_url)
        self.async_redis = None
        self.async_redis_lock = asyncio.Lock()

    def enqueue(self, queue_name: str, payload: Dict) -> None:
        self.redis.rpush(queue_name, json.dumps(payload))

    def dequeue(self, queue_name: str) -> Optional[Dict]:
        payload = self.redis.lpop(queue_name)
        return json.loads(payload) if payload else None

    def blocking_dequeue(self, queue_name: str) -> Dict:
        _, payload = self.redis.blpop(queue_name)
        return json.loads(payload)
    
    async def get_async_redis(self):
        async with self.async_redis_lock:
            if self.async_redis is None:
                self.async_redis = await aioredis.create_redis_pool(self.redis_url)
            return self.async_redis
    
    async def stop(self):
        async_redis = await self.get_async_redis()
        async_redis.close()
        await async_redis.wait_closed()
    
    async def async_enqueue(self, queue_name: str, payload: Dict) -> None:
        async_redis = await self.get_async_redis()
        await async_redis.rpush(queue_name, json.dumps(payload))
        
    async def async_dequeue(self, queue_name: str) -> Optional[Dict]:
        async_redis = await self.get_async_redis()
        payload = await async_redis.lpop(queue_name)
        await asyncio.sleep(0.1) # this sucks, but async_blocking_dequeue doesn't seem to work
        return json.loads(payload) if payload else None

    async def async_blocking_dequeue(self, queue_name: str) -> Dict:
        async_redis = await self.get_async_redis()
        _, payload = await async_redis.blpop(queue_name)
        return json.loads(payload)

        
            