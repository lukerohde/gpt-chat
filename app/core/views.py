from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string

from core.models import MessageModel

def chat(request, user_id=None):
    # You can retrieve the User object based on the user_id, if needed.
    # user = User.objects.get(pk=user_id)
    users = User.objects.exclude(pk=request.user.id)

    messages = MessageModel.objects.filter(
                Q(recipient=request.user, user__id=user_id) |
                Q(recipient__id=user_id, user=request.user)
            ).order_by('-timestamp')
    
    context = {'selected_user_id': user_id, 'users': users, 'messages': messages, 'request': request}
    if request.is_ajax():
        html = render_to_string('chat/_message_list.html', context)
        return JsonResponse({'html': html})
    else:
        return render(request, 'chat/chat.html', context)