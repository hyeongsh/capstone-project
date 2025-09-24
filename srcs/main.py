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

	try:
		while True:
			data = await ws.receive_text()
			if data == "start":
				await ws_send("neuron", "SpinalCord")
				# 10초 후 메시지 보내는 태스크 실행
				async def delayed_send():
					await asyncio.sleep(10)
					try:
						await ws.send_text("Occipital")
					except Exception as e:
						print("지연 메시지 전송 실패:", e)
				asyncio.create_task(delayed_send())
	except Exception as e:
		neuron_ws = None
		print("웹소켓 연결 끊김: ", e)

@app.websocket("/video-control")
async def video_endpoint(ws: WebSocket):
	global video_ws
	await ws.accept()
	video_ws = ws

	try:
		while True:
			data = await ws.receive_text()
			if data == "start":
				loop = asyncio.get_running_loop()
				loop.run_in_executor(None, cv.play_video, "static/video.mp4", loop)
	except Exception as e:
		video_ws = None
		print("웹소켓 연결 끊김: ", e)

# from db import SessionLocal
# from crud import get_object_by_name
# from models import Object

# db = SessionLocal()
# object = get_object_by_name(db, "fox")
# print("name =", object.name)

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)