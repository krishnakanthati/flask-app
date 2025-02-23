import unittest
import json
from app import app, socketio, mongo, active_users, user_sessions, shared_code

class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.socket_client = socketio.test_client(app, flask_test_client=self.client)
        # Clear the MongoDB users collection
        mongo.db.users.delete_many({})
        # Reset in-memory state for real-time collaboration
        active_users.clear()
        user_sessions.clear()
        shared_code['code'] = ''

    def tearDown(self):
        self.socket_client.disconnect()

    def test_register_and_login(self):
        # Test registration.
        reg_response = self.client.post(
            '/auth/register',
            json={'username': 'testuser', 'password': 'testpass'}
        )
        self.assertEqual(reg_response.status_code, 201)
        reg_data = reg_response.get_json()
        self.assertEqual(reg_data['message'], 'User registered successfully')

        # Test login.
        login_response = self.client.post(
            '/auth/login',
            json={'username': 'testuser', 'password': 'testpass'}
        )
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.get_json()
        self.assertIn('access_token', login_data)
        self.assertEqual(login_data['username'], 'testuser')

    def test_protected_route(self):
        # Register and log in a user.
        self.client.post(
            '/auth/register',
            json={'username': 'secureuser', 'password': 'securepass'}
        )
        login_response = self.client.post(
            '/auth/login',
            json={'username': 'secureuser', 'password': 'securepass'}
        )
        token = login_response.get_json()['access_token']

        # Access protected route with the token.
        headers = {'Authorization': f'Bearer {token}'}
        protected_response = self.client.get('/auth/protected', headers=headers)
        self.assertEqual(protected_response.status_code, 200)
        data = protected_response.get_json()
        self.assertEqual(data['message'], 'This is a protected route')

    def test_socketio_join_event(self):
        # Register and log in to obtain a JWT.
        self.client.post(
            '/auth/register',
            json={'username': 'socketuser', 'password': 'socketpass'}
        )
        login_response = self.client.post(
            '/auth/login',
            json={'username': 'socketuser', 'password': 'socketpass'}
        )
        token = login_response.get_json()['access_token']

        # Emit the join event with a valid token.
        self.socket_client.emit('join', {'token': token})
        # Retrieve events emitted to the client.
        received = self.socket_client.get_received()
        event_names = [event['name'] for event in received]
        # Check for expected events: update-users and receive-code.
        self.assertIn('update-users', event_names)
        self.assertIn('receive-code', event_names)

if __name__ == '__main__':
    unittest.main()
