import json
import os
import sys
import traceback
import argparse
from typing import Any, Dict, Optional
from bot_redis import RedisQueueManager

class Step:
    def __init__(self, bot_name: str, step_name: str, queue_manager: Optional[Any] = None):
        self.bot_name = bot_name
        self.step_name = step_name
        self.queue_manager = queue_manager or RedisQueueManager()

        self.inbox = f"{bot_name}_{step_name}_inbox"
        self.outbox = f"{bot_name}_{step_name}_outbox"
        self.dlq = f"{bot_name}_{step_name}_dlq"

    def run(self, payload: Dict) -> Dict:
        raise NotImplementedError("Please implement the `process` method in your step subclass.")

    def listen(self) -> None:
        while True:
            payload = self.queue_manager.blocking_dequeue(self.inbox)
            try:
                result = self.process(payload)
                self.queue_manager.enqueue(self.outbox, result)
            except Exception as e:
                error_message = str(e)
                stacktrace = traceback.format_exc()
                self.queue_manager.enqueue(self.dlq, {"payload": payload, "error_message": error_message, "stacktrace": stacktrace})

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
            instance.run(payload)
        else:
            print(f'Listening on {instance.inbox}')
            instance.listen()


if __name__ == "__main__":
    Step.main()