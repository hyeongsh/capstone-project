import Neuron from "./Neuron.js"

class BrainControl {
	constructor(scene, textBlock, heart) {
		this.scene = scene;
		this.textBlock = textBlock;
		this.heart = heart;
		this.actionImage = document.querySelector("#infoImage");
		this.textOverlay = document.querySelector(".text-overlay");
		this.infoTitle = document.querySelector("#infoTitle");
		this.infoDescription = document.querySelector("#infoDescription");
		this.currentFrame = null;
		this.afterwordsCallback = null;
		this.afterwordsMessages = [];

		// 웹소켓 설정
		this.ws = new WebSocket("ws://localhost:8000/neuron");
		this.ws.onopen = () => { console.log("Neuron WebSocket 연결됨"); }
		this.ws.onmessage = (event) => { 
			if (this.currentSpikeInterval) {
				this.currentSpikeInterval.stop();
			}
			this.spikeNeuron(event.data);
		}
		this.ws.onerror = (err) => { console.error("WebSocket 에러: ", err); }
		this.ws.onclose = () => { console.log("WebSocket 연결종료"); }
		
		// 뉴런 디자인 세팅
		this.glowLayer = new BABYLON.GlowLayer("glow", this.scene);
		this.tubeMat = new BABYLON.StandardMaterial("spikeTubeMat", this.scene);
		this.tubeMat.emissiveColor = new BABYLON.Color3(1, 0.2, 0.2);
		
		// 뉴런 맵 생성
		this.initNeurons();
		this.neurons = this.brainRegions.map(region => ({
			id: region.id,
			neuron: new Neuron(this.scene, region.position, this.glowLayer),
		}));
	}

	setScreen(screen) {
		this.screen = screen;
	}

	setAfterwordsCallback(callback, messages = []) {
		this.afterwordsCallback = callback;
		if (Array.isArray(messages)) {
			this.afterwordsMessages = messages;
		} else if (typeof messages === "string") {
			this.afterwordsMessages = [messages];
		} else {
			this.afterwordsMessages = [];
		}
	}

	spikeNeuron(action) {
		let path = [];
		let areaText = [];
		let timer;
		if (action == "detect") {
			path = this.detectPath;
			areaText = this.detectText;
			timer = 3000;
		} else if (action == "analysis") {
			path = this.analysisPath;
			areaText = this.analysisText;
			timer = 3000;
		} else if (action == "afterwords") {
			path = this.afterwordsPath;
			areaText = this.afterwordsText;
			timer = 10000;
		}
		let currentIndex = 0;
		const runPath = () => {
			const regionId = path[currentIndex];
			if (regionId == "SpinalCord") {
				this.heart.pulseBig(true);
			} else {
				this.heart.pulseBig(false);
			}
			const regionNeurons = this.neurons.filter(n => n.id === regionId);
			const printText = areaText.find(([area]) => area === regionId)?.[1];
			this.textBlock.text = printText;
			
			// brainAction 띄우기
			if (action == "analysis") {
				this.displayImage(currentIndex, "block");
			} else if (action == "afterwords") {
				const rawMessages = this.afterwordsMessages[currentIndex] ?? this.afterwordsMessages[0] ?? [];
				const messagesForStep = Array.isArray(rawMessages) || typeof rawMessages === "string"
					? rawMessages
					: [];
				if (typeof this.afterwordsCallback === "function") {
					this.afterwordsCallback(messagesForStep);
				}
			}

			const spike = setInterval(() => {
				const index1 = Math.floor(Math.random() * 21);
				const index2 = Math.floor(Math.random() * 21);
				const index3 = Math.floor(Math.random() * 21);
				const index4 = Math.floor(Math.random() * 21);
				const p1 = regionNeurons[index1].neuron.sphere.position;
				const p2 = regionNeurons[index2].neuron.sphere.position;
				const p3 = regionNeurons[index3].neuron.sphere.position;
				const p4 = regionNeurons[index4].neuron.sphere.position;
				const paths = [
					[p1, p2],
					[p2, p3],
					[p3, p4],
					[p4, p1],
					[p1, p3],
					[p2, p4]
				];
				paths.forEach((path, idx) => {
					const edgeTube = BABYLON.MeshBuilder.CreateTube(`spikeTube${idx}`, { 
						path: path,
						radius: 0.003,
						updatable: false
					}, this.scene);
					edgeTube.material = this.tubeMat;
					this.glowLayer.addIncludedOnlyMesh(edgeTube);
					setTimeout(() => {
						edgeTube.dispose();
					}, 500);
				})
				regionNeurons[index1].neuron.spikeNeuron();
				regionNeurons[index2].neuron.spikeNeuron();
				regionNeurons[index3].neuron.spikeNeuron();
				regionNeurons[index4].neuron.spikeNeuron();
			}, 300);
			this.currentSpikeInterval = {
				stop: () => {
					clearInterval(spike);
				}
			};
			setTimeout(() => {
				this.currentSpikeInterval.stop();
				if (action == "analysis") {
					this.displayImage(currentIndex, "none");
				}
				currentIndex++;
				if (currentIndex < path.length) {
					runPath();
				} else {
					this.currentSpikeInterval = null;
					if (action == "detect") {
						this.ws.send("analysis|" + this.currentFrame);
					} else if (action == "analysis") {
						this.ws.send("afterwords|" + this.currentFrame);
					} else if (action == "afterwords") {
						this.screen.play();
					}
				}
			}, timer);
		};
		runPath();
	}

