from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import json
from config import Config
from routes import api
from models import db

# Set development environment
os.environ['FLASK_ENV'] = 'development'

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Add a simple index route
@app.route('/')
def index():
    return jsonify({
        'name': 'Decentralized Secure Messaging API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': ['/api/test', '/api/auth/register', '/api/auth/login', '/api/users', '/api/chats']
    })

# Initialize Socket.IO with enhanced configuration
# Use default threading mode which works without additional dependencies
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    ping_timeout=60,      # Increase ping timeout to prevent disconnections
    ping_interval=25,     # More frequent pings to maintain connection
    engineio_logger=True, # Enable engine.io logging for debugging
    logger=True           # Enable Socket.IO logging for debugging
)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

# Initialize database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Socket.IO event handlers with improved logging and room support
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    # You can perform authentication here if needed
    print(f'Connection headers: {dict(request.headers)}')
    
    # If using JWT authentication, you could verify the token here
    auth = request.args.get('token')
    if auth:
        print(f'Auth token provided: {auth[:10]}...')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    # Note: We can't get rooms at disconnect time in the current Flask-SocketIO version
    print('Client disconnected from server')

@socketio.on('join')
def on_join(data):
    """Handle a client joining a chat room"""
    room = data.get('room')
    if not room:
        print('No room specified in join request')
        return
    
    print(f'Client {request.sid} is joining room: {room}')
    # Join the room
    join_room(room)
    
    # Notify everyone in the room that someone joined
    socketio.emit('status', {'msg': 'Someone joined the room'}, room=room, skip_sid=request.sid)

@socketio.on('leave')
def on_leave(data):
    """Handle a client leaving a chat room"""
    room = data.get('room')
    if not room:
        print('No room specified in leave request')
        return
    
    print(f'Client {request.sid} is leaving room: {room}')
    # Leave the room
    leave_room(room)
    
    # Notify everyone in the room that someone left
    socketio.emit('status', {'msg': 'Someone left the room'}, room=room)

@socketio.on('message')
def handle_message(data):
    """Handle messages from clients and broadcast to the appropriate room"""
    print(f'Received message from {request.sid}: {data}')
    
    # Check if a chat_id (room) is specified in the data
    room = data.get('chat_id')
    if not room:
        print('No chat_id specified in message, defaulting to global broadcast')
        # Broadcast to all connected clients except sender
        socketio.emit('message', data, skip_sid=request.sid)
    else:
        print(f'Broadcasting message to room {room}')
        # Broadcast only to users in the specific room
        socketio.emit('message', data, room=room, skip_sid=request.sid)
        
    # Acknowledge receipt of the message to the sender
    return {'status': 'ok', 'message': 'Message received'}

# Run the application
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True, log_output=True)
