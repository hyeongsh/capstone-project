from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
	return FileResponse(Path("templates/index.html"))

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
	await ws.accept()
	await ws.send_text("서버에 연결되었습니다!")
	try:
		while True:
			data = await ws.receive_text()
			print("클라이언트로부터: ", data)
			await ws.send_text(f"Echo: {data}")
	except Exception as e:
		print("웹소켓 연결 끊김: ", e)

if __name__ == "__main__":
	uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)