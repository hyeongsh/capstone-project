from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn
import cv
import asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

async def ws_send(message: str):
	if neuron_ws is not None:
		await neuron_ws.send_text(message)

neuron_ws = None

@app.get("/static-nocache/{path:path}")
async def nocache_static(path: str):
    response = FileResponse(f"static/{path}")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

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
			loop = asyncio.get_running_loop()
			data_list = data.split('|')
			if data_list[0] == "analysis":
				loop.run_in_executor(None, cv.frame_detail, ws_send, loop, data_list[1])
			elif data_list[0] == "afterwords":
				result = await loop.run_in_executor(None, cv.send_afterwords, data_list[1])
				await ws_send("afterwords")
	except Exception as e:
		neuron_ws = None
		print("웹소켓 연결 끊김: ", e)

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)