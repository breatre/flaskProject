from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
UPLOAD_FOLDER = '/var/www/videos'
MESSAGE_FILE = 'messages.txt'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 从文件加载留言
def load_messages():
    messages = []
    if os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                content, timestamp = line.strip().split('|')
                messages.append({'content': content, 'timestamp': timestamp})
    return messages

# 将新留言保存到文件
def save_message(content):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(MESSAGE_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{content}|{timestamp}\n")



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)  # 上传文件保存到云服务器指定目录
        return jsonify(success=True, filename=file.filename)
    return render_template('upload.html')



@app.route('/stream/<filename>')
def stream_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=False)


@app.route('/videos', methods=['GET'])
def list_videos():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(videos=files)


@app.route('/video_list', methods=['GET'])
def video_list():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('video_list.html', videos=files)


# 留言墙路由
@app.route('/message_wall', methods=['GET', 'POST'])
def message_wall():
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            save_message(content)  # 保存到文件
            return redirect(url_for('message_wall'))
    messages = load_messages()  # 从文件加载留言
    return render_template('message_wall.html', messages=messages)

if __name__ == '__main__':
    app.run(host='::', port=5000, debug=True)
