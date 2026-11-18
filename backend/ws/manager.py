import asyncio

class ConnectionManager:
    def __init__(self):
        self.clients = set()
        self.events = []
        self.lock = asyncio.Lock()

    async def connect(self, ws):
        await ws.accept()
        async with self.lock:
            for event in self.events:
                await ws.send_json(event)
            self.clients.add(ws)

    def disconnect(self, ws):
        self.clients.discard(ws)

    async def broadcast(self, event):
        async with self.lock:
            self.events.append(event)
            async def send(ws):
                try:
                    await asyncio.wait_for(ws.send_json(event), timeout=2)
                except Exception:
                    self.disconnect(ws)
            await asyncio.gather(*(send(ws) for ws in list(self.clients)))
