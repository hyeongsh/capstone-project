import Brain from "./Brain.js"
import Camera from "./Camera.js";
import Screen from "./Screen.js";
import BrainControl from "./BrainControl.js"
import Heart from "./Heart.js"

const brainCanvas = document.querySelector("#brainCanvas");
const brainEngine = new BABYLON.Engine(brainCanvas, true);

const heartCanvas = document.querySelector("#heartCanvas");
const heartContext = heartCanvas.getContext("2d");

let brainControl, brainScreen;

const defaultSecretMessage = "숨겨진 메시지가 올라옵니다.";
let secretMessageTimers = [];
const SECRET_OWNER_TIMELINE = "timeline";
const SECRET_OWNER_AFTERWORDS = "afterwords";
let secretMessageOwner = null;
let activeTimelineKey = null;

const secretMessageTimeline = [
	{ start: 121, end: 123, message: "꿈 준비중.." },
	{ start: 124, end: 126, message: "꿈 준비중..." },
	{ start: 126, end: 127, message: "시각기억 호출" },
	{ start: 127, end: 128, message: "시각기억 호출(뱀)" },
	{ start: 128, end: 129, message: "시각기억 호출(뱀, 돼지코)" },
	{ start: 129, end: 130, message: "시각기억 호출(뱀, 돼지코, 여우)" },
	{ start: 130, end: 131, message: "시각기억 호출(뱀, 돼지코, 여우, 도시)" },
	{ start: 131, end: 132, message: "시각기억 호출(뱀, 돼지코, 여우, 도시, 용)" },
	{ start: 132, end: 134, message: "꿈 초기장면 생성" },
	{ start: 134, end: 136, message: "오늘 무서운 독사를 봤어" },
	{ start: 139, end: 140, message: "어제 다큐에서 본 여우 귀엽더라" },
	{ start: 142, end: 144, message: "영화 속에 나온 드래곤 좀 살벌하던데" },
	{ start: 146, end: 148, message: "돼지코뱀? 돼지 코라도 달렸나?" },
	{ start: 150, end: 152, message: "언제까지 아침마다 이 도시를 봐야 할까" },
	{ start: 152, end: 154, message: "괴물 좀 무섭게 생겼다" },
	{ start: 154, end: 156, message: "독도 있을 것 같아" },
	{ start: 156, end: 158, message: "움직이기만 해도 건물이 무너질 거 같은데" },
	{ start: 158, end: 160, message: "도망쳐도 소용 없지 않을까" },
	{ start: 160, end: 163, message: "거 봐, 저렇게 독을 쏠 거 같았어" },
	{ start: 164, end: 165, message: "건물까지 부수면 정말 위험하겠다" },
	{ start: 166, end: 167, message: "그러면 출근도 안 하려나?" },
	{ start: 168, end: 170, message: "나가면 죽을 것 같아. 화가 많이 났어" },
	{ start: 171, end: 174, message: "포효하는 것만으로 건물이 무너지는 거 아냐?" },
	{ start: 175, end: 178, message: "브레스도 마구잡이로 쏠 거 같아" },
	{ start: 179, end: 182, message: "이러면 누군가 막으러 와야 하는데" },
	{ start: 183, end: 186, message: "잘 모르겠지만 헬기가 올 거 같아" },
	{ start: 187, end: 190, message: "와서 분명 공격을 할 거야. 폭격을 조심해야 해" },
	{ start: 191, end: 194, message: "시간을 끌면 더 올지도 몰라. 겁을 주고 도망칠까" },
	{ start: 195, end: 198, message: "내가 헬기가 되면 더 빠르게 도망칠 수 있어" },
	{ start: 199, end: 202, message: "나 헬기 운전할 줄 몰라!!" },
	{ start: 203, end: 205, message: "터진다!" },
];

const clearSecretMessageTimers = () => {
	secretMessageTimers.forEach(clearTimeout);
	secretMessageTimers = [];
};

const normalizeSecretLines = (messages) => {
	if (Array.isArray(messages)) {
		const trimmed = messages
			.map(line => (line ?? "").toString().trim())
			.filter(Boolean);
		return trimmed.length ? trimmed : [defaultSecretMessage];
	}
	if (typeof messages === "string") {
		const temp = document.createElement("div");
		temp.innerHTML = messages;
		const listItems = Array.from(temp.querySelectorAll("li"));
		if (listItems.length) {
			const liLines = listItems
				.map(li => li.textContent.trim())
				.filter(Boolean);
			if (liLines.length) {
				return liLines;
			}
		}
		const raw = (temp.textContent ?? messages).split(/\r?\n/)
			.map(segment => segment.trim())
			.filter(Boolean);
		return raw.length ? raw : [defaultSecretMessage];
	}
	return [defaultSecretMessage];
};

