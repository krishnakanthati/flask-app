Collab Code App
===============

A Flask-based collaborative code-sharing app with JWT authentication, MongoDB persistence, and real-time updates via SocketIO.

Setup
-----

1. Install Dependencies:
   Run the following command to install required packages:
     pip install -r requirements.txt

2. Start MongoDB:
   Use Docker to run a lightweight MongoDB instance:
     docker run --name mongodb-lite -d -p 27017:27017 --memory=256m --cpus="0.5" mongo:latest --wiredTigerCacheSizeGB 0.25

3. Run the App:
   Start the Flask application:
     python app.py

API Endpoints & Curl Commands
------------------------------

Register:
  Endpoint: POST /auth/register
  Description: Registers a new user.
  Example:
    curl -X POST http://localhost:5000/auth/register \
      -H "Content-Type: application/json" \
      -d '{"username": "testuser", "password": "testpass"}'

Login:
  Endpoint: POST /auth/login
  Description: Logs in a user and returns a JWT token.
  Example:
    curl -X POST http://localhost:5000/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "testuser", "password": "testpass"}'

Protected Endpoint:
  Endpoint: GET /auth/protected
  Description: A protected route that requires a valid JWT token.
  Example:
    curl -X GET http://localhost:5000/auth/protected \
      -H "Authorization: Bearer <ACCESS_TOKEN>"
  Note: Replace <ACCESS_TOKEN> with the token received from the login response.

Real-Time Collaboration
-----------------------

This app uses SocketIO for real-time collaboration with events such as "join", "send-code", and "cursor-move".

To test WebSocket events, use a WebSocket client like wscat:
  wscat -c ws://localhost:5000/socket.io/?EIO=3&transport=websocket

That's it!

Here is the code flow:
![image](https://github.com/user-attachments/assets/b90ec83b-22eb-494b-8548-bee48593b60e)

