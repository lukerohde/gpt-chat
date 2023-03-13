import os
from django.db import models
from django.contrib.auth.models import User
from .brain.working_memory import WorkingMemory
from .brain.long_term_memory import LongTermMemory
from .brain.chatgpt import ChatGPT
import datetime
import secrets
import markdown

class Bot(models.Model):

    botname = models.CharField(max_length=100, default=os.getenv("BOT_NAME"))
    primer = models.TextField()
    openai_api_key = models.CharField(max_length=100, default=os.getenv("OPENAI_API_KEY"))
    openai_completion_model = models.CharField(max_length=100, default=os.getenv("OPENAI_COMPLETION_MODEL") or "text-davinci-003")
    openai_embedding_model = models.CharField(max_length=100, default=os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-ada-002")
    openai_token_length = models.FloatField(default=os.getenv("OPENAI_TOKENS_LENGTH") or 3.5)
    openai_temperature = models.FloatField(default=os.getenv("OPENAI_TEMPERATURE") or 0.8)
    openai_response_tokens = models.IntegerField(default=os.getenv("OPENAI_RESPONSE_TOKENS") or 256)
    openai_max_tokens = models.IntegerField(default=os.getenv("OPENAI_MAX_TOKENS") or 4000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # Call parent's constructor

        self.long_term_memory = None 
        self.working_memory = None
        self.openai_chat = None
        
        
    def __str__(self):
        return str("{} {}".format(self.id, self.botname))
    
    def save(self, *args, **kwargs): 
        if self.pk is None:
            user = User.objects.create_user(username=self.botname, password=secrets.token_hex(16)) # Create user 
        super().save(*args, **kwargs) # Call parent's save method  
    
    def load_user_history(self,username):
        self.long_term_memory=LongTermMemory(self.openai_api_key, self.openai_embedding_model, self.botname, username)
        self.working_memory=WorkingMemory(self, username)
        self.openai_chat = ChatGPT(
            self.openai_api_key, 
            self.openai_completion_model, 
            self.openai_temperature, 
            self.openai_response_tokens,
        )
    

    def add_dialog(self, username, prompt):

        prompt = prompt # expect user markdown

        self.working_memory.add_dialog(
            username,
            datetime.datetime.now(),
            prompt
        )
        
        bot_memory = self.working_memory.retrieve()
        bot_memory += f"\n\n{self.botname}: "
        
        answer = self.openai_chat.answer(bot_memory)
        
        self.working_memory.add_dialog(
            self.botname,
            datetime.datetime.now(),
            answer
        )

        self.working_memory.retrieve() # just to flush the response to disk

        answer = markdown.markdown(answer) # expect markdown back, and convert to HTML
        return answer
    