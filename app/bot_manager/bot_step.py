import json
import argparse
import datetime
from typing import Any, Dict, Optional
from box import Box

from bot_manager.bot_redis import RedisQueueManager

class Step:
    def __init__(self, bot_name: str, step_name: str, config: Dict = {}):
        self.bot_name = bot_name
        self.step_name = step_name
        self.config = Box(config)

        self.inbox = f"{bot_name}_{step_name}_inbox"
        self.outbox = f"{bot_name}_{step_name}_outbox"
        self.dlq = f"{bot_name}_{step_name}_dlq"
        self._stop = False
    
    async def process(self, payload):
        raise NotImplementedError("Please implement the `process` method in your step subclass.")
                    
    def _chatml_message(self, role = str, name = str, content = str):
        content = content.replace("{date}", datetime.datetime.now().isoformat())
        
        return {
            "role": role, 
            "name": name, 
            "content": content
        }
    
    def stop(self):
        self._stop = True
        
    @property
    def activity(self):
        return self.step_name
    
    
    @classmethod
    def main(cls):
        
        parser = argparse.ArgumentParser(description="Bot script")
        parser.add_argument('--bot', type=str, help='Name of the bot', required=False)
        parser.add_argument('--step', type=str, help='Name of the step', required=False)
        parser.add_argument('--payload', type=str, help='Path to the JSON payload file.  If omitted, listen on "\{bot\}_\{step\}_inbox"', required=True)
        
        args = parser.parse_args()
        
        instance = cls(args.bot or "MyBot", args.step or "MyStep")  # Initialize the class

        if args.payload:
            with open(args.payload, 'r') as f:
                payload = json.load(f)
            print(json.dumps(instance.process(payload), indent=2))

if __name__ == "__main__":
    Step.main()