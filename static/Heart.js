
class Heart {
	constructor(scene) {
		this.scene = scene;
		this.heart = null;
		this.glassMaterial = null;
		this.scaleAnimation;
	}

	async load() {
		this.heart = await BABYLON.SceneLoader.ImportMeshAsync(
			"",
			"./models/",
			"heart.glb",
			this.scene
		);

		this.glassMaterial = new BABYLON.PBRMaterial("glass", this.scene);
		this.glassMaterial.alpha = 0.5;
		this.glassMaterial.metallic = 0.0;
		this.glassMaterial.roughness = 0.1;
		this.glassMaterial.indexOfRefraction = 1.5;
		this.glassMaterial.subSurface.isRefractionEnabled = true;
		this.glassMaterial.subSurface.refractionIntensity = 1;
		this.glassMaterial.subSurface.tintColor = new BABYLON.Color3(0.7, 0, 0);
	
		this.scaleAnimation = new BABYLON.Animation(
			"scaleBounce",
			"scaling",
			30,
			BABYLON.Animation.ANIMATIONTYPE_VECTOR3,
			BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE
		);

		const keys = [
			{ frame: 0, value: new BABYLON.Vector3(1, 1, 1) },
			{ frame: 30, value: new BABYLON.Vector3(1.03, 1.03, 1.03) },
			{ frame: 60, value: new BABYLON.Vector3(1, 1, 1) },
		]

		this.scaleAnimation.setKeys(keys);

		this.heart.meshes.forEach((mesh) => {
			if (mesh instanceof BABYLON.Mesh) {
				mesh.material = this.glassMaterial;
				mesh.scaling = new BABYLON.Vector3(1, 1, 1);
				mesh.position = new BABYLON.Vector3(0, 0, 0);
				mesh.animations = [this.scaleAnimation];
				this.scene.beginAnimation(mesh, 0, 60, true);
			}
		})
	}

	response() {
		
		const keys = [
			{ frame: 0, value: new BABYLON.Vector3(1, 1, 1) },
			{ frame: 8, value: new BABYLON.Vector3(1.07, 1.07, 1.07) },
			{ frame: 15, value: new BABYLON.Vector3(1, 1, 1) },
		]
		this.scaleAnimation.setKeys(keys);
		
		this.heart.meshes.forEach((mesh) => {
			this.scene.beginAnimation(mesh, 0, 15, true);
		});
		
		setTimeout(() => {
			const normalKeys = [
				{ frame: 0, value: new BABYLON.Vector3(1, 1, 1) },
				{ frame: 30, value: new BABYLON.Vector3(1.03, 1.03, 1.03) },
				{ frame: 60, value: new BABYLON.Vector3(1, 1, 1) },
			];
			this.scaleAnimation.setKeys(normalKeys);
			this.heart.meshes.forEach((mesh) => {
				this.scene.beginAnimation(mesh, 0, 60, true);
			});
		}, 5000);
	}

}

export default Heart;
