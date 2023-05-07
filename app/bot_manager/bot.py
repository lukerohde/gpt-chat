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
from box import Box
from aiohttp import web, ClientSession


from bot_manager.bot_step import Step
from bot_manager.bot_redis import RedisQueueManager
from bot_manager.bot_server import BotServer

class Bot:
    def __init__(self, config: Dict[str, Any], queue_manager: Optional[Any] = None, bot_server: Optional[BotServer] = None):
        self.config = Box(config)
        self.queue_manager = queue_manager or RedisQueueManager()
        self.server = bot_server or BotServer()
        self.server.register_route(f"/api/message/{self.config.name}/", self.receive_message)
        self.steps = []
        self.step_classes = {}
        self.debug = False

        self.load_config()
        self.load_step_classes()
        self.instantiate_steps()
        self.pause_event = asyncio.Event()

        self.app_server = None

    async def receive_message(self, request):
        print(f"{request.scheme} {request.method} {request.path}")
        payload = await request.json()
        await self.queue_manager.async_enqueue(self.inbox, payload)
        return self.server.web.json_response({'status': 'ok'})
    
    def load_config(self) -> None:
        self.bot_name = self.config.name
        self.inbox = f"{self.config.name}_inbox"
        self.outbox = f"{self.config.name}_outbox"
        

    def load_step_classes(self) -> Dict[str, Type[Step]]:
        step_classes = {}
        step_files = glob.glob(os.path.join(self.config.step_path, "*.py"))

        for step_file in step_files:
            module_name = os.path.splitext(os.path.basename(step_file))[0]
            print(f'inspecting {module_name}')

            if module_name == "__init__":
                continue

            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, step_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find the Step subclass in the module
            for key, value in module.__dict__.items():
                if isinstance(value, type) and issubclass(value, Step) and value != Step:
                    step_class = value
                    print(f'Found {step_class}')
                    self.step_classes[step_class.__name__] = step_class
                    break

        return step_classes
    
    def instantiate_steps(self) -> None:
        self.steps = []
        for st in self.config.steps:
            step_name = st.get('class')
            step_class = self.step_classes.get(step_name)
            if step_class:
                print(f"Loading {step_class}")
                step_config = getattr(st, 'config', Box({}))
                step_instance = step_class(self.bot_name, step_name, self.queue_manager, step_config.to_dict())
                self.steps.append(step_instance)
            else:
                print(f'WARNING: No "{step_name}" class found!')

    def process(self, payload: Dict) -> Dict:
        for step in self.steps:
            payload = step.process(payload)
        return payload
    
    async def process_async(self, payload: Optional[Dict] = {}) -> Dict:
        if payload:
            await self.queue_manager.async_enqueue(self.inbox, payload)
        
        await self.listen()
        print('process_async')


    async def send_message_to_django_app(self, reply):
        async with ClientSession() as session:
            url = 'http://app:3000/api/v1/message/'
        
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Token {self.config.token}',
            }
            async with session.post(url, data=json.dumps(reply), headers=headers) as response:
                return await response.json()

    async def send_update(self, mailbox, payload):
        with open(f'{mailbox}.json', 'w') as fp:
            json.dump(payload, fp, indent=2)
        
        print(f"Saved {mailbox}.json.")

        if 'reply' in payload or 'draft' in payload:
            if 'reply' in payload:
                msg = payload['reply']
                msg['status'] = 'reply'
                del payload["reply"]
            else:
                msg = payload['draft']
                msg['status'] = 'draft'

            await self.send_message_to_django_app(msg)
            

    async def listen(self) -> None:
        while True:
            
            async def handle_bot_inbox():
                while True:
                    payload = await self.queue_manager.async_dequeue(self.inbox)
                    if payload: 
                        await self.send_update(self.inbox, payload) 
                        await self.queue_manager.async_enqueue(self.steps[0].inbox, payload)

            async def handle_step_outbox(step: Step, next_step: Optional[Step]):
                while True:
                    payload = await self.queue_manager.async_dequeue(step.outbox)
                    if payload:
                        await self.send_update(step.outbox, payload)
                        
                        if next_step:
                            await self.queue_manager.async_enqueue(next_step.inbox, payload)
                        

                            

            async def handle_step_dlq(step: Step):
                while True:
                    payload = await self.queue_manager.async_dequeue(step.dlq)
                    
                    if payload:
                        await self.send_update(step.outbox, payload)

                        print(f"Error in {step.step_name}.")
                        print(f"\n\n{payload['error_message']}")
                        
                        if self.debug:
                            print("Loading pdb debugger...")
                            
                            import pdb; pdb.set_trace()
                            step.process(payload)

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


    @classmethod
    def main(cls):
        
        parser = argparse.ArgumentParser(description="Bot manager")
        parser.add_argument('--bot_file', type=str, help='Path to bot definition yaml file', required=False)
        parser.add_argument('--step_path', type=str, help='Path to bot definition yaml file', required=False)
        parser.add_argument('--payload', type=str, help='Path to json payload to process', required=False)
        parser.add_argument("--sync", action="store_true", help="Enable sync mode bypassing redis.")
        parser.add_argument("--debug", action="store_true", help="Break into debug mode on failure.")

        args = parser.parse_args()
        config_path = args.bot_file or os.path.join(os.getcwd(), "bot_config", "bot.yaml")
        step_path = args.step_path or os.path.join(os.getcwd(), "bot_config")
        
        config = {}

        if not os.path.isfile(config_path):
            parser.print_usage()
            print(f"The file '{config_path}' does not exist.")
            return 
        else:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

        config['step_path']=step_path
        loop = asyncio.get_event_loop()
        
        bot = Bot(config)
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
                    bot.server.start(),
                    bot.process_async(payload)
                ]

                loop.run_until_complete(asyncio.gather(*tasks))
            except KeyboardInterrupt:
                print("Shutting down gracefully...")
            finally: 
                loop.run_until_complete(bot.stop())
                loop.close()
    

if __name__ == "__main__":
    Bot.main()