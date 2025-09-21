
class Camera {
	constructor(scene, position, turn) {
		this.scene = scene;
		this.camera = new BABYLON.ArcRotateCamera(
			"Camera",
			turn, // 좌우 각도
			Math.PI / 2, // 상하 각도
			4, // 거리
			position, // target
			this.scene
		);
	}
	
	load() {
		this.camera.minZ = 0.001;	// 가까운 것도 보이게
		this.camera.wheelPrecision = 200;
		this.camera.panningSensibility = 3000;  // 기본값은 1000 (← 꽤 민감함)
		this.camera.attachControl(this.canvas, true);
	}
}

export default Camera;
