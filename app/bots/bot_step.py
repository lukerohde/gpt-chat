import json
import os
import sys
import traceback
import argparse
import asyncio
from typing import Any, Dict, Optional
from bot_redis import RedisQueueManager
from box import Box

class Step:
    def __init__(self, bot_name: str, step_name: str, queue_manager: Optional[Any] = None, config: Dict = {}):
        self.bot_name = bot_name
        self.step_name = step_name
        self.queue_manager = queue_manager or RedisQueueManager()
        self.config = Box(config)

        self.inbox = f"{bot_name}_{step_name}_inbox"
        self.outbox = f"{bot_name}_{step_name}_outbox"
        self.dlq = f"{bot_name}_{step_name}_dlq"
    
    async def process(self, payload):
        raise NotImplementedError("Please implement the `process` method in your step subclass.")

    async def listen(self) -> None:
        while True:
            payload = await self.queue_manager.async_dequeue(self.inbox)
            if payload:
                try:
                    result = await self.process(payload)
                    await self.queue_manager.async_enqueue(self.outbox, result)
                except Exception as e:
                    error_message = str(e)
                    stacktrace = traceback.format_exc()
                    await self.queue_manager.async_enqueue(self.dlq, {"payload": payload, "error_message": error_message, "stacktrace": stacktrace})
                    print(f"Error enqueued into {self.dlq}")
                    print(f"{error_message}")
                    

    async def stop(self):
        await self.queue_manager.stop()
    
    
    @classmethod
    def main(cls):
        
        parser = argparse.ArgumentParser(description="Bot script")
        parser.add_argument('--bot', type=str, help='Name of the bot', required=False)
        parser.add_argument('--step', type=str, help='Name of the step', required=False)
        parser.add_argument('--payload', type=str, help='Path to the JSON payload file.  If omitted, listen on "\{bot\}_\{step\}_inbox"', required=False)
        
        args = parser.parse_args()
        
        instance = cls(args.bot or "MyBot", args.step or "MyStep")  # Initialize the class

        if args.payload:
            with open(args.payload, 'r') as f:
                payload = json.load(f)
            instance.process(payload)
        else:
            print(f'Listening on {instance.inbox}')
            instance.listen()


if __name__ == "__main__":
    Step.main()