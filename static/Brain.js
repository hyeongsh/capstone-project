class Brain {
	constructor(scene) {
		this.scene = scene;
		this.brain = null;
		this.glassMaterial = null;
	}

	async load() {
		this.brain = await BABYLON.SceneLoader.ImportMeshAsync(
			"",
			"./static/models/",
			"brain.glb",
			this.scene
		);
		// console.log("불러온 mesh 개수:", this.brain.meshes.length);
		// this.brain.meshes.forEach((mesh) => {
		// 	console.log("mesh 이름:", mesh.name);
		// });

		this.glassMaterial = new BABYLON.PBRMaterial("glass", this.scene);
		this.glassMaterial.alpha = 0.4;
		this.glassMaterial.metallic = 0.0;
		this.glassMaterial.roughness = 0.05;
		this.glassMaterial.indexOfRefraction = 1.5;
		this.glassMaterial.subSurface.isRefractionEnabled = true;
		this.glassMaterial.subSurface.refractionIntensity = 0.98;
		this.glassMaterial.subSurface.tintColor = new BABYLON.Color3(0, 0, 0);
	
		this.brain.meshes.forEach((mesh) => {
			if (mesh instanceof BABYLON.Mesh) {
				mesh.material = this.glassMaterial;
				mesh.scaling = new BABYLON.Vector3(1, 1, 1);
				mesh.position = new BABYLON.Vector3(0, 0, 0);
			}
		})
	}
}

export default Brain;
