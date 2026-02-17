"""Real-time WebSocket service for live updates."""
from flask_socketio import emit, join_room
from flask import request
from flask_jwt_extended import decode_token
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SocketIOManager:
    """Manager for Socket.IO connections."""
    socketio = None
    user_connections = {}  # Maps user_id -> {socket_id: connection_info}


def init_socketio(socket_io):
    """Initialize Socket.IO."""
    SocketIOManager.socketio = socket_io
    
    @socket_io.on('connect')
    def on_connect(auth):
        """Handle client connection."""
        try:
            if auth and 'token' in auth:
                token = auth['token']
                decoded = decode_token(token)
                user_id = decoded['sub']
                
                # Track connection by socket ID instead of IP address
                socket_id = request.sid
                
                if user_id not in SocketIOManager.user_connections:
                    SocketIOManager.user_connections[user_id] = {}
                SocketIOManager.user_connections[user_id][socket_id] = {
                    'connected_at': datetime.utcnow(),
                    'ip_address': request.remote_addr
                }
                
                join_room(f'user_{user_id}')
                emit('connected', {
                    'message': 'Connected to real-time updates',
                    'timestamp': datetime.utcnow().isoformat()
                })
                logger.info('User %s connected', user_id)
        except ValueError as e:
            logger.error('Connection error: %s', str(e))
            return False
    
    @socket_io.on('disconnect')
    def on_disconnect():
        """Handle client disconnection."""
        socket_id = request.sid
        
        # Clean up user connections
        for user_id, connections in list(SocketIOManager.user_connections.items()):
            if socket_id in connections:
                del connections[socket_id]
                if not connections:  # Remove user if no more connections
                    del SocketIOManager.user_connections[user_id]
                logger.info('User %s socket %s disconnected', user_id, socket_id)
                break
    
    @socket_io.on('subscribe_account')
    def on_subscribe_account(data):
        """Subscribe to account updates."""
        try:
            if 'token' in data and 'account_id' in data:
                token = data['token']
                decode_token(token)
                account_id = data['account_id']
                
                room = f'account_{account_id}'
                join_room(room)
                emit('subscribed', {
                    'message': 'Subscribed to account %s' % account_id,
                    'account_id': account_id
                })
        except ValueError as e:
            logger.error('Subscription error: %s', str(e))


def emit_transaction_update(user_id, transaction_data):
    """Emit transaction update to user."""
    if SocketIOManager.socketio:
        SocketIOManager.socketio.emit('transaction_update', transaction_data, room=f'user_{user_id}')


def emit_balance_update(account_id, balance):
    """Emit balance update."""
    if SocketIOManager.socketio:
        SocketIOManager.socketio.emit('balance_update', {
            'account_id': account_id,
            'balance': balance,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'account_{account_id}')


def emit_budget_alert(user_id, budget_data):
    """Emit budget alert to user."""
    if SocketIOManager.socketio:
        SocketIOManager.socketio.emit('budget_alert', {
            'budget_id': budget_data.get('id'),
            'name': budget_data.get('name'),
            'percentage': budget_data.get('percentage'),
            'message': f"Budget '{budget_data.get('name')}' reached {budget_data.get('percentage')}%",
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'user_{user_id}')


def emit_bill_reminder(user_id, bill_data):
    """Emit bill reminder to user."""
    if SocketIOManager.socketio:
        SocketIOManager.socketio.emit('bill_reminder', {
            'bill_id': bill_data.get('id'),
            'name': bill_data.get('name'),
            'amount': bill_data.get('amount'),
            'due_date': bill_data.get('due_date'),
            'days_until_due': bill_data.get('days_until_due'),
            'message': f"Bill '{bill_data.get('name')}' due in {bill_data.get('days_until_due')} days",
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'user_{user_id}')
