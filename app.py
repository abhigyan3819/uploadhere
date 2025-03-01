from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import random
import string
import requests
import datetime

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "image")
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, "video")
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(UPLOAD_FOLDER, "visitor_log.txt")

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("No. | Timestamp | IP Address | Device/User-Agent | Location | Coordinates (Lat, Long)\n")
        f.write("=" * 120 + "\n")  

def generate_filename(extension):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + extension

def get_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        city = data.get("city", "Unknown")
        country = data.get("country", "Unknown")
        loc = data.get("loc", "Unknown,Unknown") 

        latitude, longitude = loc.split(",") if "," in loc else ("Unknown", "Unknown")
        return city, country, latitude, longitude
    except:
        return "Unknown", "Unknown", "Unknown", "Unknown"

def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        return response.json().get("ip", "Unknown")
    except:
        return "Unknown"

def log_visitor(ip, user_agent):
    city, country, latitude, longitude = get_location(ip)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "r") as file:
        lines = file.readlines()
        serial_no = len(lines) - 1  

    log_entry = f"{serial_no} | {timestamp} | {ip} | {user_agent} | {city}, {country} | {latitude}, {longitude}\n"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry)

@app.before_request
def before_request():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0]
    if ip == "127.0.0.1":
        ip = get_public_ip()

    user_agent = request.headers.get("User-Agent")
    log_visitor(ip, user_agent)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            lines = file.readlines()[2:]  
            for line in lines:
                parts = line.strip().split(" | ")
                if len(parts) == 6:
                    logs.append({
                        "no": parts[0],
                        "timestamp": parts[1],
                        "ip": parts[2],
                        "user_agent": parts[3],
                        "location": parts[4],
                        "coordinates": parts[5]
                    })
    return render_template("admin.html", logs=logs)

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

@app.route('/images/<filename>')
def get_image(filename):
    return render_template("image.html", file=f"/static/image/{filename}")

@app.route('/videos/<filename>')
def get_video(filename):
    return render_template("video.html", file=f"/static/video/{filename}")

@app.route('/gallery')
def gallery():
    images = os.listdir(IMAGE_FOLDER)
    videos = [f"/static/video/{vid}" for vid in os.listdir(VIDEO_FOLDER) if vid.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    images = [f"/static/image/{img}" for img in images if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('gallery.html', images=images, videos=videos)

@app.route('/download-log')
def download_log():
    return send_from_directory(os.getcwd(), LOG_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
