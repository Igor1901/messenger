from typing import Optional, List

from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import json
app = FastAPI()
app.mount("/static/", StaticFiles(directory="./static/"))



@app.get("/")
async def get():
    return RedirectResponse("/static/index.html")


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Optional[str] = Cookie(None),
    token: Optional[str] = Query(None),
):
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    item_id: str,
    q: Optional[int] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        message = json.dumps({"owner": cookie_or_token, "text": f"{cookie_or_token}: {data}"})
        await manager.broadcast(message)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
