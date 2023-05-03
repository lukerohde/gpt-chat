import asyncio
import glob
import os
import sys
import yaml
import argparse
from typing import Any, Dict, Optional, Type
from aiohttp import web, ClientSession

from bot_redis import RedisQueueManager
from bot import Bot
from bot_server import BotServer

# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

class BotManager:
    def __init__(self, bot_path: str, step_path: str):
        self.bot_path = bot_path
        self.step_path = step_path
        self.debug = False
        
        self.queue_manager = RedisQueueManager()
        self.server = BotServer()
        self.bots = []
        
        self.load_config()
        
        self.app_server = None

    def load_config(self):
        files = glob.glob(os.path.join(self.bot_path, "*.yaml"))
        for file in files:
            print(f"\nLoading Bot Config in {file}...")
            bot_config = {}
            with open(file, 'r') as f:
                bot_config = yaml.safe_load(f)

            bot_config['step_path'] = self.step_path
            bot = Bot(bot_config, bot_server = self.server)
            self.bots.append(bot)
        

    def process_async(self):
        tasks = [
            bot.process_async()
            for bot in self.bots
        ]
        return tasks
    
    async def stop(self):
        for bot in self.bots:
            await bot.stop()

    
    @classmethod
    def main(cls):
        
        parser = argparse.ArgumentParser(description="Bot manager")
        parser.add_argument('--bot_path', type=str, help='Path to folder of bot definition yaml files', required=False)
        parser.add_argument('--step_path', type=str, help='Path to step definition class files', required=False)
        parser.add_argument("--debug", action="store_true", help="Break into debug mode on failure.")

        args = parser.parse_args()
        bot_path = args.bot_path or os.path.join(os.path.dirname(__file__), "bots")
        step_path = args.step_path or os.path.join(os.path.dirname(__file__), "steps")

        # if not os.path.isdir(bot_path):
        #     parser.print_usage()
        #     print(f"The bot config path '{bot_path}' does not exist.")
        #     return 
        
        # if not os.path.isdir(step_path):
        #     parser.print_usage()
        #     print(f"The step file path '{step_path}' does not exist.")
        #     return 

        loop = asyncio.get_event_loop()
        
        bm = BotManager(bot_path, step_path)
        bm.debug = args.debug
        
        try:
            loop.run_until_complete(asyncio.gather(*bm.process_async(), bm.server.start()))
        except KeyboardInterrupt:
            print("Shutting down gracefully...")
        finally: 
            loop.run_until_complete(bm.stop())
            loop.close()


if __name__ == "__main__":
    BotManager.main()