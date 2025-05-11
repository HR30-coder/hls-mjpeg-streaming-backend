from channels.generic.websocket import WebsocketConsumer

class SimpleConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data="Hello, world!")

    def disconnect(self, close_code):
        print("WebSocket disconnected with code:", close_code)