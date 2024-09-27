from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import uuid
from app.controller.TranslationController import translation_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Register the translation blueprint
app.register_blueprint(translation_bp)

clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    client_id = str(uuid.uuid4())
    clients[client_id] = request.sid
    # Removed the broadcast message for client connection
    return client_id

@socketio.on('disconnect')
def handle_disconnect():
    client_id = next((k for k, v in clients.items() if v == request.sid), None)
    if client_id:
        del clients[client_id]
        # Removed the broadcast message for client disconnection

@socketio.on('message')
def handle_message(msg):
    client_id = next((k for k, v in clients.items() if v == request.sid), None)
    if client_id:
        for sid in clients.values():
            if sid != request.sid:
                send(msg, room=sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)