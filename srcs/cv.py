import asyncio
from pathlib import Path

def frame_detail(send, loop, frame: str):

	# 분석 이미지 생성 완료 신호 전송
	asyncio.run_coroutine_threadsafe(send("analysis"), loop)

def send_afterwords(frame: str):
	# main에서 호출하므로 반환하여 다음 작업으로 보내야 함.
	return frame
