from flask import Flask, render_template, request, redirect, url_for
from yt_dlp import YoutubeDL

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download_process', methods=['POST'])
def download_process():
    url = request.form['url']

    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict['formats']
        thumbnail = info_dict.get('thumbnail')
        title = info_dict.get('title')

    formats_by_quality = []
    highest_quality_format = None
    highest_quality_resolution = 0

    for fmt in formats:
        if fmt['ext'] == 'mp4' and 'format_note' in fmt:
            quality = fmt['format_note']
            file_size = fmt.get('filesize') or fmt.get('filesize_approx')
            if file_size is not None:  # Only include formats with known file size
                file_size_mb = round(
                    file_size / (1024 * 1024), 2) if isinstance(file_size, int) else 'Unknown size'
                formats_by_quality.append({
                    'format_id': fmt['format_id'],
                    'quality': quality,
                    'file_size_mb': file_size_mb,
                })

                # Find the highest quality format with the highest resolution
                if 'p' in quality:
                    try:
                        # Extract the resolution number
                        quality_num = int(
                            ''.join(filter(str.isdigit, quality)))
                    except ValueError:
                        continue  # Skip this format if resolution number cannot be extracted
                    if quality_num >= highest_quality_resolution:
                        highest_quality_resolution = quality_num
                        highest_quality_format = fmt['format_id']

    # Add MP3 option manually
    formats_by_quality.append({
        'format_id': 'mp3',
        'quality': 'MP3',
        'file_size_mb': 'Unknown'
    })

    return render_template('download_process.html', url=url, formats=formats_by_quality, thumbnail=thumbnail, title=title, highest_quality_format=highest_quality_format)


@app.route('/download_complete', methods=['POST'])
def download_complete():
    url = request.form['url']
    format_id = request.form['format_id']

    if format_id == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }
    else:
        ydl_opts = {
            'format': format_id,
            'quiet': True,
            'outtmpl': '%(title)s.%(ext)s',
        }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict['title']
        thumbnail = info_dict.get('thumbnail')

    return render_template('download_complete.html', title=title, thumbnail=thumbnail)


if __name__ == '__main__':
    app.run(debug=True)