const applySecretMessageWidth = (secretMessage, lines) => {
	if (!secretMessage || !Array.isArray(lines) || !lines.length) return;
	const maxLength = lines.reduce((len, line) => Math.max(len, line.length), 0);
	const widthScale = Math.min(1, maxLength / 16);
	const bubbleWidth = Math.min(500, 280 + widthScale * 280);
	secretMessage.style.setProperty("--secret-width", `${bubbleWidth}px`);
};

const getSecretElements = () => {
	const secretMessage = document.querySelector("#secretMessage");
	const secretText = document.querySelector("#secretText");
	if (!secretMessage || !secretText) return null;
	return { secretMessage, secretText };
};

const hideSecretMessageElement = () => {
	const elements = getSecretElements();
	if (!elements) return;
	const { secretMessage } = elements;
	secretMessage.classList.remove("show");
	secretMessage.style.removeProperty("--secret-duration");
};

function hideTimelineMessage() {
	if (secretMessageOwner === SECRET_OWNER_TIMELINE) {
		hideSecretMessageElement();
		secretMessageOwner = null;
	}
	activeTimelineKey = null;
}

function showTimelineMessage(lines) {
	const elements = getSecretElements();
	if (!elements) return;
	const { secretMessage, secretText } = elements;
	const safeLines = Array.isArray(lines) && lines.length ? lines : [defaultSecretMessage];
	applySecretMessageWidth(secretMessage, safeLines);
	clearSecretMessageTimers();
	secretMessage.classList.remove("show");
	secretMessage.style.removeProperty("--secret-duration");
	secretText.textContent = safeLines.join("\n");
	void secretMessage.offsetWidth;
	secretMessage.classList.add("show");
	secretMessageOwner = SECRET_OWNER_TIMELINE;
	activeTimelineKey = JSON.stringify(safeLines);
}

function setupSecretTimeline(videoElement, timeline) {
	if (!videoElement || !Array.isArray(timeline) || !timeline.length) return;
	const sortedTimeline = [...timeline].sort((a, b) => a.start - b.start);

	const evaluateTimeline = () => {
		const currentTime = videoElement.currentTime ?? 0;
		let foundIndex = -1;
		for (let i = 0; i < sortedTimeline.length; i++) {
			const entry = sortedTimeline[i];
			if (currentTime >= entry.start && currentTime < entry.end) {
				foundIndex = i;
				break;
			}
		}

		if (foundIndex === -1) {
			if (secretMessageOwner === SECRET_OWNER_TIMELINE) {
				hideTimelineMessage();
			}
			return;
		}

		const entryLines = normalizeSecretLines(sortedTimeline[foundIndex].message);
		const key = JSON.stringify(entryLines);

		if (secretMessageOwner && secretMessageOwner !== SECRET_OWNER_TIMELINE) {
			return;
		}

		if (secretMessageOwner !== SECRET_OWNER_TIMELINE || activeTimelineKey !== key) {
			showTimelineMessage(entryLines);
		}
	};

	videoElement.addEventListener("timeupdate", evaluateTimeline);
	videoElement.addEventListener("seeked", evaluateTimeline);
	videoElement.addEventListener("play", evaluateTimeline);
	evaluateTimeline();
}

const parseAfterwordsGroups = (rawText) => {
	const groups = [];
	let current = [];
	const lines = rawText.split(/\r?\n/);
	lines.forEach(line => {
		const trimmed = line.trim();
		if (!trimmed) return;
		if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
			if (current.length) {
				groups.push([...current]);
			}
			current = [trimmed];
			return;
		}
		current.push(trimmed);
	});
	if (current.length) {
		groups.push([...current]);
	}
	return groups.length ? groups : [[defaultSecretMessage]];
};

const loadAfterwordsMessages = async () => {
	try {
		const response = await fetch("static-nocache/data/afterward.txt", { cache: "no-cache" });
		if (!response.ok) {
			throw new Error(`Failed to load afterward.txt: ${response.status}`);
		}
		const text = await response.text();
		return parseAfterwordsGroups(text);
	} catch (error) {
		console.error("afterwords 메시지 로딩 실패", error);
		return [[defaultSecretMessage]];
	}
};

