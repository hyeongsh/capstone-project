from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn
from container import create_memory_manager
from cv_manager import CVManager
import asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

neuron_ws = None
video_ws = None

async def ws_send(ws: str, message: str):
	if ws == "neuron":
		if neuron_ws is not None:
			await neuron_ws.send_text(message)
	elif ws == "video-control":
		if video_ws is not None:
			await video_ws.send_text(message)

memory_manager = create_memory_manager()
cv = CVManager(memory_manager, send_callback=ws_send)

@app.get("/")
async def root():
	return FileResponse(Path("templates/index.html"))

@app.websocket("/neuron")
async def neuron_endpoint(ws: WebSocket):
	global neuron_ws
	await ws.accept()
	neuron_ws = ws
	await ws_send("neuron", "SpinalCord")
	# await ws_send("neuron", "Amygdala")
	try:
		while True:
			data = await ws.receive_text()
			await ws.send_text(f"Echo: {data}")
	except Exception as e:
		neuron_ws = None
		print("웹소켓 연결 끊김: ", e)

@app.websocket("/video-control")
async def video_endpoint(ws: WebSocket):
	global video_ws
	await ws.accept()
	video_ws = ws

	loop = asyncio.get_running_loop()
	loop.run_in_executor(None, cv.play_video, "static/video.mp4", loop)
	try:
		while True:
			data = await ws.receive_text()
			await ws.send_text(f"Echo: {data}")
	except Exception as e:
		video_ws = None
		print("웹소켓 연결 끊김: ", e)

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)