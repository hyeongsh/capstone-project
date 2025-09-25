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

	// 영상 스크린
	const brainScreen = new Screen(brainScene);
	brainScreen.load();
	
	// 뇌 모델
	const brain = new Brain(brainScene);
	brain.load();

	// 심전도 모델
	const heart = new Heart(heartCanvas, heartContext);

	// 텍스트 박스
	const advancedTextureBrain = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("brainUI", true, brainScene);
	const textBlock = new BABYLON.GUI.TextBlock();
	textBlock.left = "30%";
	textBlock.top = "30%";
	textBlock.color = "white";
	textBlock.fontSize = 15;
	textBlock.text = "text to test"
	advancedTextureBrain.addControl(textBlock);

	// 뉴런
	const brainControl = new BrainControl(brainScene, textBlock, heart, null);

	return { brainScene, brainControl, brainScreen };
}

createScene().then(({ brainScene, brainControl: bc, brainScreen: bs }) => {
	brainControl = bc;
	brainScreen = bs;
	brainEngine.runRenderLoop(() => {
		brainScene.render();
	});
});

window.addEventListener("resize", () => {
	brainEngine.resize();
});

document.addEventListener("DOMContentLoaded", () => {
	const pulseBtn = document.querySelector("#pulseBtn");

	pulseBtn.addEventListener("click", () => {
		console.log("시작 버튼 눌림");
		brainScreen.start();
		pulseBtn.style.display = "none";
	})
})