	displayImage(index, turn) {
		this.actionImage.style.display = turn;
		if (turn == "block") {
			this.textOverlay.classList.add("show");
		} else {
			this.textOverlay.classList.remove("show");
		}
		switch (index) {
			case 0:
				this.actionImage.src = "static-nocache/images/png1.png";
				this.infoTitle.textContent = "비트맵";
				this.infoDescription.textContent = "설명입니다.";
				break ;
			case 1:
				this.actionImage.src = "static-nocache/images/png2.png";
				this.infoTitle.textContent = "노이즈 제거";
				this.infoDescription.textContent = "설명입니다.";
				break ;
			case 2:
				this.actionImage.src = "static-nocache/images/png3.png";
				this.infoTitle.textContent = "흑백 변환";
				this.infoDescription.textContent = "설명입니다.";
				break ;
			case 3:
				this.actionImage.src = "static-nocache/images/png4.png";
				this.infoTitle.textContent = "윤곽선 생성";
				this.infoDescription.textContent = "설명입니다.";
				break ;
			case 4:
				this.actionImage.src = "static-nocache/images/png5.png";
				this.infoTitle.textContent = "강조";
				this.infoDescription.textContent = "설명입니다.";
				break ;
		}
	}

	initNeurons() {
		this.gatewayRegions = [
			// 시상: 감각 정보를 대뇌 피질로 전달하는 중계소
			{ id: "Thalamus", position: [0, 0.65, -0.05], spread: { x: 0.1, y: 0.03, z: 0.03 } }, 
			// 후두엽: 시각 정보 처리 (V1~V5 시각 피질 포함) -> 나눌 예정
			{ id: "V1", position: [0, 0.5, 0.5], spread: { x: 0.2, y: 0.09, z: 0.09 } } , 
			{ id: "V2", position: [0, 0.5, 0.5], spread: { x: 0.2, y: 0.09, z: 0.09 } } , 
			{ id: "V4", position: [0, 0.5, 0.5], spread: { x: 0.2, y: 0.09, z: 0.09 } } , 
			// 해마: 기억 저장과 회상 (특히 장기 기억)
			{ id: "Hippocampus", position: [0, 0.45, 0.1], spread: { x: 0.02, y: 0.02, z: 0.02 } }, 
			// 편도체: 감정 처리, 특히 공포와 위협 감지
			{ id: "Amygdala", position: [0, 0.38, -0.15], spread: { x: 0.02, y: 0.02, z: 0.02 } }, 
			// 시상하부: 자율신경계, 내분비계 조절 (심박수, 체온 등)
			{ id: "Hypothalamus", position: [0, 0.5, -0.1], spread: { x: 0.05, y: 0.05, z: 0.05 } }, 
			// 척수: 근육으로 명령 전달
			{ id: "SpinalCord", position: [0, 0.15, 0.16], spread: { x: 0.02, y: 0.04, z: 0.01 } }, 
			// 전전두엽: 이성적 판단, 계획, 실행 통제 (고차원적 사고)
			{ id: "Prefrontal", position: [0, 0.75, -0.6], spread: { x: 0.08, y: 0.05, z: 0.05 } }, 
			// IT: 패턴 인식 
			{ id: "IT", position: [0.4, 0.5, 0.1], spread: { x: 0.03, y: 0.1, z: 0.3 } },
		];

		this.brainRegions = this.gatewayRegions.flatMap(region => {
			const [x, y, z] = region.position;
			const { x: spreadX, y: spreadY, z: spreadZ } = region.spread;
			const clones = Array.from({ length: 20 }, () => ({
				id: region.id,
				position: [
					x + (Math.random() * spreadX * 2 - spreadX),
					y + (Math.random() * spreadY * 2 - spreadY),
					z + (Math.random() * spreadZ * 2 - spreadZ),
				],
			}));
			return [region, ...clones];
		});

		this.detectPath = ["Thalamus", "Amygdala", "Hypothalamus", "SpinalCord"];
		this.analysisPath = ["V1", "V1", "V2", "V4", "IT"];
		this.afterwordsPath = ["IT", "Amygdala", "Prefrontal"];

		this.detectText = [
			["Thalamus", "Thalamus(시상)\n감각 정보 입력 및 처리"],
			["Amygdala", "Amygdala(편도체)\n위협 감지"],
			["Hypothalamus", "Hypothalamus(시상하부)\n자율신경계 조절, 심장박동 조절"],
			["SpinalCord", "SpinalCord(척수)\n근육(심장)으로 명령 전달"],
		];

		this.analysisText = [
			["V1", "V1(1차 시각피질)\n비트맵 처리"],
			["V1", "V1\n노이즈 제거"],
			["V2", "V2\n명함 처리"],
			["V4", "V4\n윤곽선 생성"],
			["IT", "Inferotemporal cortex(하측두피질)\n패턴 통합 및 의미 부여"],
		];

		this.afterwordsText = [
			["IT", "Inferotemporal cortex(하측두피질)\n시각 정보 종합, 객체 확정"],
			["Amygdala", "Amygdala(편도체)\n위협/안전/친근 여부 평가 -> 행동 결정"],
			["Prefrontal", "Prefrontal(전전두엽)\n전략적 계획 수립"],
		]
	}
}

export default BrainControl;
