class Screen {
	constructor(scene) {
		this.scene = scene;
		this.screen = BABYLON.MeshBuilder.CreatePlane("screen", { width: 3, height: 2 }, this.scene);
		this.screenBehind = BABYLON.MeshBuilder.CreatePlane("screenBehind", { width: 3, height: 2 }, this.scene);

		// 웹소켓 설정
		this.ws = new WebSocket("ws://localhost:8000/video-control");
		this.ws.onopen = () => { console.log("Video WebSocket 연결됨"); }
		this.ws.onmessage = (event) => { 
			if (event.data == "play") {
				this.play();
			} else if (event.data == "pause") {
				this.pause();
			} else {
				this.speedControl(parseFloat(event.data));
			}
		}
		this.ws.onerror = (err) => { console.error("WebSocket 에러: ", err); }
		this.ws.onclose = () => { console.log("WebSocket 연결종료"); }
	}

	load() {
		// 영상 텍스처 준비
		this.videoElement = document.querySelector("#brainVideo");
		const videoTexture = new BABYLON.VideoTexture(
			"video",
			this.videoElement,
			this.scene,
			true,   // generateMipMaps
			false,   // invertY
			BABYLON.VideoTexture.TRILINEAR_SAMPLINGMODE,
			{ autoUpdateTexture: true, autoPlay: true }
		);

		// 스크린
		const mat = new BABYLON.StandardMaterial("screenMat", this.scene);
		this.screen.position = new BABYLON.Vector3(-0.1, 0.7, -3);
		mat.diffuseTexture = videoTexture;
		mat.emissiveTexture = videoTexture;
		this.screen.material = mat;
		this.screen.rotation.y = Math.PI;

		const matBehind = new BABYLON.StandardMaterial("mat", this.scene);
		this.screenBehind.position = new BABYLON.Vector3(-0.1, 0.7, -3);
		this.screenBehind.material = matBehind;
		matBehind.diffuseColor = new BABYLON.Color3(1, 1, 1); // 흰색
		this.pause();
	}

	play() {
		this.videoElement.play();
	}

	pause() {
		this.videoElement.pause();
	}

	speedControl(speed) {
		this.videoElement.playbackRate = speed;
	}

}

export default Screen;