import backoff
import openai
import json 
import os
from aiohttp import ClientSession

class ChatGPT():

    def __init__(self, model = "Gpt-4", llm_config = {}):
        self.model = model

        self.api_key = llm_config.get('OPENAI_API_KEY') or os.environ['OPENAI_API_KEY']
    
    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def ask(self, chatml):
        async with ClientSession() as session:
            url = 'https://api.openai.com/v1/chat/completions'
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key }",
            }

            payload = {
                "model": self.model,
                "messages": chatml
            }
            async with session.post(url, json=payload, headers=headers) as response:
                result =  await response.text()
                    
            result = json.loads(result)

            result['reply'] = ""
            
            if 'choices' in result:
                result['reply'] = result['choices'][0]['message']['content']
            elif 'error' in result:
                result['reply'] = f"OpenAI Error: {result['error']['message']}"
            else:
                result['reply'] = f"An unknown error occurred"   
            
            return result['reply']
       
    
    @staticmethod
    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def ask(messages, model = "gpt-4", api_key = None):
        async with ClientSession() as session:
            url = 'https://api.openai.com/v1/chat/completions'
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key or os.environ['OPENAI_API_KEY']}",
            }

            payload = {
                "model": model,
                "messages": messages
            }
            async with session.post(url, json=payload, headers=headers) as response:
                result =  await response.text()
                    
            result = json.loads(result)

            result['reply'] = ""
            
            if 'choices' in result:
                result['reply'] = result['choices'][0]['message']['content']
            elif 'error' in result:
                result['reply'] = f"OpenAI Error: {result['error']['message']}"
            else:
                result['reply'] = f"An unknown error occurred"   
            
            return result

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
       