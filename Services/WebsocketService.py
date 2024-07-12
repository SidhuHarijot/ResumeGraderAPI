from fastapi import WebSocket
from typing import List


class WebsocketService:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def send_json(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def send_bytes(self, message: bytes, websocket: WebSocket):
        await websocket.send_bytes(message)

    async def broadcast(self, message: str=None, json: dict=None, bytes: bytes=None):
        for connection in self.active_connections:
            if message:
                await connection.send_text(message)
            if json:
                await connection.send_json(json)
            if bytes:
                await connection.send_bytes(bytes)
