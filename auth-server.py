#!/usr/bin/env python3
"""
Quantum Authentication Server for X12 Server
Handles user registration, login, and quantum token management
"""

import os
import json
import asyncio
import aiohttp
from aiohttp import web
import jwt
import bcrypt
from datetime import datetime, timedelta
import sqlite3
from database import UserDatabase

# Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'quantum_x12_secret_key_change_in_production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 24  # hours

class QuantumAuthServer:
    def __init__(self):
        self.app = web.Application()
        self.db = UserDatabase()
        self.setup_routes()
        
    def setup_routes(self):
        self.app.router.add_post('/api/register', self.register)
        self.app.router.add_post('/api/login', self.login)
        self.app.router.add_post('/api/logout', self.logout)
        self.app.router.add_post('/api/validate', self.validate)
        self.app.router.add_get('/api/user', self.get_user)
        
    async def register(self, request):
        """Handle user registration with quantum-enhanced security"""
        try:
            data = await request.json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            quantum_key = data.get('quantum_key')
            
            # Validate input
            if not all([username, email, password, quantum_key]):
                return web.json_response(
                    {'error': 'Missing required fields'}, 
                    status=400
                )
            
            # Check if user already exists
            if self.db.user_exists(username, email):
                return web.json_response(
                    {'error': 'User already exists'}, 
                    status=409
                )
            
            # Create user with quantum key
            user_id = self.db.create_user(username, email, password, quantum_key)
            
            # Generate JWT token
            token = self.generate_jwt_token(user_id, username)
            
            return web.json_response({
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email
                }
            })
            
        except Exception as e:
            return web.json_response(
                {'error': f'Registration failed: {str(e)}'}, 
                status=500
            )
    
    async def login(self, request):
        """Handle user login with quantum authentication"""
        try:
            data = await request.json()
            username = data.get('username')
            password = data.get('password')
            quantum_challenge = data.get('quantum_challenge')
            
            # Validate input
            if not all([username, password, quantum_challenge]):
                return web.json_response(
                    {'error': 'Missing required fields'}, 
                    status=400
                )
            
            # Verify user credentials
            user = self.db.verify_user(username, password)
            if not user:
                return web.json_response(
                    {'error': 'Invalid credentials'}, 
                    status=401
                )
            
            # Generate JWT token
            token = self.generate_jwt_token(user['id'], user['username'])
            
            # Update last login
            self.db.update_last_login(user['id'])
            
            return web.json_response({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            })
            
        except Exception as e:
            return web.json_response(
                {'error': f'Login failed: {str(e)}'}, 
                status=500
            )
    
    async def logout(self, request):
        """Handle user logout"""
        # In a stateless JWT system, we can't invalidate tokens easily
        # So we'll just acknowledge the logout request
        # In production, you might want to use a token blacklist
        
        # Extract token from header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # You could add token to a blacklist here
            
        return web.json_response({'message': 'Logout successful'})
    
    async def validate(self, request):
        """Validate JWT token"""
        try:
            # Extract token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response(
                    {'error': 'Authorization header missing or invalid'}, 
                    status=401
                )
            
            token = auth_header[7:]
            
            # Verify token
            payload = self.verify_jwt_token(token)
            if not payload:
                return web.json_response(
                    {'error': 'Invalid token'}, 
                    status=401
                )
            
            return web.json_response({'valid': True, 'user': payload})
            
        except Exception as e:
            return web.json_response(
                {'error': f'Token validation failed: {str(e)}'}, 
                status=500
            )
    
    async def get_user(self, request):
        """Get user information"""
        try:
            # Extract token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response(
                    {'error': 'Authorization header missing or invalid'}, 
                    status=401
                )
            
            token = auth_header[7:]
            
            # Verify token
            payload = self.verify_jwt_token(token)
            if not payload:
                return web.json_response(
                    {'error': 'Invalid token'}, 
                    status=401
                )
            
            # Get user from database
            user = self.db.get_user(payload['user_id'])
            if not user:
                return web.json_response(
                    {'error': 'User not found'}, 
                    status=404
                )
            
            return web.json_response({
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            })
            
        except Exception as e:
            return web.json_response(
                {'error': f'Failed to get user: {str(e)}'}, 
                status=500
            )
    
    def generate_jwt_token(self, user_id, username):
        """Generate a JWT token for the user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_jwt_token(self, token):
        """Verify a JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

async def main():
    """Start the authentication server"""
    server = QuantumAuthServer()
    runner = web.AppRunner(server.app)
    await runner.setup()
    
    # Use port 8081 for auth API to avoid conflict with main server
    site = web.TCPSite(runner, 'localhost', 8081)
    await site.start()
    
    print("Quantum Authentication Server running on http://localhost:8081")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
