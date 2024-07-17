from fastapi import WebSocket
from typing import List
from .services import log, logError


class WebsocketService:
    def __init__(self):
        self.websocket = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.websocket = (websocket)

    async def disconnect(self, websocket: WebSocket):
        await websocket.close()
        self.websocket = None

    async def send_text(self, message: str):
        await self.websocket.send_text(message)
        log(f"Sent message", "WebsocketService.send_text")
    
    async def send_json(self, message: dict):
        await self.websocket.send_json(message)
        log(f"Sent message", "WebsocketService.send_json")
    
    async def send_bytes(self, message: bytes):
        await self.websocket.send_bytes(message)
