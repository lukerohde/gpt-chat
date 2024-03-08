from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
import redis
import json
import os
import aiohttp
import asyncio
import requests
from bot.models import Bot
from rest_framework.authtoken.models import Token
from core.models import MessageModel
from django.db.models import Q
from celery import Celery, shared_task

def web_client_message_notification(message, recipient):
    html = render_to_string('chat/_message_list.html', {'messages': [message,], 'current_user': recipient})
    notification = { 
        'type': 'recieve_group_message', 
        'message': html
    }
    return notification

def bot_message_notification(message, type = None):
    
    message_history = MessageModel.objects.filter(
                    Q(recipient=message.recipient, user=message.user) |
                    Q(recipient=message.user, user=message.recipient)
                ).order_by('-timestamp') # [:40][::-1] # enable 20 questions - need to protect from token overload
        
    user_profile_bot_data = message.user.userprofile.bot_data.get(message.recipient.username, {})
        
    payload = [{
        'user': m.user.username,
        'recipient': m.recipient.username, 
        'body': m.body,
        'timestamp': m.timestamp.isoformat()
    } for m in message_history ]

    notification = {
        'type': type or 'direct_message',
        'reply_to': f"TBD",
        'messages': payload,
        'user_profile_bot_data': user_profile_bot_data
    }

    return notification

@shared_task
async def async_send_to_bot(end_point, token, payload):
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}',
        }
        async with session.post(end_point, data=json.dumps(payload), headers=headers) as response:
            return await response.text()

@shared_task
def send_to_bot(end_point, token, payload):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {token}',
    }
    response = requests.post(end_point, data=json.dumps(payload), headers=headers)
    return response.text

def send_message_notifications(message):
    """
    Inform client there is a new message.
    """            
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("{}".format(message.user.id), web_client_message_notification(message, message.user))
    async_to_sync(channel_layer.group_send)("{}".format(message.recipient.id), web_client_message_notification(message, message.recipient))
    
    result = None

    bot = Bot.objects.filter(botname=message.recipient.username).first() #TODO simplify this check  
    if bot:
        token = Token.objects.filter(user=bot.bot_user).first()
    
        payload = bot_message_notification(message)
        #result = async_to_sync(send_to_bot)(bot.end_point, token, payload)
        result = send_to_bot(bot.end_point, token, payload)
    
    return result

def send_bot_reminder(message):
    # Check for reminder metadata and schedule a reminder
    reminder = message.metadata.get('reminder', {})
    if reminder:
        
        # Extract scheduling information from reminder_metadata
        countdown_seconds = reminder.get('countdown_seconds', 0)
        if countdown_seconds:   
            bot = Bot.objects.filter(botname=message.user.username).first() #TODO simplify this check  
            
            if bot: 
                token = Token.objects.filter(user=bot.bot_user).first()
        
                payload = bot_message_notification(message, 'reminder')
                payload['reminder'] = reminder
                
                #print(payload)
                #schedule send via celery
                #import ipdb; ipdb.set_trace()
                send_to_bot.apply_async((bot.end_point, str(token.key), payload), countdown = countdown_seconds)
