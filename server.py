from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import tempfile

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies.txt')

def extract_info(url, opts):
    with YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.route('/')
def root():
    return '✅ YouTube DL API is running!'

@app.route('/info')
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'forcejson': True,
        'format': 'best',
        'cookiefile': COOKIES_PATH
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'description': info.get('description'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'uploader': info.get('uploader'),
                'channel_url': info.get('channel_url'),
                'formats': [
                    {
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'acodec': f.get('acodec'),
                        'vcodec': f.get('vcodec'),
                        'url': f.get('url'),
                        'filesize': f.get('filesize'),
                        'tbr': f.get('tbr'),
                        'height': f.get('height'),
                        'width': f.get('width'),
                        'fps': f.get('fps'),
                    } for f in info.get('formats', [])
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    ydl_opts = {
        'format': 'best',
        'outtmpl': tempfile.gettempdir() + '/%(title)s.%(ext)s',
        'cookiefile': COOKIES_PATH,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filepath = ydl.prepare_filename(info)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ... (other routes remain unchanged) ...

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
