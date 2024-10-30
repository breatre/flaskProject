from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
UPLOAD_FOLDER = '/var/www/videos'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'  # SQLite 数据库文件
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 创建留言模型
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 创建数据库
with app.app_context():
    db.create_all()


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
            new_message = Message(content=content)  # 创建新的留言对象
            db.session.add(new_message)  # 将留言添加到会话
            db.session.commit()  # 提交会话
            return redirect(url_for('message_wall'))

    messages = Message.query.order_by(Message.timestamp.desc()).all()  # 从数据库加载留言
    return render_template('message_wall.html', messages=messages)

if __name__ == '__main__':
    app.run(host='::', port=5000, debug=True)
