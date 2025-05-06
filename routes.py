from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from models import db, User, Message, Chat, ChatParticipant
from auth import authenticate, generate_token
from blockchain import verify_wallet_signature
from encryption import verify_encryption_key
import uuid
from datetime import datetime

api = Blueprint('api', __name__)

# Test route that doesn't require authentication
@api.route('/test', methods=['GET'])
def test_api():
    return jsonify({
        'message': 'API is working!',
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Authentication routes
@api.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate input
    if not all(k in data for k in ('username', 'wallet_address', 'public_key', 'signature')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if username or wallet_address already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(wallet_address=data['wallet_address']).first():
        return jsonify({'error': 'Wallet address already exists'}), 400
    
    # Verify wallet signature
    if not verify_wallet_signature(data['wallet_address'], data['signature']):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Verify encryption key
    if not verify_encryption_key(data['public_key']):
        return jsonify({'error': 'Invalid encryption key'}), 400
    
    # Create new user
    new_user = User(
        username=data['username'],
        wallet_address=data['wallet_address'],
        public_key=data['public_key']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Generate JWT token
    token = generate_token(new_user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'wallet_address': new_user.wallet_address
        }
    }), 201

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    
    # Validate input
    if not all(k in data for k in ('wallet_address', 'signature')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Find user by wallet address
    user = User.query.filter_by(wallet_address=data['wallet_address']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify wallet signature
    if not verify_wallet_signature(data['wallet_address'], data['signature']):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Update last seen
    user.last_seen = datetime.utcnow()
    db.session.commit()
    
    # Generate JWT token
    token = generate_token(user.id)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'wallet_address': user.wallet_address
        }
    }), 200

# User routes
@api.route('/users', methods=['GET'])
@authenticate
def get_users(current_user):
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'wallet_address': user.wallet_address,
            'public_key': user.public_key
        } for user in users if user.id != current_user.id]
    }), 200

@api.route('/users/<user_id>', methods=['GET'])
@authenticate
def get_user(current_user, user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'wallet_address': user.wallet_address,
            'public_key': user.public_key
        }
    }), 200

# Chat routes
@api.route('/chats', methods=['GET'])
@authenticate
def get_chats(current_user):
    # Get all chats where the current user is a participant
    participations = ChatParticipant.query.filter_by(user_id=current_user.id).all()
    chat_ids = [p.chat_id for p in participations]
    chats = Chat.query.filter(Chat.id.in_(chat_ids)).all()
    
    result = []
    for chat in chats:
        participants = ChatParticipant.query.filter_by(chat_id=chat.id).all()
        participant_users = [User.query.get(p.user_id) for p in participants]
        
        # For direct chats, get the other participant
        other_user = None
        if not chat.is_group:
            for user in participant_users:
                if user.id != current_user.id:
                    other_user = user
                    break
        
        chat_data = {
            'id': chat.id,
            'name': chat.name if chat.is_group else (other_user.username if other_user else 'Unknown'),
            'is_group': chat.is_group,
            'created_at': chat.created_at.isoformat(),
            'participants': [{
                'id': user.id,
                'username': user.username
            } for user in participant_users]
        }
        result.append(chat_data)
    
    return jsonify({'chats': result}), 200

