import asyncio
import glob
import importlib
import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Any, Dict, Optional, Type
from channels.layers import get_channel_layer
from aiohttp import web, ClientSession

from bot_step import Step
from bot_redis import RedisQueueManager

# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler



class Bot:
    def __init__(self, config_path: str, queue_manager: Optional[Any] = None, external_steps: Optional[Dict[str, Type[Step]]] = None):
        self.config_path = config_path
        self.queue_manager = queue_manager or RedisQueueManager()
        self.external_steps = external_steps or {}
        self.steps = []
        self.step_classes = {}
        self.debug = False
        #self.watcher = Observer()
        #event_handler = FileSystemEventHandler()
        #event_handler.on_modified = self.on_modified
        #self.watcher.schedule(event_handler, ".", recursive=True)
        #self.watcher.start()

        self.load_config()
        self.load_step_classes()
        self.instantiate_steps()
        self.pause_event = asyncio.Event()

        self.app_server = None

    async def receive_message(self, request):
        print(f"{request.scheme} {request.method} {request.path}")
        payload = await request.json()
        await self.queue_manager.async_enqueue(self.inbox, payload)
        return web.json_response({'status': 'ok'})


    def load_config(self) -> None:
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.inbox = f"{self.config['name']}_inbox"
        self.outbox = f"{self.config['name']}_outbox"
        

    def load_step_classes(self) -> None:
        step_files = glob.glob(os.path.join(os.path.dirname(self.config_path), "*.py"))
        for step_file in step_files:
            module_name = os.path.splitext(os.path.basename(step_file))[0]
            print(f'inspecting {module_name}')
            if module_name == "__init__":
                continue
            step_module = importlib.import_module(module_name)
            step_class = None
            for key, value in step_module.__dict__.items():
                if isinstance(value, type) and issubclass(value, Step) and value != Step:
                    step_class = value
                    break
            if step_class:
                print(f'Found {step_class}')
                self.step_classes[module_name] = step_class

    def reload_steps(self):
        for step_module in self.step_classes.values():
            importlib.reload(step_module)
        self.instantiate_steps()

    def instantiate_steps(self) -> None:
        self.steps = []
        for step_name in self.config["steps"]:
            step_class = self.step_classes.get(step_name) or self.external_steps.get(step_name)
            if step_class:
                print(f'Loading {step_class}')
                step_instance = step_class(self.config["name"], step_name, self.queue_manager)
                self.steps.append(step_instance)

    def process(self, payload: Dict) -> Dict:
        for step in self.steps:
            payload = step.process(payload)
        return payload
    
    async def process_async(self, payload: Dict) -> Dict:
        if payload:
            await self.queue_manager.async_enqueue(self.inbox, payload)
        
        await self.listen()
        print('process_async')


    async def send_message_to_django_app(self, reply):
        async with ClientSession() as session:
            url = 'http://app:3000/api/v1/message/'
        
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Token eca28c8b7c8ce3b426ef105ec3aef8af90f6aeda',
            }
            async with session.post(url, data=json.dumps(reply), headers=headers) as response:
                return await response.json()

    def send_status_update(self, outbox_name, payload):
        with open(f'{outbox_name}.json', 'w') as fp:
            json.dump(payload, fp, indent=2)
        
        print(f"{outbox_name} done.  Saved output to {outbox_name}.json.")

    async def listen(self) -> None:
        print('listening...')
        while True:
            
            async def handle_bot_inbox():
                while True:
                    payload = await self.queue_manager.async_dequeue(self.inbox)
                    if payload:    
                        await self.queue_manager.async_enqueue(self.steps[0].inbox, payload)

            async def handle_step_outbox(step: Step, next_step: Optional[Step]):
                while True:
                    payload = await self.queue_manager.async_dequeue(step.outbox)
                    if payload:
                        self.send_status_update(step.outbox, payload)

                        if next_step:
                            await self.queue_manager.async_enqueue(next_step.inbox, payload)
                        else:
                            await self.send_message_to_django_app(payload["reply"])

            async def handle_step_dlq(step: Step):
                while True:
                    payload = await self.queue_manager.async_dequeue(step.dlq)
                    
                    if payload:
                        self.send_status_update(step.outbox, payload)

                        print(f"Error in {step.step_name}.")
                        print(f"\n\n{payload['error_message']}")
                        
                    if self.debug:
                        print("Loading pdb debugger...")
                        
                        import pdb; pdb.set_trace()
                        #step.process(payload)

            tasks = [handle_bot_inbox()]

            for i, step in enumerate(self.steps):
                next_step = self.steps[i + 1] if i + 1 < len(self.steps) else None
                tasks.append(step.listen())
                tasks.append(handle_step_outbox(step, next_step))
                tasks.append(handle_step_dlq(step)) 


            await asyncio.gather(*tasks)

    async def stop(self):
        await self.queue_manager.stop()
        for step in self.steps:
            await step.stop()

    # async def watch(self):
    #     while True:
    #         event = await self.queue_manager.async_dequeue("bot_file_change")
    #         if event["type"] == "modified" and Path(event["path"]).suffix == ".py":
    #             self.reload_steps()
    #             self.pause_event.set()

    # def on_modified(self, event):
    #     if event.src_path.endswith(".py"):
    #         self.queue_manager.enqueue("bot_file_change", {
    #             "type": "modified",
    #             "path": str(Path(event.src_path)),
    #         })

    async def get_app_server(self, host: Optional[str] = '0.0.0.0', port: Optional[int] = '8001'):
        self.app_server = web.Application()
        self.app_server.router.add_post(f"/api/message/{self.config['name']}/", self.receive_message)

        server = web.AppRunner(self.app_server)
        await server.setup()
        site = web.TCPSite(server, host=host, port=port)
        await site.start()
        return site

    @classmethod
    def main(cls):
        
        parser = argparse.ArgumentParser(description="Bot manager")
        parser.add_argument('--bot_file', type=str, help='Path to bot definition yaml file', required=False)
        parser.add_argument('--payload', type=str, help='Path to json payload to process', required=False)
        parser.add_argument("--sync", action="store_true", help="Enable sync mode bypassing redis.")
        parser.add_argument("--debug", action="store_true", help="Break into debug mode on failure.")

        args = parser.parse_args()
        config_path = args.bot_file or os.path.join(os.path.dirname(__file__), "bot.yaml")
        
        if not os.path.isfile(config_path):
            parser.print_usage()
            print(f"The file '{config_path}' does not exist.")
            return 
        
        loop = asyncio.get_event_loop()
        bot = Bot(config_path)
        bot.debug = args.debug
                   
        payload = None
        if args.payload: 
            with open(args.payload, 'r') as f:
                payload = json.load(f)

            
        if args.sync:    
            bot.process(payload)
        else:
            try:
                tasks = [
                    bot.get_app_server(),
                    bot.process_async(payload)
                ]

                loop.run_until_complete(asyncio.gather(*tasks))
                #loop.run_until_complete(bot.get_app_server())
            except KeyboardInterrupt:
                print("Shutting down gracefully...")
            finally: 
                loop.run_until_complete(bot.stop())
                loop.close()
    

if __name__ == "__main__":
    Bot.main()