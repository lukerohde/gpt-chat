import os
from django.db.models import (Model, IntegerField, CharField, FloatField, TextField, DateTimeField, JSONField, ForeignKey, 
                              CASCADE)
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


# from .brain.working_memory import WorkingMemory
# from .brain.long_term_memory import LongTermMemory
# from .brain.chatgpt import ChatGPT
import datetime
import secrets
import markdown
import bleach

class Bot(Model):

    botname = CharField(max_length=100, default=os.getenv("BOT_NAME"))
    end_point = CharField(max_length=255, default=f"http://bot:8001/api/message/[botname]/")
    description = CharField(max_length=255, null=True)
    config = TextField(null=True)
    
    owner = ForeignKey(User, null=True, on_delete=CASCADE, verbose_name='owner',
                      related_name='bots', db_index=True)
    bot_user = ForeignKey(User, null=True, on_delete=CASCADE, verbose_name='bot_user',
                      related_name='bot', db_index=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # Call parent's constructor

        # self.long_term_memory = None 
        # self.working_memory = None
        # self.openai_chat = None
        
        
    def __str__(self):
        return str("{} {}".format(self.id, self.botname))
    
    def save(self, *args, **kwargs): 
        if self.pk is None:
            bot_user_password = secrets.token_hex(16)
            bot_user = User.objects.create_user(username=self.botname, password=bot_user_password)
            self.bot_user = bot_user
            Token.objects.create(user=bot_user) # Create a token for the bot_user
        
        super().save(*args, **kwargs) # Call parent's save method  
    
    # def load_user_history(self,username):
    #     self.long_term_memory=LongTermMemory(self.openai_api_key, self.openai_embedding_model, self.botname, username)
    #     self.working_memory=WorkingMemory(self, username)
    #     self.openai_chat = ChatGPT(
    #         self.openai_api_key, 
    #         self.openai_completion_model, 
    #         self.openai_temperature, 
    #         self.openai_response_tokens,
    #     )
    

    # def add_dialog(self, username, prompt):

    #     prompt = prompt # expect user markdown

    #     self.working_memory.add_dialog(
    #         username,
    #         datetime.datetime.now(),
    #         prompt
    #     )
        
    #     bot_memory = self.working_memory.retrieve()
    #     bot_memory += f"\n\n{self.botname}: "
        
    #     answer = self.openai_chat.answer(bot_memory)
        
    #     self.working_memory.add_dialog(
    #         self.botname,
    #         datetime.datetime.now(),
    #         answer
    #     )

    #     self.working_memory.retrieve() # just to flush the response to disk

    #     answer = markdown.markdown(answer) # expect markdown back, and convert to HTML
    #     return answer
    