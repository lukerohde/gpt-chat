from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
import redis
import json
import os
import aiohttp
import asyncio
from bot.models import Bot
from rest_framework.authtoken.models import Token
from core.models import MessageModel
from django.db.models import Q

def web_client_notification(message, recipient):
    html = render_to_string('chat/_message_list.html', {'messages': [message,], 'current_user': recipient})
    notification = { 
        'type': 'recieve_group_message', 
        'message': html
    }
    return notification

def bot_notification(messages, user_profile_bot_data):
    
    payload = [{
        'user': m.user.username,
        'recipient': m.recipient.username, 
        'body': m.body,
        'timestamp': m.timestamp.isoformat()
    } for m in messages ]

    notification = {
        'type': 'direct_message',
        'reply_to': f"TBD",
        'messages': payload,
        'user_profile_bot_data': user_profile_bot_data
    }
    return notification

async def send_message_to_bot(end_point, token, notification):
    async with aiohttp.ClientSession() as session:
    
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}',
        }
        async with session.post(end_point, data=json.dumps(notification), headers=headers) as response:
            return await response.text()

def send_message_notifications(message):
    """
    Inform client there is a new message.
    """            
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("{}".format(message.user.id), web_client_notification(message, message.user))
    async_to_sync(channel_layer.group_send)("{}".format(message.recipient.id), web_client_notification(message, message.recipient))
    
    bot = Bot.objects.filter(botname=message.recipient.username).first()
    result = None

    if bot:
        message_history = MessageModel.objects.filter(
                    Q(recipient=message.recipient, user=message.user) |
                    Q(recipient=message.user, user=message.recipient)
                ).order_by('-timestamp')[:40][::-1] # enable 20 questions - need to protect from token overload
        
        user_profile_bot_data = message.user.userprofile.bot_data.get(message.recipient.username, {})
        
        result = async_to_sync(send_message_to_bot)(bot.end_point, Token.objects.filter(user=bot.bot_user).first(), bot_notification(message_history, user_profile_bot_data))
    return result
