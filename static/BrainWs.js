
class BrainWs {
	constructor() {
		this.ws = new WebSocket("ws://localhost:8000/ws");

		this.ws.onopen = () => {
			console.log("WebSocket 연결됨");
			this.ws.send("브라우저가 인사합니다!");
		}

		this.ws.onmessage = (event) => {
			console.log("서버 메시지: ", event.data);
		}

		this.ws.onerror = (err) => {
			console.error("websocket 에러: ", err);
		}

		this.ws.onclose = () => {
			console.log("websocket 연결종료");
		}
	}

	sendMessage() {
		if (this.ws.readyState === WebSocket.OPEN) {
			this.ws.send("메시지 전송");
		} else {
			console.log("websocket이 아직 열리지 않았습니다.");
		}
	}
}

export default BrainWs;