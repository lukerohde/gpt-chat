from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.models import MessageModel
from core.utils import send_message_notifications
from core.forms import SendMessageForm

class ChatView(View):
    def get(self, request, user_id=None):
        users = User.objects.exclude(pk=request.user.id)
        selected_user = users.filter(id=user_id).first() if user_id else users.first()
        user_id = selected_user.id if selected_user else None

        messages = MessageModel.objects.filter(
                    Q(recipient=request.user, user__id=user_id) |
                    Q(recipient__id=user_id, user=request.user)
                ).order_by('timestamp')
        
        context = {'selected_user_id': user_id, 'users': users, 'messages': messages,'form': SendMessageForm(), 'current_user': request.user}
        
        if request.is_ajax():
            html = render_to_string('chat/_message_list.html', context)
            return JsonResponse({'html': html})
        else:
            return render(request, 'chat/chat.html', context)

    def post(self, request, user_id):
        # Handle the POST request
        message_text = request.POST.get('message')
        recipient = User.objects.get(pk=user_id)

        message = MessageModel.objects.create(user_id=request.user.id, recipient=recipient, body=message_text)
        
        send_message_notifications(message)

        if request.is_ajax():
            return JsonResponse({'status': 'ok'}, status=200)
        else:   
            # Redirect to the chat page
            return redirect('chat', user_id=user_id)