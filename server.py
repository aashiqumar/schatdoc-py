from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import uuid
from flask_cors import CORS
from app.controller.TranslationController import translation_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:8000")

app.register_blueprint(translation_bp)

clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    client_id = str(uuid.uuid4())
    clients[request.sid] = client_id
    emit('client_id', client_id)

@socketio.on('disconnect')
def handle_disconnect():
    clients.pop(request.sid, None)

@socketio.on('join_channel')
def handle_join_channel(data):
    client_id = data.get('client_id')
    channel = data.get('channel')
    if client_id and channel:
        join_room(channel)
        emit('channel_joined', channel)
    else:
        print('Error: client_id or channel not provided')

@socketio.on('leave_channel')
def handle_leave_channel(data):
    client_id = data.get('client_id')
    channel = data.get('channel')
    if client_id and channel:
        leave_room(channel)
        emit('channel_left', channel)
    else:
        print('Error: client_id or channel not provided')

@socketio.on('message')
def handle_message(data):
    channel = data.get('channel')
    message = data.get('message')
    if channel and message:
        emit('message', message, room=channel)
    else:
        print('Error: channel or message not provided')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8100)