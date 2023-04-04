from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.template.loader import render_to_string

def message_notification(message, user):
    html = render_to_string('chat/_message_list.html', {'messages': [message,], 'current_user': user})
    notification = { 
        'type': 'recieve_group_message', 
        'message': html
    }
    return notification

def send_message_notifications(message):
    """
    Inform client there is a new message.
    """            
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("{}".format(message.user.id), message_notification(message, message.user))
    async_to_sync(channel_layer.group_send)("{}".format(message.recipient.id),  message_notification(message, message.recipient))
    
    # temp hack
    if "bot" in message.recipient.username:
        signal = {'type': 'add_dialog', 'message.id': '{}'.format(message.id)}
        async_to_sync(channel_layer.send)('bot-task', signal)
