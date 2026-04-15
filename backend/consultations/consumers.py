"""
WebSocket Consumer for Real-time Consultation
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ConsultationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for WebRTC signaling in video consultations
    """
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'consultation_{self.room_name}'
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others in the room that a user has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
                'role': 'doctor' if getattr(self.user, 'role', '') == 'DOCTOR' else 'patient'
            }
        )
    
    async def disconnect(self, close_code):
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id
            }
        )
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket and broadcast to others
        """
        data = json.loads(text_data)
        
        # Add sender info
        data['sender_id'] = self.user.id
        
        print(f"[Signaling] Broadcaster: User {self.user.id} sending {data.get('type')}")
        
        # Broadcast the signal/message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signal_message',
                'message': data
            }
        )
    
    async def signal_message(self, event):
        """
        Send signal to WebSocket (but don't send back to the sender)
        """
        message = event['message']
        
        # Don't send the message back to the sender
        if message.get('sender_id') != self.user.id:
            print(f"[Signaling] Receiver: User {self.user.id} catching {message.get('type')}")
            await self.send(text_data=json.dumps(message))

    async def user_joined(self, event):
        if event.get('user_id') != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user-joined',
                'user_id': event['user_id'],
                'username': event['username'],
                'role': event['role']
            }))

    async def user_left(self, event):
        if event.get('user_id') != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user-left',
                'user_id': event['user_id']
            }))

