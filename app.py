from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import random
import string

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'image')
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'video')
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

def generate_filename(extension):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + extension

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
        filename = generate_filename(file_ext)
        file_path = os.path.join(IMAGE_FOLDER, filename)
        file.save(file_path)
        return jsonify({'filename': filename, 'type': 'image'})
    elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
        filename = generate_filename(file_ext)
        file_path = os.path.join(VIDEO_FOLDER, filename)
        file.save(file_path)
        return jsonify({'filename': filename, 'type': 'video'})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/image/<filename>')
def get_image(filename):
    return render_template("image.html", file=f"/static/image/{filename}")

@app.route('/video/<filename>')
def get_video(filename):
    return render_template("video.html", file=f"/static/video/{filename}")

@app.route('/static/image/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/static/video/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
