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

const parseAfterwordsGroups = (rawText) => {
	const groups = [];
	let current = [];
	const lines = rawText.split(/\r?\n/);
	lines.forEach(line => {
		const trimmed = line.trim();
		if (!trimmed) {
			if (current.length) {
				groups.push([...current]);
				current = [];
			}
			return;
		}
		if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
			if (current.length) {
				groups.push([...current]);
			}
			current = [trimmed];
		} else {
			current.push(trimmed);
		}
	});
	if (current.length) {
		groups.push([...current]);
	}
	return groups.length ? groups : [[defaultSecretMessage]];
};

const loadAfterwordsMessages = async () => {
	try {
		const response = await fetch("static/data/afterwords.txt", { cache: "no-cache" });
		if (!response.ok) {
			throw new Error(`Failed to load afterwords.txt: ${response.status}`);
		}
		const text = await response.text();
		return parseAfterwordsGroups(text);
	} catch (error) {
		console.error("afterwords 메시지 로딩 실패", error);
		return [[defaultSecretMessage]];
	}
};

const triggerSecretMessage = (messages = defaultSecretMessage) => {
	const secretMessage = document.querySelector("#secretMessage");
	const secretText = document.querySelector("#secretText");
	if (!secretMessage || !secretText) return;

	const lines = normalizeSecretLines(messages);
	const perLineDuration = 1500; // 1초

	clearSecretMessageTimers();
	secretMessage.classList.remove("show");
	secretMessage.style.removeProperty("--secret-duration");

	const playLine = (lineIndex) => {
		if (lineIndex >= lines.length) {
			secretMessage.classList.remove("show");
			secretMessage.style.removeProperty("--secret-duration");
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
		if (typeof brainControl.setAfterwordsCallback === "function") {
			brainControl.setAfterwordsCallback(triggerSecretMessage, afterwordsGroups);
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
		pulseBtn.style.display = "none";
	})
})