@api.route('/chats', methods=['POST'])
@authenticate
def create_chat(current_user):
    data = request.json
    
    # Validate input
    if 'participants' not in data or not data['participants']:
        return jsonify({'error': 'No participants specified'}), 400
    
    is_group = len(data['participants']) > 1 or 'name' in data
    
    # For direct chats, check if a chat already exists with the participant
    if not is_group:
        participant_id = data['participants'][0]
        
        # Check if participant exists
        participant = User.query.get(participant_id)
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Check if a direct chat already exists
        existing_chats = Chat.query.filter_by(is_group=False).all()
        for chat in existing_chats:
            participants = ChatParticipant.query.filter_by(chat_id=chat.id).all()
            participant_ids = [p.user_id for p in participants]
            
            if current_user.id in participant_ids and participant_id in participant_ids:
                return jsonify({
                    'message': 'Chat already exists',
                    'chat': {
                        'id': chat.id,
                        'name': participant.username,
                        'is_group': False,
                        'created_at': chat.created_at.isoformat(),
                        'participants': [{
                            'id': p_id,
                            'username': User.query.get(p_id).username
                        } for p_id in participant_ids]
                    }
                }), 200
    
    # Create new chat
    new_chat = Chat(
        name=data.get('name') if is_group else None,
        is_group=is_group
    )
    
    db.session.add(new_chat)
    db.session.flush()  # Get the ID without committing
    
    # Add current user as participant
    current_participant = ChatParticipant(
        chat_id=new_chat.id,
        user_id=current_user.id
    )
    db.session.add(current_participant)
    
    # Add other participants
    for participant_id in data['participants']:
        if participant_id != current_user.id:
            participant = User.query.get(participant_id)
            if not participant:
                db.session.rollback()
                return jsonify({'error': f'Participant with ID {participant_id} not found'}), 404
            
            new_participant = ChatParticipant(
                chat_id=new_chat.id,
                user_id=participant_id
            )
            db.session.add(new_participant)
    
    db.session.commit()
    
    # Prepare response
    participants = ChatParticipant.query.filter_by(chat_id=new_chat.id).all()
    participant_users = [User.query.get(p.user_id) for p in participants]
    
    return jsonify({
        'message': 'Chat created successfully',
        'chat': {
            'id': new_chat.id,
            'name': new_chat.name if is_group else participant_users[0].username if participant_users[0].id != current_user.id else participant_users[1].username,
            'is_group': new_chat.is_group,
            'created_at': new_chat.created_at.isoformat(),
            'participants': [{
                'id': user.id,
                'username': user.username
            } for user in participant_users]
        }
    }), 201

@api.route('/chats/<chat_id>/messages', methods=['GET'])
@authenticate
def get_messages(current_user, chat_id):
    # Check if chat exists
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    # Check if user is a participant in the chat
    participant = ChatParticipant.query.filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if not participant:
        return jsonify({'error': 'Unauthorized access to chat'}), 403
    
    # Get all messages in the chat
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp).all()
    
    return jsonify({
        'messages': [{
            'id': message.id,
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id,
            'encrypted_content': message.encrypted_content,
            'ipfs_hash': message.ipfs_hash,
            'timestamp': message.timestamp.isoformat(),
            'read': message.read
        } for message in messages]
    }), 200

@api.route('/chats/<chat_id>/messages', methods=['POST'])
@authenticate
def send_message(current_user, chat_id):
    data = request.json
    
    # Validate input
    if 'encrypted_content' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if chat exists
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    # Check if user is a participant in the chat
    sender_participant = ChatParticipant.query.filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if not sender_participant:
        return jsonify({'error': 'Unauthorized access to chat'}), 403
    
    # For group chats, create a message for each participant
    if chat.is_group:
        participants = ChatParticipant.query.filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id != current_user.id
        ).all()
        
        for participant in participants:
            message = Message(
                sender_id=current_user.id,
                recipient_id=participant.user_id,
                encrypted_content=data['encrypted_content'],
                ipfs_hash=data.get('ipfs_hash')
            )
            db.session.add(message)
    else:
        # For direct chats, find the other participant
        recipient_participant = ChatParticipant.query.filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id != current_user.id
        ).first()
        
        if not recipient_participant:
            return jsonify({'error': 'Recipient not found'}), 404
        
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_participant.user_id,
            encrypted_content=data['encrypted_content'],
            ipfs_hash=data.get('ipfs_hash')
        )
        db.session.add(message)
    
    db.session.commit()
    
    # Get the message ID to return to the client
    # For group chats, just return the ID of the first message
    msg_id = message.id if 'message' in locals() else None
    
    # Emit WebSocket event
    # This will be handled by the Flask-SocketIO integration
    
    return jsonify({
        'message': 'Message sent successfully',
        'message_id': msg_id
    }), 201
