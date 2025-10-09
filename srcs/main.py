from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn
import cv
import asyncio
import json
from typing import Any, Dict
from cognition import cognition

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

def _parse_afterwords_payload(result: str) -> Dict[str, Any]:
	if not result:
		return {}
	text = result.strip()
	if text.startswith("```") and text.endswith("```"):
		text = text.strip("`").strip()
	if text.startswith("python") or text.startswith("json"):
		text = text.split("\n", 1)[-1]
	try:
		return json.loads(text)
	except json.JSONDecodeError:
		try:
			return json.loads(text.replace("'", '"'))
		except json.JSONDecodeError:
			lines = text.splitlines()
			pairs: Dict[str, str] = {}
			for line in lines:
				if ":" not in line:
					continue
				key_raw, value_raw = line.split(":", 1)
				key = key_raw.strip().lower()
				value = value_raw.strip()
				if not key:
					continue
				pairs[key] = value
			mapping = {
				"color": "Color",
				"animal": "Animal",
				"shape": "Shape",
				"state": "State",
				"distance": "Distance",
				"direction of movement": "Direction of Movement",
				"speed": "Speed",
			}
			sample: Dict[str, Any] = {}
			for key, value in pairs.items():
				target_key = mapping.get(key)
				if not target_key:
					continue
				if key in {"color", "shape"}:
					items = [item.strip().lower() for item in value.split(",") if item.strip()]
					sample[target_key] = items
				else:
					sample[target_key] = value.strip().lower()
			return sample

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
				result = await loop.run_in_executor(None, cv.afterward, data_list[1])
				payload = _parse_afterwords_payload(result)
				await loop.run_in_executor(None, cognition, payload, "static/data/afterward.txt")
				await ws_send("afterwords")
	except Exception as e:
		neuron_ws = None
		print("웹소켓 연결 끊김: ", e)

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
