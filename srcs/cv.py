import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import torch
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as T
import asyncio
from pathlib import Path
import requests, base64, json
from dotenv import load_dotenv

load_dotenv()

# =========================
# 기본 설정
# =========================
class CFG:
	out_dir: str = "static/images"   # 약속된 저장 경로
	canny1: int = 80
	canny2: int = 160
	denoise_h: int = 7
	denoise_template: int = 7
	denoise_search: int = 21

cfg = CFG()

# =========================
# ResNet50 + Grad-CAM
# =========================

resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT).eval()
preprocess = T.Compose([
	T.Resize(256), T.CenterCrop(224), T.ToTensor(),
	T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

class ResNetCAM:
	def __init__(self, model):
		self.model = model
		self.grad = None; self.feat = None
		target = self.model.layer4[-1].conv3
		target.register_forward_hook(self._fh)
		target.register_full_backward_hook(self._bh)
	def _fh(self, m,i,o): self.feat = o.detach()
	def _bh(self, m,gi,go): self.grad = go[0].detach()
	def logits_probs(self, x):
		with torch.enable_grad():
			logits = self.model(x); probs = F.softmax(logits, dim=1)
		return logits, probs
	def cam(self, logits, class_idx):
		self.model.zero_grad(set_to_none=True)
		onehot = torch.zeros_like(logits); onehot[:, class_idx] = 1.0
		logits.backward(gradient=onehot, retain_graph=True)
		g = self.grad.mean(dim=(2,3), keepdim=True)
		cam = (g * self.feat).sum(dim=1, keepdim=True)
		cam = F.relu(cam)
		cam -= cam.amin(dim=(2,3), keepdim=True)
		cam /= cam.amax(dim=(2,3), keepdim=True).clamp_min(1e-6)
		return cam

cam_helper = ResNetCAM(resnet)
IMAGENET_CLASSES = requests.get(
	"https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
).text.splitlines()

@torch.no_grad()
def classify_with_cam(img_bgr: np.ndarray, topk: int = 5):
	img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)).convert("RGB")
	x = preprocess(img).unsqueeze(0)
	logits, probs = cam_helper.logits_probs(x)
	v, i = torch.topk(probs[0], min(topk, len(IMAGENET_CLASSES)))
	labels_topk = [IMAGENET_CLASSES[int(j)] for j in i]
	scores_topk = [float(s) for s in v]
	cam_small = cam_helper.cam(logits, int(i[0]))[0,0].cpu().numpy()
	return (labels_topk[0], scores_topk[0], cam_small, labels_topk, scores_topk)

# =========================
# frame_detail: CAM 기반 시각처리
# =========================
def frame_detail(send, loop, frame: str):
	print("frame_detail called")
	if frame not in ["detect_snake", "approach_snake", "tongue_snake"]:
		return
		
	frame_bgr = cv2.imread("static/images/" + frame + ".png")  # 임시 입력

	out_dir = Path(cfg.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

	# 0. 원본 저장
	orig_path = out_dir / "original.png"
	cv2.imwrite(str(orig_path), frame_bgr)

	# 1. CAM Heatmap
	top1, top1_p, cam_small, labels5, scores5 = classify_with_cam(frame_bgr, topk=5)
	H,W = frame_bgr.shape[:2]
	cam = cv2.resize((cam_small*255).astype(np.uint8), (W,H))
	cam_color = cv2.applyColorMap(cam, cv2.COLORMAP_JET)
	heatmap = cv2.addWeighted(frame_bgr, 1.0, cam_color, 0.35, 0)
	cv2.imwrite(str(out_dir/"heatmap.png"), heatmap)

	# 2. 노이즈 제거
	den = cv2.fastNlMeansDenoisingColored(
		frame_bgr, None,
		h=cfg.denoise_h, hColor=cfg.denoise_h,
		templateWindowSize=cfg.denoise_template,
		searchWindowSize=cfg.denoise_search
	)
	cv2.imwrite(str(out_dir/"denoise.png"), den)

	# 3. 흑백
	gray = cv2.cvtColor(den, cv2.COLOR_BGR2GRAY)
	cv2.imwrite(str(out_dir/"gray.png"), gray)

	# 4. 엣지
	edges = cv2.Canny(gray, cfg.canny1, cfg.canny2)
	cv2.imwrite(str(out_dir/"edges.png"), edges)

	# 5. 윤곽선
	edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8), 1)
	edge_rgb = np.zeros_like(frame_bgr)
	edge_rgb[edges_closed > 0] = (0,255,0)
	outline = cv2.addWeighted(den, 1.0, edge_rgb, 0.8, 0)
	cv2.imwrite(str(out_dir/"outline.png"), outline)

	# === 웹소켓으로 상태 전송 (예시) ===
	asyncio.run_coroutine_threadsafe(send("analysis"), loop)

	# === 종료 후 afterward 호출 ===
	# afterward(str(out_dir / "original.png"))

