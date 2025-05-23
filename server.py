from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import glob

app = Flask(__name__)

COOKIES_PATH = "cookies.txt"

@app.route('/')
def index():
    return jsonify({'message': 'This is working!'})

@app.route('/yt', methods=['GET'])
def yt_download():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'force_generic_extractor': False,
        'cookiefile': COOKIES_PATH,
        'extract_flat': False,
        'dump_single_json': True,
        'restrictfilenames': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    format_id = request.args.get('format_id')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    output_dir = 'downloads'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'quiet': True,
        'format': format_id or 'best',
        'outtmpl': output_path,
        'cookiefile': COOKIES_PATH
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        title = info.get('title')
        ext = info.get('ext')
        matching_files = glob.glob(os.path.join(output_dir, f"{title}.{ext}"))
        if matching_files:
            file_path = matching_files[0]
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Downloaded file not found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    
