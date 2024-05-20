import backoff
import os

import openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class LangChainLLM():

    def __init__(self, model = "gpt-4o", llm_config = {}):
        self.model = model
        self.api_key = llm_config.get('OPENAI_API_KEY') or os.environ['OPENAI_API_KEY']
        self.config = llm_config

    def get_client(self, key=None):

        client =  ChatOpenAI(
            temperature=self.config.get('temperature',0), 
            api_key=self.api_key, 
            model=self.model,
            max_tokens=self.config.get('response_tokens', 512)
        )

        return client

    @backoff.on_exception(backoff.expo, openai.RateLimitError, max_tries=10)
    async def ask(self, chatml):
        client = self.get_client()
        messages = self.messages(chatml)

        response_buffer = ""
        chunk_count = 0
        async for chunk in client.astream(messages):
            response_buffer += chunk.content
            chunk_count += 1
        
        return response_buffer
    

    def messages(self, chatml):
        messages = []
        for message in chatml:
            if message['role'] == 'system':
                messages.append(SystemMessage(message['content']))
            elif message['role'] == 'assistant':
                messages.append(AIMessage(message['content']))
            else:
                messages.append(HumanMessage(message['content']))
            
        return messages

    @staticmethod
    def chatml(message, bot_name, dress_function = None):
        if dress_function:
            content = dress_function(message)
        else:
            content = message['body']

        chat_ml = { 
            "content": content,
            "name": message["user"],
            "role": "assistant" if message["user"] == bot_name else "user"
         }

        return chat_ml
       