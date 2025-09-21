import Neuron from "./Neuron.js"

class BrainControl {
	constructor(scene, textBlock, heart) {
		this.scene = scene;
		this.textBlock = textBlock;
		this.heart = heart;
		
		// 웹소켓 설정
		this.ws = new WebSocket("ws://localhost:8000/neuron");
		this.ws.onopen = () => { console.log("Neuron WebSocket 연결됨"); }
		this.ws.onmessage = (event) => { 
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

	spikeNeuron(regionId) {
		if (regionId === "SpinalCord") {
			this.heart.pulseBig(true);
		} else {
			this.heart.pulseBig(false);
		}
		// this.currentSpikeInterval.stop();
		if (regionId === "Temporal_lobe") {
			this.spikeNeuron("Temporal_lobe_2");
		}
		const regionNeurons = this.neurons.filter(n => n.id === regionId);
		const printText = this.areaText.find(([area]) => area === regionId)?.[1];
		this.textBlock.text = printText;
		return new Promise((resolve) => {
			const spike = setInterval(() => {
				const index1 = Math.floor(Math.random() * 21);
				const index2 = Math.floor(Math.random() * 21);
				const index3 = Math.floor(Math.random() * 21);
				const index4 = Math.floor(Math.random() * 21);
				const p1 = regionNeurons[index1].neuron.sphere.position
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
					this.heart.pulseBig(false);
					clearInterval(spike);
					resolve();
				}
			};
		});
	}

	initNeurons() {
		this.gatewayRegions = [
			// 시상: 감각 정보를 대뇌 피질로 전달하는 중계소
			{ id: "Thalamus", position: [0, 0.65, -0.05], spread: { x: 0.1, y: 0.03, z: 0.03 } }, 
			// 후두엽: 시각 정보 처리 (V1~V5 시각 피질 포함)
			{ id: "Occipital", position: [0, 0.5, 0.5], spread: { x: 0.2, y: 0.09, z: 0.09 } } , 
			// 해마: 기억 저장과 회상 (특히 장기 기억)
			{ id: "Hippocampus", position: [0, 0.45, 0.1], spread: { x: 0.02, y: 0.02, z: 0.02 } }, 
			// 편도체: 감정 처리, 특히 공포와 위협 감지
			{ id: "Amygdala", position: [0, 0.38, -0.15], spread: { x: 0.02, y: 0.02, z: 0.02 } }, 
			// 시상하부: 자율신경계, 내분비계 조절 (심박수, 체온 등)
			{ id: "Hypothalamus", position: [0, 0.5, -0.1], spread: { x: 0.05, y: 0.05, z: 0.05 } }, 
			// 연수: 심박수, 호흡 등 생명 유지 기능 조절
			{ id: "Medulla", position: [0, 0.3, 0.1], spread: { x: 0.02, y: 0.04, z: 0.01 } }, 
			// 척수: 근육으로 명령 전달
			{ id: "SpinalCord", position: [0, 0.15, 0.16], spread: { x: 0.02, y: 0.04, z: 0.01 } }, 
			// 게슈윈트: 언어 처리 및 시각 연결
			{ id: "Geschwind", position: [0.4, 0.75, 0.35], spread: { x: 0.02, y: 0.04, z: 0.04 } }, 
			// 두정엽: 시공간 감각, 위치 정보 처리 ("어디에 있는가")
			{ id: "Parietal", position: [0, 0.9, 0.1], spread: { x: 0.2, y: 0.09, z: 0.09 } }, 
			// 전전두엽: 이성적 판단, 계획, 실행 통제 (고차원적 사고)
			{ id: "Prefrontal", position: [0, 0.75, -0.6], spread: { x: 0.08, y: 0.05, z: 0.05 } }, 
			// 안와전두엽: 감정적 의사결정, 보상/처벌 판단
			{ id: "Orbitofrontal", position: [0, 0.53, -0.45], spread: { x: 0.08, y: 0.03, z: 0.1 } }, 
			// 측두엽: 소리 자극 분석
			{ id: "Temporal_lobe", position: [0.4, 0.5, 0.1], spread: { x: 0.03, y: 0.1, z: 0.3 } },
			{ id: "Temporal_lobe_2", position: [-0.4, 0.5, 0.1], spread: { x: 0.03, y: 0.1, z: 0.3 } },
			// 브로카: 실제로 행동할 동작 계획
			{ id: "Broca", position: [0.3, 0.65, -0.35], spread: {x: 0.05, y: 0.03, z: 0.03 } },
			// 운동피질: 운동 명령 계획
			{ id: "MotorCortex", position: [0, 0.9, -0.1], spread: {x: 0.2, y: 0.1, z: 0.05 } },
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

		this.areaText = [
			["Thalamus", "Thalamus(시상)\n감각 정보 입력 및 처리"],
			["Occipital", "Occipital(후두엽)\n시각 정보 처리 (형태, 색, 움직임 등)"],
			["Hippocampus", "Hippocampus(해마)\n기억 저장과 회상"],
			["Amygdala", "Amygdala(편도체)\n감정 처리, 특히 위협 감지"],
			["Hypothalamus", "Hypothalamus(시상하부)\n자율신경계 조절"],
			["Medulla", "Medulla(연수)\n심박수, 호흡 조절"],
			["Geschwind", "Geschwind(게슈윈드)\n언어 처리 및 시각 연결"],
			["Prefrontal", "Prefrontal(전전두엽)\n논리적 사고, 계획, 실행 제어"],
			["Orbitofrontal", "Orbitofrontal(안와전두엽)\n감정과 보상을 고려한 의사결정"],
			["Parietal", "Parietal(두정엽)\n위치 인식과 시공간 통합 정보 처리"],
			["SpinalCord", "SpinalCord(척수)\n근육으로 명령 전달"],
			["Temporal_lobe", "Temporal(측두엽)\n청각 정보 분석 및 기억, 감정과의 연동"],
			["Broca", "Broca(브로카영역)\n말을 구성하고 표현하기 위한 언어 운동 계획"],
			["MotorCortex", "MotorCortex(운동피질)\n말하거나 반응하기 위한 실제 움직임 제어"],
		]
	}
}

export default BrainControl;
