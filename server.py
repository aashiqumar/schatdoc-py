from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import uuid
from app.controller.TranslationController import translation_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Register the translation blueprint
app.register_blueprint(translation_bp)

clients = {}
codes = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    client_id = str(uuid.uuid4())
    clients[client_id] = {'sid': request.sid, 'code': None}
    emit('client_id', client_id)

@socketio.on('disconnect')
def handle_disconnect():
    client_id = next((k for k, v in clients.items() if v['sid'] == request.sid), None)
    if client_id:
        code = clients[client_id]['code']
        if code in codes:
            codes[code].remove(client_id)
            if not codes[code]:
                del codes[code]
        del clients[client_id]

@socketio.on('create_code')
def handle_create_code(data):
    client_id = data['client_id']
    code = data['code']
    if code not in codes:
        codes[code] = []
    codes[code].append(client_id)
    clients[client_id]['code'] = code
    emit('code_created', code, room=clients[client_id]['sid'])

@socketio.on('join_code')
def handle_join_code(data):
    client_id = data['client_id']
    code = data['code']
    if code in codes:
        codes[code].append(client_id)
        clients[client_id]['code'] = code
        emit('code_joined', code, room=clients[client_id]['sid'])
    else:
        emit('error', 'Code not found', room=clients[client_id]['sid'])

@socketio.on('message')
def handle_message(data):
    client_id = next((k for k, v in clients.items() if v['sid'] == request.sid), None)
    if client_id:
        code = clients[client_id]['code']
        message = data['message']
        if code in codes:
            for cid in codes[code]:
                if cid != client_id:
                    send(message, room=clients[cid]['sid'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)