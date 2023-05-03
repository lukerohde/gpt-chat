
from aiohttp import web, ClientSession
from typing import Any, Dict, Optional, Type

class BotServer:

    def __init__(self, host: Optional[str] = '0.0.0.0', port: Optional[int] = '8001'):
        self.host = host 
        self.port = port
        self.app_server = web.Application()  
        self.web = web      

    def register_route(self, route: str, callback):
        self.app_server.router.add_post(route, callback)

    def display_routes(self):
        print("Registered routes:")
        for route in self.app_server.router.routes():
            print(f"- {route.method} {route.resource.canonical}")

    async def start(self):
        print(f"\nStarting bot server...")
        self.display_routes()
        server = web.AppRunner(self.app_server)
        await server.setup()
        site = web.TCPSite(server, host=self.host, port=self.port)
        await site.start()
        print(f"Server is listening on {self.host}:{self.port}")
        
        return site # this return value feels wonky but work??