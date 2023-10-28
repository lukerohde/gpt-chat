import os
from aiohttp import web, ClientSession
from typing import Any, Dict, Optional, Type
import asyncio

class BotServer:

    def __init__(self, host: Optional[str] = '0.0.0.0', port: Optional[int] = None):
        self.host = host 
        self.port = port or os.getenv('BOT_PORT', '3001')
        self.app_server = web.Application()  
        self.web = web   
        self.site = None   
        self.server = None
        self.loop = None
        self.routes = {}

    def register_route(self, route: str, callback):
        self.routes[route] = callback

    def display_routes(self):
        print("Registered routes:")
        for route in self.app_server.router.routes():
            print(f"- {route.method} {route.resource.canonical}")

    async def start(self):
        print(f"\nStarting bot server...")
        self.loop = asyncio.get_event_loop()
        for route, callback in self.routes.items():
            self.app_server.router.add_post(route, callback)
        self.server = web.AppRunner(self.app_server)
        await self.server.setup()
        self.site = web.TCPSite(self.server, host=self.host, port=self.port)
        
        
        await self.site.start()
        print(f"Server is listening on {self.host}:{self.port}")
        
        
        self.display_routes()
        
        return self.site # this return value feels wonky but work??
    

    async def stop(self):

        await(self.server.shutdown())    
        await(self.server.cleanup())
        print(f"Server shutdown and cleaned up")
    
    # def stop(self):
    #     loop = asyncio.get_event_loop()
        
    #     print("stopping server")
    #     shutdown_future = asyncio.run_coroutine_threadsafe(self.server.shutdown(), loop)
    #     cleanup_future = asyncio.run_coroutine_threadsafe(self.server.cleanup(), loop)

    #     # Block until the coroutines are finished and get their results:
    #     shutdown_result = shutdown_future.result()
    #     print("server shutdown")
    #     cleanup_result = cleanup_future.result()
    #     print("server cleaned up")
        