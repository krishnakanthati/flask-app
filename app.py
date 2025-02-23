import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_pymongo import PyMongo

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configure secret keys and MongoDB URI (read from environment variable)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/collab_code_db")

# Initialize Flask extensions
mongo = PyMongo(app)
users_collection = mongo.db.users
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

# In-memory structures for real-time collaboration
active_users = {}      # Stores {sid: username}
user_sessions = {}     # Maps session ID to username
cursor_positions = {}  # Stores {username: {x: 0, y: 0}}
shared_code = {'code': ''}  # Stores shared code among users

@app.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400

    username = data['username']
    password = data['password']

    # Check if user already exists in MongoDB
    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 400

    # Store hashed password in MongoDB
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({'username': username, 'password': hashed_password})
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid request'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    # Retrieve user from MongoDB
    user = users_collection.find_one({'username': username})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token, 'username': username}), 200

@app.route('/auth/protected', methods=['GET'])
@jwt_required()
def protected():
    """Protected route (requires authentication)."""
    return jsonify({'message': 'This is a protected route'}), 200

# WebSocket event handlers for real-time collaboration
@socketio.on('connect')
def handle_connect():
    print(f"New connection: {request.sid}")

@socketio.on('join')
def handle_join(data):
    token = data.get("token")
    try:
        decoded = decode_token(token)
        username = decoded['sub']
        active_users[request.sid] = username
        user_sessions[request.sid] = username

        # Emit update to all clients, including the sender
        emit("update-users", {"users": list(active_users.values())}, broadcast=True, include_self=True)
        # Send the current shared code to the newly connected client
        emit("receive-code", shared_code, room=request.sid)
    except Exception as e:
        print(f"Invalid token: {e}")

@socketio.on('send-code')
def handle_code_change(data):
    shared_code['code'] = data.get('code', '')
    emit('receive-code', shared_code, broadcast=True)

@socketio.on('cursor-move')
def handle_cursor_move(data):
    username = user_sessions.get(request.sid)
    if username:
        cursor_positions[username] = data
        emit("cursor-update", {"username": username, "position": data}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    username = user_sessions.pop(sid, None)
    if username:
        active_users.pop(sid, None)
        emit("update-users", {"users": list(active_users.values())}, broadcast=True)
        emit("cursor-update", {"username": username, "position": None}, broadcast=True)
    print(f"Session {sid} disconnected")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
