class Screen {
	constructor(scene) {
		this.scene = scene;
		this.screen = BABYLON.MeshBuilder.CreatePlane("screen", { width: 3, height: 2 }, this.scene);
		this.screenBehind = BABYLON.MeshBuilder.CreatePlane("screenBehind", { width: 3, height: 2 }, this.scene);
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