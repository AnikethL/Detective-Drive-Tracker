# flask_app.py
from flask import Flask, render_template, Response, send_from_directory, redirect, url_for
from flask_cors import CORS
import os
import shutil  # For deleting files
import time
from multiprocessing import Process
from v4 import main as opencv_main

app = Flask(__name__)
CORS(app)

IMAGE_FOLDER = 'static/images'

def get_latest_frame():
    frame_path = 'lastFrame.jpg'
    
    while True:
        if os.path.exists(frame_path):
            with open(frame_path, 'rb') as f:
                frame = f.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(0.1)
        else:
            time.sleep(0.1)  # Wait for a short time if the frame is not yet available

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Render the template instead of directly returning the video feed
    return render_template('video_feed.html')


@app.route('/video_feed_content')
def video_feed_content():
    return Response(get_latest_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/image_gallery')
def image_gallery():
    image_files = os.listdir(IMAGE_FOLDER)
    return render_template('images.html', images=image_files)

@app.route('/empty_images_folder', methods=['POST'])
def empty_images_folder():
    # Delete all files in the images folder
    for filename in os.listdir(IMAGE_FOLDER):
        file_path = os.path.join(IMAGE_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Error: {e}")

    return render_template('images.html', images=[])

def start_server():
    app.run(host='0.0.0.0', debug=False)

if __name__ == '__main__':
    p1 = Process(target=opencv_main)
    p2 = Process(target=start_server)
    p1.start()
    p2.start()
    p1.join()
    p2.join()