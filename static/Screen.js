class Screen {
	constructor(scene) {
		this.scene = scene;
		this.screen = BABYLON.MeshBuilder.CreatePlane("screen", { width: 3, height: 2 }, this.scene);
		this.screenBehind = BABYLON.MeshBuilder.CreatePlane("screenBehind", { width: 3, height: 2 }, this.scene);
		this.stopTime = [39, 61, 89, 207];
		// this.stopTime = [1, 2, 3, 207];
		// this.stopTime = [];
		this.stopIndex = 0;
		this.stop = true;
		this.timeCheckInterval = null;
		this.timerContainer = document.querySelector("#screenTimer");
		this.timeLabel = document.querySelector("#screenTime");
		this.statusLabel = document.querySelector("#screenStatus");
	}

	setControl(brainControl) {
		this.brainControl = brainControl;
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
		if (this.videoElement) {
			this.videoElement.addEventListener("timeupdate", () => this.updateTimerDisplay());
			this.videoElement.addEventListener("ended", () => this.handleEnded());
		}
		this.pause();
		this.updateTimerDisplay();
		this.updateStatus();
	}
	
	start() {
		this.stop = false;
		this.updateStatus();
		if (!this.videoElement) return;
		this.videoElement.play();
		this.timeCheck();
	}
	
	play() {
		this.stop = false;
		this.updateStatus();
		if (!this.videoElement) return;
		this.videoElement.play();
	}
	
	pause() {
		this.stop = true;
		this.updateStatus();
		if (!this.videoElement) return;
		this.videoElement.pause();
		this.updateTimerDisplay();
	}

	speedControl(speed) {
		this.videoElement.playbackRate = speed;
	}

	timeCheck() {
		if (this.timeCheckInterval) return;
		this.timeCheckInterval = setInterval(() => {
			if (!this.stop) {
				if (this.videoElement.currentTime >= this.stopTime[this.stopIndex]) {
					this.pause();
					switch (this.stopIndex) {
						case 0:
							this.brainControl.currentFrame = "detect_snake";
							break ;
						case 1:
							this.brainControl.currentFrame = "approach_snake";
							break ;
						case 2:
							this.brainControl.currentFrame = "tongue_snake";
							break ;
						case 3:
							return ;
					}
					this.brainControl.spikeNeuron("detect")
					this.stopIndex++;
				}
			}
		}, 120);

	}

	formatTime(seconds) {
		const total = Math.max(0, Math.floor(seconds || 0));
		const mins = String(Math.floor(total / 60)).padStart(2, "0");
		const secs = String(total % 60).padStart(2, "0");
		return `${mins}:${secs}`;
	}

	updateTimerDisplay() {
		if (!this.timeLabel || !this.videoElement) return;
		this.timeLabel.textContent = this.formatTime(this.videoElement.currentTime);
	}

	updateStatus() {
		if (this.statusLabel) {
			this.statusLabel.textContent = this.stop ? "PAUSED" : "PLAYING";
		}
		if (this.timerContainer) {
			this.timerContainer.classList.toggle("is-paused", this.stop);
		}
	}

	handleEnded() {
		this.stop = true;
		this.updateStatus();
		this.updateTimerDisplay();
	}

	getVideoElement() {
		return this.videoElement;
	}

}

export default Screen;
