import cv2
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import json, urllib
import cv2  # OpenCV: 동영상/이미지 처리 라이브러리
import torch  # PyTorch: 딥러닝 프레임워크
import torchvision.models as models  # 사전학습된 모델 제공
import torchvision.transforms as transforms  # 이미지 전처리 도구
from PIL import Image  # 이미지 파일을 다루는 라이브러리
import json, urllib  # json: 데이터 처리, urllib: 인터넷에서 파일 다운로드
import asyncio

STATE_READ = 1
STATE_DETECT = 2
STATE_ANALYSIS = 3
STATE_AFTERWORDS = 4
STATE_WAIT = 5

class CVManager:
	def __init__(self, send):
		self.send = send
		# 1. 사전학습된 모델 로드
		self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
		self.model.eval()
		self.state = STATE_READ

	def play_video(self, video_file, loop):
		# 동영상 파일에서 프레임을 하나씩 읽어서 분류
		self.cap = cv2.VideoCapture(video_file)  # 동영상 파일 열기
		asyncio.run_coroutine_threadsafe(self.send("video-control", "play"), loop)

		frame_id = 0  # 프레임 번호 초기화
		while self.cap.isOpened():  # 동영상이 열려있는 동안 반복
			if self.state == STATE_READ:
				ret, frame = self.cap.read()  # 한 프레임 읽기
				self.cur_frame = frame
				if not ret:  # 더 이상 읽을 프레임이 없으면 종료
					break
				# if services.check_validate_object():
				# 	self.state = STATE_DETECT
				### 임시
				if frame_id >= 100:
					self.state = STATE_DETECT

				frame_id += 1  # 프레임 번호 증가
				if cv2.waitKey(10) & 0xFF == 27:
					break
			elif self.state == STATE_DETECT:
				# TODO: 프레임을 멈추고, 프론트에게 시간 주기

				# 웹소켓
				asyncio.run_coroutine_threadsafe(self.send("video-control", "pause"), loop)
				asyncio.run_coroutine_threadsafe(self.send("neuron", "detect"), loop)
				self.state = STATE_WAIT
			elif self.state == STATE_ANALYSIS:
				# TODO: 분석으로 이미지 파일 5단계 생성하고, 이미지 디렉터리에 저장해서, 웹소켓으로 분석 완료했다고 보내주기
				asyncio.run_coroutine_threadsafe(self.send("neuron", "analysis"), loop)
				self.state = STATE_WAIT
			elif self.state == STATE_AFTERWORDS:
				# TODO: 객체에 대한 로우 데이터 or 심볼릭 데이터를 보내는 상태 -> API 사용
				self.state = STATE_WAIT
		self.cap.release()

	def complete_detect(self):
		self.state = STATE_ANALYSIS

	def complete_analysis(self):
		self.state = STATE_AFTERWORDS

	def complete_afterwords(self):
		self.state = STATE_READ
