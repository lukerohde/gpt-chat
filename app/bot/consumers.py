from time import sleep
from channels.consumer import SyncConsumer
from core.models import MessageModel

class BotTaskConsumer(SyncConsumer):
    def add_dialog(self, message):
        print('in dialog' + "{}".format(message))
        sleep(1)
        m = self.get_message(message['message.id'])
        body = f"Hi {m.user.username}!"
        reply = MessageModel(user=m.recipient, recipient=m.user, body=body)
        reply.save()

    def get_message(self, id):
        m = MessageModel.objects.get(pk=id)
        return m
        