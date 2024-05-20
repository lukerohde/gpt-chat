import asyncio
import glob
import os
import time
import yaml
import argparse
from typing import Any, Dict, Optional, Type
from aiohttp import web, ClientSession
import signal

from bot_manager.bot_watcher import BotWatcher
from bot_manager.bot_redis import RedisQueueManager
from bot_manager.bot import Bot
from bot_manager.bot_server import BotServer

# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

class BotManager:
    def __init__(self, bot_path: str, step_path: str):
        self.bot_path = bot_path
        self.step_path = step_path
        self.debug = False
        
        self.queue_manager = RedisQueueManager()
        self.server = BotServer()
        self.bots = {}
        
        self.load_config()
        
        self.app_server = None

    def load_config(self):
        files = glob.glob(os.path.join(self.bot_path, "*.yaml"))
        for file in files:
            self.load_bot(file)

    def reload_bot(self, file):
        # TODO Figure out how to reload.  I think I have reload the whole bot
        self.server.stop()

        if self.bots.get(file, None):
            # stop the bot if it is being reloaded
            self.bots[file].stop()

        self.load_bot(file)
        self.server.restart()
    
    def load_bot(self, file):

        print(f"\nLoading Bot Config in {file}...")
        bot_config = {}
        with open(file, 'r') as f:
            bot_config = yaml.safe_load(f)

        bot_config['step_path'] = self.step_path
        bot = Bot(bot_config, queue_manager=self.queue_manager, bot_server = self.server)
        
        self.bots[file] = bot


    def process_async(self):
        t = [
            bot.process_async()
            for _, bot in self.bots.items()
        ]
        self.tasks = asyncio.gather(*t)
        return self.tasks
    
    def stop_bots(self):
        t = [
            bot.stop()
            for _, bot in self.bots.items()
        ]
        return asyncio.gather(*t)
    
    async def stop(self):
        await self.stop_bots()
        await self.tasks
        await self.queue_manager.stop()
        await self.server.stop()
    
    @classmethod
    def main(cls):
        
        parser = argparse.ArgumentParser(description="Bot manager")
        parser.add_argument('--bot_path', type=str, help='Path to folder of bot definition yaml files', required=False)
        parser.add_argument('--step_path', type=str, help='Path to step definition class files', required=False)
        parser.add_argument("--debug", action="store_true", help="Break into debug mode on failure.")

        args = parser.parse_args()
        bot_path = args.bot_path or os.path.join(os.getcwd(), "bot_config")
        step_path = args.step_path or os.path.join(os.getcwd(), "bot_config/steps")

        if not os.path.isdir(bot_path):
            parser.print_usage()
            print(f"The bot config path '{bot_path}' does not exist.")
            return 
        
        if not os.path.isdir(step_path):
            parser.print_usage()
            print(f"The step file path '{step_path}' does not exist.")
            return 

        loop = asyncio.get_event_loop()
        bm = None
        tasks = None
        server = None
        
        async def start_bot():
            nonlocal bm
            nonlocal tasks
            nonlocal server
            nonlocal loop
            nonlocal watcher

            bm = BotManager(bot_path, step_path)
            bm.debug = args.debug
            server = loop.create_task(bm.server.start())
            tasks = bm.process_async()
            watcher.resume()

        def stop_bot():
            loop.run_until_complete(bm.stop())
        

        def bot_reloader(file):
            nonlocal loop
            if bm:
                print(f"shutting down {len(asyncio.all_tasks(loop=loop))} tasks...")
                future = asyncio.run_coroutine_threadsafe(bm.stop(), loop)
                try:
                    future.result(timeout=10)  
                except concurrent.futures.TimeoutError:
                    print("Timeout waiting for bm.stop() to finish.")
                
                print(f"{len(asyncio.all_tasks(loop=loop))} tasks still running.")
                
            print(f"\n\nRELOADING AND RESTARTING...")
            asyncio.run_coroutine_threadsafe(start_bot(), loop)
            


        print(f'-- WATCHING {bot_path} --')
        watcher = BotWatcher()
        watcher.start_watching_path(bot_path, bot_reloader)
        #watcher.start_watching_path(step_path, bot_reloader)
        watcher.start()
        
        loop.create_task(start_bot())

        try:
            loop.run_forever()
        except KeyboardInterrupt:  # pragma: no branch
            pass
        finally:
            stop_bot()

if __name__ == "__main__":
    BotManager.main()