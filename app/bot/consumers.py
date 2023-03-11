from time import sleep
from channels.consumer import SyncConsumer
from core.models import MessageModel
from .models import Bot

class BotTaskConsumer(SyncConsumer):
    def add_dialog(self, message):
        # instantiate a new instance of a bot for each user/bot combo
        # we'll have to update the bot to keep a separate memory for each user
        # for now each bot will be a class of bot with configuration in admin


        print('in dialog' + "{}".format(message))
        m = self.get_message(message['message.id'])

        bot = bot = Bot.objects.filter(botname=m.recipient.username).first()
        if bot is not None:
            bot.load_user_history(m.user.username)
            answer = bot.add_dialog(m.user.username, m.body)

            reply = MessageModel(user=m.recipient, recipient=m.user, body=answer)
            reply.save()

    def get_message(self, id):
        m = MessageModel.objects.get(pk=id)
        return m
        