const triggerSecretMessage = (messages = defaultSecretMessage) => {
	const elements = getSecretElements();
	if (!elements) return;
	const { secretMessage, secretText } = elements;

	if (secretMessageOwner === SECRET_OWNER_TIMELINE) {
		hideTimelineMessage();
	}

	const lines = normalizeSecretLines(messages);
	applySecretMessageWidth(secretMessage, lines);

	secretMessageOwner = SECRET_OWNER_AFTERWORDS;
	activeTimelineKey = null;

	const totalDuration = 10000;
	const perLineDuration = Math.max(1200, Math.floor((totalDuration - 1000) / Math.max(lines.length, 1)));

	clearSecretMessageTimers();
	secretMessage.classList.remove("show");
	secretMessage.style.removeProperty("--secret-duration");

	const playLine = (lineIndex) => {
		if (lineIndex >= lines.length) {
			hideSecretMessageElement();
			secretMessageOwner = null;
			return;
		}

		const line = lines[lineIndex] ?? "";
		secretMessage.classList.remove("show");
		secretMessage.style.setProperty("--secret-duration", `${perLineDuration}ms`);
		void secretMessage.offsetWidth;
		secretText.textContent = line;
		secretMessage.classList.add("show");

		secretMessageTimers.push(setTimeout(() => {
			playLine(lineIndex + 1);
		}, perLineDuration));
	};

	playLine(0);
};

// true로 설정하면 그래픽이 더 부드럽게 렌더링됩니다.
const createScene = async function () {
	const brainScene = new BABYLON.Scene(brainEngine);
	
	// 배경색
	brainScene.clearColor = new BABYLON.Color4(0, 0, 0, 1);

	// 환경 텍스쳐 (반사 느낌)
	brainScene.environmentTexture = await BABYLON.CubeTexture.CreateFromPrefilteredData(
		"https://playground.babylonjs.com/textures/environment.env",
		brainScene
	);
	brainScene.environmentTexture.rotationY = BABYLON.Tools.ToRadians(270);  // y축 기준 90도 회전
	const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), brainScene);
	light.intensity = 1.0;

	// 카메라
	const brainCamera = new Camera(brainScene, new BABYLON.Vector3(0, 0.5, -1.5), Math.PI / 4);
	brainCamera.load();
	
	// 심전도 모델
	const heart = new Heart(heartCanvas, heartContext);
	
	// 텍스트 박스
	const advancedTextureBrain = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("brainUI", true, brainScene);
	const textBlock = new BABYLON.GUI.TextBlock();
	textBlock.left = "30%";
	textBlock.top = "30%";
	textBlock.color = "white";
	textBlock.fontSize = 15;
	textBlock.text = ""
	advancedTextureBrain.addControl(textBlock);
	
	// 뉴런
	const brainControl = new BrainControl(brainScene, textBlock, heart);
	
	// 뇌 모델
	const brain = new Brain(brainScene);
	brain.load();
	
	// 영상 스크린
	const brainScreen = new Screen(brainScene);
	brainScreen.load();

	brainControl.setScreen(brainScreen);
	brainScreen.setControl(brainControl);

	return { brainScene, brainControl, brainScreen };
}

Promise.all([createScene(), loadAfterwordsMessages()])
	.then(([{ brainScene, brainControl: bc, brainScreen: bs }, afterwordsGroups]) => {
		brainControl = bc;
		brainScreen = bs;
		if (brainScreen && typeof brainScreen.getVideoElement === "function") {
			setupSecretTimeline(brainScreen.getVideoElement(), secretMessageTimeline);
		}
		if (typeof brainControl.setAfterwordsCallback === "function") {
			brainControl.setAfterwordsCallback(triggerSecretMessage, afterwordsGroups);
		}
		if (typeof brainControl.setAfterwordsLoader === "function") {
			brainControl.setAfterwordsLoader(loadAfterwordsMessages);
		}
		brainEngine.runRenderLoop(() => {
			brainScene.render();
		});
	})
	.catch(error => {
		console.error("초기화 실패", error);
	});

window.addEventListener("resize", () => {
	brainEngine.resize();
});

document.addEventListener("DOMContentLoaded", () => {
	const pulseBtn = document.querySelector("#pulseBtn");

	pulseBtn.addEventListener("click", () => {
		console.log("시작 버튼 눌림");
		if (!brainScreen) {
			console.warn("Scene is not ready yet.");
			return;
		}
		brainScreen.start();
		if (typeof brainControl.spikeAlways === "function") {
			brainControl.spikeAlways();
		}
		pulseBtn.style.display = "none";
	})
})
