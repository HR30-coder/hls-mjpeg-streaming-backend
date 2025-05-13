Project Title: RTSP Stream Manager - Backend

Description:
-------------
This Django ASGI backend supports a full-stack RTSP video stream viewer. It includes REST APIs for storing RTSP links, and two streaming mechanisms:
1. MJPEG over WebSockets — low-latency streaming.
2. HLS over HTTP — bandwidth-efficient with adaptive playback.

Key Features:
--------------
1. 🔌 WebSocket endpoint for MJPEG frame streaming (low latency as moving jpeg are simply full jpeg images with immediate rendering possible but high on bandwidth).
2. 🎞️ HTTP endpoint for HLS streaming (auto-transcoded using FFmpeg) (high on latency because few chunks are required before the streaming can start and next frame is built based on prev chunk).
3. 🗃️ SQLite3-based storage of RTSP links via Django ORM.
4. 📡 REST API for managing RTSP link data.

Tech Stack:
------------
- Python 3.9+
- Django
- Django REST Framework
- Django Channels (ASGI)
- SQLite3
- FFmpeg (system dependency) 
- Uvicorn (ASGI server)

Local Setup Instructions:
---------------------------
1. Clone the repository:
   git clone <your_backend_repo_url>

2. Navigate to the project folder:
   cd backend

3. Install dependencies:
   pip install -r requirementss.txt

4. Apply migrations:
   python manage.py makemigrations
   python manage.py migrate

5. Run the server with ASGI + WebSocket support:
   uvicorn rtspbackend.asgi:application --host 127.0.0.1 --port 8080 --lifespan off

   🔌 The backend will be available at: http://127.0.0.1:8080

Endpoints:
📡 REST API Routing (`streamservice/urls.py`):
  Base Path: /video/

  - GET   /video/                      → List all RTSP links
  - POST  /video/                      → Add a new RTSP link
  - GET   /video/<slug>/              → Start HLS stream for a given slug
  - GET   /video/play/<int:id>/       → Serve the video player (e.g., return m3u8)

🔁 WebSocket Routing (`routing.py`):
  - ws://127.0.0.1:8080/ws/stream/<slug>/     → Stream MJPEG bytes over WebSocket
  - ws://127.0.0.1:8080/ws/hellostream/       → Test or experimental stream (SimpleConsumer)

Example Flow:
--------------
1. Add RTSP link via POST to `/video/`
2. On frontend, start playback:
   - For MJPEG → connect to `ws://127.0.0.1:8080/ws/stream/<slug>/`
   - For HLS   → load `http://127.0.0.1:8080/video/play/<id>/` in `video.js`

Environment Notes:
-------------------
- FFmpeg is required and must be accessible via system PATH.
- The backend must be run using an ASGI server like `uvicorn` for WebSocket support.

Database:
----------
- Uses SQLite3 for development.
- Streams are stored using Django models in the `streamservice` app.

Notes:
-------
- MJPEG streams provide minimal latency but higher bandwidth usage.
- HLS streams buffer more but support adaptive playback and lower bandwidth.
- As this is a POC have ot added the authentication but this can be integrated easily using django's builting aut providers
