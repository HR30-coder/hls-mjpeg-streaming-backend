from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,FileResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from .models import Stream
from django.conf import settings
import json,os,subprocess,uuid
from django.utils.text import slugify

# Create your views here.


def videoServe(request,id):
    filename = f"{id}.mp4"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    if not os.path.exists(filepath):
        raise Http404("Video not found")
    
    fileSize = os.path.getsize(filepath)
    fileRange = request.headers.get("Range","");
    start,end = 0,None
    
    if fileRange.startswith('bytes='):
        range_match = fileRange.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        if range_match[1]:
            end = int(range_match[1])
    
    end = end if end is not None else fileSize - 1
    length = end - start + 1

    with open(filepath,"rb") as f:
        f.seek(start)
        data = f.read(length)

    response = HttpResponse(data, status=206, content_type='video/mp4')
    response['Content-Range'] = f'bytes {start}-{end}/{fileSize}'
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(length)

    return response

@csrf_exempt
def startStream(request, slug):
    try:
        stream = Stream.objects.get(slug=slug)  #find the stream where the slug is this
    except Stream.DoesNotExist:
        raise Http404("Stream not found")

    output_dir = os.path.join(settings.BASE_DIR, 'outputs', slug)
    playlist_path = os.path.join(output_dir, 'playlist.m3u8')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # If FFmpeg is already running, avoid restarting
    if not os.path.exists(playlist_path):
        # Build FFmpeg command to generate HLS
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', stream.url,
            '-c:v', 'libx264',
            '-f', 'hls',
            '-hls_time', '4',
            '-hls_list_size', '5',
            '-hls_flags', 'delete_segments+program_date_time',
            playlist_path
        ]

        # Run FFmpeg as a background process
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return JsonResponse({
            'message': 'Stream started',
            'playlist_url': f'/outputs/{slug}/playlist.m3u8'
        })

    else:
        return JsonResponse({
            'message': 'Stream already started',
            'playlist_url': f'/outputs/{slug}/playlist.m3u8'
        })


@csrf_exempt
def streamHandle(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            if not url:
                return JsonResponse({'error': 'URL is not provided'}, status=400)

            # Generate a unique slug (optional: slugify part of the URL)
            raw_slug = slugify(url.split("//")[-1])[:30]  # basic readable part
            unique_slug = f"{raw_slug}-{uuid.uuid4().hex[:8]}"

            stream = Stream.objects.create(url=url, slug=unique_slug)
            return JsonResponse({'message': 'Stream saved', 'slug': stream.slug}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        streams = Stream.objects.all().values('slug', 'url', 'created')
        return JsonResponse(list(streams), safe=False)
