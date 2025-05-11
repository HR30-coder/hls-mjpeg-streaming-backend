from channels.generic.websocket import WebsocketConsumer
from subprocess import Popen, PIPE

class StreamConsumer(WebsocketConsumer):
    def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']

        from .models import Stream  # ✅ Import inside the method
        try:
            stream_obj = Stream.objects.get(slug=self.slug)
            print(stream_obj)
        except Stream.DoesNotExist:
            print("Stream does not exist")
            self.close()
            return

        self.rtsp_url = stream_obj.url
        self.accept()

        # Start FFmpeg process to stream MJPEG
        self.process = Popen(
            ['ffmpeg', '-i', self.rtsp_url, '-f', 'mjpeg', '-q:v', '5', '-'],
            stdout=PIPE, stderr=PIPE
        )
        self.running = True
        self.stream_video()

    def disconnect(self, close_code):
        self.running = False
        if self.process:
            self.process.kill()

    def stream_video(self):
        while self.running:
            data = self.process.stdout.read(1024)
            if not data:
                break
            self.send(bytes_data=data)