# =========================
# afterward: Claude API 활용
# =========================
def afterward(img_path: str):
	img_path = "static/images/" + img_path + ".png"
		
	API_KEY = os.getenv("ANTHROPIC_API_KEY")
	print("APIKEY = ", API_KEY)
	url = "https://api.anthropic.com/v1/messages"

	img = cv2.imread(img_path)

	resized = cv2.resize(img, (800, 600))

	success, buf = cv2.imencode(".jpg", resized, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
		
	img_b64 = base64.b64encode(buf).decode("utf-8")

	headers = {
		"x-api-key": API_KEY,
		"anthropic-version": "2023-06-01",
		"content-type": "application/json"
	}

	data = {
		"model": "claude-3-opus-20240229",
		"max_tokens": 500,
		"messages": [
			{"role": "user", "content": [
				{"type": "text", "text": "이 이미지 속 뱀의 거리감, 색깔, 머리 모양, 독성 여부를 설명해줘."},
				{"type": "text", "text": "색깔, 모양을 보고 이게 어떤 동물인지 유추할 수 있을 정도로 자세한 정보를 보내줘. 키워드 형식으로"},
				{"type": "text", "text": "딕셔너리 형태로 설명을 나열해줘."},
				{"type": "text", "text": "모든 key와 value의 출력이 영어로 출력되게 해줘. value는 무조건 소문자로만 나오게 해줘"},
				{"type": "text", "text": "출력 순서는 Color : (최소 2개. , 콤마로 split), Animal : , Shape : ,"},
				{"type": "text", "text": "여기에서 모양은 색깔 외에 외적으로 보이는 모든 특징이 들어가면 될 거 같아. 예를 들면 머리 모양(뾰족머리, 둥근머리), 크기 등"},
				{"type": "text", "text": "그리고 나서 또 State : (Coiled, Flicking, Head Raised, Carwling), Distance : (close, far), Direction of Movement : (left, right), Speed : (slow, fast, medium) "},
				{"type": "text", "text": "동물 상태, 나와의 거리, 이동 방향, 이동 속도는 () 안에 예시들 중에서 선택해서 한 가지로만 얘기해줘"},
				{"type": "text", "text": "만약 동물이 가깝고 입을 열고 있으면 동물 상태를 (Flicking)이 나오도록 해줘."},
				{"type": "text", "text": "나와의 거리가 가까움이 되면 이동 속도를 멈춤 제외하고 slow, fast 중 골라줘"},
				{"type": "text", "text": "동물의 눈,코,입이 보이지 않고 동물의 외형 전체가 다 보이면 Distance를 far, 동물의 얼굴이 보이고 동물의 외형이 프레임에 의해 짤리면 Distance를 close라고 얘기해줘"},
				{"type": "text", "text": "State, Distance, Direction of Movement, Speed는 () 안에 예시들 중에서 선택해서 한 가지로만 얘기해줘"},
				{"type": "text", "text": "무조건 딕셔너리 형태로 key : value 이렇게 맞춰서 보내줘."},
				{"type": "text", "text": "그리고 무조건 명사 형태로 끝나는 키워드 형식으로 출력 되어야 해."},
				{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}}
			]}
		]
	}

	resp = requests.post(url, headers=headers, json=data)
	resp_json = resp.json()
	if "content" in resp_json:
		print("\nClaude 분석 결과:\n", resp_json["content"][0]["text"])
		return resp_json["content"][0]["text"]
	elif "error" in resp_json:
		print("API Error:", resp_json["error"]["message"])

		

# =========================
# 테스트 실행
# =========================
if __name__ == "__main__":
	frame_detail("detect_snake")
