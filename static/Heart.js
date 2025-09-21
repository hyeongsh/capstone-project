
class Heart {
	constructor(canvas, context) {
		this.canvas = canvas
		this.context = context;
		this.width = canvas.width;
		this.height = canvas.height;

		this.baseline = this.height / 2;
		this.step = 7;
		this.points = [];
		this.speed = 2;
		this.pos = 0;
		this.frameCount = 0;
		// === 패턴 정의 ===
    	// 상대적인 y 값 배열 (baseline 기준)
		this.pattern = [
			0, 6, 0,              // P파
			-10, 40, -20, 0,      // QRS (Q 아래, R 위로, S 아래, baseline)
			0, 15, 0              // T파
		];

		let x = 0;
		while (x < this.width) {
			for (let i = 0; i < this.pattern.length && x < this.width; i++) {
				this.points.push({ x: x, y: this.baseline - this.pattern[i] });
				x += this.step;
			}
		}

		this.animate = this.animate.bind(this);
		requestAnimationFrame(this.animate);
	}

	load() {
		this.context.fillStyle = "black"; // 배경색
	    this.context.fillRect(0, 0, this.width, this.height); // 캔버스 전체 덮기
		
		this.context.beginPath();
		this.context.strokeStyle = "red";
		this.context.lineWidth = 2;
		this.context.moveTo(this.points[0].x, this.points[0].y);
		for (let i = 1; i <= this.pos; i++) {
			this.context.lineTo(this.points[i].x, this.points[i].y);
		}
		this.context.stroke();

		this.context.beginPath();
		this.context.arc(this.points[this.pos].x, this.points[this.pos].y, 3, 0, 2 * Math.PI, false);
		this.context.fillStyle = "red";
		this.context.fill();

		if (this.pos + 10 < this.points.length) {
			this.context.beginPath();
			this.context.strokeStyle = "red";
			this.context.lineWidth = 2;
			this.context.moveTo(this.points[this.pos + 10].x, this.points[this.pos + 10].y);
			for (let i = this.pos + 11; i < this.points.length; i++) {
				this.context.lineTo(this.points[i].x, this.points[i].y);
			}
			this.context.stroke();
		}
	}

	animate() {
		this.frameCount = (this.frameCount + 1) % 4;
		if (this.frameCount == 0) {
			this.pos += 1;
		}
		if (this.pos >= this.points.length) {
			this.pos = 0;
		}
		this.load();
		requestAnimationFrame(this.animate);
	}

	// 심장 박동 이벤트 (점 확 튀기기)
    pulseBig(big) {
		if (big) {
			this.pattern = [
				0, 12, 0,              // P파 (더 크게)
				-20, 70, -40, 0,       // QRS (더 크게)
				0, 30, 0               // T파 (더 크게)
			]
		} else {
			this.pattern = [
				0, 6, 0,              // P파
				-10, 40, -20, 0,      // QRS (Q 아래, R 위로, S 아래, baseline)
				0, 15, 0              // T파
			];			
		}
		this.points = [];
		let x = 0;
		while (x < this.width) {
			for (let i = 0; i < this.pattern.length && x < this.width; i++) {
				this.points.push({ x: x, y: this.baseline - this.pattern[i] });
				x += this.step;
			}
		}
		this.pos = 0;
    }
}

export default Heart;
