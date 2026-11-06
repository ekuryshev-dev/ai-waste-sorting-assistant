#webSocket work asynch. The server can maintain multiple
# connections and send messages to them without creating a
# separate HTTP request for each notification.

from fastapi import WebSocket


class AnalyticsConnectionManager:

    def __init__(self):
        self._connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast_update(self, region_code):
        for connection in self._connections.copy():
            try:
                await connection.send_json({
                    "event": "analytics_updated",
                    "region_code": region_code
                })
            except (RuntimeError, OSError):
                self.disconnect(connection)
