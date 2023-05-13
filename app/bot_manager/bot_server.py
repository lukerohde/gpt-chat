import os
from aiohttp import web, ClientSession
from typing import Any, Dict, Optional, Type

class BotServer:

    def __init__(self, host: Optional[str] = '0.0.0.0', port: Optional[int] = None):
        self.host = host 
        self.port = port or os.getenv('BOT_PORT', '3001')
        self.app_server = web.Application()  
        self.web = web   
        self.site = None   
        self.server = None

    def register_route(self, route: str, callback):
        self.app_server.router.add_post(route, callback)

    def display_routes(self):
        print("Registered routes:")
        for route in self.app_server.router.routes():
            print(f"- {route.method} {route.resource.canonical}")

    async def start(self):
        print(f"\nStarting bot server...")
        self.display_routes()
        self.server = web.AppRunner(self.app_server)
        await self.server.setup()
        self.site = web.TCPSite(self.server, host=self.host, port=self.port)
        await self.site.start()
        print(f"Server is listening on {self.host}:{self.port}")
        
        return self.site # this return value feels wonky but work??
    
    def stop(self):
        print("stopping server")
        self.server.cleanup()