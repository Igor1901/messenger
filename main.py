import pathlib
import uuid
from typing import List

import aiofiles
from fastapi import Depends, FastAPI, WebSocket, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import HTTPConnection
from starlette.responses import FileResponse
from starlette.websockets import WebSocketDisconnect

UPLOADS_DIR = pathlib.Path('./uploads')

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


app = FastAPI()
app.mount("/static/", StaticFiles(directory="./static/"))
app.mount("/uploads/", StaticFiles(directory="./uploads/"))


def get_connection_manager(request: HTTPConnection):
    return request.app.state.conection_manager


@app.on_event("startup")
async def application_startup():
    UPLOADS_DIR.mkdir(exist_ok=True)
    app.state.conection_manager = ConnectionManager()


@app.get("/")
async def get():
    return FileResponse("./static/index.html", media_type="text/html")


@app.post("/upload-file/{username}")
async def upload_file(username: str, file: UploadFile = File(...), manager: ConnectionManager = Depends(get_connection_manager)):
    file_id = uuid.uuid4()
    file_extensions = pathlib.Path(file.filename).suffixes
    filename = pathlib.Path(''.join((str(file_id), *file_extensions)))

    filepath = UPLOADS_DIR / filename
    async with aiofiles.open(filepath, 'wb') as new_file:
        await new_file.write(await file.read())

    message_id = str(uuid.uuid4())
    message_to_broadcast = {
        "id": message_id,
        "owner": username,
        "type": "upload",
        "content": str(filepath),
    }
    await manager.broadcast(message_to_broadcast)
    return {"id": message_id}


@app.websocket("/socket/{username}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    await manager.connect(websocket)
    async for message in websocket.iter_json():
        message_to_broadcast = {
            "id": str(uuid.uuid4()),
            "owner": username,
            "type": "text",
            "content": message["content"],
        }
        await manager.broadcast(message_to_broadcast)
