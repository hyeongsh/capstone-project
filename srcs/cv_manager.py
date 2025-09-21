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


from service.memory_manager import MemoryManager

class CVManager:
	def __init__(self, db: MemoryManager, send_callback):
		self.db = db
		self.send_callback = send_callback
		# 1. 사전학습된 모델 로드
		self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
		self.model.eval()
		self.slow_until = 0

		# 2. ImageNet 클래스 인덱스 로드
		url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
		self.imagenet_classes = urllib.request.urlopen(url).read().decode("utf-8").splitlines()

		# 3. 이미지 전처리: 모델이 요구하는 입력 형태로 변환
		# - 크기 조정, 가운데 자르기, 텐서 변환, 정규화
		self.transform = transforms.Compose([
			transforms.Resize(256),  # 짧은 변 기준 256픽셀로 크기 조정
			transforms.CenterCrop(224),  # 중앙 224x224로 자르기
			transforms.ToTensor(),  # 이미지를 PyTorch 텐서로 변환
			transforms.Normalize(
				mean=[0.485, 0.456, 0.406],  # 각 채널별 평균값
				std=[0.229, 0.224, 0.225]    # 각 채널별 표준편차
			)
		])

	def play_video(self, video_file, loop):
		# 동영상 파일에서 프레임을 하나씩 읽어서 분류
		self.cap = cv2.VideoCapture(video_file)  # 동영상 파일 열기
		asyncio.run_coroutine_threadsafe(self.send_callback("video-control", "play"), loop)

		frame_id = 0  # 프레임 번호 초기화
		while self.cap.isOpened():  # 동영상이 열려있는 동안 반복
			ret, frame = self.cap.read()  # 한 프레임 읽기
			if not ret:  # 더 이상 읽을 프레임이 없으면 종료
				break
			
			# OpenCV 프레임(BGR)을 PIL 이미지(RGB)로 변환
			img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGB")
			img_t = self.transform(img).unsqueeze(0)  # 전처리 및 배치 차원 추가

			with torch.no_grad():  # 추론 시에는 기울기 계산 비활성화
				outputs = self.model(img_t)  # 모델에 입력
				probs = torch.nn.functional.softmax(outputs[0], dim=0)  # 확률로 변환

			# 가장 확률이 높은(top3) 클래스와 점수 추출
			top3 = torch.topk(probs, 3)
			top3_list = []
			for indice, value in zip(top3.indices, top3.values):
				label = self.imagenet_classes[indice]  # 클래스 이름
				score = value.item()  # 확률 점수
				# 프레임 번호, 예측 결과, 점수 출력
				top3_list.append({"label": label, "prob": score})

			frame_id += 1  # 프레임 번호 증가

			if self.db.validate_object(top3_list):
				self.slow_until = 10
				# 🔥 여기서 메시지 보내기
				if self.send_callback:
					# 동기 함수라 직접 await 못 함 → run_coroutine_threadsafe 사용
					asyncio.run_coroutine_threadsafe(
						self.send_callback("video-control", "0.1"), loop
					)
			if self.slow_until > 0:
				# 프레임 상단에 텍스트로 표시
				cv2.putText(frame, self.db.current_object, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
				self.slow_until -= 1
				if cv2.waitKey(500) & 0xFF == 27:
					break
			else:
				asyncio.run_coroutine_threadsafe(
					self.send_callback("video-control", "1"), loop
				)
				if cv2.waitKey(10) & 0xFF == 27:
					break
	
		self.cap.release()

